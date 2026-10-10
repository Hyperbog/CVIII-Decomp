#pragma once
#include <cstdint>
#include <stdexcept>

namespace cv3 {
class CpuBus {
public:
    virtual ~CpuBus() = default;
    virtual std::uint8_t read(std::uint16_t address) = 0;
    virtual void write(std::uint16_t address, std::uint8_t value) = 0;
};

struct CpuRegisters {
    std::uint16_t pc = 0;
    std::uint8_t a = 0, x = 0, y = 0, sp = 0xFD, p = 0x24;
};

// Original Ricoh 2A03 instruction interpreter. Decimal flag is preserved but
// ADC/SBC are always binary. This is a CPU, not a PPU/mapper/frame emulator.
// All 151 OFFICIAL NMOS 6502 opcodes; unsupported opcodes fail explicitly.
class Cpu2A03 {
public:
    explicit Cpu2A03(CpuBus& bus) : bus_(bus) {}
    void reset();
    void set_registers(CpuRegisters value) noexcept { state_ = value; state_.p |= 0x20; }
    [[nodiscard]] const CpuRegisters& registers() const noexcept { return state_; }
    [[nodiscard]] std::uint64_t instruction_count() const noexcept { return instructions_; }
    [[nodiscard]] std::uint64_t cycle_count() const noexcept { return cycles_; }
    void nmi(); // caller is responsible for timing/edge detection
    void irq(); // ignored while interrupt-disable flag is set
    // Returns number of CPU cycles for one official opcode including branch and page-cross costs.
    std::uint8_t step();
private:
    CpuBus& bus_;
    CpuRegisters state_{};
    std::uint64_t instructions_ = 0, cycles_ = 0;
    std::uint8_t get();
    std::uint16_t get16();
    std::uint16_t read16(std::uint16_t at);
    std::uint16_t readzp16(std::uint8_t at);
    void push(std::uint8_t value);
    std::uint8_t pop();
    void nz(std::uint8_t value);
    bool flag(std::uint8_t bit) const { return (state_.p & bit) != 0; }
    void setflag(std::uint8_t bit, bool on);
    void vector(std::uint16_t address, bool brk);
};
} // namespace cv3
