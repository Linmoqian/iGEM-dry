#include "GPIO.h"

void gpioInit() {
    // GPIO13 属于 ADC2，若后续启用 WiFi 需换到 ADC1 引脚（GPIO32~39）
    pinMode(SENSOR_PIN, INPUT);
}

int readSensorRaw() {
    return analogRead(SENSOR_PIN);
}
