#include "actor_preflight_0514.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;

static unsigned test_delta(){
 unsigned count=0;
 for(unsigned a=0;a<256;++a){
  for(unsigned b=0;b<256;++b){
   Ram ram{};ram.fill(0x9d);ram[0x62]=static_cast<std::uint8_t>(2+(a%254));
   ram[0x53]=static_cast<std::uint8_t>(a);
   ram[0x08]=static_cast<std::uint8_t>(b);
   const Ram old=ram;const std::uint8_t p=static_cast<std::uint8_t>((a*41+b*19)&255u);
   const auto got=cv3::produce_delta6b_d2fe(ram,16,0x73u,p);
   const unsigned d=(a-b)&255u;
   const unsigned c=a>=b?1u:0u;
   const unsigned v=((a^b)&(a^d)&128u)?64u:0u;
   const unsigned expected=(p&0x3cu)|c|v|(d==0?2u:0u)|(d&128u);
   assert(got.a==d&&got.x==16&&got.y==((ram[0x62]-1u)&255u));
   assert(got.p==expected&&ram[0x6b]==d);
   for(unsigned i=0;i<ram.size();++i)if(i!=0x6b)assert(ram[i]==old[i]);
   ++count;
  }
 }
 for(unsigned branch=0;branch<2;++branch){
  Ram ram{};ram.fill(0);ram[0x62]=static_cast<std::uint8_t>(branch);const Ram old=ram;
  bool rejected=false;
  try{(void)cv3::produce_delta6b_d2fe(ram,16,0,0);}catch(const std::invalid_argument&){rejected=true;}
  assert(rejected&&ram==old);++count;
 }
 return count;
}
static unsigned test_gate(){
 unsigned count=0;
 for(unsigned typ=0;typ<256;++typ){
  for(unsigned scenario=0;scenario<8;++scenario){
   for(unsigned slot=1;slot<=17;++slot){
    Ram ram{};ram.fill(0xab);
    const unsigned mask=(scenario&1u)?(scenario&4u?0x10u:1u):0;
    ram[0x0470u+slot]=static_cast<std::uint8_t>(0x44u|mask);
    ram[0x0400u+slot]=scenario&2u?0u:0x92u;
    ram[0x054eu+slot]=static_cast<std::uint8_t>(typ);
    const Ram before=ram;
    const auto p=static_cast<std::uint8_t>(scenario*31u+typ);
    const auto got=cv3::actor_postprocess_b1f8_gate(ram,static_cast<std::uint8_t>(slot),0x9au,p);
    const unsigned dest= mask || (scenario&2u) || typ>=0x83u ||(typ>=0x58u&&typ<0x61u)
         ? 0xb1f7u : typ>=0x80u?0xb258u:0xb217u;
    assert(got.next_pc==dest && got.x==slot && got.y==0x9a && ram==before);
    // Flags and A are computed independently from the final executed CMP/AND.
    const unsigned value=mask?mask:(scenario&2u)?0u:typ;
    assert(got.a==value);
    assert((got.p&0x7cu)==(p&0x7cu)); // CMP/AND preserve V, I/D/B
    ++count;
   }
  }
 }
 for(unsigned bad : {0u,18u,255u}){
  Ram ram{};ram.fill(0);bool rejected=false;
  try{(void)cv3::actor_postprocess_b1f8_gate(ram,static_cast<std::uint8_t>(bad),0,0);}
  catch(const std::invalid_argument&){rejected=true;}
  assert(rejected);++count;
 }
 return count;
}
int main(){const auto d=test_delta(),g=test_gate();
 std::cout<<"PASS original D2FE delta producer "<<d<<" cases; raw0B B1F8 actor gate "<<g<<" cases\n";
}
