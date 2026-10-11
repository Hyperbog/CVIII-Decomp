#include "scheduler_linked_actor_0524.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
std::uint8_t cpx13(std::uint8_t p,std::uint8_t x) noexcept {
    const auto diff=static_cast<std::uint8_t>(x-0x13u);
    return static_cast<std::uint8_t>((p&~0x83u) |
        (x>=0x13u ? 1u:0u)|(x==0x13u ? 2u:0u)|(diff&0x80u));
}
void b56b_clear(std::array<std::uint8_t,0x800>& r,std::uint8_t x) noexcept {
    r[0x0657u+x]=0u;
    r[0x0470u+x]=0u;
    r[0x05c1u+x]=0u;
    r[0x0400u+x]=0u;
}
}
SchedulerStep0522 scheduler_fe63_to_next_0524(
    std::array<std::uint8_t,0x800>& r,
    std::uint8_t x,std::uint8_t a,std::uint8_t y,std::uint8_t p) {
    if(x<0x0du || x>0x12u)
        throw std::invalid_argument("0524: unlifted lower-index $8161");
    if(r[0x054eu+x]!=0x4du || r[0x041cu+x]<0xf8u)
        return scheduler_fe63_to_next_0523(r,x,a,y,p);
    r[0x23u]=0x0bu; // $FE63 -> $E2D0 selects bank $0B.
    const auto attr=r[0x0470u+x];
    r[0x0470u+x]=(attr&0x09u)!=0u
        ? static_cast<std::uint8_t>(attr|0x80u)
        : static_cast<std::uint8_t>(attr&0x7fu);
    const auto linked_x=r[0x061du+x]; // $81B2 LDA $061D,X; TAX.
    if((r[0x0470u+linked_x]&0x81u)!=0u) {
        // $81BD JSR $B56B; $81C0 STA $054E,X.
        b56b_clear(r,linked_x);
        r[0x054eu+linked_x]=0u;
    }
    // $81C3 LDX $69; JSR $B56B; STA $054E,X; RTS.
    const auto owner_x=r[0x69];
    b56b_clear(r,owner_x);
    r[0x054eu+owner_x]=0u;
    const auto next_x=static_cast<std::uint8_t>(owner_x+1u);
    return {next_x>=0x13u ? std::uint16_t{0xfe75u}
                           : std::uint16_t{0xfdecu},
            0u,next_x,y,cpx13(p,next_x),0x0bu};
}
}
