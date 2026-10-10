#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Structured native CPU boundary values. This is NOT a 6502 interpreter.
struct ActorPreflight0514 {
    std::uint16_t next_pc; // original raw-$0B branch boundary or next CPU return
    std::uint8_t a, x, y, p;
};
// Original bank 30 (physical PRG $03D2FE), CPU $D2FE-$D30C, selected
// $62>=2 producer. Does not model $62==0/1 scrolling paths.
[[nodiscard]] ActorPreflight0514 produce_delta6b_d2fe(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t x,
    std::uint8_t initial_a, std::uint8_t initial_p);
// Original bank $0B (physical $02F1F8), CPU $B1F8-$B215 eligibility
// gate, stopping before $B1F7 RTS, $B217 collision or $B258 bypass.
// Source actor indices X=1..17 only, including real scheduler X=14..17.
[[nodiscard]] ActorPreflight0514 actor_postprocess_b1f8_gate(
    const std::array<std::uint8_t,0x800>& ram, std::uint8_t x,
    std::uint8_t initial_y, std::uint8_t initial_p);
}
