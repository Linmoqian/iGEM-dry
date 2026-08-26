#include <Arduino.h>
#include "DATA.h"
#include "GPIO.h"

void gpioInit() {
    pinMode(SENSOR_PIN, INPUT);
}

int readSensorValue() {
    return analogRead(SENSOR_PIN);
}
