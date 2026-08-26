#include "Timer.h"

// 依赖 Arduino-ESP32 core >= 3.0；2.x 的 timerBegin/timerAlarm 签名不同
static hw_timer_t* s_timer = nullptr;
static volatile bool s_tick = false;

void IRAM_ATTR onTimerISR() {
    // ISR 只置标志：禁止在中断里做采样、串口输出等耗时操作
    s_tick = true;
}

void timerInit() {
    s_timer = timerBegin(1000000);  // 1 MHz 计数频率，1 tick = 1 us
    timerAttachInterrupt(s_timer, &onTimerISR);
    timerAlarm(s_timer, static_cast<uint64_t>(SAMPLE_INTERVAL_MS) * 1000U, true, 0);
}

// 主循环每次调用；有到期采样节拍时消费并返回 true
bool timerConsumeTick() {
    if (!s_tick) {
        return false;
    }
    s_tick = false;
    return true;
}
