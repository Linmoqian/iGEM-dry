/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#pragma once
#include <Arduino.h>

struct SensorData {
    const char* sensorId;
    uint32_t deviceUptimeMs;
    bool gpsValid;
    double latitudeDeg;
    double longitudeDeg;
};
