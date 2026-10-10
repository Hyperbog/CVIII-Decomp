#include "actor_collision_measure_0516.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <stdexcept>
#include <string>
int main(int argc,char** argv){
 if(argc!=11 && argc!=12){std::cerr<<"usage: CLI BEFORE AFTER X A Y P ENDPC ENDA ENDY ENDP\n";return 2;}
 try {
   std::array<std::uint8_t,0x800> in{},expected{};
   auto load=[](const char* f,auto& data){std::ifstream s(f,std::ios::binary);if(!s||!s.read(reinterpret_cast<char*>(data.data()),data.size())||s.peek()!=EOF)throw std::runtime_error("2048 byte RAM expected");};
   load(argv[1],in);load(argv[2],expected);
   auto num=[](const char* p){return std::stoul(p,nullptr,0);};
   const auto x=static_cast<std::uint8_t>(num(argv[3]));
   const auto o=(argc==12 && std::string(argv[11])=="composed") ?
      cv3::actor_collision_measure_b1f8_to_b393(in,x,static_cast<std::uint8_t>(num(argv[5])),static_cast<std::uint8_t>(num(argv[6]))) :
      cv3::actor_collision_measure_b339(in,x,static_cast<std::uint8_t>(num(argv[4])),static_cast<std::uint8_t>(num(argv[5])),static_cast<std::uint8_t>(num(argv[6])));
   unsigned bad=0;
   for(unsigned i=0;i<in.size();++i){
     if(i>=0x100 && i<0x200)continue;
     if(in[i]!=expected[i]){if(bad<9)std::cerr<<std::hex<<i<<" native="<<unsigned(in[i])<<" mesen="<<unsigned(expected[i])<<"\n";++bad;}
   }
   if(bad||o.next_pc!=num(argv[7])||o.a!=num(argv[8])||o.y!=num(argv[9])||o.p!=num(argv[10])){
     std::cerr<<"FAIL bytes="<<bad<<" pc="<<std::hex<<o.next_pc<<" A="<<unsigned(o.a)<<" Y="<<unsigned(o.y)<<" P="<<unsigned(o.p)<<" vertical="<<o.vertical_compared<<"\n";return 1;
   }
   std::cout<<"PASS 1792/1792 ROM Mesen RAM, PC, A/Y/P; vertical="<<o.vertical_compared<<"\n";
 }catch(const std::exception& ex){std::cerr<<ex.what()<<"\n";return 3;}
}
