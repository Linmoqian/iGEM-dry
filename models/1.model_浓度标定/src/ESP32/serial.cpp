#include <Arduino.h>
#include "DATA.h"
#include "serial.h"

void serialInit() {
    Serial.begin(SERIAL_BAUD_RATE);
}

void sendSensorValue(int value) {
    Serial.println(value);
}
