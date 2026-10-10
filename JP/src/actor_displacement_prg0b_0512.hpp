#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Original JP raw bank $0B:$80E3-$810E: horizontal branch ($65 bit7 clear)
// of the fixed-bank $FDF8 actor displacement routine. Excludes the
// separate vertical path at $810F and downstream collision/actor updates.
// Source executes 20 instructions on $6B>=0; 21 on $6B<0.
struct ActorDisplacement0512 {
    std::uint8_t a;
    std::uint8_t x;
    std::uint8_t y;
    std::uint8_t p;
};
[[nodiscard]] ActorDisplacement0512 apply_prg0b_actor_displacement_80e3_horizontal(
    std::array<std::uint8_t,0x800>& ram,
    std::uint8_t actor_x,
    std::uint8_t initial_p);
}
