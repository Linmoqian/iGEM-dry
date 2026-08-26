#pragma once
#include <Arduino.h>

// 单次采集样本：仅光强 + 时间戳
struct SampleData {
    float lightIntensity;  // 光强，标定系数确定前先存原始 ADC 读数
    uint32_t timeMs;       // 开机以来的毫秒时间戳
};
