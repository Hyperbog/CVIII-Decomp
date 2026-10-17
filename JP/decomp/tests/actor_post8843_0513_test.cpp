#include "actor_displacement_vertical_prg0b_0513.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <array>
#include <cstdint>
#include <iostream>
using Ram=std::array<std::uint8_t,0x800>;
int main(){
  std::uint64_t cases=0;
  for(unsigned axis=0;axis<2;++axis){
   for(unsigned pos=0;pos<256;++pos){
    for(unsigned delta=0;delta<256;++delta){
     Ram r{};r.fill(0xa5);
     r[0x65]=static_cast<std::uint8_t>(0x80u|axis);
     r[0x6b]=static_cast<std::uint8_t>(delta);
     r[0x041d]=static_cast<std::uint8_t>(pos);
     r[0x0471]=0x44; // low attribute bit 0
     r[0x054f]=0x3b;
     r[0x0607]=static_cast<std::uint8_t>(pos);
     r[0x061e]=static_cast<std::uint8_t>(delta);
     auto before=r;
     const auto prefix=cv3::apply_prg0b_actor_displacement_80e3_vertical(r,1,0);
     if(prefix.exit==cv3::ActorVerticalExit0513::TransferToRaw8843){
       const auto out=cv3::apply_prg0b_actor_8843_continuation(r,prefix);
       assert(out.exit==cv3::ActorVerticalExit0513::ReturnToFixedFDFB);
       if(delta!=0){
         const int added=int(delta)-(axis ? 256:0);
         const unsigned total=(int((delta<<8)|pos)+added)&65535;
         assert(r[0x0607]==(total&255u));
         assert(r[0x061e]==(total>>8));
         assert(r[4]==(axis ? 0xffu:0u));
       }else{
         assert(r[0x0607]==before[0x0607]&&r[0x061e]==before[0x061e]);
         assert(r[4]==before[4]);
       }
     }
     const auto full=cv3::apply_prg0b_actor_displacement_80e3_vertical_complete(before,1,0);
     assert(full.exit==cv3::ActorVerticalExit0513::ReturnToFixedFDFB);
     assert(before==r);
     ++cases;
    }
   }
  }
  std::cout<<"PASS 0513 post-$8843 original 16-bit type-$3B arithmetic "<<cases<<" cases\n";
}
