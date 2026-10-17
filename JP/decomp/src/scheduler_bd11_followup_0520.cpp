#include "scheduler_bd11_followup_0520.hpp"
#include "scheduler_postcollision_0519.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
std::uint8_t nz(std::uint8_t p,std::uint8_t v) noexcept {
 return static_cast<std::uint8_t>((p & ~0x82u) | (v & 0x80u) | (v==0?2u:0u));
}
std::uint8_t cmp(std::uint8_t p,std::uint8_t a,std::uint8_t b) noexcept {
 const auto d=static_cast<std::uint8_t>(a-b);
 return static_cast<std::uint8_t>((p & ~0x83u) | (a>=b?1u:0u) | (d==0?2u:0u) | (d&0x80u));
}
}
SchedulerFollowup0520 scheduler_bd11_and_fe34_0520(
   const std::array<std::uint8_t,0x800>& r,
   std::uint8_t x,std::uint8_t /*entry_a*/,std::uint8_t y,std::uint8_t p) {
 if(x<1 || x>18 || r[0x69]<1 || r[0x69]>18)
   throw std::invalid_argument("Original JP BD11/FE34 scheduler expects X=1..18 and $69 in 1..18");
 // raw $0B:$BD11 LDA $A8, $BD13 BEQ $BD1A.
 auto a=r[0xa8];p=nz(p,a);
 if(a!=0)return {0xbd15u,a,x,y,p}; // first unimplemented JSR $E744
 // $BD1A LDA $05EF,X; $BD1D BEQ $BD10 RTS to fixed $FE34.
 a=r[0x05efu+x];p=nz(p,a);
 if(a!=0)return {0xbd1fu,a,x,y,p}; // alternative source-actor table dispatcher
 // $BD10 RTS transfers to fixed $FE34; RTS does not affect status.
 // $FE34 LDX $69; $FE36 LDA $054E,X; CMP #$58/ #$30.
 x=r[0x69];p=nz(p,x);
 a=r[0x054eu+x];p=nz(p,a);
 p=cmp(p,a,0x58u);
 if(a<0x58u) {
   p=cmp(p,a,0x30u);
   if(a>=0x30u) {
     a=r[0xa8];p=nz(p,a);
     if(a!=0)return {0xfe63u,a,x,y,p};
   }
 }
 // $FE45 LDA $0470,X; AND #$40; BEQ $FE54.
 a=r[0x0470u+x];p=nz(p,a);
 a=static_cast<std::uint8_t>(a&0x40u);p=nz(p,a);
 if(a!=0) {
   a=0x0bu;p=nz(p,a); // $FE4C LDA #$0B; next source JSR $E2D0
   return {0xfe4eu,a,x,y,p};
 }
 // $FE54 LDA $054E,X; BEQ $FE6E.
 a=r[0x054eu+x];p=nz(p,a);
 if(a==0)return {0xfe6eu,a,x,y,p};
 // $FE59 LDA $0470,X; AND #$20; BNE $FE63.
 a=r[0x0470u+x];p=nz(p,a);
 a=static_cast<std::uint8_t>(a&0x20u);p=nz(p,a);
 if(a!=0)return {0xfe63u,a,x,y,p};
 return {0xfe60u,a,x,y,p}; // before original JSR $EF93
}
SchedulerFollowup0520 scheduler_fdfe_to_followup_0520(
 const std::array<std::uint8_t,0x800>& r,
 std::uint8_t a,std::uint8_t y,std::uint8_t p) {
 const auto gate=scheduler_post_collision_fe00_0519(r,a,y,p);
 if(gate.next_pc!=0xfe31u)
   return {gate.next_pc,gate.a,gate.x,gate.y,gate.p};
 // FE31 JSR BD11, bounded path returns FE34; hardware stack modeled neither
 // here nor in the other original-source-shaped, native C++ routines.
 return scheduler_bd11_and_fe34_0520(r,gate.x,gate.a,gate.y,gate.p);
}
}
