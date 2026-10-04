#include "oam_renderer.hpp"

#include <array>
#include <cassert>
#include <cstdint>

namespace {

using Ram = std::array<std::uint8_t, 0x800>;
using Bank = std::array<std::uint8_t, 0x4000>;

void put_ptr(Bank& bank, std::uint16_t address, std::uint16_t value) {
    bank[address - 0x8000] = static_cast<std::uint8_t>(value);
    bank[address - 0x8000 + 1] = static_cast<std::uint8_t>(value >> 8u);
}

void set_object(Ram& ram, std::uint8_t slot, std::uint8_t selector,
                std::uint8_t frame, std::uint8_t y, std::uint8_t x,
                std::uint8_t override_value, bool non_mirrored) {
    ram[0x0400 + slot] = frame;
    ram[0x041C + slot] = y;
    ram[0x0438 + slot] = x;
    ram[0x0454 + slot] = override_value;
    ram[0x0470 + slot] = 0;
    ram[0x048C + slot] = selector;
    ram[0x04A8 + slot] = non_mirrored ? 1 : 0;
}

void test_attribute_override_and_compressed_reuse() {
    Ram ram{};
    Bank bank{};
    put_ptr(bank, 0x817F, 0x9000);
    put_ptr(bank, 0x9002, 0x9100);

    auto* d = &bank[0x9100 - 0x8000];
    d[0] = 2;
    d[1] = 0x02; d[2] = 0x20; d[3] = 0x03; d[4] = 0x04;
    d[5] = 0x03; d[6] = 0x21;              d[7] = 0xFC;

    set_object(ram, 0, 0, 2, 0x20, 0x40, 0x21, true);
    ram[0x22] = 0xBC;  // +$44 wraps to OAM byte offset 0.

    cv3::OamContext ctx{ram, bank};
    assert(cv3::build_oam_shadow(ctx) == cv3::OamFrameResult::Completed);

    // The ROM does (raw & $FC) | override, with no mask on the override byte.
    assert(ram[0x0200] == 0x21);
    assert(ram[0x0201] == 0x20);
    assert(ram[0x0202] == 0x21);
    assert(ram[0x0203] == 0x44);

    constexpr std::uint8_t second = 0xC4;
    assert(ram[0x0200 + second] == 0x21);
    assert(ram[0x0201 + second] == 0x21);
    assert(ram[0x0202 + second] == 0x21);  // reused final attribute from $10
    assert(ram[0x0203 + second] == 0x3C);
}

void test_first_compressed_record_uses_incoming_cache() {
    Ram ram{};
    Bank bank{};
    put_ptr(bank, 0x817F, 0x9000);
    put_ptr(bank, 0x9002, 0x9180);

    // One compressed record: odd Y/control means no attribute byte is encoded.
    auto* d = &bank[0x9180 - 0x8000];
    d[0] = 1;
    d[1] = 0x03;  // arithmetic-shifted Y = +1; bit 0 requests cached attribute
    d[2] = 0x44;  // tile
    d[3] = 0x05;  // X

    set_object(ram, 0, 0, 2, 0x20, 0x30, 0x00, true);
    ram[0x10] = 0xA7;  // incoming renderer state; $8001/$8070 must not reset it
    ram[0x22] = 0xBC;

    cv3::OamContext ctx{ram, bank};
    assert(cv3::build_oam_shadow(ctx) == cv3::OamFrameResult::Completed);

    assert(ram[0x0200] == 0x21);
    assert(ram[0x0201] == 0x44);
    assert(ram[0x0202] == 0xA7);  // exact incoming $10 survives into first sprite
    assert(ram[0x0203] == 0x35);
    assert(ram[0x10] == 0xA7);    // compressed record does not transform/update cache
}

void test_mirror_and_tile_plus_80() {
    Ram ram{};
    Bank bank{};
    put_ptr(bank, 0x817F + 0x16, 0x9200);
    put_ptr(bank, 0x9202, 0x9300);

    auto* d = &bank[0x9300 - 0x8000];
    d[0] = 1;
    d[1] = 0xFE; d[2] = 0x90; d[3] = 0x02; d[4] = 0xF0;

    set_object(ram, 0, 0x16, 2, 0x10, 0x02, 0, false);
    ram[0xAD] = 1;
    ram[0x22] = 0xBC;

    cv3::OamContext ctx{ram, bank};
    assert(cv3::build_oam_shadow(ctx) == cv3::OamFrameResult::Completed);
    assert(ram[0x0200] == 0x0F);
    assert(ram[0x0201] == 0x10);  // $90 + $80 wraps
    assert(ram[0x0202] == 0x42);  // mirror toggles OAM bit $40
    assert(ram[0x0203] == 0x0A);  // $F8-$F0 + base X 2
}

void test_oam_full_non_local_exit() {
    Ram ram{};
    Bank bank{};
    put_ptr(bank, 0x817F, 0x9000);
    put_ptr(bank, 0x9002, 0x9400);

    auto* d = &bank[0x9400 - 0x8000];
    d[0] = 64;
    std::size_t p = 1;
    d[p++] = 0x00; d[p++] = 0x01; d[p++] = 0x02; d[p++] = 0x00;
    for (int i = 1; i < 64; ++i) {
        d[p++] = 0x01;  // odd Y-code: reuse attribute, so record is 3 bytes
        d[p++] = static_cast<std::uint8_t>(i + 1);
        d[p++] = 0x00;
    }

    set_object(ram, 0, 0, 2, 0, 0, 0, true);
    ram[0x22] = 0xBC;

    cv3::OamContext ctx{ram, bank};
    assert(cv3::build_oam_shadow(ctx) == cv3::OamFrameResult::OamFull);
    assert(ram[0x07] == 0);
    assert(ram[0x05] == 0);  // $8001 INC $05 was skipped
    assert(ram[0x04] == 0);  // post-sprite local X was never saved back
    assert(ram[0x03] == 1);  // descriptor count DEC was skipped on full path
}

}  // namespace

int main() {
    test_attribute_override_and_compressed_reuse();
    test_first_compressed_record_uses_incoming_cache();
    test_mirror_and_tile_plus_80();
    test_oam_full_non_local_exit();
}
