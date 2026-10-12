#pragma once
// Mapper 24 / VRC6a IRQ counter, ROM-free and CPU-cycle driven.
// This standalone chip primitive is NOT yet attached to the native CPU/bus.
// Reference: https://www.nesdev.org/wiki/VRC_IRQ and /wiki/VRC6.
#include <cstdint>
#include <stdexcept>

namespace jpstatic {
class Vrc6IrqCounter {
 public:
  // VRC6a addresses are exact: $F000 latch, $F001 control, $F002 ack.
  void write(uint16_t address, uint8_t value) {
    switch (address) {
      case 0xf000:
        latch_ = value;  // Changing latch does not immediately reload counter.
        break;
      case 0xf001:
        irq_line_ = false;  // Every control write acknowledges an IRQ.
        mode_cycle_ = (value & 0x04u) != 0;
        enabled_ = (value & 0x02u) != 0;
        enable_after_ack_ = (value & 0x01u) != 0;
        prescaler_ = 341;  // Reset NTSC 114/114/113 divider.
        if (enabled_) counter_ = latch_;
        break;
      case 0xf002:
        irq_line_ = false;
        enabled_ = enable_after_ack_;  // Control's A bit becomes E.
        // Ack does not reset the counter or prescaler.
        break;
      default:
        throw std::runtime_error("not a VRC6a IRQ register");
    }
  }
  // A VRC IRQ runs during VBlank and rendering-off; it does not count
  // PPU scanlines directly. CPU/mapper bus-access phasing is NOT modeled.
  void clock_cpu_cycles(uint64_t cycles) {
    for (uint64_t n = 0; n < cycles; ++n) {
      ++elapsed_cpu_cycles_;
      if (!enabled_) continue;  // Both prescaler and counter freeze.
      if (mode_cycle_) {
        clock_counter();
      } else {
        prescaler_ -= 3;
        if (prescaler_ <= 0) {
          prescaler_ += 341;
          clock_counter();
        }
      }
    }
  }
  bool irq_line() const { return irq_line_; }
  bool enabled() const { return enabled_; }
  bool cycle_mode() const { return mode_cycle_; }
  bool enabled_after_ack() const { return enable_after_ack_; }
  uint8_t latch() const { return latch_; }
  uint8_t counter() const { return counter_; }
  int prescaler() const { return prescaler_; }
  uint64_t cpu_cycles() const { return elapsed_cpu_cycles_; }
  uint64_t irq_events() const { return irq_events_; }

 private:
  void clock_counter() {
    if (counter_ == 0xff) {
      counter_ = latch_;
      irq_line_ = true;
      ++irq_events_;
    } else {
      ++counter_;
    }
  }
  uint8_t latch_ = 0, counter_ = 0;
  bool enabled_ = false, mode_cycle_ = false;
  bool enable_after_ack_ = false, irq_line_ = false;
  int prescaler_ = 341;
  uint64_t elapsed_cpu_cycles_ = 0, irq_events_ = 0;
};
}  // namespace jpstatic
