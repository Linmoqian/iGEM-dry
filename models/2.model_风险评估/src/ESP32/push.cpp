/*
Created on 2026-08-27
Updated on 2026-08-27
@author: https://github.com/Linmoqian
*/

#include <Arduino.h>
#include <cstring>
#include "push.h"
#include "serial.h"

static void pushToServer(const SensorData&) {
    Serial.println("[error] 云端推送协议未配置");
}

void pushInfo(const SensorData& data, const char* style) {
    if (strcmp(style, "serial") == 0) {
        sendSensorData(data);
    } else if (strcmp(style, "server") == 0) {
        pushToServer(data);
    } else {
        Serial.println("[error] 未知推送方式");
    }
}
