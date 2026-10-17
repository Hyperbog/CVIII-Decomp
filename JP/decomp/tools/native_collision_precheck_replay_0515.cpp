#include "actor_collision_precheck_0515.hpp"
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
        throw std::runtime_error("Expected exact 2048 byte Mesen RAM snapshot");
}
int main(int argc,char** argv){
    if(argc!=12){std::cerr<<"usage: replay 217|1f8 BEFORE AFTER X initY initP destPC outA outX outY outP\n";return 2;}
    try{
        Ram before{},after{};load(argv[2],before);load(argv[3],after);
        auto n=[](const char* s){return static_cast<unsigned>(std::stoul(s,nullptr,0));};
        const auto x=static_cast<std::uint8_t>(n(argv[4]));
        const auto y=static_cast<std::uint8_t>(n(argv[5]));
        const auto p=static_cast<std::uint8_t>(n(argv[6]));
        const auto ret=std::string(argv[1])=="217" ?
            cv3::actor_collision_b217_precheck(before,x,y,p):
            cv3::actor_pre_collision_b1f8_through_b231(before,x,y,p);
        unsigned mismatch=0;
        for(unsigned i=0;i<before.size();++i){
            if(i>=0x100 && i<0x200)continue;
            if(before[i]!=after[i]){
                if(mismatch<10)std::cerr<<std::hex<<i<<" native="<<unsigned(before[i])
                     <<" original="<<unsigned(after[i])<<"\n";
                ++mismatch;
            }
        }
        if(mismatch||ret.next_pc!=n(argv[7])||ret.a!=n(argv[8])||
           ret.x!=n(argv[9])||ret.y!=n(argv[10])||ret.p!=n(argv[11])){
            std::cerr<<"FAIL mismatch="<<mismatch<<" destination="<<std::hex<<ret.next_pc
                     <<" A="<<unsigned(ret.a)<<" Y="<<unsigned(ret.y)
                     <<" P="<<unsigned(ret.p)<<"\n";return 1;
        }
        std::cout<<"PASS source-original admission: 1792/1792 nonstack RAM and A/X/Y/P + target PC\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 3;}
}
