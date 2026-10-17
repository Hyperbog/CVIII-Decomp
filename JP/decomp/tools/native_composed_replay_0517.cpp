#include "actor_collision_result_0517.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static void read(const char* path,Ram& data){std::ifstream f(path,std::ios::binary);if(!f||!f.read(reinterpret_cast<char*>(data.data()),data.size())||f.peek()!=EOF)throw std::runtime_error("Bad 2KiB RAM");}
int main(int argc,char** argv){
 if(argc!=10){std::cerr<<"usage: composed BEFORE AFTER X inY inP wantPC wantA wantY wantP\n";return 2;}
 try {
 Ram a{},b{};read(argv[1],a);read(argv[2],b);
 auto n=[](const char* s){return static_cast<unsigned>(std::stoul(s,nullptr,0));};
 auto result=cv3::actor_collision_b1f8_through_tail_0517(a,static_cast<std::uint8_t>(n(argv[3])),static_cast<std::uint8_t>(n(argv[4])),static_cast<std::uint8_t>(n(argv[5])));
 unsigned bad=0;for(unsigned i=0;i<a.size();++i){if(i>=256 && i<512)continue;if(a[i]!=b[i]){if(bad<8)std::cerr<<std::hex<<i<<" "+std::to_string(a[i])+" vs "+std::to_string(b[i])<<"\n";++bad;}}
 if(bad||result.next_pc!=n(argv[6])||result.a!=n(argv[7])||result.y!=n(argv[8])||result.p!=n(argv[9])){
  std::cerr<<"FAIL mismatch="<<bad<<" pc="<<std::hex<<result.next_pc<<" A="<<unsigned(result.a)<<" Y="<<unsigned(result.y)<<" P="<<unsigned(result.p)<<"\n";return 1;}
 std::cout<<"PASS original native 91-instruction integrated collision + post-tail: 1792/1792 original RAM, CPU A/Y/P and fixed PC\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}
}
