#pragma once

#include <cstdint>

namespace cv3 {

// Konami VRC4/VRC6/VRC7 IRQ counter used by Mapper 24.
// This models the mapper-side IRQ source only. CPU interrupt polling/latency is
// deliberately left to the CPU runtime.
class Vrc6Irq {
public:
    void cpu_write(std::uint16_t address, std::uint8_t value);
    void step_cpu_cycle();

    [[nodiscard]] std::uint8_t latch() const noexcept { return latch_; }
    [[nodiscard]] std::uint8_t counter() const noexcept { return counter_; }
    [[nodiscard]] bool enabled() const noexcept { return enable_; }
    [[nodiscard]] bool cycle_mode() const noexcept { return cycle_mode_; }
    [[nodiscard]] bool enable_after_ack() const noexcept { return enable_after_ack_; }
    [[nodiscard]] bool irq_pending() const noexcept { return irq_pending_; }

private:
    void write_control(std::uint8_t value);
    void acknowledge();
    void clock_counter();

    std::uint8_t latch_ = 0;
    std::uint8_t counter_ = 0;
    bool cycle_mode_ = false;
    bool enable_ = false;
    bool enable_after_ack_ = false;
    bool irq_pending_ = false;

    // Scanline mode starts at 341 PPU dots and consumes 3 dots per CPU cycle.
    // Allow negative values so 341/3 naturally yields 114,114,113 cycles.
    int prescaler_ = 341;
};

}  // namespace cv3
