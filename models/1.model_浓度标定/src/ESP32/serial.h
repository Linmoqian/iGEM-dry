#pragma once
#include <Arduino.h>
#include "DATA.h"

constexpr unsigned long BAUD_RATE = 115200;

void serialInit();
void sendSample(const SampleData& sample);
