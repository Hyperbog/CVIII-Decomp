#include "actor_slot_0509.hpp"

namespace cv3 {
ActorSlotScan scan_actor_slot(const std::array<std::uint8_t,0x800>& ram) noexcept {
    for (std::uint8_t x=1; x<0x0d; ++x) {
        if (ram[0x054Eu+x]==0) return {true,x,0};
    }
    return {false,0x0d,1};
}
void clear_actor_four_fields(std::array<std::uint8_t,0x800>& ram,std::uint8_t x) noexcept {
    for (const auto base:kFourActorFields) ram[base+x]=0;
}
void clear_actor_eighteen_fields(std::array<std::uint8_t,0x800>& ram,std::uint8_t x) noexcept {
    clear_actor_four_fields(ram,x);
    for (const auto base:kRemainingActorFields) ram[base+x]=0;
}
} // namespace cv3
