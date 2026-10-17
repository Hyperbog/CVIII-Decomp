#include "actor_displacement_prg0b_0512.hpp"
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using Ram=std::array<std::uint8_t,0x800>;
static void load(const char* filename,Ram& a){
    std::ifstream file(filename,std::ios::binary);
    if(!file||!file.read(reinterpret_cast<char*>(a.data()),a.size())||file.peek()!=EOF)
        throw std::runtime_error("requires exact 2048-byte Mesen internal RAM snapshot");
}
int main(int argc,char** argv){
    if(argc!=8){std::cerr<<"usage: native_displacement_replay BEFORE.bin AFTER.bin actorX initialP expectedA expectedY expectedP\n";return 2;}
    try {
        Ram before{},after{};
        load(argv[1],before);load(argv[2],after);
        const auto x=static_cast<std::uint8_t>(std::stoul(argv[3],nullptr,0));
        const auto p=static_cast<std::uint8_t>(std::stoul(argv[4],nullptr,0));
        const auto want_a=static_cast<std::uint8_t>(std::stoul(argv[5],nullptr,0));
        const auto want_y=static_cast<std::uint8_t>(std::stoul(argv[6],nullptr,0));
        const auto want_p=static_cast<std::uint8_t>(std::stoul(argv[7],nullptr,0));
        const auto result=cv3::apply_prg0b_actor_displacement_80e3_horizontal(before,x,p);
        unsigned mismatch=0;
        for(unsigned i=0;i<before.size();++i){
            if(i>=0x100&&i<0x200)continue;
            if(before[i]!=after[i]){
                if(mismatch<12)std::cerr<<std::hex<<i<<" native="<<unsigned(before[i])
                    <<" original="<<unsigned(after[i])<<"\n";
                ++mismatch;
            }
        }
        if(mismatch || result.a!=want_a || result.y!=want_y || result.p!=want_p){
            std::cerr<<"FAIL 0512 RAM="<<mismatch<<" A="<<unsigned(result.a)
                     <<" Y="<<unsigned(result.y)<<" P="<<unsigned(result.p)<<"\n";return 1;
        }
        std::cout<<"PASS 1792/1792 non-stack RAM bytes A="<<unsigned(result.a)
                 <<" X="<<unsigned(result.x)<<" Y="<<unsigned(result.y)
                 <<" P="<<unsigned(result.p)<<"\n";
    }catch(const std::exception& ex){std::cerr<<ex.what()<<"\n";return 3;}
}
