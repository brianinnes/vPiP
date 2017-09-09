#include "vpipController.h"
#include <unistd.h>
#include <stdio.h>
#include <cstring>
#include <iostream>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

vpipController::vpipController(unsigned char address) {
    this->devAddr = address;
    this->i2cFileDesc = 0;
    this->setDefaultConfig();
    printf("Size of config = %d\n", sizeof(this->controllerConfig));
}

vpipController::~vpipController() {
    this->closeI2C();
}

int vpipController::openI2C() {
    if (0 != this->i2cFileDesc) {
        closeI2C();
    }
    this->i2cFileDesc = open("/dev/i2c-1", O_RDWR);
    if(this->i2cFileDesc < 0){
        printf("Could not open I2C connection\n");
        return 1;
    }
    if (ioctl(this->i2cFileDesc, I2C_SLAVE, this->devAddr) < 0) {
        printf("Failed to acquire bus access\n");
        return 2;
    }
    sendConfigToController();
    return 0;
}

void vpipController::closeI2C() {
    if (0 != this->i2cFileDesc) {
        close(this->i2cFileDesc);
        this->i2cFileDesc = 0;
    }
}

unsigned char vpipController::sendByte(unsigned char data) {
    unsigned char queueLength = 0;
    unsigned char buff[2];
    buff[0] = DATA_BYTE;
    buff[1] = data;
    this->sendToControllerResponse(buff, 2, &queueLength, 1);
    return queueLength;
}

unsigned char vpipController::getQueueLength() {
    unsigned char queueLength = 0;
    unsigned char buff = DATA_CAPACITY;
    this->sendToControllerResponse(&buff, 1, &queueLength, 1);
    return queueLength;
}

unsigned char vpipController::sendDataBlock(unsigned char *data, int length){
    unsigned char queueLength = 0;
    int sendLength = length + 1;
    unsigned char buff[length];
    buff[0] = DATA_BLOCK;
    memcpy(buff+1,data, length);
    this->sendToControllerResponse(buff, sendLength, &queueLength, 1);
    return queueLength;
}


void vpipController::setDefaultConfig() {
    this->controllerConfig.pins.stepperEnable = 9;
    this->controllerConfig.pins.leftStep = 3;
    this->controllerConfig.pins.leftDir = 2;
    this->controllerConfig.pins.rightStep = 5;
    this->controllerConfig.pins.rightDir = 4;
    this->controllerConfig.pins.microSteppingM0 = 8;
    this->controllerConfig.pins.microSteppingM1 = 7;
    this->controllerConfig.pins.microSteppingM2 = 6;
    this->controllerConfig.pins.penServo = 14;
    this->controllerConfig.pins.leftStopSense = 16;
    this->controllerConfig.pins.rightStopSense = 15;
    this->controllerConfig.penUpAngle = 170;
    this->controllerConfig.penDownAngle = 85;
    this->controllerConfig.autohome = true;
    this->controllerConfig.microSteppingM0 = 0;
    this->controllerConfig.microSteppingM1 = 1;
    this->controllerConfig.microSteppingM2 = 0;
    this->controllerConfig.senseTimeout = 2500;
    this->controllerConfig.senseTrigger = 250;
}

int vpipController::sendToControllerNoResponse(unsigned char*data, int length) {
    struct i2c_rdwr_ioctl_data pkt;
    struct i2c_msg msg[1];
    msg[0].addr = this->devAddr;
    msg[0].flags = 0;
    msg[0].len = length;
    msg[0].buf = data;
    pkt.msgs = msg;
    pkt.nmsgs = 1;

    int ret = ioctl(this->i2cFileDesc, I2C_RDWR, &pkt);
    if (0 > ret) {
        printf("Write to I2C device failed : %d - %s\n", ret, strerror(errno));
    }
    return ret;
}

int vpipController::sendToControllerResponse(unsigned char *data, int length, unsigned char *resp, int rLength) {
    struct i2c_rdwr_ioctl_data pkt;
    struct i2c_msg msg[2];
    msg[0].addr = this->devAddr;
    msg[0].flags = 0;
    msg[0].len = length;
    msg[0].buf = data;
    msg[1].addr = this->devAddr;
    msg[1].flags = I2C_M_RD;
    msg[1].len = rLength;
    msg[1].buf = resp;
    pkt.msgs = msg;
    pkt.nmsgs = 2;

    int ret = ioctl(this->i2cFileDesc, I2C_RDWR, &pkt);
    if (0 > ret) {
        printf("Write with response to I2C device failed : %d - %s\n", ret, strerror(errno));
    }
    return ret;
}



void vpipController::sendConfigToController() {
    int length = sizeof(this->controllerConfig) + 1;
    unsigned char buff[length];
    buff[0] = CONFIG_ALL;
    memcpy(buff+1,(void*)&this->controllerConfig, sizeof(this->controllerConfig));
    this->sendToControllerNoResponse(buff, length);
}
