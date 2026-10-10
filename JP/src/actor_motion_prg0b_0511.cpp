#include "actor_motion_prg0b_0511.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
// NMOS 6502 ADC flag semantics for the 2A03 (decimal mode has no effect).
std::uint8_t adc(std::uint8_t a, std::uint8_t b, std::uint8_t& p) noexcept {
    const unsigned sum = unsigned(a)+unsigned(b)+unsigned(p&1u);
    const std::uint8_t result = static_cast<std::uint8_t>(sum);
    const bool overflow = ((~(a^b) & (a^result))&0x80u)!=0;
    p = static_cast<std::uint8_t>((p & ~0xC3u) |
        (sum>255 ? 0x01u : 0u) |
        (result==0 ? 0x02u : 0u) |
        (result & 0x80u) |
        (overflow ? 0x40u : 0u));
    return result;
}
void nz(std::uint8_t a, std::uint8_t& p) noexcept {
    p=static_cast<std::uint8_t>((p & ~0x82u)|(a & 0x80u)|(a==0 ? 0x02u:0u));
}
}
Prg0bMotionResult apply_prg0b_actor_motion_8001(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t x, std::uint8_t initial_p) {
    if (x>12) throw std::invalid_argument("raw $0B actor motion requires X<=12");
    auto p=initial_p;
    // $8001-$8010: preserve higher actor direction/attribute bits and
    // sign-extend the horizontal *integer* speed into $01.
    std::uint8_t a=ram[0x0470u+x]; nz(a,p);
    a=static_cast<std::uint8_t>(a & 0xfeu); nz(a,p);
    ram[0]=a;
    std::uint8_t y=0; nz(y,p);
    a=ram[0x04f2u+x]; nz(a,p);
    if (a & 0x80u) { y=0xff; nz(y,p); }
    ram[1]=y;
    // $8012: JSR $8037. Source $8037 CLC + two 8-bit ADCs form a
    // fractional/integer 16-bit X update with authentic carry propagation.
    p=static_cast<std::uint8_t>(p & ~1u);
    a=ram[0x04c4u+x]; nz(a,p);
    a=adc(a,ram[0x0509u+x],p);ram[0x04c4u+x]=a;
    a=ram[0x0438u+x]; nz(a,p);
    a=adc(a,ram[0x04f2u+x],p);ram[0x0438u+x]=a;
    // $8015-$8020: carry + velocity sign update the 9th X-coordinate bit.
    a=ram[0x0470u+x]; nz(a,p);
    a=static_cast<std::uint8_t>(a & 1u); nz(a,p);
    a=adc(a,ram[1],p);
    a=static_cast<std::uint8_t>(a & 1u); nz(a,p);
    a=static_cast<std::uint8_t>(a | ram[0]); nz(a,p);
    ram[0x0470u+x]=a;
    // $8023-$8036: 16-bit Y update (fraction $04DB plus $0537; high
    // $041C plus $0520). The final ADC sets live A/N/Z/C/V.
    p=static_cast<std::uint8_t>(p & ~1u);
    a=ram[0x04dbu+x]; nz(a,p);
    a=adc(a,ram[0x0537u+x],p);ram[0x04dbu+x]=a;
    a=ram[0x041cu+x]; nz(a,p);
    a=adc(a,ram[0x0520u+x],p);ram[0x041cu+x]=a;
    return {a,y,p};
}
}
