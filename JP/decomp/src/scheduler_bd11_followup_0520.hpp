#pragma once
#include <array>
#include <cstdint>
namespace cv3 {
// Bounded original Japanese VRC6 ROM CPU $BD11 entry (raw bank $0B) and
// fixed bank $FE34 actor continuation. No 6502 engine and no JSR/RTS stack.
// next_pc is exact original boundary before the first unsupported source
// operation (BD15, BD1F, FE4C, FE60, FE63, FE6E).
struct SchedulerFollowup0520 {std::uint16_t next_pc;std::uint8_t a,x,y,p;};
[[nodiscard]] SchedulerFollowup0520 scheduler_bd11_and_fe34_0520(
  const std::array<std::uint8_t,0x800>& ram,
  std::uint8_t entry_x, std::uint8_t entry_a,
  std::uint8_t entry_y, std::uint8_t entry_p);
// Starts at original fixed $FDFE and continues to next unmapped helper
// when original scheduler gate 0519 routes through $FE31 JSR $BD11.
[[nodiscard]] SchedulerFollowup0520 scheduler_fdfe_to_followup_0520(
  const std::array<std::uint8_t,0x800>& ram,
  std::uint8_t initial_a,std::uint8_t initial_y,std::uint8_t initial_p);
}
