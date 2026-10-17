#include "scheduler_bd11_followup_0520.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static std::uint8_t nz(std::uint8_t p,std::uint8_t v){return std::uint8_t((p&~0x82u)|(v&0x80u)|(v==0?2:0));}
static std::uint8_t cmp(std::uint8_t p,std::uint8_t a,std::uint8_t b){const auto d=std::uint8_t(a-b);return std::uint8_t((p&~0x83u)|(a>=b?1:0)|(d==0?2:0)|(d&0x80u));}
static void check(unsigned serial){
 const unsigned type=serial&255,flags=(serial>>8)&15,slot=1+(serial%18),variant=serial%3;
 Ram r{};r.fill(0xa5);r[0x69]=std::uint8_t(slot);
 r[0x54e + slot]=std::uint8_t(type);r[0x470+slot]=std::uint8_t(flags*17u);
 r[0xa8]=std::uint8_t(variant==1?0x71:0);r[0x05ef+slot]=std::uint8_t(variant==2?0x82:0);
 const auto old=r;const auto p0=std::uint8_t((serial*21u+17)&255);
 const auto got=cv3::scheduler_bd11_and_fe34_0520(r,std::uint8_t(slot),0x36,0x59,p0);
 auto p=nz(p0,r[0xa8]);auto a=r[0xa8];unsigned dest=0;
 if(a)dest=0xbd15;
 else {a=r[0x05ef+slot];p=nz(p,a);if(a)dest=0xbd1f;
 else {p=nz(p,std::uint8_t(slot));a=std::uint8_t(type);p=nz(p,a);p=cmp(p,a,0x58);
 if(a<0x58){p=cmp(p,a,0x30);if(a>=0x30){a=r[0xa8];p=nz(p,a);if(a)dest=0xfe63;}}
 if(!dest){a=r[0x470+slot];p=nz(p,a);a=std::uint8_t(a&0x40);p=nz(p,a);
 if(a){a=0x0b;p=nz(p,a);dest=0xfe4e;}
 else{a=std::uint8_t(type);p=nz(p,a);
 if(a==0)dest=0xfe6e;
 else{a=r[0x470+slot];p=nz(p,a);a=std::uint8_t(a&0x20);p=nz(p,a);dest=a?0xfe63:0xfe60;}
 }}}}
 assert(got.next_pc==dest && got.a==a && got.x==slot && got.y==0x59 && got.p==p);
 assert(r==old);
}
int main(){std::uint64_t count=0;
 for(unsigned i=0;i<18u*256u*16u;++i){check(i);++count;}
 for(unsigned mode=0;mode<4096;++mode){Ram r{};r.fill(0x5a);r[0x69]=15;r[0x054e + 15]=0x80;r[0x0470+15]=0x81;r[0xa8]=0;r[0x05ef+15]=0;
 const auto before=r;const auto got=cv3::scheduler_fdfe_to_followup_0520(r,0x01,0,0x01);
 assert(got.next_pc==0xfe60 && got.a==0 && got.x==15 && got.y==0 && got.p==3 && r==before);++count;}
 for(unsigned invalid:{0u,19u,255u}){
 Ram r{};r.fill(0);r[0x69]=15;
 const auto before=r;bool thrown=false;
 try{(void)cv3::scheduler_bd11_and_fe34_0520(r,std::uint8_t(invalid),0,0,0);}catch(const std::invalid_argument&){thrown=true;}
 assert(thrown&&r==before);++count;
 }
 std::cout<<"PASS 0520 original BD11-to-FE34 followup and natural composed scheduler: "<<count<<" bounded native cases\n";
}
