/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#include <Arduino.h>
#include <cmath>
#include "GPS.h"
#include "data.h"

SensorData getSensorData(const char* sensorId) {
    SensorData data{sensorId, static_cast<uint32_t>(millis()), false, NAN, NAN};
    data.gpsValid = readGps(data.latitudeDeg, data.longitudeDeg);
    return data;
}
