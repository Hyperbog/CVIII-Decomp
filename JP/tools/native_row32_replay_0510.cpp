#include "actor_event_row32_0510.hpp"
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
int main(int argc,char** argv){
 if(argc!=3){std::cerr<<"usage: native_row32_replay SOURCE_MESEN_RAM DEST_MESEN_RAM\n";return 2;}
 try {
  std::array<std::uint8_t,0x800> original{},expected{};
  auto read=[&](const char* file,auto& bytes){
   std::ifstream f(file,std::ios::binary);if(!f || !f.read(reinterpret_cast<char*>(bytes.data()),bytes.size()) || f.peek()!=EOF)
    throw std::runtime_error("invalid 2048-byte emulator RAM dump");
  };
  read(argv[1],original);read(argv[2],expected);
  const auto source_x=original[0x69];
  const auto result=cv3::run_row32_event(original,source_x);
  unsigned mismatches=0;
  for(unsigned i=0;i<0x800;++i){
   // The semantic C++ lift does not reproduce 6502 subroutine return stack
   // frames in $0100-$01FF; all other system RAM must match exactly.
   if(i>=0x100 && i<0x200)continue;
   if(original[i]!=expected[i]){
    if(mismatches<12)std::cerr<<std::hex<<i<<": actual="<<unsigned(original[i])<<" original="<<unsigned(expected[i])<<"\n";
    ++mismatches;
   }
  }
  if(mismatches) {std::cerr<<"FAIL original Mesen RAM bytes mismatched: "<<mismatches<<"\n";return 1;}
  int expected_slot=0;
  std::array<std::uint8_t,0x800> initial{};read(argv[1],initial);
  for(int x=1;x<=12;++x)if(initial[0x054e + x]==0){expected_slot=x;break;}
  if(result.outcome!=cv3::Row32Outcome::Spawned || result.destination!=expected_slot){
   std::cerr<<"FAIL actual Mesen row32 actor spawn did not select X=1\n";return 1;
  }
  std::cout<<"PASS native source lift vs independent original Mesen RAM, 1792/1792 non-stack bytes; live actor slot="<<unsigned(result.destination)<<"\n";
  return 0;
 }catch(const std::exception& ex){std::cerr<<ex.what()<<"\n";return 3;}
}
