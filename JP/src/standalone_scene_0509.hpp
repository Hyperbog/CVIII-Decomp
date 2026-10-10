#pragma once
#include "actor_slot_0509.hpp"
#include "collision_math.hpp"
#include "oam_renderer.hpp"
#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace cv3 {
// ROM-INDEPENDENT TECHNICAL DEMONSTRATOR, NOT CASTLEVANIA III GAMEPLAY.
// Uses the previously proved raw-$0D OAM assembler, fixed PRG31 object field
// clear, and raw-$0B 8-bit collision primitives against SYNTHETIC ROM-FREE
// descriptors and procedure-generated 2bpp tiles and a placeholder scene.
class StandaloneScene0509 {
public:
    static constexpr unsigned kWidth=256, kHeight=240;
    // Demonstration-only control bits (not NES $4016 layout).
    enum Input : std::uint8_t {Right=1,Left=2,Jump=4,RemoveEnemy=8};
    StandaloneScene0509();
    void step(std::uint8_t input);
    [[nodiscard]] std::vector<std::uint8_t> render_rgb() const;
    [[nodiscard]] std::uint64_t frame() const noexcept {return frame_;}
    [[nodiscard]] std::uint64_t near_contact_frames() const noexcept {return contact_frames_;}
    [[nodiscard]] bool enemy_present() const noexcept {return enemy_present_;}
    [[nodiscard]] std::uint8_t player_x() const noexcept {return x_;}
    [[nodiscard]] std::uint8_t player_y() const noexcept {return y_;}
    [[nodiscard]] const std::array<std::uint8_t,0x800>& ram() const noexcept {return ram_;}
    [[nodiscard]] OamFrameResult last_oam_status() const noexcept {return oam_status_;}
    [[nodiscard]] static std::uint64_t fnv1a64(const std::vector<std::uint8_t>& pixels) noexcept;
private:
    void configure_synthetic_resources();
    void stage_object(std::uint8_t slot,std::uint8_t selector,std::uint8_t x,std::uint8_t y);
    static void put_ptr(std::array<std::uint8_t,0x4000>& b,std::uint16_t addr,std::uint16_t pointer);
    std::array<std::uint8_t,0x800> ram_{};
    std::array<std::uint8_t,0x4000> synthetic_descriptors_{};
    std::array<std::uint8_t,0x2000> synthetic_chr_{};
    std::uint64_t frame_=0,contact_frames_=0;
    std::uint8_t x_=48, y_=105, enemy_x_=142,enemy_y_=105;
    bool enemy_present_=true;
    OamFrameResult oam_status_=OamFrameResult::Completed;
};
} // namespace cv3
