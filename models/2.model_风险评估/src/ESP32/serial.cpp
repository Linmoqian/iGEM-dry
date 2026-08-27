/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#include <Arduino.h>
#include "serial.h"

void serialInit() {
    Serial.begin(SERIAL_BAUD_RATE);
}

void sendSensorData(const SensorData& data) {
    Serial.print(data.sensorId);
    Serial.print(',');
    Serial.print(data.deviceUptimeMs);
    Serial.print(',');
    Serial.print(data.gpsValid ? 1 : 0);

    if (!data.gpsValid) {
        Serial.println(",,");
        return;
    }

    Serial.print(',');
    Serial.print(data.latitudeDeg, 6);
    Serial.print(',');
    Serial.println(data.longitudeDeg, 6);
}
