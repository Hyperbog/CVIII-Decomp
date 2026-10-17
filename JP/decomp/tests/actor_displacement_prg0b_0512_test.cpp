#include "actor_displacement_prg0b_0512.hpp"
#include <array>
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using Ram=std::array<std::uint8_t,0x800>;
static void test(unsigned oldlo,unsigned signbit,unsigned delta,unsigned attrs,unsigned ps,unsigned actor) {
    Ram r{};r.fill(0xa5);
    r[0x65]=static_cast<std::uint8_t>(signbit & 0x7f);
    r[0x6b]=static_cast<std::uint8_t>(delta);
    r[0x0438+actor]=static_cast<std::uint8_t>(oldlo);
    r[0x0470+actor]=static_cast<std::uint8_t>(attrs);
    const auto baseline=r;
    const auto outcome=cv3::apply_prg0b_actor_displacement_80e3_horizontal(r,
                              static_cast<std::uint8_t>(actor),static_cast<std::uint8_t>(ps));
    // Mathematical 9-bit signed displacement, independent of the two SBCs.
    const int signed_delta=static_cast<std::int8_t>(delta);
    const unsigned full=(static_cast<unsigned>((int(((attrs&1u)<<8)|oldlo)-signed_delta)&511));
    assert(r[0x0438+actor]==(full&255u));
    assert(r[0x0470+actor]==((attrs&0xfeu)|(full>>8)));
    assert(r[0]==(delta>=128 ? 255u:0u));
    assert(r[1]==(attrs&0xfeu));
    assert(outcome.x==actor&&outcome.y==(delta>=128?255u:0u));
    assert(outcome.a==r[0x0470+actor]);
    // Independently derive flags from the 8-bit HIGH subtraction performed
    // after the low-byte borrow. Unchanged I/D/B and overflow are intentional.
    const unsigned loan=(oldlo<delta) ? 1u:0u;
    const unsigned high_before=attrs&1u;
    const unsigned signed_extension=(delta>=128)?255u:0u;
    const unsigned high_diff=high_before-signed_extension-loan;
    const unsigned high_result=high_diff&255u;
    const unsigned c=high_diff<=255 ? 1u:0u;
    const unsigned v=((high_before^high_result)&(high_before^signed_extension)&128u)?64u:0u;
    const unsigned expected=(ps&0x3cu)|c|v|(outcome.a==0?2u:0u)|(outcome.a&128u);
    assert(outcome.p==expected);
    for(unsigned i=2;i<r.size();++i){
        if(i==0x0438+actor || i==0x0470+actor)continue;
        assert(r[i]==baseline[i]);
    }
}
int main(){
    unsigned cases=0;
    // Exhaustively test all 65,536 low-coordinate / signed displacement
    // combinations, fold in the 9th bit, arbitrary attributes and status.
    for(unsigned pos=0;pos<256;++pos)
        for(unsigned delta=0;delta<256;++delta){
            const auto attr=((pos*13+delta*17)&0xfeu) | ((pos^delta)&1u);
            test(pos,(pos+delta)&127,delta,attr,(pos*7+delta*11)&255u,1+(delta%12));
            ++cases;
        }
    // Orthogonal ninth-bit and both delta-sign branches, all destination slots.
    for(unsigned i=0;i<8192;++i){
        test((i*19)&255,(i*13)&127,(i*23)&255,((i*31)&0xfeu)|((i>>3)&1u),
             (i*37)&255,1+(i%12));++cases;
    }
    for(unsigned i=1;i<=12;++i){
        Ram r{};r.fill(0);
        r[0x65]=0x80;
        const auto before=r;
        bool rejected=false;
        try{(void)cv3::apply_prg0b_actor_displacement_80e3_horizontal(r,
            static_cast<std::uint8_t>(i),0);}catch(const std::invalid_argument&){rejected=true;}
        assert(rejected && r==before);++cases;
    }
    Ram r{};r.fill(0);bool rejected=false;
    try{(void)cv3::apply_prg0b_actor_displacement_80e3_horizontal(r,0,0);}
    catch(const std::invalid_argument&){rejected=true;}
    assert(rejected);++cases;
    rejected=false;
    try{(void)cv3::apply_prg0b_actor_displacement_80e3_horizontal(r,13,0);}
    catch(const std::invalid_argument&){rejected=true;}
    assert(rejected);++cases;
    std::cout<<"PASS 0512 original raw0B $80E3 horizontal displacement: "<<cases<<" cases\n";
}
