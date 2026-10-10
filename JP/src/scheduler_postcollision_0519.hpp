#pragma once
#include <array>
#include <cstdint>
namespace cv3 {
// Bounded original fixed-bank $FDFE/$FE00 actor scheduler decision.
// Ends BEFORE the first indirect/JSR action helper, or at $FE6E loop advance.
// This does NOT run $BD11, $FF56, $FE8C or the bank09 movement caller.
struct SchedulerGate0519 {std::uint16_t next_pc;std::uint8_t a,x,y,p;};
[[nodiscard]] SchedulerGate0519 scheduler_post_collision_fe00_0519(
    const std::array<std::uint8_t,0x800>& ram,std::uint8_t initial_a,
    std::uint8_t initial_y,std::uint8_t initial_p);
}
