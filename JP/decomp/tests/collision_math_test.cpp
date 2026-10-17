#include "../src/collision_math.hpp"

#include <cassert>
#include <cstdint>

int main() {
    using namespace cv3;

    // Exhaustively verify the 6502 absolute-difference behavior for all inputs.
    for (unsigned a = 0; a < 256; ++a) {
        for (unsigned b = 0; b < 256; ++b) {
            const auto aa = static_cast<std::uint8_t>(a);
            const auto bb = static_cast<std::uint8_t>(b);
            const auto expected = static_cast<std::uint8_t>(a >= b ? a - b : b - a);
            assert(abs_delta8(aa, bb) == expected);
        }
    }

    // 8-bit coordinate construction wraps, matching ADC low-byte semantics.
    {
        const auto p = make_probe(0xF8, 0xFC, 0x10, 0x09);
        assert(p.x_or_a == 0x08);
        assert(p.y_or_b == 0x05);
    }

    // $B76C-style in-place offset adjustment.
    {
        CollisionScratch p{0xFE, 0x7F};
        adjust_probe(p, 0x05, 0x81);
        assert(p.x_or_a == 0x03);
        assert(p.y_or_b == 0x00);
    }

    // Carry-compare users branch on distance >= limit.
    assert(distance_below(0x20, 0x27, 0x08));
    assert(!distance_below(0x20, 0x28, 0x08));
    assert(distance_below(0xF0, 0x10, 0xF0));
    assert(!distance_below(0x00, 0xFF, 0xFF));

    return 0;
}
