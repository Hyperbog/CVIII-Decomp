#include "actor_collision_measure_0516.hpp"
#include "actor_collision_tables_0516.hpp"
#include "actor_collision_precheck_0515.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
struct Cpu {
  std::uint8_t a,y,p;
  void nz(std::uint8_t value) noexcept { p=std::uint8_t((p&~0x82u)|(value&0x80u)|(value==0?2u:0u)); }
  void lda(std::uint8_t v) noexcept {a=v;nz(a);}
  void ldy(std::uint8_t v) noexcept {y=v;nz(y);}
  void iny() noexcept {y=std::uint8_t(y+1);nz(y);}
  void clc() noexcept {p=std::uint8_t(p&~1u);}
  void sec() noexcept {p=std::uint8_t(p|1u);}
  void adc(std::uint8_t v) noexcept {
    auto old=a;const auto sum=unsigned(a)+unsigned(v)+unsigned(p&1u);
    a=std::uint8_t(sum);
    const unsigned ov=(~(old^v)&(old^a)&0x80u)?0x40u:0u;
    p=std::uint8_t((p&~0xc3u)|(sum>255u?1u:0u)|(a==0?2u:0u)|(a&0x80u)|ov);
  }
  void sbc(std::uint8_t v) noexcept {
    auto old=a;const auto sub=unsigned(a)-unsigned(v)-unsigned((p&1u)^1u);
    a=std::uint8_t(sub);
    const unsigned ov=((old^v)&(old^a)&0x80u)?0x40u:0u;
    p=std::uint8_t((p&~0xc3u)|(sub<=255u?1u:0u)|(a==0?2u:0u)|(a&0x80u)|ov);
  }
  void cmp(std::uint8_t v) noexcept {
    const auto sub=std::uint8_t(a-v);
    p=std::uint8_t((p&~0x83u)|(a>=v?1u:0u)|(sub==0?2u:0u)|(sub&0x80u));
  }
  void and_(std::uint8_t v) noexcept {a=std::uint8_t(a&v);nz(a);}
  void eor(std::uint8_t v) noexcept {a=std::uint8_t(a^v);nz(a);}
  // ROM $80B3 and $80C1 source helper, including shared $80BC and $80C0.
  void absolute_difference(std::uint8_t first,std::uint8_t second) noexcept {
    sec();lda(first);sbc(second);
    if(!(p&1u)){eor(0xffu);adc(1u);} // SBC's carry=0 is preserved for ADC
  }
};
}
CollisionMeasure0516 actor_collision_measure_b1f8_to_b393(
  std::array<std::uint8_t,0x800>& ram, std::uint8_t x,
  std::uint8_t y,std::uint8_t p) {
  const auto gate=actor_pre_collision_b1f8_through_b231(ram,x,y,p);
  if(gate.next_pc!=0xb232u)
      return {gate.next_pc,gate.a,gate.x,gate.y,gate.p,false};
  return actor_collision_measure_b339(ram,x,gate.a,gate.y,gate.p);
}
CollisionMeasure0516 actor_collision_measure_b339(
   std::array<std::uint8_t,0x800>& r, std::uint8_t x,
   std::uint8_t a,std::uint8_t y,std::uint8_t p) {
  if(x<1 || x>17 || r[0x7f]>8 || r[0xB7]!=0 || r[0x054eu+x]>0x68u ||
     (r[0x048cu+x]==0x08u && r[0x0400u+x]>=0xeeu))
     throw std::invalid_argument("JP B339 bounded source entry: unsupported E5BE/B396/ROM-index route");
  Cpu c{a,y,p};
  c.ldy(r[0x7f]);
  c.lda(rom0516::baseX[c.y]);r[0]=c.a;
  c.lda(rom0516::baseY[c.y]);r[1]=c.a;
  c.ldy(r[0x054eu+x]);
  c.lda(r[0x048cu+x]);c.cmp(0x08u);
  if(c.a==0x08u){c.lda(r[0x0400u+x]);c.cmp(0xeeu);}
  c.lda(r[0xB7]);
  c.clc();
  c.ldy(r[0x054eu+x]);
  c.lda(rom0516::radiusX[c.y]);c.adc(r[0]);r[2]=c.a;
  c.absolute_difference(r[0x0438u+x],r[0x0438]);
  c.cmp(r[2]);
  if(c.p&1u)return {0xB393u,c.a,x,c.y,c.p,false};
  c.clc();c.lda(rom0516::radiusY[c.y]);c.adc(r[1]);r[3]=c.a;
  c.ldy(0);
  c.lda(r[0x7f]);c.cmp(0x04u);
  if(c.p&1u)c.iny();
  c.clc();c.lda(rom0516::playerOffsetY[c.y]);c.adc(r[0x041c]);r[0x11]=c.a;
  c.absolute_difference(r[0x041cu+x],r[0x11]);
  c.cmp(r[3]);
  return {0xB393u,c.a,x,c.y,c.p,true};
}
}
