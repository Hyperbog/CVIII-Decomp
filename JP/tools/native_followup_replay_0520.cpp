#include "scheduler_bd11_followup_0520.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void load(const char* file,Ram& r){
 std::ifstream s(file,std::ios::binary);
 if(!s || !s.read(reinterpret_cast<char*>(r.data()),r.size()) || s.peek()!=EOF)
  throw std::runtime_error("Expected exact 2048-byte original Mesen system RAM");
}
int main(int argc,char** argv){
 if(argc!=13){std::cerr<<"usage: replay bd11|fdfe BEFORE AFTER X inA inY inP nextPC A X Y P\n";return 2;}
 try{
  Ram before{},after{};load(argv[2],before);load(argv[3],after);
  auto u=[](const char* s){return std::stoul(s,nullptr,0);};
  const std::string mode=argv[1];
  const auto result=mode=="bd11" ? cv3::scheduler_bd11_and_fe34_0520(before,static_cast<std::uint8_t>(u(argv[4])),static_cast<std::uint8_t>(u(argv[5])),static_cast<std::uint8_t>(u(argv[6])),static_cast<std::uint8_t>(u(argv[7]))) :
   mode=="fdfe" ? cv3::scheduler_fdfe_to_followup_0520(before,static_cast<std::uint8_t>(u(argv[5])),static_cast<std::uint8_t>(u(argv[6])),static_cast<std::uint8_t>(u(argv[7]))) : throw std::invalid_argument("Unknown mode");
  unsigned wrong=0;for(unsigned i=0;i<before.size();++i){
   if(mode=="fdfe" && i>=0x100&&i<0x200)continue; // original FE31 JSR
   if(before[i]!=after[i])++wrong;
  }
  if(wrong||result.next_pc!=u(argv[8])||result.a!=u(argv[9])||result.x!=u(argv[10])||result.y!=u(argv[11])||result.p!=u(argv[12])){
   std::cerr<<"FAIL RAM="<<wrong<<" PC="<<std::hex<<result.next_pc<<" A="<<unsigned(result.a)<<" X="<<unsigned(result.x)<<" Y="<<unsigned(result.y)<<" P="<<unsigned(result.p)<<"\n";return 1;
  }
  std::cout<<"PASS original Mesen native BD11/FE34 "<<(mode=="fdfe"?1792:2048)<<" RAM bytes + PC/A/X/Y/P\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}
}
