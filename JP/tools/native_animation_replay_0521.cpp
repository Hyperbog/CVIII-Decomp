#include "actor_animation_ef93_0521.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void load(const char* f,Ram& r){std::ifstream s(f,std::ios::binary);if(!s||!s.read(reinterpret_cast<char*>(r.data()),r.size())||s.peek()!=EOF)throw std::runtime_error("Expected 2048 bytes of original RAM");}
int main(int argc,char** argv){if(argc!=12 && argc!=13){std::cerr<<"usage: replay BEFORE AFTER X initialA initialY initialP expectedPC expectedA expectedY expectedP\n";return 2;}
 try{
 Ram before{},after{};load(argv[1],before);load(argv[2],after);
 auto val=[](const char* s){return unsigned(std::stoul(s,nullptr,0));};
 const auto x=std::uint8_t(val(argv[3]));
 const bool composed=argc==13 && std::string(argv[12])=="composed";
 if(argc==13 && !composed)throw std::invalid_argument("Invalid compositional replay mode");
 const auto got=composed ? cv3::actor_animation_fdfe_to_fe63_0521(before,std::uint8_t(val(argv[4])),std::uint8_t(val(argv[5])),std::uint8_t(val(argv[6]))) : cv3::actor_animation_ef93_0521(before,x,std::uint8_t(val(argv[4])),std::uint8_t(val(argv[5])),std::uint8_t(val(argv[6])));
 unsigned bad=0;
 for(unsigned i=0;i<before.size();++i){if(composed && i>=0x100 && i<0x200)continue;
 if(before[i]!=after[i]){if(bad<6)std::cerr<<std::hex<<"RAM["<<i<<"] native="<<unsigned(before[i])<<" original="<<unsigned(after[i])<<"\n";++bad;}}
 if(bad||got.next_pc!=val(argv[7])||got.a!=val(argv[8])||got.y!=val(argv[9])||got.p!=val(argv[10])||got.x!=val(argv[11])){
 std::cerr<<"FAIL: "<<bad<<" RAM byte mismatches; PC "<<std::hex<<got.next_pc<<" A "<<unsigned(got.a)<<" X "<<unsigned(got.x)<<" Y "<<unsigned(got.y)<<" P "<<unsigned(got.p)<<"\n";return 1;}
 std::cout<<"PASS native original JP EF93: "<<(composed?1792:2048)<<" RAM bytes, A/X/Y/P/PC; refreshed="<<got.refreshed<<"\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}
}
