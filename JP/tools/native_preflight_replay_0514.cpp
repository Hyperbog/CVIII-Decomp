#include "actor_preflight_0514.hpp"
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void load(const char* path,Ram& a){
 std::ifstream f(path,std::ios::binary);
 if(!f || !f.read(reinterpret_cast<char*>(a.data()),a.size()) || f.peek()!=EOF)
   throw std::runtime_error("Expected exact 2048-byte Mesen internal RAM");
}
int main(int argc,char** argv){
 if(argc!=13){
  std::cerr<<"usage: replay MODE BEFORE AFTER X entryA entryY entryP nextPC outA outX outY outP\n";
  return 2;
 }
 try{
   Ram input{},original{};load(argv[2],input);load(argv[3],original);
   auto to=[](const char* s){return static_cast<unsigned>(std::stoul(s,nullptr,0));};
   const auto x=static_cast<std::uint8_t>(to(argv[4]));
   const auto a=static_cast<std::uint8_t>(to(argv[5]));
   const auto y=static_cast<std::uint8_t>(to(argv[6]));
   const auto p=static_cast<std::uint8_t>(to(argv[7]));
   const auto wantPC=to(argv[8]);
   cv3::ActorPreflight0514 result{};
   if(std::string(argv[1])=="delta")
       result=cv3::produce_delta6b_d2fe(input,x,a,p);
   else if(std::string(argv[1])=="gate")
       result=cv3::actor_postprocess_b1f8_gate(input,x,y,p);
   else throw std::invalid_argument("unsupported preflight mode");
   unsigned mismatch=0;
   for(unsigned i=0;i<input.size();++i){
      if(i>=0x100 && i<0x200)continue; // original 6502 JSR stack
      if(input[i]!=original[i]){
          if(mismatch<8)std::cerr<<std::hex<<i<<" native="<<unsigned(input[i])
                            <<" mesen="<<unsigned(original[i])<<"\n";
          ++mismatch;
      }
   }
   if(mismatch || (wantPC && result.next_pc!=wantPC) ||
      result.a!=to(argv[9]) || result.x!=to(argv[10]) ||
      result.y!=to(argv[11]) || result.p!=to(argv[12])){
       std::cerr<<"FAIL mismatches="<<mismatch<<" route="<<std::hex
                <<result.next_pc<<" A="<<unsigned(result.a)<<" X="<<unsigned(result.x)
                <<" Y="<<unsigned(result.y)<<" P="<<unsigned(result.p)<<"\n";
       return 1;
   }
   std::cout<<"PASS "<<argv[1]<<" original-Mesen 1792/1792 nonstack RAM bytes and A/X/Y/P";
   if(wantPC)std::cout<<" + branch PC";
   std::cout<<"\n";
   return 0;
 }catch(const std::exception& ex){std::cerr<<ex.what()<<"\n";return 3;}
}
