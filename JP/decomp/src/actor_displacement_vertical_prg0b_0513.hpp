#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Source: authenticated original JP raw PRG bank $0B:$80E3-$815E.
// Only the $65 negative-axis branch is lifted. The separate $8843 callee
// is represented by an explicit source-equivalent continuation helper.
// This is structured C++ state transition; no 6502 stack is emulated.
enum class ActorVerticalExit0513 : std::uint8_t {
    ReturnToFixedFDFB, TransferToRaw8843
};
struct ActorVertical0513 {
    ActorVerticalExit0513 exit;
    std::uint8_t a, x, y, p;
    bool removed; // actual type/frame stores to $054E,X and $0400,X
};
[[nodiscard]] ActorVertical0513 apply_prg0b_actor_displacement_80e3_vertical(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t actor_x,
    std::uint8_t initial_p);
// Original raw bank $0B:$8843-$886B continuation, entered only after the
// prefix transfers control. This source routine may perform type-$3B
// 16-bit movement ($0606/$061D), or return immediately for other types.
[[nodiscard]] ActorVertical0513 apply_prg0b_actor_8843_continuation(
    std::array<std::uint8_t,0x800>& ram, const ActorVertical0513& prefix);
// Complete bounded vertical branch from $80E3 to fixed $FDFB (via $8843).
[[nodiscard]] ActorVertical0513 apply_prg0b_actor_displacement_80e3_vertical_complete(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t actor_x,
    std::uint8_t initial_p);
} // namespace cv3
