#include "ntsc_ppu_clock_0554.hpp"
#include <cstdint>
#include <iostream>
#include <stdexcept>
using jpstatic::NtscPpuClock;

static void expect(bool test, const char* what) {
  if (!test) throw std::runtime_error(what);
}
static void test_cpu_ratio_and_epoch() {
  NtscPpuClock p;
  expect(p.scanline() == 0 && p.dot() == 0 && !p.odd_frame(),
         "unexpected deterministic clock epoch");
  p.advance_cpu_cycles(114);
  expect(p.cpu_cycles() == 114 && p.ppu_dots() == 342,
         "NTSC CPU-to-PPU 3:1 ratio");
  expect(p.scanline() == 1 && p.dot() == 1, "cross-scanline CPU step");
}
static void test_vblank_status_edge() {
  NtscPpuClock p;
  p.write_control(0x80);
  p.advance_ppu_dots(241ull * 341 + 1);
  expect(p.scanline() == 241 && p.dot() == 1 && !p.vblank(),
         "vblank asserted one dot too early");
  p.advance_ppu_dots(1);
  expect(p.vblank() && p.nmi_line() && p.nmi_pending(),
         "vblank/NMI start not at scanline 241 dot 1");
  expect(p.read_status_vblank_only() == 0x80, "status read must see old vblank");
  expect(!p.vblank() && !p.nmi_line(), "status read must clear vblank");
  expect(p.read_status_vblank_only() == 0, "second status poll must clear");
  expect(p.take_nmi() && !p.take_nmi(),
         "a latched NMI edge survives $2002 read until acknowledged");
  // The next frame must reassert VBlank even when rendering is disabled.
  p.advance_ppu_dots(341ull * 262);
  expect(p.vblank() && p.nmi_pending(), "next-frame NMI after status clear");
}
static void test_enable_mid_vblank_and_prerender_clear() {
  NtscPpuClock p;
  p.advance_ppu_dots(241ull * 341 + 2);
  expect(p.vblank() && !p.nmi_pending(), "no NMI while disabled");
  p.write_control(0x80);
  expect(p.nmi_line() && p.take_nmi(), "enabling NMI during vblank");
  p.write_control(0);
  p.write_control(0x80);
  expect(p.take_nmi(), "new rising NMI edge on PPUCTRL toggling");
  p.advance_ppu_dots(20ull * 341);
  expect(!p.vblank() && !p.nmi_line(),
         "vblank cleared on prerender dot 1");
}
static void test_even_odd_frame_lengths() {
  constexpr uint64_t standard = 341ull * 262;
  NtscPpuClock off;
  off.advance_ppu_dots(standard);
  expect(off.frames() == 1 && off.odd_frame(), "first full even frame");
  off.advance_ppu_dots(standard);
  expect(off.frames() == 2 && off.ppu_dots() == 2 * standard,
         "rendering off must not skip odd-frame dot");

  NtscPpuClock on;
  on.write_mask(0x08);  // BG enabled; sprites need not be.
  on.advance_ppu_dots(standard);
  expect(on.frames() == 1, "even frame has all dots");
  on.advance_ppu_dots(standard - 2);
  expect(on.frames() == 1 && on.scanline() == 261 && on.dot() == 339,
         "odd-frame last pre-render dot before skip");
  on.advance_ppu_dots(1);
  expect(on.frames() == 2 && on.dot() == 0 && on.scanline() == 0,
         "odd frame must skip prerender dot 340");
  expect(on.ppu_dots() == 2 * standard - 1, "odd frame total PPU dots");
}
int main() {
  try {
    test_cpu_ratio_and_epoch();
    test_vblank_status_edge();
    test_enable_mid_vblank_and_prerender_clear();
    test_even_odd_frame_lengths();
    std::cout << "PASS JP0554 NTSC timing: 3:1, vblank, NMI edge, odd-frame skip\n";
  } catch (const std::exception& e) {
    std::cerr << "FAIL JP0554: " << e.what() << '\n';
    return 1;
  }
}
