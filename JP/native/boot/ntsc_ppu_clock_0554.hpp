#pragma once
// NTSC 2C02 dot/vblank/NMI-line clock for future native frame scheduling.
// No renderer, DMA, APU, register open bus, or CPU-instruction timing is implied.
#include <cstdint>

namespace jpstatic {
class NtscPpuClock {
 public:
  static constexpr unsigned dots_per_line = 341;
  static constexpr unsigned lines_per_frame = 262;
  static constexpr unsigned vblank_start_line = 241;
  static constexpr unsigned prerender_line = 261;

  // Explicit deterministic epoch: visible scanline 0 / dot 0 / even frame.
  // This is NOT a model of arbitrary PPU power-on or reset phase.
  unsigned scanline() const { return line_; }
  unsigned dot() const { return dot_; }
  uint64_t frames() const { return frames_; }
  uint64_t ppu_dots() const { return ppu_dots_; }
  uint64_t cpu_cycles() const { return cpu_cycles_; }
  bool odd_frame() const { return (frames_ & 1u) != 0; }
  bool vblank() const { return vblank_; }
  bool rendering_enabled() const { return (mask_ & 0x18u) != 0; }
  bool active_rendering() const {
    return rendering_enabled() && (line_ < 240 || line_ == prerender_line);
  }
  bool nmi_line() const { return vblank_ && (control_ & 0x80u); }
  bool nmi_pending() const { return pending_nmi_; }

  void write_control(uint8_t value) {
    const bool old_line = nmi_line();
    control_ = value;
    detect_nmi_rise(old_line);
  }
  void write_mask(uint8_t value) { mask_ = value; }

  // Only bit 7 is modeled. Real $2002 also contains sprite flags/open bus.
  // Reading clears the VBlank flag and thus deasserts the NMI line.
  uint8_t read_status_vblank_only() {
    const uint8_t value = vblank_ ? 0x80 : 0;
    vblank_ = false;
    return value;
  }
  // CPU-side NMI acknowledgement; status reads must not erase a latched edge.
  bool take_nmi() {
    const bool result = pending_nmi_;
    pending_nmi_ = false;
    return result;
  }

  // Each CPU clock advances three 2C02 dots (NTSC 2A03:2C02 ratio).
  // Instruction bus accesses are NOT cycle-positioned by this class.
  void advance_cpu_cycles(uint64_t count) {
    for (uint64_t i = 0; i < count; ++i) {
      ++cpu_cycles_;
      advance_ppu_dots(3);
    }
  }
  void advance_ppu_dots(uint64_t count) {
    for (uint64_t i = 0; i < count; ++i) {
      if (line_ == vblank_start_line && dot_ == 1) {
        const bool old_line = nmi_line();
        vblank_ = true;
        detect_nmi_rise(old_line);
      }
      if (line_ == prerender_line && dot_ == 1) vblank_ = false;
      ++ppu_dots_;
      // NTSC skips pre-render dot 340 on odd frames with BG or sprites on.
      if (line_ == prerender_line && dot_ == 339 &&
          odd_frame() && (mask_ & 0x18u)) {
        begin_next_frame();
      } else if (++dot_ == dots_per_line) {
        dot_ = 0;
        if (++line_ == lines_per_frame) begin_next_frame();
      }
    }
  }

 private:
  void detect_nmi_rise(bool old_line) {
    if (!old_line && nmi_line()) pending_nmi_ = true;
  }
  void begin_next_frame() {
    line_ = 0;
    dot_ = 0;
    ++frames_;
  }
  unsigned line_ = 0, dot_ = 0;
  uint8_t control_ = 0, mask_ = 0;
  bool vblank_ = false, pending_nmi_ = false;
  uint64_t frames_ = 0, ppu_dots_ = 0, cpu_cycles_ = 0;
};
}  // namespace jpstatic
