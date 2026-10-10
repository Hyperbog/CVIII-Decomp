#include "actor_event_row32_0510.hpp"
#include <array>
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace {
using Ram=std::array<std::uint8_t,0x800>;
void seed(Ram& r, std::uint8_t source=3) {
 r.fill(0xa5);
 for(int slot=1;slot<=12;++slot)r[0x054e + slot]=0;
 r[0x69]=source;r[0x23]=0x0a;r[0x24]=0;
 r[0x07c2+source]=0x32;
 r[0x07c8+source]=0;
 r[0x07e0+source]=0;
 r[0x07da+source]=0xa0;
 r[0x07d4+source]=0x50;
}
void check_success(const Ram& r, std::uint8_t source, std::uint8_t slot) {
 assert(r[0x0400+slot]==0);
 assert(r[0x054e+slot]==0x3d);
 assert(r[0x0438+slot]==0xa0 && r[0x041c+slot]==0x50);
 assert(r[0x05ef+slot]==0x13);
 assert(r[0x0657+slot]==0x20 && r[0x067b+slot]==0x01);
 assert(r[0x0470+slot]==0x04 && r[0x0645+slot]==source);
 assert(r[0x07c8+source]==static_cast<std::uint8_t>((slot<<4)|1));
 assert(r[0x00]==0xa0 && r[0x01]==0x50 && r[0x02]==0x13 && r[0x03]==0x3d);
 assert(r[0x0d]==3 && r[0x0e]==0);
 assert(r[0x06]==static_cast<std::uint8_t>(slot<<4));
 assert(r[0x24]==0x0a);
 for(int f : {0x04f2,0x0509,0x0520,0x0537,0x068d,0x0454,
                0x0565,0x04c4,0x04db,0x05c1,0x05d8,0x0606,
                0x061d,0x0633}) assert(r[f+slot]==0);
}
}
int main(){
 // Exhaustively cover the original 12-slot first free scan when type-$3D
 // population remains zero. This is the source-equivalent native lift,
 // never a claim the original game visits all these initial states.
 std::uint64_t cases=0;
 for(unsigned mask=0;mask<4096;++mask){
  Ram r{};seed(r);
  for(unsigned i=0;i<12;++i)r[0x054f+i]=(mask&(1u<<i))?0x81:0;
  const auto res=cv3::run_row32_event(r,3);
  int first=0;
  for(int i=1;i<=12;++i)if(!(mask&(1u<<(i-1)))){first=i;break;}
  if(first){
   assert(res.outcome==cv3::Row32Outcome::Spawned);
   assert(res.destination==first);
   check_success(r,3,static_cast<std::uint8_t>(first));
  }else{
   assert(res.outcome==cv3::Row32Outcome::AtLimit);
   assert(res.destination==0 && r[0x07cb]==2);
  }
  ++cases;
 }
 // At least three original type-$3D actors in slots 1..8 trigger the
 // dedicated $8DC1 cap, *even when a free destination exists elsewhere*.
 for(int extra=0;extra<=5;++extra){
  Ram r{};seed(r);
  for(int i=1;i<=3+extra;++i)r[0x054e + i]=0x3d;
  const auto before=r;
  const auto res=cv3::run_row32_event(r,3);
  assert(res.outcome==cv3::Row32Outcome::AtLimit);
  assert(res.existing_matching_actors==3+extra);
  assert(r[0x07cb]==2);
  for(int i=1;i<=12;++i)assert(r[0x054e + i]==before[0x054e + i]);
  ++cases;
 }
 // A nonzero original $07E0,X guard leaves actor state untouched but the
 // two-level $8501 pointer scratch has already been written.
 for(unsigned x=0;x<6;++x){
  Ram r{};seed(r,static_cast<std::uint8_t>(x));
  r[0x07e0+x]=1;
  const auto before=r;
  const auto res=cv3::run_row32_event(r,static_cast<std::uint8_t>(x));
  assert(res.outcome==cv3::Row32Outcome::Guarded);
  for(unsigned i=0;i<r.size();++i){
   if(i<=3)continue;
   assert(before[i]==r[i]);
  }
  assert(r[0]==0x26 && r[1]==0x8b && r[2]==0x2c && r[3]==0x8b);
  ++cases;
 }
 // The dispatcher contract is a *selected* source row, not a generic
 // approximation over unrelated event-handler states.
 for(int fault=0;fault<3;++fault){
  Ram r{};seed(r);
  if(fault==0)r[0x07c5]=0x31;
  if(fault==1)r[0x07cb]=0x02;
  if(fault==2)r[0x69]=4;
  bool rejected=false;
  try{(void)cv3::run_row32_event(r,3);}catch(const std::invalid_argument&){rejected=true;}
  assert(rejected);
  ++cases;
 }
 std::cout<<"PASS 0510 faithful original row32 native lift: "<<cases<<" source-bounded cases\n";
}
