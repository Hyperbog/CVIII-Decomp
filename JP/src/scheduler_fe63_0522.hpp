#pragma once
#include <array>
#include <cstdint>
namespace cv3 {
// Original JP fixed FE63-FE75, raw bank0B 8161 and 826C.
// Supported actor indices 0D-12; no 6502 stack, unsupported callback,
// or whole-actor-frame implementation.
struct SchedulerStep0522 {
    std::uint16_t next_pc;
    std::uint8_t a, x, y, p, prg16_bank;
};
[[nodiscard]] SchedulerStep0522 scheduler_fe63_to_next_0522(
    std::array<std::uint8_t, 0x800>& ram,
    std::uint8_t actor_x, std::uint8_t entry_a,
    std::uint8_t entry_y, std::uint8_t entry_p);
} // namespace cv3
