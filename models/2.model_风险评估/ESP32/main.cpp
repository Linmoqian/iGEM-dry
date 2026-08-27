/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#include <Arduino.h>
#include "GPS.h"
#include "data.h"
#include "push.h"
#include "serial.h"

const char* SENSOR_ID = "sensor-01";
const char* PUSH_STYLE = "serial";
constexpr int GPS_RX_PIN = 16;
constexpr int GPS_TX_PIN = 17;
constexpr unsigned long GPS_BAUD_RATE = 9600;
constexpr unsigned long SAMPLE_INTERVAL_MS = 1000;

void setup() {
    serialInit();
    gpsInit(GPS_BAUD_RATE, GPS_RX_PIN, GPS_TX_PIN);
}

void loop() {
    pushInfo(getSensorData(SENSOR_ID), PUSH_STYLE);
    delay(SAMPLE_INTERVAL_MS);
}
