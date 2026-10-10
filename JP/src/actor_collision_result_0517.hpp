#pragma once
#include <array>
#include <cstdint>
namespace cv3 {
// Original raw PRG bank $0B postcollision tail $B235-$B31F.
// Source entry assumes original B339 has returned to B235 after JSR/RTS.
// Return PC is a deliberately bounded STOP: FDFE means the original
// actor routine has returned to its fixed-bank caller; other PCs denote
// unlifted original helpers, not a completed collision/attachment update.
struct CollisionTail0517 {
  std::uint16_t next_pc;
  std::uint8_t a,x,y,p;
};
[[nodiscard]] CollisionTail0517 actor_collision_tail_b235(
  std::array<std::uint8_t,0x800>& ram,
  std::uint8_t x, std::uint8_t a, std::uint8_t y, std::uint8_t p);
} // namespace cv3

namespace cv3 {
// Connected natural Stage1 bounded semantic native path.
// Only when B1F8/B217 admission reaches B232 and original B339 returns at
// B393. Then executes the source-equivalent B235 tail through fixed FDFE
// or returns the exact first unsupported original PC boundary.
[[nodiscard]] CollisionTail0517 actor_collision_b1f8_through_tail_0517(
  std::array<std::uint8_t,0x800>& ram,
  std::uint8_t x, std::uint8_t y, std::uint8_t p);
}
