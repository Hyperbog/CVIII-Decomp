#pragma once
#include <array>
#include <cstdint>
namespace cv3 {
// Original Japanese ROM bank $0B:$B339-$B393, using $80B3 and $80C1
// distance helpers. Bounded to $B7=0, room $7F in 0..8, actor type
// $054E,X in 0..$68, and $048C=8/$0400>=EE alternate path excluded.
// The source $B393 RTS is NOT executed in this C++ boundary (no stack).
struct CollisionMeasure0516 {
    std::uint16_t next_pc;
    std::uint8_t a, x, y, p;
    bool vertical_compared;
};
// Connected original Stage 1 native path: B1F8 admission -> B217 ->
// B232 JSR B339. Returns B393 before RTS, or an earlier gate exit.
[[nodiscard]] CollisionMeasure0516 actor_collision_measure_b1f8_to_b393(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t actor_x,
    std::uint8_t initial_y, std::uint8_t initial_p);
[[nodiscard]] CollisionMeasure0516 actor_collision_measure_b339(
    std::array<std::uint8_t,0x800>& ram,
    std::uint8_t actor_x, std::uint8_t initial_a,
    std::uint8_t initial_y, std::uint8_t initial_p);
}
