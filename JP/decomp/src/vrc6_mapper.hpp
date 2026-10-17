#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace cv3 {

enum class NametableMirroring : std::uint8_t {
    Vertical,
    Horizontal,
    OneScreenA,
    OneScreenB,
};

// Target-game Mapper 24 / Konami VRC6a memory mapper.
//
// This class models the PRG, CHR, PRG-RAM-enable, and CIRAM-mirroring behavior
// used by Akumajou Densetsu. VRC6 audio and IRQ timing are intentionally kept
// outside this class; their register ranges are not interpreted here.
class Vrc6Mapper {
public:
    static constexpr std::size_t kPrgSize = 0x40000;   // 256 KiB
    static constexpr std::size_t kChrSize = 0x20000;   // 128 KiB in target ROM
    static constexpr std::size_t kPrgRamSize = 0x2000;

    Vrc6Mapper(std::span<const std::uint8_t> prg,
               std::span<const std::uint8_t> chr);

    [[nodiscard]] std::uint8_t cpu_read(std::uint16_t address) const;
    void cpu_write(std::uint16_t address, std::uint8_t value);

    [[nodiscard]] std::uint8_t ppu_read(std::uint16_t address) const;

    [[nodiscard]] bool prg_ram_enabled() const noexcept;
    [[nodiscard]] std::uint8_t prg16_bank() const noexcept;
    [[nodiscard]] std::uint8_t prg8_bank() const noexcept;
    [[nodiscard]] std::uint8_t banking_style() const noexcept;
    [[nodiscard]] std::uint8_t chr_register(std::size_t index) const;
    [[nodiscard]] std::uint8_t chr_bank_for_1k_slot(std::size_t slot) const;
    [[nodiscard]] NametableMirroring mirroring() const;
    [[nodiscard]] std::uint8_t ciram_a10(std::uint16_t ppu_address) const;

private:
    [[nodiscard]] std::size_t prg_offset(std::uint16_t address) const;
    [[nodiscard]] std::uint8_t selected_chr_bank(std::size_t slot) const;

    std::vector<std::uint8_t> prg_;
    std::vector<std::uint8_t> chr_;
    std::array<std::uint8_t, kPrgRamSize> prg_ram_{};

    std::uint8_t prg16_bank_ = 0;
    std::uint8_t prg8_bank_ = 0;
    std::uint8_t banking_style_ = 0x20;  // target game always uses CHR A10 pass-through
    std::array<std::uint8_t, 8> chr_regs_{};
};

}  // namespace cv3
