#include <Arduino.h>
#include "GPIO.h"
#include "serial.h"
#include "Timer.h"

void setup() {
    serialInit();
    gpioInit();
}

void loop() {
    sendSensorValue(readSensorValue());
    waitForNextSample();
}
