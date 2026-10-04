#include "oam_renderer.hpp"

#include <cstddef>
#include <cstdint>

namespace cv3 {
namespace {

constexpr std::uint16_t kSpriteSetTable = 0x817F;

std::uint8_t read_prg(const OamContext& ctx, std::uint16_t address) {
    // Valid game data keeps these reads in VRC6 bank $0D ($8000-$BFFF).
    // Deliberately no invented ROM-side selector/frame bounds check here.
    return ctx.bank13[static_cast<std::size_t>(address - 0x8000u)];
}

std::uint8_t read_y(const OamContext& ctx, std::uint16_t base, std::uint8_t y) {
    return read_prg(ctx, static_cast<std::uint16_t>(base + y));
}

std::uint16_t read_ptr_wrapped_y(const OamContext& ctx,
                                 std::uint16_t base,
                                 std::uint8_t y) {
    const std::uint8_t lo = read_y(ctx, base, y);
    y = static_cast<std::uint8_t>(y + 1u);
    const std::uint8_t hi = read_y(ctx, base, y);
    return static_cast<std::uint16_t>(lo | (static_cast<std::uint16_t>(hi) << 8u));
}

int signed_byte(std::uint8_t value) {
    return value < 0x80u ? static_cast<int>(value)
                         : static_cast<int>(value) - 0x100;
}

std::uint8_t arithmetic_shift_right_one(std::uint8_t value) {
    return static_cast<std::uint8_t>((value >> 1u) | (value & 0x80u));
}

bool render_object(OamContext& ctx, std::uint8_t object_index) {
    auto& ram = ctx.ram;

    const std::uint8_t selector = ram[0x048Cu + object_index];
    ram[0x0F] = selector;

    const std::uint16_t set_pointer = read_ptr_wrapped_y(ctx, kSpriteSetTable, selector);
    ram[0x08] = static_cast<std::uint8_t>(set_pointer);
    ram[0x09] = static_cast<std::uint8_t>(set_pointer >> 8u);

    const std::uint8_t frame_offset = ram[0x0400u + object_index];
    const std::uint16_t descriptor_pointer = read_ptr_wrapped_y(ctx, set_pointer, frame_offset);
    ram[0x0A] = static_cast<std::uint8_t>(descriptor_pointer);
    ram[0x0B] = static_cast<std::uint8_t>(descriptor_pointer >> 8u);

    std::uint8_t cursor = 0;
    ram[0x03] = read_y(ctx, descriptor_pointer, cursor);

    const bool mirrored = ram[0x04A8u + object_index] == 0;
    std::uint8_t oam_offset = ram[0x04];

    while (true) {
        cursor = static_cast<std::uint8_t>(cursor + 1u);
        const std::uint8_t y_code = read_y(ctx, descriptor_pointer, cursor);
        const bool reuse_attribute = (y_code & 0x01u) != 0;
        const std::uint8_t y_delta = arithmetic_shift_right_one(y_code);
        ram[0x0200u + oam_offset] = static_cast<std::uint8_t>(y_delta + ram[0x01]);

        cursor = static_cast<std::uint8_t>(cursor + 1u);
        std::uint8_t tile = read_y(ctx, descriptor_pointer, cursor);
        if (ram[0xAD] != 0 && selector >= 0x16u) {
            tile = static_cast<std::uint8_t>(tile + 0x80u);
        }
        ram[0x0201u + oam_offset] = tile;

        // Y-code bit 0 is a compression flag. When set, no attribute byte is
        // present and the final transformed attribute in zero-page $10 is reused.
        if (!reuse_attribute) {
            cursor = static_cast<std::uint8_t>(cursor + 1u);
            std::uint8_t attribute = read_y(ctx, descriptor_pointer, cursor);
            if (ram[0x00] != 0) {
                attribute = static_cast<std::uint8_t>((attribute & 0xFCu) | ram[0x00]);
            }
            if (mirrored) {
                attribute ^= 0x40u;
            }
            ram[0x10] = attribute;
        }
        ram[0x0202u + oam_offset] = ram[0x10];

        cursor = static_cast<std::uint8_t>(cursor + 1u);
        std::uint8_t x_code = read_y(ctx, descriptor_pointer, cursor);
        if (mirrored) {
            x_code = static_cast<std::uint8_t>(0xF8u - x_code);
        }

        const int x_sum = static_cast<int>(ram[0x02]) + signed_byte(x_code);
        if (x_sum >= 0 && x_sum <= 0xFF) {
            ram[0x0203u + oam_offset] = static_cast<std::uint8_t>(x_sum);
        } else {
            ram[0x0200u + oam_offset] = 0xF4u;
        }

        oam_offset = static_cast<std::uint8_t>(oam_offset + 0xC4u);
        ram[0x07] = static_cast<std::uint8_t>(ram[0x07] - 1u);
        if (ram[0x07] == 0) {
            // Original $80ED: PLA; PLA; RTS. $04/$03 are not updated here and
            // $8001's unused-slot fill is skipped.
            return true;
        }

        ram[0x03] = static_cast<std::uint8_t>(ram[0x03] - 1u);
        if (ram[0x03] == 0) {
            ram[0x04] = oam_offset;
            return false;
        }
    }
}

}  // namespace

OamFrameResult build_oam_shadow(OamContext& ctx) {
    auto& ram = ctx.ram;

    ram[0x05] = 0;
    ram[0x07] = 0x40;
    ram[0x22] = static_cast<std::uint8_t>(ram[0x22] + 0x44u);
    ram[0x04] = ram[0x22];

    while (ram[0x05] < 0x1Cu) {
        const std::uint8_t object_index = ram[0x05];
        if (ram[0x0400u + object_index] != 0 &&
            (ram[0x0470u + object_index] & 0x80u) == 0) {
            ram[0x00] = ram[0x0454u + object_index];
            ram[0x01] = ram[0x041Cu + object_index];
            ram[0x02] = ram[0x0438u + object_index];
            if (render_object(ctx, object_index)) {
                return OamFrameResult::OamFull;
            }
        }
        ram[0x05] = static_cast<std::uint8_t>(ram[0x05] + 1u);
    }

    std::uint8_t oam_offset = ram[0x04];
    std::uint8_t remaining = ram[0x07];
    do {
        ram[0x0200u + oam_offset] = 0xF4u;
        oam_offset = static_cast<std::uint8_t>(oam_offset + 0xC4u);
        remaining = static_cast<std::uint8_t>(remaining - 1u);
    } while (remaining != 0);

    return OamFrameResult::Completed;
}

}  // namespace cv3
