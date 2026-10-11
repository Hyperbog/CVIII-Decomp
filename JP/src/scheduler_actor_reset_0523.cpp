#include "scheduler_actor_reset_0523.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
std::uint8_t cmp_status(std::uint8_t p, std::uint8_t lhs,
                        std::uint8_t rhs) noexcept {
    const auto result = static_cast<std::uint8_t>(lhs - rhs);
    return static_cast<std::uint8_t>((p & ~0x83u)
        | (lhs >= rhs ? 0x01u : 0u)
        | (result == 0 ? 0x02u : 0u) | (result & 0x80u));
}
}
SchedulerStep0522 scheduler_fe63_to_next_0523(
    std::array<std::uint8_t, 0x800>& r,
    std::uint8_t x, std::uint8_t a,
    std::uint8_t y, std::uint8_t p) {
    if (x < 0x0du || x > 0x12u)
        throw std::invalid_argument("0523: unlifted $8161 actor-index family");
    const auto type = r[0x054eu + x];
    const auto pos = r[0x041cu + x];
    const bool reset = type >= 0x30u && type < 0x66u && pos >= 0xf8u;
    if (!reset)
        return scheduler_fe63_to_next_0522(r, x, a, y, p);
    // $8193 CMP #$4D / BEQ $81B2, which can call unlifted $B56B.
    // Refuse this original branch before the mapper/RAM is modified.
    if (type == 0x4du)
        throw std::invalid_argument("0523: $8193->$81B2/$B56B unlifted");

    // $FE63 LDA #$0B; JSR $E2D0 writes mapper and bank shadow.
    r[0x23] = 0x0bu;
    // $8161 edits $0470,X; $819A A9 #$00 then four STAs clear
    // $054E,X/$0470,X/$0400,X/$05EF,X (overriding prior attr edit).
    r[0x054eu + x] = 0u;
    r[0x0470u + x] = 0u;
    r[0x0400u + x] = 0u;
    r[0x05efu + x] = 0u;
    // $81A8 RTS; $FE6E INX / CPX #$13 / BCS or JMP $FDEC.
    const auto next_x = static_cast<std::uint8_t>(x + 1u);
    p = cmp_status(p, next_x, 0x13u);
    return {next_x == 0x13u ? std::uint16_t{0xfe75u}
                            : std::uint16_t{0xfdecu},
            0u, next_x, y, p, 0x0bu};
}
} // namespace cv3
