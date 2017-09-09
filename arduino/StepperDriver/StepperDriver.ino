#include <Wire.h>

// comment out to disable PENUP support
#define ENABLE_PENUP

#define I2C_ADDRESS 8

struct config_t {
    struct pins_t {
        unsigned char stepperEnable;
        unsigned char leftStep;
        unsigned char rightStep;
        unsigned char leftDir;
        unsigned char rightDir;
        unsigned char microSteppingM0;
        unsigned char microSteppingM1;
        unsigned char microSteppingM2;
        unsigned char penServo;
        unsigned char leftStopSense;
        unsigned char rightStopSense;
    } pins;
    unsigned char penUpAngle;
    unsigned char penDownAngle;
    bool autohome;
    unsigned char microSteppingM0;
    unsigned char microSteppingM1;
    unsigned char microSteppingM2;
    short senseTimeout;
    short senseTrigger;
} controllerConfig;

#ifdef ENABLE_PENUP
#include <Servo.h>
Servo penUpServo;
char penTransitionDirection; // -1, 0, 1
const long PENUP_TRANSITION_US = 524288; // time to go from pen up to down, or down to up
const int PENUP_TRANSITION_US_LOG = 19; // 2^19 = 524288
const long PENUP_COOLDOWN_US = 1250000;
#endif

const unsigned int TIME_SLICE_US = 2048; // number of microseconds per time step
const unsigned int TIME_SLICE_US_LOG = 11; // log base 2 of TIME_SLICE_US
const unsigned int POS_FACTOR = 8; // fixed point factor each position is multiplied by
const unsigned int POS_FACTOR_LOG = 3; // log base 2 of POS_FACTOR, used after multiplying two fixed point numbers together

const char RESET_COMMAND = 0x80; // -128, (128) command to reset
const char PENUP_COMMAND = 0x81; // -127, (129) command to lift pen
const char PENDOWN_COMMAND = 0x7F; // 127,(127) command to lower pen

const unsigned char MOVE_DATA_CAPACITY = 255;
char moveData[MOVE_DATA_CAPACITY]; // buffer of move data, circular buffer
unsigned char moveDataStart = 0; // where data is currently being read from
unsigned char moveDataLength = 0; // the number of items in the moveDataBuffer
unsigned char moveDataRequestPending = 0; // number of bytes requested

char leftDelta, rightDelta; // delta in the current slice
long leftStartPos, rightStartPos; // start position for this slice
long leftCurPos, rightCurPos; // current position of the spools

unsigned long curTime; // current time in microseconds
unsigned long sliceStartTime; // start of current slice in microseconds

void receiveI2CEvent(int count);
void requestI2CEvent();

// setup
// --------------------------------------
void setup() {
  Serial.begin(57600);

  // Start I2C connection
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveI2CEvent);
  Wire.onRequest(requestI2CEvent);
  ResetMovementVariables();

  Serial.println("Stepper Driver");
}

void readConfiguration() {
  int length = sizeof(controllerConfig);
  unsigned char *buff = (void *)&controllerConfig;
  for (int i = 0; i < length; i++) {
    if (Wire.available()) {
      buff[i] = Wire.read();
    }
  }

  pinMode(controllerConfig.pins.microSteppingM0, OUTPUT);
  pinMode(controllerConfig.pins.microSteppingM1, OUTPUT);
  pinMode(controllerConfig.pins.microSteppingM2, OUTPUT);
  digitalWrite(controllerConfig.pins.microSteppingM0, controllerConfig.microSteppingM0);
  digitalWrite(controllerConfig.pins.microSteppingM1, controllerConfig.microSteppingM1);
  digitalWrite(controllerConfig.pins.microSteppingM2, controllerConfig.microSteppingM2);

  pinMode(controllerConfig.pins.leftStep, OUTPUT);
  pinMode(controllerConfig.pins.leftDir, OUTPUT);
  pinMode(controllerConfig.pins.rightStep, OUTPUT);
  pinMode(controllerConfig.pins.rightDir, OUTPUT);
  pinMode(controllerConfig.pins.stepperEnable, OUTPUT);
  digitalWrite(controllerConfig.pins.stepperEnable, LOW);

  pinMode(controllerConfig.pins.leftStopSense, OUTPUT);
  pinMode(controllerConfig.pins.rightStopSense, OUTPUT);
  digitalWrite(controllerConfig.pins.leftStopSense, HIGH);
  digitalWrite(controllerConfig.pins.rightStopSense, HIGH);
#ifdef ENABLE_PENUP
  penUpServo.attach(controllerConfig.pins.penServo);
  penUpServo.write(controllerConfig.penUpAngle);
  delay(1000);
  penUpServo.write(controllerConfig.penDownAngle);
  delay(1000);
  penUpServo.write(controllerConfig.penUpAngle);
  penTransitionDirection = 0;
#endif
  if (controllerConfig.autohome) {
    digitalWrite(controllerConfig.pins.stepperEnable, LOW);
    AutoHome();
  }
}

void receiveDataByte() {
  unsigned char dataByte = 0;
  if (Wire.available()) {
    dataByte = Wire.read();
    MoveDataPut(dataByte);
  }
}

void readDataBlock() {
  while(Wire.available()) {
    unsigned char dataByte = Wire.read();
    MoveDataPut(dataByte);
  }
}

void receiveI2CEvent(int count) {
  unsigned char action;
  if (Wire.available()){
    action = Wire.read();
    switch (action) {
      case 0x00 :
        readConfiguration();
        break;
       case 0x80:
        receiveDataByte();
        break;
       case 0x81:
        break;
       case 0x82:
        readDataBlock();
       default :
        break;
    }
  }
}

void requestI2CEvent() {
  Wire.write(moveDataLength);
}

// Reset all movement variables
// --------------------------------------
void ResetMovementVariables()
{
  leftDelta = rightDelta = leftStartPos = rightStartPos = leftCurPos = rightCurPos = 0;
  sliceStartTime = curTime;
}

// Main execution loop
// --------------------------------------
void loop() {
  curTime = micros();
  while (true) {
    delayMicroseconds(100);
  }
  /*
  if (curTime < sliceStartTime) { // protect against 70 minute overflow
    sliceStartTime = 0;
  }

  long curSliceTime = curTime - sliceStartTime;

#ifdef ENABLE_PENUP
  if (penTransitionDirection) {
    UpdatePenTransition(curSliceTime);
    if (!penTransitionDirection) {
      sliceStartTime = curTime;
    }
  } else {
#endif
    // move to next slice if necessary
    while(curSliceTime > TIME_SLICE_US) {
      SetSliceVariables();
      curSliceTime -= TIME_SLICE_US;
      sliceStartTime += TIME_SLICE_US;

#ifdef ENABLE_PENUP
      if (penTransitionDirection) {
        sliceStartTime = curTime;
        return;
      }
#endif
    }

    UpdateStepperPins(curSliceTime);
#ifdef ENABLE_PENUP
  }
#endif

//  ReadSerialMoveData();
//  RequestMoreSerialMoveData();
*/

}

// Update stepper pins
// --------------------------------------
void UpdateStepperPins(long curSliceTime) {
  long leftTarget = ((long(leftDelta) * curSliceTime) >> TIME_SLICE_US_LOG) + leftStartPos;
  long rightTarget = ((long(rightDelta) * curSliceTime) >> TIME_SLICE_US_LOG) + rightStartPos;

  int leftSteps = (leftTarget - leftCurPos) >> POS_FACTOR_LOG;
  int rightSteps = (rightTarget - rightCurPos) >> POS_FACTOR_LOG;

  boolean leftPositiveDir = true;
  if (leftSteps < 0) {
    leftPositiveDir = false;
    leftSteps = -leftSteps;
  }
  boolean rightPositiveDir = true;
  if (rightSteps < 0) {
    rightPositiveDir = false;
    rightSteps = -rightSteps;
  }

  do {
    if (leftSteps) {
      Step(controllerConfig.pins.leftStep, controllerConfig.pins.leftDir, leftPositiveDir);
      if (leftPositiveDir) {
        leftCurPos += POS_FACTOR;
      } else {
        leftCurPos -= POS_FACTOR;
      }
      leftSteps--;

//      UpdateStatusLeds(leftCurPos >> 13);
    }

    if (rightSteps) {
      Step(controllerConfig.pins.rightStep, controllerConfig.pins.rightDir, rightPositiveDir);
      if (rightPositiveDir) {
        rightCurPos += POS_FACTOR;
      } else {
        rightCurPos -= POS_FACTOR;
      }
      rightSteps--;
    }

    if (leftSteps || rightSteps) {
      delayMicroseconds(50); // delay a small amount of time before refiring the steps to smooth things out
    } else {
      break;
    }
  } while(true);
}

// Update pen position
// --------------------------------------
#ifdef ENABLE_PENUP
void UpdatePenTransition(long curSliceTime) {

  //int targetAngle = ((float)(PENDOWN_ANGLE - PENUP_ANGLE) * ((float)curSliceTime / (float)PENUP_TRANSITION_US)) + PENUP_ANGLE;
  //if (targetAngle > PENDOWN_ANGLE) {
    //targetAngle = PENDOWN_ANGLE;

    if (curSliceTime > PENUP_COOLDOWN_US) {
      penTransitionDirection = 0; // are done moving the pen servo
    }
  //}

  if (penTransitionDirection == 1) {
  //targetAngle = 180 - targetAngle;
    penUpServo.write(controllerConfig.penUpAngle);
  } else if (penTransitionDirection == -1) {
    penUpServo.write(controllerConfig.penDownAngle);
  }

  //penUpServo.write(targetAngle);
}
#endif

// Step
// --------------------------------------
void Step(int stepPin, int dirPin, boolean dir) {
  digitalWrite(dirPin, dir);

  digitalWrite(stepPin, LOW);
  digitalWrite(stepPin, HIGH);
}

// Set all variables based on the data currently in the buffer
// --------------------------------------
void SetSliceVariables() {
  // set slice start pos to previous slice start plus previous delta
  leftStartPos = leftStartPos + long(leftDelta);
  rightStartPos = rightStartPos + long(rightDelta);

  if (moveDataLength < 2) {
    leftDelta = rightDelta = 0;
  } else {
    leftDelta = MoveDataGet();
    rightDelta = MoveDataGet();

#ifdef ENABLE_PENUP
    if (leftDelta == PENUP_COMMAND) {
      leftDelta = rightDelta = 0;
      penTransitionDirection = 1;
    } else if (leftDelta == PENDOWN_COMMAND) {
      leftDelta = rightDelta = 0;
      penTransitionDirection = -1;
    }
#else
    if (leftDelta == PENUP_COMMAND || leftDelta == PENDOWN_COMMAND) {
       leftDelta = rightDelta = 0;
    }
#endif
  }
}


// Read serial data if its available
// --------------------------------------
void ReadSerialMoveData() {

  if(Serial.available()) {
    char value = Serial.read();

    // Check if this value is the sentinel reset value
    if (value == RESET_COMMAND) {
      ResetMovementVariables();
      moveDataRequestPending = 0;
      moveDataLength = 0;
      return;
    }

    MoveDataPut(value);
    moveDataRequestPending--;

  }
}

// Put a value onto the end of the move data buffer
// --------------------------------------
void MoveDataPut(char value) {
  int writePosition = moveDataStart + moveDataLength;
  if (writePosition >= MOVE_DATA_CAPACITY) {
    writePosition = writePosition - MOVE_DATA_CAPACITY;
  }

  moveData[writePosition] = value;

  if (moveDataLength == MOVE_DATA_CAPACITY) { // full, overwrite existing data
    moveDataStart++;
    if (moveDataStart == MOVE_DATA_CAPACITY) {
      moveDataStart = 0;
    }
  }
  else {
    moveDataLength++;
  }
}

// Return a piece of data sitting in the moveData buffer, removing it from the buffer
// --------------------------------------
char MoveDataGet() {
  if (moveDataLength == 0) {
    return 0;
  }

  char result = moveData[moveDataStart];
  moveDataStart++;
  if (moveDataStart == MOVE_DATA_CAPACITY) {
    moveDataStart = 0;
  }
  moveDataLength--;

  return result;
}

// Return the amount of data sitting in the moveData buffer
// --------------------------------------
void RequestMoreSerialMoveData() {
  if (moveDataRequestPending > 0 || MOVE_DATA_CAPACITY - moveDataLength < 128)
    return;

  // request 128 bytes of data
  Serial.write(128);
  moveDataRequestPending = 128;
}


void AutoHome() {
  bool rHoming = true;
  bool lHoming = true;

  for (int i = 0; i < 200; i++) {
    Step(controllerConfig.pins.leftStep, controllerConfig.pins.leftDir, 0);
    Step(controllerConfig.pins.rightStep, controllerConfig.pins.rightDir, 1);
   delay(10);
  }

  while (rHoming || lHoming) {
    pinMode(controllerConfig.pins.leftStopSense, INPUT);
    pinMode(controllerConfig.pins.rightStopSense, INPUT);
    digitalWrite(controllerConfig.pins.leftStopSense, LOW);
    digitalWrite(controllerConfig.pins.rightStopSense, LOW);
    unsigned long startTime = micros();
    unsigned long time = micros() - startTime;
    bool lhigh = true;
    bool rhigh = true;
    while ((lhigh || rhigh) && (time < controllerConfig.senseTimeout))
    {
      if (lhigh && lHoming && (digitalRead(controllerConfig.pins.leftStopSense) == LOW)) {
        lhigh = false;
        if (time > controllerConfig.senseTrigger) {
          lHoming = false;
        }
      }
      if (rhigh && rHoming &&(digitalRead(controllerConfig.pins.rightStopSense) == LOW)) {
        rhigh = false;
        if (time > controllerConfig.senseTrigger) {
          rHoming = false;
        }
      }
      time = micros() - startTime;
    }
    pinMode(controllerConfig.pins.leftStopSense, OUTPUT);
    pinMode(controllerConfig.pins.rightStopSense, OUTPUT);
    digitalWrite(controllerConfig.pins.leftStopSense, HIGH);
    digitalWrite(controllerConfig.pins.rightStopSense, HIGH);
    if (lHoming) {
      Step(controllerConfig.pins.leftStep, controllerConfig.pins.leftDir, 1);
    }
    if (rHoming) {
      Step(controllerConfig.pins.rightStep, controllerConfig.pins.rightDir, 0);
    }
    delayMicroseconds(300000);
  }
}
