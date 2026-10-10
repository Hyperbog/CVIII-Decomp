#include "scheduler_postcollision_0519.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void load(const char* path,Ram& a){std::ifstream f(path,std::ios::binary);if(!f||!f.read(reinterpret_cast<char*>(a.data()),a.size())||f.peek()!=EOF)throw std::runtime_error("Expected original 2KiB RAM dump");}
int main(int argc,char** argv){if(argc!=11){std::cerr<<"usage: replay BEFORE AFTER inA inY inP nextPC outA outX outY outP\n";return 2;}
 try{Ram r{},after{};load(argv[1],r);load(argv[2],after);auto u=[](const char* s){return unsigned(std::stoul(s,nullptr,0));};
 auto out=cv3::scheduler_post_collision_fe00_0519(r,std::uint8_t(u(argv[3])),std::uint8_t(u(argv[4])),std::uint8_t(u(argv[5])));
 unsigned bad=0;for(unsigned i=0;i<r.size();++i)if(r[i]!=after[i])++bad;
 if(bad||out.next_pc!=u(argv[6])||out.a!=u(argv[7])||out.x!=u(argv[8])||out.y!=u(argv[9])||out.p!=u(argv[10])){std::cerr<<"FAIL RAM="<<bad<<" PC="<<std::hex<<out.next_pc<<" A="<<unsigned(out.a)<<" X="<<unsigned(out.x)<<" Y="<<unsigned(out.y)<<" P="<<unsigned(out.p)<<"\n";return 1;}
 std::cout<<"PASS 2048/2048 original system RAM bytes, PC/A/X/Y/P\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}}
