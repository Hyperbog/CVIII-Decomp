// ROM-free command-stream reporter for the existing native VRC6 IRQ engine.
// Input: W <decimal register> <decimal byte>, S <decimal cycles>.
// Output after each event: latch counter cyclemode enabled afterack pending.
#include "vrc6_irq.hpp"
#include <cstdint>
#include <iostream>
#include <string>

int main() {
    cv3::Vrc6Irq irq;
    std::string kind;
    std::uint32_t a = 0, b = 0;
    while (std::cin >> kind >> a >> b) {
        if (kind == "W") {
            if (a > 65535 || b > 255) return 2;
            irq.cpu_write(static_cast<std::uint16_t>(a), static_cast<std::uint8_t>(b));
        } else if (kind == "S") {
            if (a > 1000000 || b != 0) return 3;
            for (std::uint32_t i = 0; i < a; ++i) irq.step_cpu_cycle();
        } else return 4;
        std::cout << static_cast<unsigned>(irq.latch()) << ' '
                  << static_cast<unsigned>(irq.counter()) << ' '
                  << static_cast<unsigned>(irq.cycle_mode()) << ' '
                  << static_cast<unsigned>(irq.enabled()) << ' '
                  << static_cast<unsigned>(irq.enable_after_ack()) << ' '
                  << static_cast<unsigned>(irq.irq_pending()) << '\n';
    }
    return std::cin.eof() ? 0 : 5;
}
