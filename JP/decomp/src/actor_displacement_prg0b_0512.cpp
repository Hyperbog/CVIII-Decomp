#include "actor_displacement_prg0b_0512.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
std::uint8_t with_nz(std::uint8_t p, std::uint8_t value) noexcept {
    return static_cast<std::uint8_t>((p & ~0x82u) | (value & 0x80u) |
            (value==0 ? 0x02u:0u));
}
// Exact NMOS-6502 SBC flags for the NES 2A03 (binary arithmetic).
std::uint8_t subtract(std::uint8_t a, std::uint8_t operand,
                       std::uint8_t& p) noexcept {
    const unsigned diff = unsigned(a)-unsigned(operand)-unsigned((p&1u)^1u);
    const auto result = static_cast<std::uint8_t>(diff);
    const auto overflow = ((a^result)&(a^operand)&0x80u)!=0;
    p = static_cast<std::uint8_t>((p & ~0xc3u) |
            (diff<256u ? 1u:0u) | (result==0 ? 2u:0u) |
            (result&0x80u) | (overflow ? 0x40u:0u));
    return result;
}
}
ActorDisplacement0512 apply_prg0b_actor_displacement_80e3_horizontal(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t x,
    std::uint8_t initial_p) {
    if(x<1 || x>12 || (ram[0x65]&0x80u)!=0)
        throw std::invalid_argument("$0B:$80E3 horizontal branch requires X=1..12, $65 bit7 clear");
    auto p=initial_p;
    // $80E3-$80EA: retain attribute bits except high X coordinate in $01.
    std::uint8_t a=ram[0x0470u+x];p=with_nz(p,a);
    a=static_cast<std::uint8_t>(a&0xfeu);p=with_nz(p,a);ram[1]=a;
    std::uint8_t y=0;p=with_nz(p,y);
    // $80EC-$80F1: sign-extend the $6B signed displacement into ZP $00.
    a=ram[0x6b];p=with_nz(p,a);
    if(a&0x80u){y=0xff;p=with_nz(p,y);}
    ram[0]=y;
    a=ram[0x65];p=with_nz(p,a); // BMI $810F not taken in this scope.
    // $80F7-$80FD: 8-bit whole X subtraction, C preserves no-borrow.
    p=static_cast<std::uint8_t>(p|1u);
    a=ram[0x0438u+x];p=with_nz(p,a);
    a=subtract(a,ram[0x6b],p);ram[0x0438u+x]=a;
    // $8100-$810B: 9th X bit minus signed extension and earlier borrow;
    // preserve every attribute bit except bit0. C and V survive the final ORA.
    a=ram[0x0470u+x];p=with_nz(p,a);
    a=static_cast<std::uint8_t>(a&1u);p=with_nz(p,a);
    a=subtract(a,ram[0],p);
    a=static_cast<std::uint8_t>(a&1u);p=with_nz(p,a);
    a=static_cast<std::uint8_t>(a|ram[1]);p=with_nz(p,a);
    ram[0x0470u+x]=a;
    return {a,x,y,p};
}
}
