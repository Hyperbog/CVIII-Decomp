#include "vrc6_irq_0554.hpp"
#include <iostream>
#include <stdexcept>
using jpstatic::Vrc6IrqCounter;

static void require(bool ok, const char* message) {
  if (!ok) throw std::runtime_error(message);
}
static void cycle_mode_and_ack() {
  Vrc6IrqCounter irq;
  irq.write(0xf000, 0xfe);
  irq.write(0xf001, 0x07);  // M=1, E=1, A=1.
  require(irq.counter() == 0xfe && irq.cycle_mode(), "control reload");
  irq.clock_cpu_cycles(1);
  require(irq.counter() == 0xff && !irq.irq_line(), "pre-overflow count");
  irq.clock_cpu_cycles(1);
  require(irq.counter() == 0xfe && irq.irq_line() && irq.irq_events() == 1,
          "overflow reload and assertion");
  irq.write(0xf002, 0xff);  // Value ignored; enable copied from A.
  require(!irq.irq_line() && irq.enabled(), "ack must clear and reenable");
  irq.clock_cpu_cycles(2);
  require(irq.irq_line() && irq.irq_events() == 2, "IRQ repetition");
  irq.write(0xf001, 0x04);  // Cycle mode with E=A=0.
  require(!irq.enabled() && !irq.irq_line(), "control disable/ack");
  const auto frozen = irq.counter();
  irq.clock_cpu_cycles(1000);
  require(irq.counter() == frozen, "disabled counter must freeze");
  require(irq.cpu_cycles() == 1004, "CPU elapsed cycles tracked");
}
static void scanline_divider() {
  Vrc6IrqCounter irq;
  irq.write(0xf000, 0xff);
  irq.write(0xf001, 0x03);  // M=0, E=1, A=1.
  irq.clock_cpu_cycles(113);
  require(irq.prescaler() == 2 && !irq.irq_line(), "first divider phase");
  irq.clock_cpu_cycles(1);
  require(irq.irq_line() && irq.irq_events() == 1 &&
          irq.prescaler() == 340, "first IRQ at 114 CPU cycles");
  irq.write(0xf002, 0);
  irq.clock_cpu_cycles(113);
  require(!irq.irq_line() && irq.prescaler() == 1, "second phase 113");
  irq.clock_cpu_cycles(1);
  require(irq.irq_line() && irq.prescaler() == 339, "second phase 114");
  irq.write(0xf002, 0);
  irq.clock_cpu_cycles(112);
  require(!irq.irq_line() && irq.prescaler() == 3, "third phase 112");
  irq.clock_cpu_cycles(1);
  require(irq.irq_line() && irq.prescaler() == 341 &&
          irq.irq_events() == 3, "third phase 113");
}
static void ack_and_latch_rules() {
  Vrc6IrqCounter irq;
  irq.write(0xf000, 0xff);
  irq.write(0xf001, 0x06);  // Cycle mode, enabled, A=0 (one-shot after ack).
  irq.clock_cpu_cycles(1);
  require(irq.irq_line(), "one-shot must assert first");
  irq.write(0xf002, 0);
  require(!irq.irq_line() && !irq.enabled(), "A=0 disables on ack");
  irq.clock_cpu_cycles(20);
  require(!irq.irq_line() && irq.irq_events() == 1, "one-shot disabled");
  irq.write(0xf000, 0x80);
  require(irq.counter() == 0xff, "latch write must not reload live count");
  irq.write(0xf001, 0x07);  // Reload on enabled control write.
  require(irq.counter() == 0x80 && irq.enabled(), "enabled control reload");
  irq.clock_cpu_cycles(128);
  require(irq.irq_line() && irq.counter() == 0x80, "updated latch on overflow");
  irq.write(0xf002, 0);
  require(irq.enabled() && !irq.irq_line(), "A=1 enables on ack");
}
static void ack_preserves_scanline_phase() {
  Vrc6IrqCounter irq;
  irq.write(0xf000, 0xff);
  irq.write(0xf001, 0x03);
  irq.clock_cpu_cycles(7);
  require(irq.prescaler() == 320, "scanline prescaler after 7");
  irq.write(0xf002, 0);  // Must preserve current prescaler.
  require(irq.prescaler() == 320, "ack reset prescaler");
  irq.clock_cpu_cycles(107);
  require(irq.irq_line(), "ack preserved remaining 107 cycles");
  irq.write(0xf001, 0x03);
  require(irq.prescaler() == 341 && irq.counter() == 0xff &&
          !irq.irq_line(), "control resets prescaler/counter and ack");
}
static void unsupported_register_rejected() {
  Vrc6IrqCounter irq;
  bool failed = false;
  try { irq.write(0xf003, 0); }
  catch (const std::runtime_error&) { failed = true; }
  require(failed, "unknown VRC6a IRQ register must fail closed");
}
int main() {
  try {
    cycle_mode_and_ack();
    scanline_divider();
    ack_and_latch_rules();
    ack_preserves_scanline_phase();
    unsupported_register_rejected();
    std::cout << "PASS JP0554 VRC6a IRQ latch, 114/114/113 divider, "
                 "cycle mode and control/ack behavior\n";
  } catch (const std::exception& e) {
    std::cerr << "FAIL JP0554 VRC6 IRQ: " << e.what() << '\n';
    return 1;
  }
}
