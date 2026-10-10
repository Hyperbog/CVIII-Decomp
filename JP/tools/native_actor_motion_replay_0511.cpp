#include "actor_motion_prg0b_0511.hpp"
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>

int main(int argc,char** argv) {
 if(argc!=5){std::cerr<<"usage: MOTION_BEFORE_2K.bin MOTION_AFTER_2K.bin START_STATUS_HEX ACTOR_X\n";return 2;}
 using Ram=std::array<std::uint8_t,0x800>;Ram before{},after{};
 auto load=[](const char* p,Ram& a){std::ifstream f(p,std::ios::binary);
    if(!f||!f.read(reinterpret_cast<char*>(a.data()),a.size())||f.peek()!=EOF)
        throw std::runtime_error("invalid Mesen 2 KiB physical RAM dump");};
 try {
  load(argv[1],before);load(argv[2],after);
  const unsigned initial_p=std::stoul(argv[3],nullptr,16);
  const auto slot=static_cast<std::uint8_t>(std::stoul(argv[4],nullptr,0));
  const auto o=cv3::apply_prg0b_actor_motion_8001(before,slot,static_cast<std::uint8_t>(initial_p));
  unsigned mismatches=0;
  for(unsigned i=0;i<0x800;++i){
   if(i>=0x100&&i<0x200)continue;
   if(before[i]!=after[i]){
    if(mismatches<12) std::cerr<<std::hex<<i<<" native="<<unsigned(before[i])<<" Mesen="<<unsigned(after[i])<<"\n";
    ++mismatches;
   }
  }
  if(mismatches){std::cerr<<"FAIL "<<mismatches<<" /1792 source RAM bytes\n";return 1;}
  std::cout<<"PASS 1792/1792 nonstack, non-X-sentinel RAM bytes; A="<<unsigned(o.a)
           <<" Y="<<unsigned(o.y)<<" P="<<unsigned(o.p)<<"\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}
}
