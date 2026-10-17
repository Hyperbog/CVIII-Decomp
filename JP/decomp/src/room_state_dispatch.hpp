#pragma once
#include <cstdint>

namespace cv3 {
// Raw VRC6 bank $0A:$B4CC (JSR fixed $E7FB at $B4CE).
// Mechanically computes the inline table address, WITHOUT assuming $19<12.
// This does not execute the stack/zero-page writes of the actual $E7FB ABI.
struct RoomStateDispatch {
    std::uint16_t pointer_entry;
    std::uint16_t destination;
    std::uint8_t final_a;
    std::uint8_t final_y;
    bool carry;
    bool zero;
    bool negative;
};
template <typename MappedRead8>
[[nodiscard]] inline RoomStateDispatch decode_room_state(
        MappedRead8&& read, std::uint8_t selector_19,
        std::uint8_t incoming_y) {
    // ASL A in $E7FB is *8-bit*: selectors differing by $80 alias.
    const std::uint8_t offset = static_cast<std::uint8_t>(selector_19 << 1);
    const std::uint16_t p = static_cast<std::uint16_t>(0xB4D1u + offset);
    const auto low = static_cast<std::uint8_t>(read(p));
    // Fixed $E7FB increments 8-bit Y twice. For selectors $7F/$FF,
    // second INY wraps to $00 and reads the original JSR return byte.
    const std::uint16_t high_location = static_cast<std::uint16_t>(
        0xB4D0u + static_cast<std::uint8_t>(offset + 2u));
    const auto high = static_cast<std::uint8_t>(read(high_location));
    const auto dest = static_cast<std::uint16_t>(low | (static_cast<unsigned>(high)<<8));
    // $E7FB ends: LDA (ret),Y [high] ; LDY $03 [saved Y] ; STA $03 ; JMP ($0002).
    // The final Z/N flags come from restored Y, not the pointer high byte.
    return {p,dest,high,incoming_y,(selector_19&0x80u)!=0,
            incoming_y==0,(incoming_y&0x80u)!=0};
}
} // namespace cv3
