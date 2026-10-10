#include "actor_collision_precheck_0515.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram = std::array<std::uint8_t, 0x800>;

static std::uint8_t nz(std::uint8_t p, std::uint8_t a) {
    return static_cast<std::uint8_t>((p & ~0x82u) | (a & 0x80u) | (a==0u?2u:0u));
}
static std::uint8_t cmp(std::uint8_t p, std::uint8_t a, std::uint8_t b) {
    const auto d=static_cast<std::uint8_t>(a-b);
    return static_cast<std::uint8_t>((p & ~0x83u) | (a>=b?1u:0u) |
                                     (d==0u?2u:0u) | (d&0x80u));
}
static void check(Ram& r, unsigned x, unsigned initial_p) {
    const auto before=r;
    auto a=r[0x7e];auto p=nz(static_cast<std::uint8_t>(initial_p),a);
    a&=0xf0u; p=nz(p,a);
    unsigned pc=0;
    if(a) pc=0xb258u;
    else {
        a=r[0x54e + x];p=nz(p,a);p=cmp(p,a,0x69u);
        if(a>=0x69u) pc=0xb162u;
        else {
            a=r[0x470+x];p=nz(p,a);a&=2u;p=nz(p,a);
            if(a)pc=0xb1d8u;
            else{a=r[0x7d];p=nz(p,a);pc=a?0xb258u:0xb232u;}
        }
    }
    const auto got=cv3::actor_collision_b217_precheck(r,static_cast<std::uint8_t>(x),0x9au,static_cast<std::uint8_t>(initial_p));
    assert(got.next_pc==pc && got.a==a && got.x==x && got.y==0x9a && got.p==p && r==before);
}
int main(){
    unsigned cases=0;
    // 65536 combinations of original $7E and actor type, cycle through
    // carry/overflow and actor slot indices. These are synthetic domains.
    for(unsigned high=0;high<256;++high){
        for(unsigned typ=0;typ<256;++typ){
            Ram r{};r.fill(0xa5);
            const unsigned x=1+(typ%17u);
            r[0x7e]=static_cast<std::uint8_t>(high);
            r[0x54e + x]=static_cast<std::uint8_t>(typ);
            r[0x470+x]=static_cast<std::uint8_t>((typ*17+high*13)&255u);
            r[0x7d]=static_cast<std::uint8_t>(high*19);
            check(r,x,(typ*31+high*7)&255u);
            ++cases;
        }
    }
    // Force every edge, including subtle branch precedence when >1 test is true.
    for(unsigned typ=0;typ<256;++typ)for(unsigned attr=0;attr<8;++attr)
        for(unsigned blocked=0;blocked<8;++blocked){
            Ram r{};r.fill(0);
            r[0x7e]=static_cast<std::uint8_t>(blocked&1u ? 0x10u:0u);
            r[0x7d]=static_cast<std::uint8_t>(blocked&2u ? 0x81u:0u);
            r[0x54f]=static_cast<std::uint8_t>(typ);
            r[0x471]=static_cast<std::uint8_t>((attr&1u?2u:0u)|(attr&2u?0x80u:0u));
            check(r,1,(attr*41+typ*3+blocked*13)&255u);
            ++cases;
        }
    // First integrated original actor preflight from B1F8 to B232.
    for(unsigned typ=0;typ<256;++typ)for(unsigned frame=0;frame<4;++frame){
        Ram r{};r.fill(0);
        r[0x471]=static_cast<std::uint8_t>((frame&1u)?0x11u:0x44u);
        r[0x401]=static_cast<std::uint8_t>((frame&2u)?0u:0x92u);
        r[0x54f]=static_cast<std::uint8_t>(typ);
        r[0x7e]=0;r[0x7d]=0;
        const auto before=r;
        auto answer=cv3::actor_pre_collision_b1f8_through_b231(r,1,0,1);
        assert(r==before);
        if(frame==0 && typ==0x3d)assert(answer.next_pc==0xb232u && answer.p==2u);
        assert(answer.next_pc==0xb232u||answer.next_pc==0xb1f7u||
               answer.next_pc==0xb258u||answer.next_pc==0xb162u||answer.next_pc==0xb1d8u);
        ++cases;
    }
    for(unsigned bad:{0u,18u,255u}){
        Ram r{};r.fill(0);const auto before=r;
        bool rejected=false;
        try{(void)cv3::actor_collision_b217_precheck(r,static_cast<std::uint8_t>(bad),0,0);}
        catch(const std::invalid_argument&){rejected=true;}
        assert(rejected && r==before);
        ++cases;
    }
    std::cout<<"PASS 0515 source-faithful B217 admission and integrated B1F8 gating: "<<cases<<" cases\n";
}
