#include "actor_animation_ef93_0521.hpp"
#include "original_ef93_tables_0521.hpp"
#include "scheduler_bd11_followup_0520.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
struct Cpu {
 std::uint8_t a,y,p;
 void nz(std::uint8_t v) noexcept {p=std::uint8_t((p&~0x82u)|(v&0x80u)|(v==0?2u:0u));}
 void lda(std::uint8_t v) noexcept {a=v;nz(a);}
 void ldy(std::uint8_t v) noexcept {y=v;nz(y);}
 void iny() noexcept {y=std::uint8_t(y+1u);nz(y);}
 void clc() noexcept {p=std::uint8_t(p&~1u);}
 void asl() noexcept {const auto old=a;a=std::uint8_t(a<<1u);p=std::uint8_t((p&~1u)|(old>>7u));nz(a);}
 void adc(std::uint8_t operand) noexcept {
  const auto old=a;const auto sum=unsigned(a)+unsigned(operand)+unsigned(p&1u);a=std::uint8_t(sum);
  const auto over=(~(old^operand)&(old^a)&0x80u)?0x40u:0u;
  p=std::uint8_t((p&~0xc3u)|(sum>0xffu?1u:0u)|(a==0?2u:0u)|(a&0x80u)|over);
 }
 void cmp(std::uint8_t operand) noexcept {
  const auto diff=std::uint8_t(a-operand);
  p=std::uint8_t((p&~0x83u)|(a>=operand?1u:0u)|(diff==0?2u:0u)|(diff&0x80u));
 }
};
}
AnimationUpdate0521 actor_animation_ef93_0521(std::array<std::uint8_t,0x800>& r,
 std::uint8_t x,std::uint8_t a,std::uint8_t y,std::uint8_t p) {
 if(x<1u||x>18u)throw std::invalid_argument("Original JP actor index must be 1..18");
 const auto index=0x057cu+x;
 const auto timer=std::uint8_t(r[index]-1u); // $EF93 DEC $057C,X, wraps 0->FF
 // A source-path rejection before any RAM writes, so unsupported descriptor
 // bytes never receive a misleading partially executed native state.
 if(timer==0u && (r[0x048cu+x]!=0x0eu || r[0x05aau+x]>15u))
    throw std::invalid_argument("Unlifted $EFD2 descriptor pointer / $F359 frame index");
 Cpu cpu{a,y,p};r[index]=timer;cpu.nz(timer);
 if(timer!=0u)return {0xfe63u,cpu.a,x,cpu.y,cpu.p,false}; // EF98 RTS
 // $EF99 LDY $048C,X, indexed pointer table $EFD2/$EFD3 to $F359.
 cpu.ldy(r[0x048cu+x]);
 cpu.lda(ef93rom0521::descriptorPointerLow);r[0x08]=cpu.a;
 cpu.lda(ef93rom0521::descriptorPointerHigh);r[0x09]=cpu.a;
 cpu.lda(r[0x05aau+x]);cpu.asl();cpu.clc();cpu.adc(r[0x05aau+x]);cpu.y=cpu.a;cpu.nz(cpu.y);
 auto frame_offset=static_cast<unsigned>(cpu.y);
 cpu.lda(ef93rom0521::descriptor0e[frame_offset]);cpu.clc();cpu.adc(r[0x0593u+x]);r[0x0400u+x]=cpu.a;
 cpu.iny();cpu.lda(ef93rom0521::descriptor0e[++frame_offset]);r[index]=cpu.a;
 cpu.iny();++frame_offset;
 for(unsigned i=0;i<2u;++i){const auto next=std::uint8_t(r[0x0593u+x]+1u);r[0x0593u+x]=next;cpu.nz(next);}
 cpu.lda(r[0x0593u+x]);cpu.cmp(ef93rom0521::descriptor0e[frame_offset]);
 if((cpu.p&1u)!=0u){cpu.lda(0u);r[0x0593u+x]=cpu.a;}
 return {0xfe63u,cpu.a,x,cpu.y,cpu.p,true};
}
AnimationUpdate0521 actor_animation_fdfe_to_fe63_0521(
 std::array<std::uint8_t,0x800>& r,
 std::uint8_t a,std::uint8_t y,std::uint8_t p) {
 const auto gate=scheduler_fdfe_to_followup_0520(r,a,y,p);
 if(gate.next_pc!=0xfe60u)
   return {gate.next_pc,gate.a,gate.x,gate.y,gate.p,false};
 // Real $FE60 JSR $EF93. Native does not model original JSR hardware stack.
 return actor_animation_ef93_0521(r,gate.x,gate.a,gate.y,gate.p);
}
}
