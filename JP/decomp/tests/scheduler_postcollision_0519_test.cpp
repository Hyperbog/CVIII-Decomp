#include "scheduler_postcollision_0519.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <array>
#include <stdexcept>
#include <cstdint>
#include <iostream>
using Ram=std::array<std::uint8_t,0x800>;
static std::uint8_t nz(std::uint8_t p,std::uint8_t v){return std::uint8_t((p&~0x82u)|(v&0x80u)|(v==0?2u:0u));}
static std::uint8_t cmp(std::uint8_t p,std::uint8_t a,std::uint8_t v){const auto d=std::uint8_t(a-v);return std::uint8_t((p&~0x83u)|(a>=v?1u:0u)|(d==0?2u:0u)|(d&0x80u));}
int main(){unsigned tested=0;
 for(unsigned slot=1;slot<=18;++slot)for(unsigned type=0;type<256;++type)for(unsigned attr=0;attr<16;++attr){
  Ram r{};r.fill(0x5a);r[0x69]=std::uint8_t(slot);r[0x54e + slot]=std::uint8_t(type);r[0x470 + slot]=std::uint8_t((attr*17u)&255u);
  const auto old=r;
  const auto input_p=std::uint8_t((slot*13+type*19+attr*37)&255u);
  auto got=cv3::scheduler_post_collision_fe00_0519(r,0x84,0x4f,input_p);
  auto p=nz(input_p,std::uint8_t(slot)); auto a=std::uint8_t(type);p=nz(p,a);unsigned pc=0;
  if(a==0)pc=0xfe6e;
  else {p=cmp(p,a,0x30);
   if(a<0x30){a=9;p=nz(p,a);pc=0xfe0b;}
   else {a=r[0x470 + slot];p=nz(p,a);a&=2;p=nz(p,a);
    if(a)pc=0xfe1d;
    else {a=std::uint8_t(type);p=nz(p,a);
     if(a&128)pc=0xfe31;
     else {p=cmp(p,a,0x69);pc=a>=0x69?0xfe36:0xfe2c;}
    }
   }
  }
  assert(got.next_pc==pc&&got.a==a&&got.x==slot&&got.y==0x4f&&got.p==p&&r==old);
  ++tested;
 }
 for(unsigned slot:{0u,19u,255u}){Ram r{};r.fill(0);r[0x69]=std::uint8_t(slot);const auto old=r;bool bad=false;try{(void)cv3::scheduler_post_collision_fe00_0519(r,0,0,0);}catch(const std::invalid_argument&){bad=true;}assert(bad&&r==old);++tested;}
 std::cout<<"PASS original fixed-bank FDFE/FE00 bounded scheduler gate: "<<tested<<" cases\n";
}
