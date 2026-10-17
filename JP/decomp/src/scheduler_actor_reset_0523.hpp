#pragma once
#include "scheduler_fe63_0522.hpp"
#include <array>
#include <cstdint>

namespace cv3 {
// Bounded 0523 extension: original raw 0B:$826C->$8193->$81A8
// reset when type $30..$65 (except $4D) and position >=$F8.
// Other entries reuse source-bounded 0522. Unlifted type $4D->$81B2
// and actor indices outside $0D..$12 throw BEFORE touching RAM.
[[nodiscard]] SchedulerStep0522 scheduler_fe63_to_next_0523(
    std::array<std::uint8_t, 0x800>& ram,
    std::uint8_t actor_x, std::uint8_t entry_a,
    std::uint8_t entry_y, std::uint8_t entry_p);
} // namespace cv3
