#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Structured state lift of original JP raw VRC6 bank $0B:$8001-$8036,
// including its JSR to $8037-$804A. Not a 6502 interpreter; the eight RAM
// writes, 8-bit carry/overflow, and 9-bit horizontal coordinate are preserved.
// Entry scope: original active actor index X=0..12; source actor RAM arrays.
// Register snapshot describes A/Y/P on return, not the hardware JSR/RTS stack.
struct Prg0bMotionResult {
    std::uint8_t a;
    std::uint8_t y;
    std::uint8_t p;
};
[[nodiscard]] Prg0bMotionResult apply_prg0b_actor_motion_8001(
    std::array<std::uint8_t,0x800>& ram,
    std::uint8_t actor_x,
    std::uint8_t initial_p);
}
