#include "actor_collision_result_0517.hpp"
#include <stdexcept>
namespace cv3 {
namespace {
void nz(std::uint8_t& p, std::uint8_t value) noexcept {
  p=static_cast<std::uint8_t>((p & ~0x82u) | (value & 0x80u) |
        (value==0 ? 0x02u:0u));
}
void cmp(std::uint8_t& p, std::uint8_t lhs, std::uint8_t rhs) noexcept {
  const auto diff=static_cast<std::uint8_t>(lhs-rhs);
  p=static_cast<std::uint8_t>((p & ~0x83u) | (lhs>=rhs?1u:0u) |
      (diff==0?2u:0u) | (diff & 0x80u));
}
}
CollisionTail0517 actor_collision_tail_b235(
    std::array<std::uint8_t,0x800>& ram, std::uint8_t x,
    std::uint8_t a, std::uint8_t y, std::uint8_t p) {
  if(x<1 || x>17)throw std::invalid_argument("Original B235 actor index X=1..17");
  // $B235 BCS $B258: carry comes from B339's last distance CMP.
  if(!(p & 1u)) {
    a=ram[0x0657u+x];nz(p,a);ram[0x7e]=a; // B237-B23A
    a=ram[0x054eu+x];nz(p,a);cmp(p,a,0x39u); // B23C-B23F
    if(a==0x39u)return {0xb243u,a,x,y,p}; // special FF15/B568 unlifted
    ram[0x8e]=x; // B249 STX $8E, flags unchanged
    y=0;nz(p,y); // B24B LDY #$00
    a=ram[0x0438u+x];nz(p,a);
    cmp(p,a,ram[0x0438]);
    if(!(p&1u)){y=static_cast<std::uint8_t>(y+1u);nz(p,y);}
    ram[0x8d]=y; // B256 STY $8D
  }
  // $B258-$B269: source actor-type filtering and short RTS.
  a=ram[0x054eu+x];nz(p,a);cmp(p,a,0x16u);
  if(a==0x16u)return {0xfdfeu,a,x,y,p};
  cmp(p,a,0x37u);
  if(a==0x37u)return {0xfdfeu,a,x,y,p};
  cmp(p,a,0x61u);
  if(a>=0x61u) {
    cmp(p,a,0x7fu);
    if(a<0x7fu)return {0xfdfeu,a,x,y,p};
  }
  // $B26B-$B27A: attachment-postprocessing eligibility.
  a=ram[0x068du+x];nz(p,a);
  a=static_cast<std::uint8_t>(a & 1u);nz(p,a);
  if(a==0) {
    a=ram[0x0630];nz(p,a);
    if(a!=0) {
      a=ram[0x0413];nz(p,a);
      if(a!=0)return {0xb27cu,a,x,y,p}; // JSR B3EC not implemented
    }
  }
  // $B29D-$B31F: original empty-slot follower scan, three slots 20..22.
  a=0x14;nz(p,a);ram[0x9b]=a;
  while(true) {
    y=ram[0x9b];nz(p,y); // B2A1 LDY $9B
    a=ram[0x054eu+y];nz(p,a); // B2A3 LDA $054E,Y
    if(a!=0)return {0xb2a8u,a,x,y,p}; // attachment transfer unlifted
    auto next=static_cast<std::uint8_t>(ram[0x9b]+1u);
    ram[0x9b]=next;nz(p,next); // B317 INC $9B
    a=next;nz(p,a);cmp(p,a,0x17u); // B319 LDA $9B; B31B CMP #$17
    if((p&1u)!=0)return {0xfdfeu,a,x,y,p}; // B31F RTS -> fixed FDFE
  }
}
} // namespace cv3

#include "actor_collision_measure_0516.hpp"
namespace cv3 {
CollisionTail0517 actor_collision_b1f8_through_tail_0517(
  std::array<std::uint8_t,0x800>& ram,
  std::uint8_t x, std::uint8_t y, std::uint8_t p) {
  const auto measure=actor_collision_measure_b1f8_to_b393(ram,x,y,p);
  if(measure.next_pc!=0xb393u)
    return {measure.next_pc,measure.a,measure.x,measure.y,measure.p};
  // Original $B393 is RTS to $B235; it changes only the emulated stack.
  return actor_collision_tail_b235(ram,measure.x,measure.a,measure.y,measure.p);
}
}
