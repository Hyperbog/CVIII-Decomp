#include "vrc6_irq.hpp"

namespace cv3 {

void Vrc6Irq::cpu_write(std::uint16_t address, std::uint8_t value) {
    switch (address & 0xF003u) {
        case 0xF000:
            latch_ = value;
            return;
        case 0xF001:
            write_control(value);
            return;
        case 0xF002:
            acknowledge();
            return;
        default:
            return;
    }
}

void Vrc6Irq::write_control(std::uint8_t value) {
    irq_pending_ = false;
    cycle_mode_ = (value & 0x04u) != 0;
    enable_ = (value & 0x02u) != 0;
    enable_after_ack_ = (value & 0x01u) != 0;
    prescaler_ = 341;
    if (enable_) {
        counter_ = latch_;
    }
}

void Vrc6Irq::acknowledge() {
    irq_pending_ = false;
    enable_ = enable_after_ack_;
}

void Vrc6Irq::clock_counter() {
    if (counter_ == 0xFFu) {
        counter_ = latch_;
        irq_pending_ = true;
    } else {
        ++counter_;
    }
}

void Vrc6Irq::step_cpu_cycle() {
    if (!enable_) {
        return;
    }
    if (cycle_mode_) {
        clock_counter();
        return;
    }

    prescaler_ -= 3;
    if (prescaler_ <= 0) {
        prescaler_ += 341;
        clock_counter();
    }
}

}  // namespace cv3
