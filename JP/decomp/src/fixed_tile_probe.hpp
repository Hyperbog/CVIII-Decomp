#pragma once

#include <cstdint>

namespace cv3 {
// JP physical PRG31 $FD11-$FD2B, after preceding code established $13,
// high-byte Y and fine offset $11. This is NOT a complete collision routine.
// The CPU bus callback must preserve mapped reads even when Y points into code.
struct FixedTileProbeIndex {
    std::uint8_t or_result;
    std::uint8_t table_index;
    std::uint8_t base_tile;
    std::uint8_t effective_index;
    bool adc_carry;
};
template <typename CpuRead>
[[nodiscard]] inline FixedTileProbeIndex fixed_tile_probe_index(
    CpuRead&& cpu_read, std::uint8_t low_position,
    std::uint8_t high_position, std::uint8_t fine_offset) {
    const auto address = static_cast<std::uint16_t>(0xFD62u + high_position);
    const auto combined = static_cast<std::uint8_t>(
        (low_position >> 5) | static_cast<std::uint8_t>(cpu_read(address)));
    std::uint8_t index = combined;
    while (index >= 12u) index = static_cast<std::uint8_t>(index - 12u);
    const auto tile = static_cast<std::uint8_t>(
        cpu_read(static_cast<std::uint16_t>(0xFD4Du + index)));
    const unsigned sum = static_cast<unsigned>(tile) + fine_offset;
    return {combined,index,tile,static_cast<std::uint8_t>(sum),sum > 255u};
}
} // namespace cv3
