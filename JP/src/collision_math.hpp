#pragma once

#include <cstdint>

namespace cv3 {

// Shared zero-page $10/$11 is reused by the JP raw-bank $0B collision sweep as
// an 8-bit coordinate scratch pair. Arithmetic wraps exactly like the 6502.
struct CollisionScratch {
    std::uint8_t x_or_a = 0;
    std::uint8_t y_or_b = 0;
};

[[nodiscard]] constexpr std::uint8_t wrap_add8(std::uint8_t a, std::uint8_t b) noexcept {
    return static_cast<std::uint8_t>(a + b);
}

// Faithful lift of the SEC/SBC ... EOR #$FF / ADC #$01 absolute-difference
// idiom used at raw-bank $0B:$B707/$B713/$B71D and $80B3/$80C1/$80CB/$80D5.
[[nodiscard]] constexpr std::uint8_t abs_delta8(std::uint8_t a, std::uint8_t b) noexcept {
    return a >= b ? static_cast<std::uint8_t>(a - b)
                  : static_cast<std::uint8_t>(b - a);
}

[[nodiscard]] constexpr CollisionScratch make_probe(
    std::uint8_t base_x,
    std::uint8_t base_y,
    std::uint8_t offset_x,
    std::uint8_t offset_y) noexcept {
    return {wrap_add8(base_x, offset_x), wrap_add8(base_y, offset_y)};
}

constexpr void adjust_probe(
    CollisionScratch& scratch,
    std::uint8_t offset_x,
    std::uint8_t offset_y) noexcept {
    scratch.x_or_a = wrap_add8(scratch.x_or_a, offset_x);
    scratch.y_or_b = wrap_add8(scratch.y_or_b, offset_y);
}

[[nodiscard]] constexpr bool distance_below(
    std::uint8_t a,
    std::uint8_t b,
    std::uint8_t limit) noexcept {
    return abs_delta8(a, b) < limit;
}

}  // namespace cv3
