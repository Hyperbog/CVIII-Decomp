#include "actor_collision_result_0517.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static void test_one(unsigned serial){
 const unsigned type=serial&255u, seed=serial>>8;
 const bool carry=(seed&1u)!=0;
 const unsigned x=1u+(seed%17u);
 const bool actor_on_left=(seed&2u)!=0;
 const unsigned mode=(seed>>2)&3u;
 const bool active_follower=(seed&0x40u)!=0;
 Ram r{};r.fill(0x6bu);
 r[0x054eu+x]=static_cast<std::uint8_t>(type);
 r[0x0657u+x]=0x20u;
 r[0x0438]=0x81u;
 r[0x0438u+x]=static_cast<std::uint8_t>(actor_on_left?0x71u:0x91u);
 r[0x068du+x]=static_cast<std::uint8_t>(mode==1?1:0);
 r[0x0630]=static_cast<std::uint8_t>(mode==2||mode==3?1:0);
 r[0x0413]=static_cast<std::uint8_t>(mode==3?1:0);
 for(unsigned k=20;k<=22;++k)r[0x054eu+k]=0;
 if(active_follower)r[0x054eu+20u+(seed%3u)]=1;
 r[0x9b]=0x88;r[0x8d]=0x89;r[0x8e]=0x8a;r[0x7e]=0x8b;
 const Ram original=r;
 const auto ps=static_cast<std::uint8_t>(((seed*11u+type*17u)&0xfcu) | (carry?1u:0u));
 const auto got=cv3::actor_collision_tail_b235(r,static_cast<std::uint8_t>(x),0x5fu,0x55u,ps);
 const bool type39=!carry&&type==0x39u;
 const bool short_exit=type==0x16u||type==0x37u||(type>=0x61u&&type<0x7fu);
 const bool scan=(mode!=3u); // mode=3: $630!=0 and $413!=0, bit clear
 unsigned destination;
 if(type39)destination=0xb243u;
 else if(short_exit)destination=0xfdfeu;
 else if(!scan)destination=0xb27cu;
 else if(active_follower)destination=0xb2a8u;
 else destination=0xfdfeu;
 assert(got.next_pc==destination&&got.x==x);
 if(!carry){
  assert(r[0x7e]==0x20u);
  if(!type39){assert(r[0x8e]==x);assert(r[0x8d]==(actor_on_left?1u:0u));}
 }else{assert(r[0x7e]==original[0x7e]&&r[0x8d]==original[0x8d]&&r[0x8e]==original[0x8e]);}
 if(!type39&&!short_exit&&scan){
  if(active_follower){assert(r[0x9b]==0x14u+seed%3u&&got.y==0x14u+seed%3u);}
  else{assert(r[0x9b]==0x17u&&got.y==0x16u&&got.a==0x17u&&(got.p&3u)==3u);}
 }else assert(r[0x9b]==original[0x9b]);
 for(unsigned i=0;i<r.size();++i){
  if(i==0x7e||i==0x8e||i==0x8d||i==0x9b)continue;
  assert(r[i]==original[i]);
 }
}
int main(){
 for(unsigned i=0;i<65536;++i)test_one(i);
 for(unsigned bad:{0u,18u,255u}){
  Ram r{};r.fill(0);auto copy=r;bool caught=false;
  try{(void)cv3::actor_collision_tail_b235(r,static_cast<std::uint8_t>(bad),0,0,0);}catch(const std::invalid_argument&){caught=true;}
  assert(caught&&r==copy);
 }
 std::cout<<"PASS 0517 source-faithful collision result / empty follower scan: 65539 cases\n";
}
