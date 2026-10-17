#include "vrc6_mapper.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

std::vector<std::uint8_t> make_prg() {
    std::vector<std::uint8_t> prg(cv3::Vrc6Mapper::kPrgSize);
    for (std::size_t bank = 0; bank < 32; ++bank) {
        for (std::size_t i = 0; i < 0x2000; ++i) {
            prg[bank * 0x2000 + i] = static_cast<std::uint8_t>(bank);
        }
    }
    return prg;
}

std::vector<std::uint8_t> make_chr() {
    std::vector<std::uint8_t> chr(cv3::Vrc6Mapper::kChrSize);
    for (std::size_t bank = 0; bank < 128; ++bank) {
        for (std::size_t i = 0; i < 0x400; ++i) {
            chr[bank * 0x400 + i] = static_cast<std::uint8_t>(bank);
        }
    }
    return chr;
}

void test_prg_windows_and_register_mirrors() {
    auto prg = make_prg();
    auto chr = make_chr();
    cv3::Vrc6Mapper m(prg, chr);

    m.cpu_write(0x8000, 0x0B);
    assert(m.prg16_bank() == 0x0B);
    assert(m.cpu_read(0x8000) == 22);  // physical PRG22
    assert(m.cpu_read(0xA000) == 23);  // physical PRG23

    // Only A0/A1/A12-A15 are decoded: $8ABC mirrors $8000.
    m.cpu_write(0x8ABC, 0x09);
    assert(m.prg16_bank() == 0x09);
    assert(m.cpu_read(0x8000) == 18);
    assert(m.cpu_read(0xBFFF) == 19);

    m.cpu_write(0xC002, 0x07);
    assert(m.prg8_bank() == 7);
    assert(m.cpu_read(0xC000) == 7);
    assert(m.cpu_read(0xDFFF) == 7);

    // Fixed window is always the last physical 8 KiB bank.
    assert(m.cpu_read(0xE000) == 31);
    assert(m.cpu_read(0xFFFF) == 31);
}

void test_prg_ram_enable() {
    auto prg = make_prg();
    auto chr = make_chr();
    cv3::Vrc6Mapper m(prg, chr);

    m.cpu_write(0x6000, 0x5A);
    assert(m.cpu_read(0x6000) == 0xFF);  // disabled

    m.cpu_write(0xB003, 0xA0);           // bit 7 enables WRAM
    assert(m.prg_ram_enabled());
    m.cpu_write(0x6000, 0x5A);
    assert(m.cpu_read(0x6000) == 0x5A);

    m.cpu_write(0xB003, 0x20);
    assert(!m.prg_ram_enabled());
    assert(m.cpu_read(0x6000) == 0xFF);
}

void load_chr_regs(cv3::Vrc6Mapper& m) {
    for (std::uint16_t i = 0; i < 4; ++i) m.cpu_write(0xD000 + i, static_cast<std::uint8_t>(10 + 2 * i));
    for (std::uint16_t i = 0; i < 4; ++i) m.cpu_write(0xE000 + i, static_cast<std::uint8_t>(30 + 2 * i));
}

void test_chr_modes() {
    auto prg = make_prg();
    auto chr = make_chr();
    cv3::Vrc6Mapper m(prg, chr);
    load_chr_regs(m);

    // Mode 0: 8 independent 1 KiB banks R0..R7.
    m.cpu_write(0xB003, 0x20);
    const std::array<std::uint8_t, 8> mode0{10,12,14,16,30,32,34,36};
    for (std::size_t s = 0; s < 8; ++s) {
        assert(m.chr_bank_for_1k_slot(s) == mode0[s]);
        assert(m.ppu_read(static_cast<std::uint16_t>(s * 0x400)) == mode0[s]);
    }

    // Mode 1: R0..R3 become four 2 KiB banks. With B003:5 set,
    // PPU A10 supplies the low bank bit.
    m.cpu_write(0xB003, 0x21);
    const std::array<std::uint8_t, 8> mode1{10,11,12,13,14,15,16,17};
    for (std::size_t s = 0; s < 8; ++s) assert(m.chr_bank_for_1k_slot(s) == mode1[s]);

    // Modes 2/3: R0..R3 are 1 KiB; R4/R5 are two 2 KiB banks.
    m.cpu_write(0xB003, 0x22);
    const std::array<std::uint8_t, 8> mode2{10,12,14,16,30,31,32,33};
    for (std::size_t s = 0; s < 8; ++s) assert(m.chr_bank_for_1k_slot(s) == mode2[s]);

    m.cpu_write(0xB003, 0x23);
    for (std::size_t s = 0; s < 8; ++s) assert(m.chr_bank_for_1k_slot(s) == mode2[s]);

    // With bit 5 clear, nominal 2 KiB banks repeat the selected 1 KiB page.
    m.cpu_write(0xB003, 0x01);
    const std::array<std::uint8_t, 8> dup{10,10,12,12,14,14,16,16};
    for (std::size_t s = 0; s < 8; ++s) assert(m.chr_bank_for_1k_slot(s) == dup[s]);
}

void test_target_game_mirroring_values() {
    auto prg = make_prg();
    auto chr = make_chr();
    cv3::Vrc6Mapper m(prg, chr);

    m.cpu_write(0xB003, 0x20);
    assert(m.mirroring() == cv3::NametableMirroring::Vertical);
    assert(m.ciram_a10(0x2000) == 0 && m.ciram_a10(0x2400) == 1);
    assert(m.ciram_a10(0x2800) == 0 && m.ciram_a10(0x2C00) == 1);

    m.cpu_write(0xB003, 0x24);
    assert(m.mirroring() == cv3::NametableMirroring::Horizontal);
    assert(m.ciram_a10(0x2000) == 0 && m.ciram_a10(0x2400) == 0);
    assert(m.ciram_a10(0x2800) == 1 && m.ciram_a10(0x2C00) == 1);

    m.cpu_write(0xB003, 0x28);
    assert(m.mirroring() == cv3::NametableMirroring::OneScreenA);
    for (auto a : {0x2000,0x2400,0x2800,0x2C00}) assert(m.ciram_a10(a) == 0);

    m.cpu_write(0xB003, 0x2C);
    assert(m.mirroring() == cv3::NametableMirroring::OneScreenB);
    for (auto a : {0x2000,0x2400,0x2800,0x2C00}) assert(m.ciram_a10(a) == 1);
}

void test_target_rom(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("cannot open ROM");
    std::vector<std::uint8_t> rom((std::istreambuf_iterator<char>(f)), {});
    assert(rom.size() == 0x60010);
    assert(rom[0] == 'N' && rom[1] == 'E' && rom[2] == 'S' && rom[3] == 0x1A);
    assert(rom[4] == 0x10 && rom[5] == 0x10); // 256 KiB PRG, 128 KiB CHR
    const unsigned mapper = (rom[6] >> 4) | (rom[7] & 0xF0);
    assert(mapper == 24);

    std::span<const std::uint8_t> prg(rom.data() + 16, cv3::Vrc6Mapper::kPrgSize);
    std::span<const std::uint8_t> chr(rom.data() + 16 + cv3::Vrc6Mapper::kPrgSize, cv3::Vrc6Mapper::kChrSize);
    cv3::Vrc6Mapper m(prg, chr);

    // Scheduler-proven raw-bank selections from checkpoint 0501.
    m.cpu_write(0x8000, 0x0B);
    assert(m.cpu_read(0xB3B6) == prg[23 * 0x2000 + 0x13B6]);
    assert(m.cpu_read(0xB3B6) == 0x85); // verified STA $10 site
    m.cpu_write(0x8000, 0x09);
    assert(m.cpu_read(0x8001) == prg[18 * 0x2000 + 1]);
    m.cpu_write(0x8000, 0x0A);
    assert(m.cpu_read(0x84EA) == prg[20 * 0x2000 + 0x04EA]);

    // Fixed vectors must always come from PRG31.
    assert(m.cpu_read(0xFFFA) == 0x57 && m.cpu_read(0xFFFB) == 0xE0); // NMI $E057
    assert(m.cpu_read(0xFFFC) == 0x0B && m.cpu_read(0xFFFD) == 0xE0); // RESET $E00B
    assert(m.cpu_read(0xFFFE) == 0xF5 && m.cpu_read(0xFFFF) == 0xE0); // IRQ $E0F5
}

}  // namespace

int main(int argc, char** argv) {
    test_prg_windows_and_register_mirrors();
    test_prg_ram_enable();
    test_chr_modes();
    test_target_game_mirroring_values();
    if (argc == 2) test_target_rom(argv[1]);
}
