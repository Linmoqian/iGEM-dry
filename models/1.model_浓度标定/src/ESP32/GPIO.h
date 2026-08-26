#pragma once
#include <Arduino.h>

constexpr int SENSOR_PIN = 13;  // 传感器 ADC 输入引脚

void gpioInit();
int readSensorRaw();
