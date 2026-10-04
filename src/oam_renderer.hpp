#pragma once

#include <array>
#include <cstdint>

namespace cv3 {

struct OamContext {
    std::array<std::uint8_t, 0x800>& ram;
    const std::array<std::uint8_t, 0x4000>& bank13;
};

enum class OamFrameResult {
    Completed,
    OamFull,
};

// Faithful structured lift of PRG26:$8001 with the $8070 non-local
// PLA/PLA/RTS path represented explicitly as OamFull.
OamFrameResult build_oam_shadow(OamContext& ctx);

}  // namespace cv3
