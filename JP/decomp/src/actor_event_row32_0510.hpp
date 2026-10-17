#pragma once
#include <array>
#include <cstdint>

namespace cv3 {
// Explicitly limited source-equivalent lift of JP raw bank $0A:$8501 -> $8B2C
// (event row $32, event low nibble zero). This is NOT a 6502 emulator.
// Entry: source slot X=0..5, RAM[$69]=X; fixed-bank actor helpers are reused.
// Result is a semantic outcome, not source CPU A/X/Y/P stack state.
enum class Row32Outcome : std::uint8_t { Guarded, Spawned, AtLimit };
struct Row32Result {
    Row32Outcome outcome;
    std::uint8_t destination; // 1..12 if spawned, 0 otherwise
    std::uint8_t existing_matching_actors; // type $3D in slots 1..8
};
[[nodiscard]] Row32Result run_row32_event(
    std::array<std::uint8_t, 0x800>& ram, std::uint8_t source_x);
} // namespace cv3
