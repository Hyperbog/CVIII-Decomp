#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Authenticated Japanese raw bank $0B:$B217-$B231 collision admission.
// next_pc is one of $B258, $B162, $B1D8, or $B232 (JSR $B339).
// No RAM writes in this source span. Does not implement $B339 collision.
struct CollisionPrecheck0515 {
    std::uint16_t next_pc;
    std::uint8_t a, x, y, p;
};
[[nodiscard]] CollisionPrecheck0515 actor_collision_b217_precheck(
    const std::array<std::uint8_t, 0x800>& ram, std::uint8_t actor_x,
    std::uint8_t initial_y, std::uint8_t initial_p);

// Compose the previously certified source-shaped B1F8 eligibility gate
// with B217; also preserves B1F7/B258 exits, avoids executing B339.
[[nodiscard]] CollisionPrecheck0515 actor_pre_collision_b1f8_through_b231(
    const std::array<std::uint8_t, 0x800>& ram, std::uint8_t actor_x,
    std::uint8_t initial_y, std::uint8_t initial_p);
}  // namespace cv3
