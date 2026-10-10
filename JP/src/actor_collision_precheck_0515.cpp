#include "actor_collision_precheck_0515.hpp"
#include "actor_preflight_0514.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
std::uint8_t nz(std::uint8_t p, std::uint8_t a) noexcept {
    return static_cast<std::uint8_t>((p & ~0x82u) | (a & 0x80u) |
                                     (a == 0u ? 0x02u : 0u));
}
std::uint8_t cmp(std::uint8_t p, std::uint8_t a, std::uint8_t b) noexcept {
    const auto d = static_cast<std::uint8_t>(a - b);
    return static_cast<std::uint8_t>((p & ~0x83u) | (a >= b ? 1u : 0u) |
                                     (d == 0u ? 2u : 0u) | (d & 0x80u));
}
}
CollisionPrecheck0515 actor_collision_b217_precheck(
    const std::array<std::uint8_t, 0x800>& ram, std::uint8_t x,
    std::uint8_t y, std::uint8_t p) {
    if (x < 1 || x > 17)
        throw std::invalid_argument("original bank0B B217 actor index X must be 1..17");
    // $B217 LDA $7E / $B219 AND #$F0 / $B21B BNE $B258.
    auto a = ram[0x7e]; p = nz(p, a);
    a = static_cast<std::uint8_t>(a & 0xf0u); p = nz(p, a);
    if (a != 0) return {0xb258u, a, x, y, p};
    // $B21D LDA $054E,X / $B220 CMP #$69 / $B222 BCC $B227.
    a = ram[0x054eu + x]; p = nz(p, a);
    p = cmp(p, a, 0x69u);
    if (a >= 0x69u) return {0xb162u, a, x, y, p};  // $B224 JMP $B162
    // $B227 LDA $0470,X / $B22A AND #$02 / $B22C BNE $B1D8.
    a = ram[0x0470u + x]; p = nz(p, a);
    a = static_cast<std::uint8_t>(a & 2u); p = nz(p, a);
    if (a != 0) return {0xb1d8u, a, x, y, p};
    // $B22E LDA $7D / $B230 BNE $B258; fallthrough to JSR $B339.
    a = ram[0x7d]; p = nz(p, a);
    return {static_cast<std::uint16_t>(a ? 0xb258u : 0xb232u), a, x, y, p};
}
CollisionPrecheck0515 actor_pre_collision_b1f8_through_b231(
    const std::array<std::uint8_t, 0x800>& ram, std::uint8_t x,
    std::uint8_t y, std::uint8_t p) {
    const auto gate = actor_postprocess_b1f8_gate(ram, x, y, p);
    if (gate.next_pc != 0xb217u)
        return {gate.next_pc, gate.a, gate.x, gate.y, gate.p};
    return actor_collision_b217_precheck(ram, gate.x, gate.y, gate.p);
}
}  // namespace cv3
