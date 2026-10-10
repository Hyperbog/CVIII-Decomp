#include "actor_motion_prg0b_0511.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace {
using Ram=std::array<std::uint8_t,0x800>;
constexpr unsigned x=1;
// Independent mathematical 24-bit reference model: X is 9-bit fixed-point,
// and Y is 8-bit fixed-point; signed 8-bit whole deltas are 2's complement.
void verify_case(unsigned xpos,unsigned sub,unsigned dx,unsigned dxsub,
                 unsigned ypos,unsigned ysub,unsigned dy,unsigned dysub,
                 unsigned xhigh, unsigned other, unsigned prior_p) {
    Ram ram{};
    ram.fill(0xa5);
    ram[0x0438+x]=static_cast<std::uint8_t>(xpos);
    ram[0x04c4+x]=static_cast<std::uint8_t>(sub);
    ram[0x04f2+x]=static_cast<std::uint8_t>(dx);
    ram[0x0509+x]=static_cast<std::uint8_t>(dxsub);
    ram[0x041c+x]=static_cast<std::uint8_t>(ypos);
    ram[0x04db+x]=static_cast<std::uint8_t>(ysub);
    ram[0x0520+x]=static_cast<std::uint8_t>(dy);
    ram[0x0537+x]=static_cast<std::uint8_t>(dysub);
    ram[0x0470+x]=static_cast<std::uint8_t>((other&0xfeu)|(xhigh&1u));
    const auto before=ram;
    const auto actual=cv3::apply_prg0b_actor_motion_8001(ram,x,static_cast<std::uint8_t>(prior_p));
    const int delta_x=static_cast<int>(static_cast<std::int8_t>(dx))*256+static_cast<int>(dxsub);
    const int delta_y=static_cast<int>(static_cast<std::int8_t>(dy))*256+static_cast<int>(dysub);
    const unsigned total_x=static_cast<unsigned>((int((xhigh*256+xpos)*256+sub)+delta_x)&0x1ffff);
    const unsigned total_y=static_cast<unsigned>((int(ypos*256+ysub)+delta_y)&0xffff);
    assert(ram[0x0438+x]==((total_x>>8)&255u));
    assert(ram[0x04c4+x]==(total_x&255u));
    assert(ram[0x0470+x]==((other&0xfeu)|((total_x>>16)&1u)));
    assert(ram[0x041c+x]==((total_y>>8)&255u));
    assert(ram[0x04db+x]==(total_y&255u));
    assert(ram[0]==(other&0xfeu));
    assert(ram[1]==(dx>=0x80 ? 0xffu:0u));
    assert(actual.a==ram[0x041c+x]);
    assert(actual.y==ram[1]);
    // Source final status is the second vertical ADC; preserve I/D/B bits.
    const unsigned last=unsigned(ypos)+unsigned(dy)+(unsigned(ysub)+unsigned(dysub)>255u);
    const auto expected_p=(prior_p&0x3cu)| (last>255 ? 1u:0u) |
          (actual.a==0 ? 2u:0u) | (actual.a&0x80u) |
          (((~(ypos^dy)&(ypos^actual.a))&0x80u) ? 0x40u:0u);
    assert(actual.p==expected_p);
    for(unsigned i=2;i<ram.size();++i){
        if(i==0x0438+x||i==0x04c4+x||i==0x0470+x||
           i==0x041c+x||i==0x04db+x)continue;
        assert(ram[i]==before[i]);
    }
}
}
int main(){
 unsigned cases=0;
 // Exhaustive fraction/speed domain; deterministic orthogonal folding of
 // entire signed whole velocity range and both X-bit wrap directions.
 for(unsigned fraction=0;fraction<256;++fraction){
  for(unsigned speed_fraction=0;speed_fraction<256;++speed_fraction){
    const unsigned v=(fraction+speed_fraction)&255;
    verify_case(v,fraction,v,speed_fraction,(v*3)&255,
                speed_fraction,(speed_fraction*7)&255,fraction,
                (fraction^speed_fraction)&1u,(v*19)&0xfeu,
                (fraction*13+speed_fraction)&255);
    ++cases;
  }
 }
 // Selected fixed-point wrap, negative velocities, all native object slots,
 // including actual source-field sign extension and a zero crossing.
 for(unsigned i=0;i<4096;++i){
   verify_case((i*11)&255,(i*7)&255,(i*13)&255,(i*17)&255,
               (i*19)&255,(i*23)&255,(i*29)&255,(i*31)&255,
               (i>>3)&1,(i*37)&0xfe,(i*41)&255);
   ++cases;
 }
 for(unsigned i=0;i<=12;++i){
    Ram z{}; z.fill(0);z[0x0470+i]=0x7c;z[0x0438+i]=0x80;
    const auto r=cv3::apply_prg0b_actor_motion_8001(z,static_cast<std::uint8_t>(i),0x20);
    assert(r.a==0 && r.y==0 && (r.p&0x20)==0x20);
    assert(z[0x0438+i]==0x80 && z[0]==0x7c);
    ++cases;
 }
 bool bad=false;Ram z{};try{(void)cv3::apply_prg0b_actor_motion_8001(z,13,0);}catch(const std::invalid_argument&){bad=true;}
 assert(bad);++cases;
 std::cout<<"PASS source-aligned raw0B 8001 actor 2-axis motion: "<<cases<<" cases\n";
}
