#pragma once
#include <Arduino.h>

constexpr uint32_t SAMPLE_INTERVAL_MS = 1000;  // 采样周期

void timerInit();
bool timerConsumeTick();
