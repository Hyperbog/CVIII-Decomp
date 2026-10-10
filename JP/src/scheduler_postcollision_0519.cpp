#include "scheduler_postcollision_0519.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
std::uint8_t nz(std::uint8_t p, std::uint8_t v) noexcept {
 return static_cast<std::uint8_t>((p&~0x82u)|(v&0x80u)|(v==0?0x02u:0u));
}
std::uint8_t cmp(std::uint8_t p,std::uint8_t a,std::uint8_t b) noexcept {
 const auto d=static_cast<std::uint8_t>(a-b);
 return static_cast<std::uint8_t>((p&~0x83u)|(a>=b?1u:0u)|(d==0?2u:0u)|(d&0x80u));
}
}
SchedulerGate0519 scheduler_post_collision_fe00_0519(
 const std::array<std::uint8_t,0x800>& ram,std::uint8_t /*initial_a*/,
 std::uint8_t y,std::uint8_t p) {
 const auto x=ram[0x69];
 if(x<1 || x>18)throw std::invalid_argument("Fixed FDFE scheduler requires real actor X 1..18");
 // $FDFE LDX $69; $FE00 LDA $054E,X; $FE03 BEQ $FE6E.
 p=nz(p,x);
 auto a=ram[0x054eu+x];p=nz(p,a);
 if(a==0) return {0xfe6eu,a,x,y,p};
 // $FE05 CMP #$30 / $FE07 BCS $FE16.
 p=cmp(p,a,0x30u);
 if(a<0x30u) {
   // $FE09 LDA #$09; STOP before $FE0B JSR $E2D0.
   a=9;p=nz(p,a);
   return {0xfe0bu,a,x,y,p};
 }
 // $FE16 LDA $0470,X; $FE19 AND #$02 / $FE1B BEQ $FE23.
 a=ram[0x0470u+x];p=nz(p,a);
 a=static_cast<std::uint8_t>(a&2u);p=nz(p,a);
 if(a!=0)return {0xfe1du,a,x,y,p}; // before JSR $FE8C
 // $FE23 LDA $054E,X / $FE26 BMI $FE31.
 a=ram[0x054eu+x];p=nz(p,a);
 if(a&0x80u)return {0xfe31u,a,x,y,p}; // before JSR $BD11
 // $FE28 CMP #$69 / $FE2A BCS $FE36.
 p=cmp(p,a,0x69u);
 return {static_cast<std::uint16_t>(a>=0x69u?0xfe36u:0xfe2cu),a,x,y,p};
}
}
