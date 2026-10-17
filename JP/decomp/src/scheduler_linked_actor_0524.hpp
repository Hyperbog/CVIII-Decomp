#pragma once
#include "scheduler_actor_reset_0523.hpp"
#include <array>
#include <cstdint>
namespace cv3 {
// JP raw bank0B $81B2-$81CB->$B56B-$B579 special type4D.
[[nodiscard]] SchedulerStep0522 scheduler_fe63_to_next_0524(
    std::array<std::uint8_t,0x800>& ram,
    std::uint8_t actor_x,std::uint8_t entry_a,
    std::uint8_t entry_y,std::uint8_t entry_p);
}
