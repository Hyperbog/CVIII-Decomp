#include "vrc6_irq.hpp"

#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void run(cv3::Vrc6Irq& irq, int cycles) {
    for (int i = 0; i < cycles; ++i) irq.step_cpu_cycle();
}

void test_cycle_mode_and_one_shot_ack() {
    cv3::Vrc6Irq irq;
    irq.cpu_write(0xF000, 0xFE);
    irq.cpu_write(0xF001, 0x06); // M=1 E=1 A=0
    assert(irq.enabled() && irq.cycle_mode());
    assert(irq.counter() == 0xFE);
    irq.step_cpu_cycle();
    assert(irq.counter() == 0xFF && !irq.irq_pending());
    irq.step_cpu_cycle();
    assert(irq.counter() == 0xFE && irq.irq_pending());

    irq.cpu_write(0xF002, 0x00);
    assert(!irq.irq_pending());
    assert(!irq.enabled());
    run(irq, 100);
    assert(irq.counter() == 0xFE);
}

void test_repeating_ack_preserves_counter_phase() {
    cv3::Vrc6Irq irq;
    irq.cpu_write(0xF000, 0xFE);
    irq.cpu_write(0xF001, 0x07); // M=1 E=1 A=1
    run(irq, 2);
    assert(irq.irq_pending() && irq.counter() == 0xFE);
    irq.cpu_write(0xF002, 0xA5);
    assert(!irq.irq_pending() && irq.enabled());
    irq.step_cpu_cycle();
    assert(irq.counter() == 0xFF && !irq.irq_pending());
    irq.step_cpu_cycle();
    assert(irq.counter() == 0xFE && irq.irq_pending());
}

void test_scanline_prescaler_114_114_113() {
    cv3::Vrc6Irq irq;
    irq.cpu_write(0xF000, 0xFC);
    irq.cpu_write(0xF001, 0x02); // M=0 E=1 A=0
    assert(irq.counter() == 0xFC);

    run(irq, 113);
    assert(irq.counter() == 0xFC);
    run(irq, 1);
    assert(irq.counter() == 0xFD);

    run(irq, 113);
    assert(irq.counter() == 0xFD);
    run(irq, 1);
    assert(irq.counter() == 0xFE);

    run(irq, 112);
    assert(irq.counter() == 0xFE);
    run(irq, 1);
    assert(irq.counter() == 0xFF);

    run(irq, 114);
    assert(irq.irq_pending());
    assert(irq.counter() == 0xFC);
}

void test_control_ack_and_disable_semantics() {
    cv3::Vrc6Irq irq;
    irq.cpu_write(0xF000, 0x80);
    irq.cpu_write(0xF001, 0x02);
    assert(irq.counter() == 0x80);
    run(irq, 114);
    assert(irq.counter() == 0x81);

    // A control write acknowledges, resets the prescaler, and with E clear
    // leaves the current counter unchanged.
    irq.cpu_write(0xF001, 0x01); // E=0 A=1
    assert(!irq.irq_pending() && !irq.enabled());
    assert(irq.counter() == 0x81);
    run(irq, 1000);
    assert(irq.counter() == 0x81);

    // ACK copies saved A to E without reloading counter or prescaler.
    irq.cpu_write(0xF002, 0x00);
    assert(irq.enabled());
    run(irq, 113);
    assert(irq.counter() == 0x81);
    run(irq, 1);
    assert(irq.counter() == 0x82);
}

void test_mapper24_register_mirrors() {
    cv3::Vrc6Irq irq;
    irq.cpu_write(0xFABC, 0xAA); // masks to F000
    assert(irq.latch() == 0xAA);
    irq.cpu_write(0xF9FD, 0x06); // masks to F001
    assert(irq.cycle_mode() && irq.enabled() && irq.counter() == 0xAA);
    irq.cpu_write(0xF7FE, 0x00); // masks to F002
    assert(!irq.irq_pending() && !irq.enabled());
}

void test_target_rom_irq_register_sites(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open ROM");
    std::vector<std::uint8_t> rom((std::istreambuf_iterator<char>(f)), {});
    assert(rom.size() == 0x60010);
    const auto fixed = rom.data() + 16 + 31 * 0x2000;
    const auto at = [&](std::uint16_t cpu) -> const std::uint8_t* {
        return fixed + (cpu - 0xE000u);
    };

    // Established IRQ-handler distinction: $E118 clears Control before ACK;
    // $E11D is the Acknowledge write itself.
    const auto* clear = at(0xE118);
    assert(clear[0] == 0xA9 && clear[1] == 0x00);
    assert(clear[2] == 0x8D && clear[3] == 0x01 && clear[4] == 0xF0);
    const auto* ack = at(0xE11D);
    assert(ack[0] == 0x8D && ack[1] == 0x02 && ack[2] == 0xF0);
}

}  // namespace

int main(int argc, char** argv) {
    test_cycle_mode_and_one_shot_ack();
    test_repeating_ack_preserves_counter_phase();
    test_scanline_prescaler_114_114_113();
    test_control_ack_and_disable_semantics();
    test_mapper24_register_mirrors();
    if (argc == 2) test_target_rom_irq_register_sites(argv[1]);
}
