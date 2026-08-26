#include <Arduino.h>
#include "DATA.h"
#include "GPIO.h"
#include "serial.h"
#include "Timer.h"

void setup() {
    serialInit();
    gpioInit();
    timerInit();
}

void loop() {
    if (!timerConsumeTick()) {
        return;
    }

    SampleData sample;
    sample.lightIntensity = static_cast<float>(readSensorRaw());
    sample.timeMs = millis();
    sendSample(sample);
}
