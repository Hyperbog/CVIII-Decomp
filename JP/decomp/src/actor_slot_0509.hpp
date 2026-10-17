#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Original fixed PRG31:$FF06-$FF14. Tests slots X=$01..$0C in order.
// RAM $054E,X is the observed occupied/nonzero scan byte; the all-full
// path returns A=$01 and X=$0D. A vacant slot returns A=$00.
struct ActorSlotScan {
    bool available;
    std::uint8_t x;
    std::uint8_t a;
};
[[nodiscard]] ActorSlotScan scan_actor_slot(const std::array<std::uint8_t,0x800>& ram) noexcept;

// Faithful store-level lift of fixed PRG31:$FF15-$FF23 (4 fields) and
// $FF24-$FF55 (calls FF15 and then clears 14 additional fields).
// Caller must supply the original X. Neither entry clears $054E,X.
void clear_actor_four_fields(std::array<std::uint8_t,0x800>& ram, std::uint8_t x) noexcept;
void clear_actor_eighteen_fields(std::array<std::uint8_t,0x800>& ram, std::uint8_t x) noexcept;

inline constexpr std::array<std::uint16_t,4> kFourActorFields = {
    0x04F2,0x0509,0x0520,0x0537
};
inline constexpr std::array<std::uint16_t,14> kRemainingActorFields = {
    0x067B,0x068D,0x0454,0x0470,0x0565,0x04C4,0x04DB,
    0x05C1,0x05D8,0x05EF,0x0606,0x061D,0x0633,0x0645
};
} // namespace cv3
