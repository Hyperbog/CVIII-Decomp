#include "actor_preflight_0514.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
std::uint8_t nz(std::uint8_t p, std::uint8_t a) noexcept {
    return static_cast<std::uint8_t>((p & ~0x82u) | (a & 0x80u) |
        (a == 0 ? 0x02u : 0u));
}
std::uint8_t cmp(std::uint8_t p, std::uint8_t a,
                 std::uint8_t operand) noexcept {
    const auto diff=static_cast<std::uint8_t>(a-operand);
    return static_cast<std::uint8_t>((p & ~0x83u) |
       (a >= operand ? 0x01u : 0u) |
       (diff == 0 ? 0x02u : 0u) | (diff & 0x80u));
}
}
ActorPreflight0514 produce_delta6b_d2fe(std::array<std::uint8_t,0x800>& ram,
                    std::uint8_t x, std::uint8_t a, std::uint8_t p) {
    if (ram[0x62] < 2) throw std::invalid_argument(
        "D2FE short delta producer only applies for RAM $62 >= 2");
    // D2FE LDY $62; D300 BEQ; D302 DEY; D303 BEQ.
    std::uint8_t y=ram[0x62];p=nz(p,y);
    y=static_cast<std::uint8_t>(y-1u);p=nz(p,y);
    // D305 LDA $53; D307 SEC; D308 SBC $08.
    a=ram[0x53];p=nz(p,a);
    p=static_cast<std::uint8_t>(p|1u);
    const auto b=ram[0x08];
    const auto delta=static_cast<std::uint8_t>(a-b);
    const bool overflow=((a^b)&(a^delta)&0x80u)!=0;
    p=static_cast<std::uint8_t>((p & ~0xc3u) |
       (a>=b ? 0x01u:0u) | (delta==0 ? 0x02u:0u) |
       (delta&0x80u) | (overflow ? 0x40u:0u));
    a=delta;
    ram[0x6b]=a; // D30A STA $6B; D30C RTS; RTS does not change flags.
    return {0u,a,x,y,p}; // next_pc=0: source RTS caller-dependent.
}
ActorPreflight0514 actor_postprocess_b1f8_gate(
                    const std::array<std::uint8_t,0x800>& ram,
                    std::uint8_t x, std::uint8_t y, std::uint8_t p) {
    if(x<1 || x>17) throw std::invalid_argument(
        "B1F8 original fixed actor scheduler X must be 1..17");
    // B1F8 LDA $0470,X; B1FB AND #$11; B1FD BNE $B1F7.
    auto a=ram[0x0470u+x];p=nz(p,a);
    a=static_cast<std::uint8_t>(a&0x11u);p=nz(p,a);
    if(a!=0) return {0xb1f7u,a,x,y,p};
    // B1FF LDA $0400,X; B202 BEQ $B1F7.
    a=ram[0x0400u+x];p=nz(p,a);
    if(a==0) return {0xb1f7u,a,x,y,p};
    // B204 LDA $054E,X; B207 CMP #$83; B209 BCS $B1F7.
    a=ram[0x054eu+x];p=nz(p,a);
    p=cmp(p,a,0x83u);
    if(a>=0x83u) return {0xb1f7u,a,x,y,p};
    // B20B CMP #$80; B20D BCS $B258.
    p=cmp(p,a,0x80u);
    if(a>=0x80u) return {0xb258u,a,x,y,p};
    // B20F CMP #$58; B211 BCC $B217.
    p=cmp(p,a,0x58u);
    if(a<0x58u) return {0xb217u,a,x,y,p};
    // B213 CMP #$61; B215 BCC $B1F7 (otherwise fall into B217).
    p=cmp(p,a,0x61u);
    return {static_cast<std::uint16_t>(a<0x61u ? 0xb1f7u : 0xb217u),a,x,y,p};
}
}
