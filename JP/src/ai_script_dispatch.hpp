#pragma once

#include <cstdint>

namespace cv3 {

// Raw VRC6 bank $0B: $BD28-$BD66. This models ONLY the address/dispatch
// portion after the $BD11 stopwatch, zero-script and script-$27 prechecks.
// The caller supplies a live CPU bus reader. It must honor the active mapper,
// so pointers into RAM or other PRG windows are not silently ROM-clamped.
struct AiScriptDispatch {
    std::uint16_t script_pointer_entry;
    std::uint16_t script_base;
    std::uint16_t record_address;
    std::uint8_t action;
    std::uint16_t handler_pointer_entry;
    std::uint16_t handler;
    std::uint8_t y_at_handler;
    std::uint8_t a_at_handler;
    bool carry_at_handler;
    bool zero_at_handler;
    bool negative_at_handler;
};

template <typename ReadCpu8>
[[nodiscard]] inline AiScriptDispatch decode_ai_script_action(
    ReadCpu8&& read_cpu8, std::uint8_t script_id,
    std::uint8_t subscript_index) {
    // The caller MUST have passed the actual prechecks. Script ID $00
    // returns early; ID $27 invokes the conditional $82CD helper.
    const auto index = static_cast<std::uint8_t>(script_id << 1);
    const auto ptr = static_cast<std::uint16_t>(0xBEA3u + index);
    const auto lo = static_cast<std::uint8_t>(read_cpu8(ptr));
    const auto hi = static_cast<std::uint8_t>(read_cpu8(static_cast<std::uint16_t>(ptr + 1u)));
    const auto script = static_cast<std::uint16_t>(lo | (static_cast<unsigned>(hi) << 8));
    const auto displacement = static_cast<std::uint8_t>(subscript_index << 2);
    const auto record = static_cast<std::uint16_t>(script + displacement);
    const auto action = static_cast<std::uint8_t>(read_cpu8(record));
    const bool carry = (action & 0x80u) != 0;
    const auto doubled = static_cast<std::uint8_t>(action << 1);
    const auto entry = static_cast<std::uint16_t>((carry ? 0xBE67u : 0xBD67u) + doubled);
    const auto target_lo = static_cast<std::uint8_t>(read_cpu8(entry));
    const auto target_hi = static_cast<std::uint8_t>(read_cpu8(static_cast<std::uint16_t>(entry + 1u)));
    const auto target = static_cast<std::uint16_t>(target_lo | (static_cast<unsigned>(target_hi) << 8));
    return {ptr, script, record, action, entry, target, doubled, target_hi,
            carry, target_hi == 0, (target_hi & 0x80u) != 0};
}

}  // namespace cv3
