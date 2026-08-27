/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#pragma once
#include "model.h"

constexpr unsigned long SERIAL_BAUD_RATE = 115200;

void serialInit();
void sendSensorData(const SensorData& data);
