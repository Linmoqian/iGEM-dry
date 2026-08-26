#include "serial.h"

void serialInit() {
    Serial.begin(BAUD_RATE);
}

// 行协议："<lightIntensity>,<timeMs>\n"，供 PC 端按行解析
void sendSample(const SampleData& sample) {
    Serial.print(sample.lightIntensity, 4);
    Serial.print(',');
    Serial.println(sample.timeMs);
}
