#ifndef  _VPIP_CONTROLLER_H
#define _VPIP_CONTROLLER_H

#define CONFIG_ALL 0x00
#define DATA_BYTE 0x80
#define DATA_CAPACITY 0x81
#define DATA_BLOCK 0x82


struct __attribute__ ((packed)) config_t {
    struct __attribute__ ((packed)) pins_t {
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
};

class vpipController
{
    public:
    vpipController(unsigned char addr);
    ~vpipController();

    int openI2C();
    void closeI2C();

    unsigned char sendByte(unsigned char data);
    unsigned char getQueueLength();
    unsigned char sendDataBlock(unsigned char *data, int length);

    private:
    unsigned char devAddr;
    int i2cFileDesc;
    config_t controllerConfig;

    void setDefaultConfig();
    int sendToControllerNoResponse(unsigned char*data, int length);
    int sendToControllerResponse(unsigned char *data, int length, unsigned char *resp, int rLength);
    void sendConfigToController();
};

#endif // _VPIP_CONTROLLER_H
