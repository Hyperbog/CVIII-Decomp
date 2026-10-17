#include "actor_collision_measure_0516.hpp"
#include "actor_collision_tables_0516.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static unsigned one(unsigned actorX,unsigned playerX,unsigned actorY,unsigned playerY,unsigned typ,unsigned room,unsigned inP){
 Ram r{};r.fill(0xa5);
 r[0x7f]=static_cast<std::uint8_t>(room);
 r[0xb7]=0;
 r[0x54f]=static_cast<std::uint8_t>(typ);
 r[0x48d]=0;
 r[0x401]=0x92;
 r[0x439]=static_cast<std::uint8_t>(actorX);
 r[0x438]=static_cast<std::uint8_t>(playerX);
 r[0x41d]=static_cast<std::uint8_t>(actorY);
 r[0x41c]=static_cast<std::uint8_t>(playerY);
 const auto before=r;
 const auto output=cv3::actor_collision_measure_b339(r,1,0,0,static_cast<std::uint8_t>(inP));
 const unsigned bx=cv3::rom0516::baseX[room],by=cv3::rom0516::baseY[room];
 const unsigned dx=(actorX>=playerX?actorX-playerX:playerX-actorX);
 const unsigned tx=(bx+cv3::rom0516::radiusX[typ])&255u;
 const bool checkY=dx<tx;
 const unsigned ty=(by+cv3::rom0516::radiusY[typ])&255u;
 const unsigned adj=(playerY+cv3::rom0516::playerOffsetY[room>=4?1:0])&255u;
 const unsigned dy=actorY>=adj?actorY-adj:adj-actorY;
 assert(output.next_pc==0xb393 && output.x==1 && output.vertical_compared==checkY);
 assert(r[0]==bx && r[1]==by && r[2]==tx);
 assert(r[3]==(checkY?ty:before[3]));
 assert(r[0x11]==(checkY?adj:before[0x11]));
 assert(output.a==(checkY?dy:dx));
 assert((output.p&1u)==((checkY?dy>=ty:dx>=tx)?1u:0u));
 assert((output.p&0x3cu)==(inP&0x3cu) || ((output.p&0x3cu)&~0x40u)==(inP&0x3cu));
 assert(output.y==(checkY?(room>=4?1u:0u):typ));
 for(unsigned i=4;i<r.size();++i){if(i==0x11)continue;assert(r[i]==before[i]);}
 return 1;
}
int main(){unsigned long tests=0;
 for(unsigned ax=0;ax<256;++ax)for(unsigned px=0;px<256;++px)
  tests+=one(ax,px,(ax*17+px*23)&255,(ax*7+px*31)&255,0x3d,(ax+px)%9,(ax*19+px*13)&255);
 for(unsigned ay=0;ay<256;++ay)for(unsigned py=0;py<256;++py)
  tests+=one(0x80,0x80,ay,py,(ay+py)%0x69,(ay*11+py*13)%9,(ay*37+py*7)&255);
 for(unsigned type=0;type<0x69;++type)for(unsigned room=0;room<9;++room)
  for(unsigned s=0;s<8;++s)tests+=one((s*31+room)&255,(s*31+room)&255,
          (s*27+type)&255,(s*13+type)&255,type,room,(type*11+room*19+s)&255);
 // Composed B1F8->B217->B232->B339 path, with source gate bypasses.
 for(unsigned typ=0;typ<0x58;++typ)for(unsigned mask=0;mask<8;++mask){
  Ram r{};r.fill(0);r[0x54f]=static_cast<std::uint8_t>(typ);r[0x401]=0x92;
  r[0x471]=static_cast<std::uint8_t>((mask&1u)?0x45u:0x44u);
  r[0x7e]=static_cast<std::uint8_t>((mask&2u)?0x10u:0u);
  r[0x7d]=static_cast<std::uint8_t>((mask&4u)?1u:0u);
  const auto before=r;
  const auto out=cv3::actor_collision_measure_b1f8_to_b393(r,1,0,1);
  if(mask&1u)assert(out.next_pc==0xb1f7u);
  else if(mask&2u)assert(out.next_pc==0xb258u);
  else if(mask&4u)assert(out.next_pc==0xb258u);
  else assert(out.next_pc==0xb393u);
  if(mask)assert(before==r);
  ++tests;
 }
 for(unsigned badx : {0u,18u,255u}){
  Ram r{};r.fill(0);bool failed=false;
  try{(void)cv3::actor_collision_measure_b339(r,static_cast<std::uint8_t>(badx),0,0,0);}catch(const std::invalid_argument&){failed=true;}
  assert(failed);++tests;
 }
 for(unsigned mode=0;mode<4;++mode){Ram r{};r.fill(0);r[0x54f]=0x3d;
  if(mode==0)r[0xB7]=1;
  if(mode==1)r[0x7f]=9;
  if(mode==2)r[0x54f]=0x69;
  if(mode==3){r[0x48d]=8;r[0x401]=0xee;}
  const auto copy=r;bool failed=false;
  try{(void)cv3::actor_collision_measure_b339(r,1,0,0,0);}catch(const std::invalid_argument&){failed=true;}
  assert(failed && r==copy);++tests;
 }
 std::cout<<"PASS original bank0B B339/80B3/80C1 source bounded: "<<tests<<" cases\n";
}
