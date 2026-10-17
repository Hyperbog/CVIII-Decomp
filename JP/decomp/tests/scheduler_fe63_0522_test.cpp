#include "scheduler_fe63_0522.hpp"
#include <array>
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <cstdint>
#include <stdexcept>
int main() {
    unsigned passed = 0, unsupported = 0;
    constexpr std::array<std::uint8_t, 7> types{0, 0x2f, 0x30, 0x65, 0x66, 0x80, 0xff};
    constexpr std::array<std::uint8_t, 4> positions{0, 0xf7, 0xf8, 0xff};
    constexpr std::array<std::uint8_t, 3> statuses{0x00, 0x4d, 0xff};
    for (unsigned x = 0x0d; x <= 0x12; ++x)
    for (unsigned attr = 0; attr < 256; ++attr)
    for (auto type : types)
    for (auto pos : positions)
    for (auto p : statuses) {
        std::array<std::uint8_t, 0x800> ram{};
        ram.fill(0x5a);
        ram[0x23] = 0x77;
        ram[0x0470u + x] = static_cast<std::uint8_t>(attr);
        ram[0x054eu + x] = type;
        ram[0x041cu + x] = pos;
        const auto before = ram;
        const bool blocked = type >= 0x30 && type < 0x66 && pos >= 0xf8;
        try {
            const auto got = cv3::scheduler_fe63_to_next_0522(ram,
                static_cast<std::uint8_t>(x), 0xa5, 0x49, p);
            assert(!blocked);
            assert(got.next_pc == (x == 0x12 ? 0xfe75 : 0xfdec));
            assert(got.x == x + 1 && got.y == 0x49 && got.prg16_bank == 0x0b);
            assert(got.a == (type >= 0x30 && type < 0x66 ? pos : type));
            const auto d = static_cast<std::uint8_t>((x + 1u) - 0x13u);
            const auto flags = static_cast<std::uint8_t>((p & ~0x83u) |
                (x == 0x12 ? 0x03u : 0u) | (d & 0x80u));
            assert(got.p == flags);
            auto expected = before;
            expected[0x23] = 0x0b;
            expected[0x0470u + x] = (attr & 0x09u)
                ? static_cast<std::uint8_t>(attr | 0x80u)
                : static_cast<std::uint8_t>(attr & 0x7fu);
            assert(ram == expected);
            ++passed;
        } catch (const std::invalid_argument&) {
            assert(blocked && ram == before);
            ++unsupported;
        }
    }
    for (unsigned x : {0u, 1u, 12u, 19u, 255u}) {
        std::array<std::uint8_t, 0x800> ram{};
        const auto before = ram;
        try {
            (void)cv3::scheduler_fe63_to_next_0522(ram,
                static_cast<std::uint8_t>(x), 0, 0, 0);
            assert(false);
        } catch (const std::invalid_argument&) { assert(ram == before); }
    }
    assert(passed == 110592u && unsupported == 18432u);
}
