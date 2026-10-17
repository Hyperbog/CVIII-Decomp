#include "scheduler_fe63_0522.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
constexpr std::uint8_t kActorFirst = 0x0d;
constexpr std::uint8_t kActorLast = 0x12;
std::uint8_t cmp_status(std::uint8_t p, std::uint8_t lhs,
                        std::uint8_t rhs) noexcept {
    const auto result = static_cast<std::uint8_t>(lhs - rhs);
    return static_cast<std::uint8_t>((p & ~0x83u) |
        (lhs >= rhs ? 0x01u : 0u) |
        (result == 0 ? 0x02u : 0u) | (result & 0x80u));
}
} // namespace
SchedulerStep0522 scheduler_fe63_to_next_0522(
    std::array<std::uint8_t, 0x800>& r,
    std::uint8_t x, std::uint8_t /*entry_a*/,
    std::uint8_t y, std::uint8_t p) {
    if (x < kActorFirst || x > kActorLast)
        throw std::invalid_argument("0522: $8161 actor X<$0D remains unlifted");
    const std::uint8_t type = r[0x054eu + x];
    const std::uint8_t position = r[0x041cu + x];
    // $826C->$8193 takes an unlifted reset/callback branch.
    if (type >= 0x30u && type < 0x66u && position >= 0xf8u)
        throw std::invalid_argument("0522: unlifted $826C->$8193 callback");
    // $FE63 LDA #$0B; $FE65 JSR $E2D0: STA $23; STA $8000.
    r[0x23] = 0x0bu;
    // $8161: actor indices >=$0D return before other callbacks.
    const std::size_t attr_addr = 0x0470u + x;
    const auto attr = r[attr_addr];
    r[attr_addr] = (attr & 0x09u) != 0u
        ? static_cast<std::uint8_t>(attr | 0x80u)
        : static_cast<std::uint8_t>(attr & 0x7fu);
    // $826C: direct RTS exits for types <$30 or >=$66 and
    // type $30-$65 with $041C,X<$F8.
    const auto a = (type >= 0x30u && type < 0x66u) ? position : type;
    // $FE6E INX / CPX #$13 / BCS $FE75 / JMP $FDEC.
    const auto next_x = static_cast<std::uint8_t>(x + 1u);
    p = cmp_status(p, next_x, 0x13u);
    return {next_x >= 0x13u ? std::uint16_t{0xfe75u}
                             : std::uint16_t{0xfdecu},
            a, next_x, y, p, 0x0bu};
}
} // namespace cv3
