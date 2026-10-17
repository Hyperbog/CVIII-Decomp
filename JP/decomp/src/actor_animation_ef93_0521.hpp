#pragma once
#include <array>
#include <cstdint>
namespace cv3 {
// Original fixed $EF93-$EFD1; assumes caller FE60 JSR has entered $EF93.
// Bounded descriptor support: when DEC timer reaches zero, only actor
// descriptor $048C,X==$0E and frame index $05AA,X<=15 are supported.
// Nonzero timer path does not read descriptor and supports all values.
// Stops after original RTS at fixed $FE63. This is not a CPU interpreter.
struct AnimationUpdate0521 {std::uint16_t next_pc;std::uint8_t a,x,y,p;bool refreshed;};
[[nodiscard]] AnimationUpdate0521 actor_animation_ef93_0521(
    std::array<std::uint8_t,0x800>& ram,
    std::uint8_t actor_x,std::uint8_t entry_a,
    std::uint8_t entry_y,std::uint8_t entry_p);
// Connect prior original source $FDFE -> $FE60 to $EF93, stopping at
// $FE63 or an exact earlier unlifted original source call boundary.
[[nodiscard]] AnimationUpdate0521 actor_animation_fdfe_to_fe63_0521(
    std::array<std::uint8_t,0x800>& ram,
    std::uint8_t initial_a,std::uint8_t initial_y,std::uint8_t initial_p);
}
