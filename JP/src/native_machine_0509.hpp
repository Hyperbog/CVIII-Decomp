#pragma once
#include "cpu_2a03.hpp"
#include "vrc6_mapper.hpp"
#include "vrc6_irq.hpp"
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace cv3 {

// Headless 2A03 + VRC6a mapped-bus integration for original-JP instruction
// verification. Not a gameplay port: incomplete 2C02 rendering, audio, DMA
// bus-cycle ordering and per-cycle CPU interrupt sampling.
class NativeMachine0509 final : public CpuBus {
public:
    NativeMachine0509(std::span<const std::uint8_t> prg,
                      std::span<const std::uint8_t> chr);
    std::uint8_t read(std::uint16_t address) override;
    void write(std::uint16_t address,std::uint8_t value) override;
    void reset();
    std::uint64_t step(); // one instruction and mapper/PPU clocks
    void set_controller1(std::uint8_t buttons) noexcept { controller_[0]=buttons; }
    void set_controller2(std::uint8_t buttons) noexcept { controller_[1]=buttons; }
    [[nodiscard]] const CpuRegisters& cpu_state() const noexcept { return cpu_.registers(); }
    [[nodiscard]] std::uint64_t executed_instructions() const noexcept { return cpu_.instruction_count(); }
    [[nodiscard]] std::uint64_t cycles() const noexcept { return cpu_cycles_; }
    [[nodiscard]] std::uint64_t frames() const noexcept { return frames_; }
    [[nodiscard]] std::uint64_t nmis() const noexcept { return nmis_; }
    [[nodiscard]] std::uint64_t irqs() const noexcept { return irqs_; }
    [[nodiscard]] std::uint8_t ram_at(std::uint16_t at) const noexcept { return ram_[at&0x7FF]; }
    [[nodiscard]] const Vrc6Mapper& mapper() const noexcept { return mapper_; }
    [[nodiscard]] const std::array<std::uint8_t,256>& oam() const noexcept { return oam_; }
private:
    void clocks(std::uint32_t cpu_cycles);
    void update_nmi();
    std::uint8_t ppu_read(std::uint16_t addr);
    void ppu_write(std::uint16_t addr,std::uint8_t v);
    Vrc6Mapper mapper_;
    Vrc6Irq irq_{};
    Cpu2A03 cpu_;
    std::array<std::uint8_t,2048> ram_{};
    std::array<std::uint8_t,2048> ciram_{};
    std::array<std::uint8_t,32> palette_{};
    std::array<std::uint8_t,256> oam_{};
    std::array<std::uint8_t,2> controller_{};
    std::array<std::uint8_t,2> shifts_{};
    std::uint8_t ppu_ctrl_=0,ppu_mask_=0,oam_addr_=0,ppu_scroll_=0,ppu_status_=0,ppu_read_buffer_=0;
    std::uint16_t ppu_addr_=0;
    bool ppu_latch_=false,strobe_=false,nmi_line_=false,nmi_pending_=false;
    std::uint64_t cpu_cycles_=0,frames_=0,nmis_=0,irqs_=0;
    std::uint32_t ppu_dot_in_frame_=0,dma_stall_=0;
};
} // namespace cv3
