#include "../src/ai_script_dispatch.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <vector>

int main(int argc, char** argv) {
    using namespace cv3;
    // Real JP ROM integration fixture: never commit ROM bytes to this repo.
    assert(argc == 2);
    std::ifstream f(argv[1], std::ios::binary);
    assert(f.good());
    std::vector<std::uint8_t> rom(std::istreambuf_iterator<char>{f}, {});
    assert(rom.size() == 0x60010u);
    assert(rom[6] == 0x80u || rom[6] == 0x81u);
    std::array<std::uint8_t, 65536> bus{};
    for (unsigned i = 0; i < 0x4000; ++i) {
        bus[0x8000 + i] = rom[16 + 0x0B * 0x4000 + i];
    }
    auto read = [&](std::uint16_t addr) { return bus[addr]; };

    // Synthetic RAM record, but authentic JP-ROM handler pointer tables.
    bus[0xBEA5] = 0x00; bus[0xBEA6] = 0x40;
    for (unsigned action = 0; action < 256; ++action) {
        bus[0x4000] = static_cast<std::uint8_t>(action);
        const auto r = decode_ai_script_action(read, 1, 0);
        const auto entry = (action < 128 ? 0xBD67 : 0xBE67) + 2 * (action & 0x7F);
        const auto target = static_cast<std::uint16_t>(
            bus[entry] | (static_cast<unsigned>(bus[entry + 1]) << 8));
        assert(r.script_pointer_entry == 0xBEA5);
        assert(r.record_address == 0x4000);
        assert(r.action == action);
        assert(r.handler_pointer_entry == entry);
        assert(r.handler == target);
        assert(r.carry_at_handler == (action >= 128));
        assert(r.y_at_handler == static_cast<std::uint8_t>(2 * action));
        assert(r.a_at_handler == (target >> 8));
        assert(r.zero_at_handler == ((target >> 8) == 0));
        assert(r.negative_at_handler == ((target >> 15) != 0));
    }
    bus[0xBEA5] = rom[16 + 0x0B * 0x4000 + (0xBEA5 - 0x8000)];
    bus[0xBEA6] = rom[16 + 0x0B * 0x4000 + (0xBEA6 - 0x8000)];
    assert(decode_ai_script_action(read, 1, 0).script_base == 0xA61A);
    // 16-bit record address carry/wrap and 8-bit subscript multiplication.
    bus[0xBEA5] = 0xF0; bus[0xBEA6] = 0xFF;
    bus[0x002C] = 0x80;
    const auto wrap = decode_ai_script_action(read, 1, 15);
    assert(wrap.record_address == 0x002C && wrap.action == 0x80);
    bus[0xBEA5] = 0x00; bus[0xBEA6] = 0x40;
    bus[0x4000] = 0x00;
    assert(decode_ai_script_action(read, 1, 64).record_address == 0x4000);
    // 6502 ASL discards the original script-ID high bit.
    assert(decode_ai_script_action(read, 0x81, 0).script_pointer_entry == 0xBEA5);
    return 0;
}
