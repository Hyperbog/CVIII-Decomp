#include "actor_animation_ef93_0521.hpp"
#include "original_ef93_tables_0521.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static void one(unsigned frame,unsigned phase,unsigned seed,unsigned slot){
 Ram r{};r.fill(0xa5);r[0x048c+slot]=0x0e;r[0x05aa+slot]=std::uint8_t(frame);
 r[0x0593+slot]=std::uint8_t(phase);
 const auto init_timer=std::uint8_t((seed%4u)==0u?1u:((seed%4u)==1u?2u:((seed%4u)==2u?0u:0x80u)));
 r[0x057c+slot]=init_timer;
 r[0x400+slot]=0x3d;r[0x08]=0x12;r[0x09]=0x34;
 const auto old=r;
 const auto result=cv3::actor_animation_ef93_0521(r,std::uint8_t(slot),0x5d,0x2e,std::uint8_t(seed));
 assert(result.next_pc==0xfe63&&result.x==slot);
 const auto t=std::uint8_t(init_timer-1u);
 if(t!=0){
  assert(!result.refreshed&&result.a==0x5d&&result.y==0x2e);
  assert((result.p&0x82u)==std::uint8_t((t&0x80u)|(t==0?2:0)));
  for(unsigned i=0;i<r.size();++i)if(i!=0x057c+slot)assert(r[i]==old[i]);
 }else{
  assert(result.refreshed&&r[0x08]==0x59&&r[0x09]==0xf3);
  const auto base=3u*frame;
  assert(r[0x400+slot]==std::uint8_t(cv3::ef93rom0521::descriptor0e[base]+phase));
  assert(r[0x057c+slot]==cv3::ef93rom0521::descriptor0e[base+1]);
  const auto after=std::uint8_t(phase+2u);
  assert(r[0x0593+slot]==(after>=cv3::ef93rom0521::descriptor0e[base+2]?0u:after));
  assert(result.y==base+2u);
  for(unsigned i=0;i<r.size();++i)
   if(i!=0x057c+slot&&i!=0x08&&i!=0x09&&i!=0x400+slot&&i!=0x0593+slot)assert(r[i]==old[i]);
 }
}
int main(){std::uint64_t count=0;
 for(unsigned frame=0;frame<16;++frame)for(unsigned phase=0;phase<256;++phase)
 for(unsigned seed=0;seed<16;++seed) {one(frame,phase,seed,1u+((frame+phase+seed)%18u));++count;}
 for(unsigned invalid:{0u,19u,255u}){Ram r{};r.fill(0);auto old=r;bool caught=false;try{(void)cv3::actor_animation_ef93_0521(r,std::uint8_t(invalid),0,0,0);}catch(const std::invalid_argument&){caught=true;}assert(caught&&r==old);++count;}
 for(unsigned descriptor:{0u,1u,28u,255u}){Ram r{};r.fill(0);r[0x057d]=1;r[0x048d]=std::uint8_t(descriptor);auto old=r;bool caught=false;try{(void)cv3::actor_animation_ef93_0521(r,1,0,0,0);}catch(const std::invalid_argument&){caught=true;}assert(caught&&r==old);++count;}
 for(unsigned frame:{16u,17u,128u,255u}){Ram r{};r.fill(0);r[0x057d]=1;r[0x048d]=0x0e;r[0x05ab]=std::uint8_t(frame);auto old=r;bool caught=false;try{(void)cv3::actor_animation_ef93_0521(r,1,0,0,0);}catch(const std::invalid_argument&){caught=true;}assert(caught&&r==old);++count;}
 std::cout<<"PASS original fixed EF93 animation descriptor0E: "<<count<<" native cases\n";
}
