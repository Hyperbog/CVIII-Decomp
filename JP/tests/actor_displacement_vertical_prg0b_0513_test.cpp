#include "actor_displacement_vertical_prg0b_0513.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static void check(unsigned v,unsigned delta,unsigned high,unsigned axis,
                  unsigned type,unsigned attr,unsigned ps,unsigned slot) {
    Ram r{};r.fill(0xa5);
    const auto p0=static_cast<std::uint8_t>(ps);
    r[0x65]=static_cast<std::uint8_t>(0x80u|(axis&1u));
    r[0x6b]=static_cast<std::uint8_t>(delta);
    r[0x041c+slot]=static_cast<std::uint8_t>(v);
    r[0x0470+slot]=static_cast<std::uint8_t>((attr&0xfeu)|(high&1u));
    r[0x054e + slot]=static_cast<std::uint8_t>(type);
    r[0x0400+slot]=0x43;
    const Ram original=r;
    const auto outcome=cv3::apply_prg0b_actor_displacement_80e3_vertical(r,
       static_cast<std::uint8_t>(slot),p0);
    const int logical=static_cast<int>((high&1u)*256+v)+static_cast<std::int8_t>(delta);
    const auto total=static_cast<unsigned>(logical)&511u;
    const auto new_y=static_cast<std::uint8_t>(total);
    const auto new_h=static_cast<std::uint8_t>(total>>8);
    assert(r[0x041c+slot]==new_y);
    assert(r[0x0470+slot]==((attr&0xfeu)|new_h));
    assert(r[0]==(delta>=128?0xffu:0u));
    assert(r[1]==(attr&0xfeu));
    assert(outcome.x==slot && outcome.y==(delta>=128?0xffu:0u));
    const bool transfer=(axis&1u) ? new_y>=0x30u : new_h==0u;
    const bool cleared=(!transfer) && (type>=0x80u || type<0x68u);
    assert(outcome.removed==cleared);
    assert(outcome.exit==(transfer?cv3::ActorVerticalExit0513::TransferToRaw8843:
                               cv3::ActorVerticalExit0513::ReturnToFixedFDFB));
    assert(r[0x054e + slot]==(cleared?0u:type));
    assert(r[0x0400+slot]==(cleared?0u:0x43u));
    if(cleared) assert(outcome.a==0u);
    else if(!transfer)assert(outcome.a==type);
    else if(axis&1u)assert(outcome.a==new_y);
    else assert(outcome.a==0u);
    // Instruction-side-effects only; original program stack not simulated.
    for(unsigned i=2;i<r.size();++i){
        if(i==0x041c+slot||i==0x0470+slot||i==0x054e + slot||i==0x0400+slot)continue;
        assert(r[i]==original[i]);
    }
    // The processor's I/D/B status bits cannot be changed by this sequence.
    assert((outcome.p&0x3cu)==(p0&0x3cu));
}
int main(){
    std::uint64_t cases=0;
    // All 256x256 integer Y/delta pairs under both vertical axis flavors.
    // Deliberately fold different type thresholds and attribute high bits.
    for(unsigned v=0;v<256;++v)for(unsigned delta=0;delta<256;++delta)
        for(unsigned axis=0;axis<2;++axis){
            const unsigned types[]={0x00,0x3d,0x67,0x68,0x7f,0x80,0xff};
            const auto type=types[(v+delta+axis)%7u];
            check(v,delta,(v+delta+axis)&1u,axis,type,
                  ((v*13+delta*19)&0xfeu), (v*17+delta*7+axis)&255u,
                  1+(delta%12));
            ++cases;
        }
    // Cross product of actual deletion boundaries, odd/even choice, 9th bit.
    for(unsigned i=0;i<8192;++i){
       const unsigned types[]={0x00,0x3d,0x67,0x68,0x7f,0x80,0xff};
       check((i*41)&255,(i*17)&255,(i>>5)&1u,(i>>6)&1u,
             types[i%7],(i*31)&0xfeu,(i*23)&255,1+(i%12));
       ++cases;
    }
    for(unsigned i=1;i<=12;++i){
      Ram r{};r.fill(0xa5);r[0x65]=0;
      const auto old=r;bool rejected=false;
      try{(void)cv3::apply_prg0b_actor_displacement_80e3_vertical(r,static_cast<std::uint8_t>(i),0);}
      catch(const std::invalid_argument&){rejected=true;}
      assert(rejected&&r==old);++cases;
    }
    for(unsigned i: {0u,13u,255u}){
      Ram r{};r.fill(0xa5);r[0x65]=0x80;
      const auto old=r;bool rejected=false;
      try{(void)cv3::apply_prg0b_actor_displacement_80e3_vertical(r,static_cast<std::uint8_t>(i),0);}
      catch(const std::invalid_argument&){rejected=true;}
      assert(rejected&&r==old);++cases;
    }
    std::cout<<"PASS 0513 bank-$0B vertical prefix native cases="<<cases<<"\n";
}
