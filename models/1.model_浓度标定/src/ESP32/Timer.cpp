#include <Arduino.h>
#include "DATA.h"
#include "Timer.h"

void waitForNextSample() {
    delay(SAMPLE_INTERVAL_MS);
}
