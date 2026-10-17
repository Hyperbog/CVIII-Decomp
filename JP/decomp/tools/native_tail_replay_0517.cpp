#include "actor_collision_result_0517.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void read(const char* path,Ram& data){
  std::ifstream f(path,std::ios::binary);
  if(!f||!f.read(reinterpret_cast<char*>(data.data()),data.size())||f.peek()!=EOF)throw std::runtime_error("Expected Mesen 2048-byte RAM dump");
}
int main(int argc,char** argv){
 if(argc!=12){std::cerr<<"usage: tail_replay BEFORE AFTER X inA inY inP wantPC wantA wantY wantP wantX\n";return 2;}
 try{
  Ram input{},actual{};read(argv[1],input);read(argv[2],actual);
  auto n=[](const char* s){return static_cast<unsigned>(std::stoul(s,nullptr,0));};
  auto o=cv3::actor_collision_tail_b235(input,
        static_cast<std::uint8_t>(n(argv[3])),
        static_cast<std::uint8_t>(n(argv[4])),
        static_cast<std::uint8_t>(n(argv[5])),
        static_cast<std::uint8_t>(n(argv[6])));
  unsigned mismatches=0;
  for(unsigned i=0;i<input.size();++i){
    if(i>=0x100 && i<0x200)continue;
    if(input[i]!=actual[i]){
      if(mismatches<8)std::cerr<<std::hex<<i<<" native="<<unsigned(input[i])<<" original="<<unsigned(actual[i])<<"\n";
      ++mismatches;
    }
  }
  if(mismatches || o.next_pc!=n(argv[7])||o.a!=n(argv[8])||o.y!=n(argv[9])||o.p!=n(argv[10])||o.x!=n(argv[11])){
    std::cerr<<"FAIL mismatches="<<mismatches<<" next="<<std::hex<<o.next_pc<<" A="<<unsigned(o.a)<<" Y="<<unsigned(o.y)<<" P="<<unsigned(o.p)<<" X="<<unsigned(o.x)<<"\n";return 1;
  }
  std::cout<<"PASS 1792/1792 nonstack Mesen RAM bytes + PC/A/X/Y/P; next="<<std::hex<<o.next_pc<<"\n";
 }catch(const std::exception& ex){std::cerr<<ex.what()<<"\n";return 3;}
}
