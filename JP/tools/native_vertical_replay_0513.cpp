#include "actor_displacement_vertical_prg0b_0513.hpp"
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void load(const char* name,Ram& data) {
  std::ifstream f(name,std::ios::binary);
  if(!f||!f.read(reinterpret_cast<char*>(data.data()),data.size())||f.peek()!=EOF)
    throw std::runtime_error("Expected physical 2KiB Mesen RAM snapshot");
}
int main(int argc,char** argv) {
 if(argc!=9 && argc!=10){std::cerr<<"usage: native_vertical_replay BEFORE AFTER actorX entryP exitPC exitA exitY exitP\n";return 2;}
 try {
   Ram before{},after{};load(argv[1],before);load(argv[2],after);
   const auto x=static_cast<std::uint8_t>(std::stoul(argv[3],nullptr,0));
   const auto p=static_cast<std::uint8_t>(std::stoul(argv[4],nullptr,0));
   const auto expected_pc=static_cast<unsigned>(std::stoul(argv[5],nullptr,0));
   const auto a=static_cast<std::uint8_t>(std::stoul(argv[6],nullptr,0));
   const auto y=static_cast<std::uint8_t>(std::stoul(argv[7],nullptr,0));
   const auto expected_p=static_cast<std::uint8_t>(std::stoul(argv[8],nullptr,0));
   const auto result=(argc==10 && std::string(argv[9])=="complete") ?
        cv3::apply_prg0b_actor_displacement_80e3_vertical_complete(before,x,p) :
        cv3::apply_prg0b_actor_displacement_80e3_vertical(before,x,p);
   unsigned different=0;
   for(unsigned i=0;i<before.size();++i){
     if(i>=0x100 && i<0x200)continue;
     if(before[i]!=after[i]){
       if(different<6)std::cerr<<std::hex<<i<<" native="<<unsigned(before[i])<<" emulator="<<unsigned(after[i])<<"\n";
       ++different;
     }
   }
   const unsigned exit_pc=result.exit==cv3::ActorVerticalExit0513::ReturnToFixedFDFB?0xfdfbu:0x8843u;
   if(different||exit_pc!=expected_pc||result.a!=a||result.y!=y||result.p!=expected_p){
     std::cerr<<"FAIL different="<<different<<" PC="<<std::hex<<exit_pc
              <<" A="<<unsigned(result.a)<<" Y="<<unsigned(result.y)<<" P="<<unsigned(result.p)<<"\n";
     return 1;
   }
   std::cout<<"PASS exact 1792 nonstack original Mesen RAM bytes, A/Y/P and control transfer\n";
   return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}
}
