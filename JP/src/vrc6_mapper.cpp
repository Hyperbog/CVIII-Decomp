#include "vrc6_mapper.hpp"

#include <cassert>
#include <stdexcept>

namespace cv3 {
namespace {
constexpr std::uint16_t kRegisterMask = 0xF003;
constexpr std::size_t kPrg16Size = 0x4000;
constexpr std::size_t kPrg8Size = 0x2000;
constexpr std::size_t kChr1kSize = 0x0400;
}

Vrc6Mapper::Vrc6Mapper(std::span<const std::uint8_t> prg,
                       std::span<const std::uint8_t> chr)
    : prg_(prg.begin(), prg.end()), chr_(chr.begin(), chr.end()) {
    if (prg_.size() != kPrgSize) {
        throw std::invalid_argument("Akumajou Densetsu VRC6 PRG must be 256 KiB");
    }
    if (chr_.size() != kChrSize) {
        throw std::invalid_argument("Akumajou Densetsu VRC6 CHR must be 128 KiB");
    }
}

bool Vrc6Mapper::prg_ram_enabled() const noexcept {
    return (banking_style_ & 0x80u) != 0;
}

std::uint8_t Vrc6Mapper::prg16_bank() const noexcept { return prg16_bank_; }
std::uint8_t Vrc6Mapper::prg8_bank() const noexcept { return prg8_bank_; }
std::uint8_t Vrc6Mapper::banking_style() const noexcept { return banking_style_; }

std::uint8_t Vrc6Mapper::chr_register(std::size_t index) const {
    if (index >= chr_regs_.size()) {
        throw std::out_of_range("VRC6 CHR register index");
    }
    return chr_regs_[index];
}

std::size_t Vrc6Mapper::prg_offset(std::uint16_t address) const {
    if (address >= 0x8000 && address <= 0xBFFF) {
        const std::size_t bank = prg16_bank_ & 0x0Fu;
        return bank * kPrg16Size + (address - 0x8000u);
    }
    if (address >= 0xC000 && address <= 0xDFFF) {
        const std::size_t bank = prg8_bank_ & 0x1Fu;
        return bank * kPrg8Size + (address - 0xC000u);
    }
    if (address >= 0xE000) {
        return (31u * kPrg8Size) + (address - 0xE000u);
    }
    throw std::out_of_range("address is outside VRC6 PRG ROM windows");
}

std::uint8_t Vrc6Mapper::cpu_read(std::uint16_t address) const {
    if (address >= 0x6000 && address <= 0x7FFF) {
        return prg_ram_enabled() ? prg_ram_[address - 0x6000u] : 0xFFu;
    }
    if (address >= 0x8000) {
        return prg_[prg_offset(address)];
    }
    return 0xFFu;
}

void Vrc6Mapper::cpu_write(std::uint16_t address, std::uint8_t value) {
    if (address >= 0x6000 && address <= 0x7FFF) {
        if (prg_ram_enabled()) {
            prg_ram_[address - 0x6000u] = value;
        }
        return;
    }
    if (address < 0x8000) {
        return;
    }

    // VRC6a only decodes CPU A0, A1, and A12-A15 for mapper registers.
    const auto reg = static_cast<std::uint16_t>(address & kRegisterMask);
    if (reg >= 0x8000 && reg <= 0x8003) {
        prg16_bank_ = value & 0x0Fu;
        return;
    }
    if (reg == 0xB003) {
        banking_style_ = value;
        return;
    }
    if (reg >= 0xC000 && reg <= 0xC003) {
        prg8_bank_ = value & 0x1Fu;
        return;
    }
    if (reg >= 0xD000 && reg <= 0xD003) {
        chr_regs_[reg - 0xD000u] = value;
        return;
    }
    if (reg >= 0xE000 && reg <= 0xE003) {
        chr_regs_[4u + (reg - 0xE000u)] = value;
        return;
    }
    // $9000-$B002 are VRC6 audio; $F000-$F002 are IRQ registers.
    // Those subsystems intentionally live outside the PRG/CHR mapper lift.
}

std::uint8_t Vrc6Mapper::selected_chr_bank(std::size_t slot) const {
    assert(slot < 8);
    const std::uint8_t mode = banking_style_ & 0x03u;

    // NESdev Mapper-24 pattern-table mapping:
    // mode 0: 8 x 1 KiB, R0..R7
    // mode 1: 4 x 2 KiB, R0..R3
    // mode 2/3: 4 x 1 KiB (R0..R3) + 2 x 2 KiB (R4..R5)
    std::uint8_t reg_index = 0;
    bool two_kib = false;
    if (mode == 0) {
        reg_index = static_cast<std::uint8_t>(slot);
    } else if (mode == 1) {
        reg_index = static_cast<std::uint8_t>(slot / 2u);
        two_kib = true;
    } else if (slot < 4) {
        reg_index = static_cast<std::uint8_t>(slot);
    } else {
        reg_index = static_cast<std::uint8_t>(4u + ((slot - 4u) / 2u));
        two_kib = true;
    }

    std::uint8_t bank = chr_regs_[reg_index];
    if (two_kib) {
        if (banking_style_ & 0x20u) {
            // Target-game configuration: CHR A10 comes from PPU A10.
            bank = static_cast<std::uint8_t>((bank & 0xFEu) | (slot & 1u));
        }
        // With bit 5 clear the register LSB directly controls A10, so both
        // halves of the nominal 2 KiB region map the same 1 KiB page.
    }
    return bank;
}

std::uint8_t Vrc6Mapper::chr_bank_for_1k_slot(std::size_t slot) const {
    if (slot >= 8) {
        throw std::out_of_range("VRC6 CHR slot");
    }
    return static_cast<std::uint8_t>(selected_chr_bank(slot) % (chr_.size() / kChr1kSize));
}

std::uint8_t Vrc6Mapper::ppu_read(std::uint16_t address) const {
    if (address >= 0x2000) {
        throw std::out_of_range("VRC6 mapper ppu_read only handles pattern-table CHR");
    }
    const std::size_t slot = address / kChr1kSize;
    const std::size_t bank = chr_bank_for_1k_slot(slot);
    return chr_[bank * kChr1kSize + (address & 0x03FFu)];
}

NametableMirroring Vrc6Mapper::mirroring() const {
    // Akumajou Densetsu uses mapper mode 0, CIRAM nametables, and bit 5 set.
    // In this mode B003 bits 2-3 are exactly V/H/1A/1B.
    switch ((banking_style_ >> 2u) & 0x03u) {
        case 0: return NametableMirroring::Vertical;
        case 1: return NametableMirroring::Horizontal;
        case 2: return NametableMirroring::OneScreenA;
        case 3: return NametableMirroring::OneScreenB;
    }
    return NametableMirroring::Vertical;
}

std::uint8_t Vrc6Mapper::ciram_a10(std::uint16_t ppu_address) const {
    assert(ppu_address >= 0x2000 && ppu_address < 0x3000);
    switch (mirroring()) {
        case NametableMirroring::Vertical:
            return static_cast<std::uint8_t>((ppu_address >> 10u) & 1u);
        case NametableMirroring::Horizontal:
            return static_cast<std::uint8_t>((ppu_address >> 11u) & 1u);
        case NametableMirroring::OneScreenA:
            return 0;
        case NametableMirroring::OneScreenB:
            return 1;
    }
    return 0;
}

}  // namespace cv3
