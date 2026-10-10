#include "actor_displacement_vertical_prg0b_0513.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
std::uint8_t nz(std::uint8_t p, std::uint8_t value) noexcept {
    return static_cast<std::uint8_t>((p & ~0x82u) | (value & 0x80u) |
                                      (value==0 ? 0x02u : 0u));
}
std::uint8_t adc(std::uint8_t a,std::uint8_t b,std::uint8_t& p) noexcept {
    const unsigned total=unsigned(a)+unsigned(b)+unsigned(p&1u);
    const auto out=static_cast<std::uint8_t>(total);
    const bool overflow=((~(a^b)&(a^out))&0x80u)!=0;
    p=static_cast<std::uint8_t>((p&~0xc3u) | (total>255u?1u:0u) |
         (out==0?2u:0u) | (out&0x80u) | (overflow?0x40u:0u));
    return out;
}
void cmp(std::uint8_t a,std::uint8_t b,std::uint8_t& p) noexcept {
    const auto diff=static_cast<std::uint8_t>(a-b);
    p=static_cast<std::uint8_t>((p&~0x83u) | (a>=b?1u:0u) |
            (diff==0?2u:0u) | (diff&0x80u));
}
} // namespace
ActorVertical0513 apply_prg0b_actor_displacement_80e3_vertical(
        std::array<std::uint8_t,0x800>& ram, std::uint8_t x,
        std::uint8_t initial_p) {
    if(x<1 || x>12 || (ram[0x65]&0x80u)==0)
        throw std::invalid_argument("vertical $80E3 requires X=1..12 and $65 negative");
    std::uint8_t p=initial_p;
    // Original $80E3-$80F5 preamble with sign extension in Y/$00.
    auto a=ram[0x0470u+x];p=nz(p,a);
    a=static_cast<std::uint8_t>(a&0xfeu);p=nz(p,a);
    ram[1]=a;
    std::uint8_t y=0;p=nz(p,y);
    a=ram[0x6b];p=nz(p,a);
    if(a&0x80u){y=0xff;p=nz(p,y);}
    ram[0]=y;
    a=ram[0x65];p=nz(p,a);
    // $810F AND #$01 / BNE $8140.
    a=static_cast<std::uint8_t>(a&1u);p=nz(p,a);
    const bool odd=(a!=0);
    p=static_cast<std::uint8_t>(p&~1u); // $8113 / $8140 CLC
    a=ram[0x041cu+x];p=nz(p,a);
    a=adc(a,ram[0x6b],p);ram[0x041cu+x]=a;
    a=ram[0x0470u+x];p=nz(p,a);
    a=static_cast<std::uint8_t>(a&1u);p=nz(p,a);
    a=adc(a,ram[0],p);
    a=static_cast<std::uint8_t>(a&1u);p=nz(p,a);
    a=static_cast<std::uint8_t>(a|ram[1]);p=nz(p,a);
    ram[0x0470u+x]=a;
    // Even axis: $812A AND #$01, BEQ $815E: JMP $8843.
    // Odd axis: $8157 LDA Y; CMP #$30; BCS $815E: JMP $8843.
    if(!odd) {
        a=static_cast<std::uint8_t>(a&1u);p=nz(p,a);
        if(a==0) return {ActorVerticalExit0513::TransferToRaw8843,a,x,y,p,false};
    }else{
        a=ram[0x041cu+x];p=nz(p,a);
        cmp(a,0x30u,p);
        if(a>=0x30u) return {ActorVerticalExit0513::TransferToRaw8843,a,x,y,p,false};
    }
    // $812E-$813F type gate. BMI removes negative types, CMP $68/BCC
    // removes ordinary < $68 actors; type $68-$7F is retained.
    a=ram[0x054eu+x];p=nz(p,a);
    if((a&0x80u)==0) {
        cmp(a,0x68u,p);
        if(a>=0x68u) return {ActorVerticalExit0513::ReturnToFixedFDFB,a,x,y,p,false};
    }
    a=0;p=nz(p,a);
    ram[0x054eu+x]=0;
    ram[0x0400u+x]=0;
    return {ActorVerticalExit0513::ReturnToFixedFDFB,a,x,y,p,true};
}
ActorVertical0513 apply_prg0b_actor_8843_continuation(
        std::array<std::uint8_t,0x800>& ram, const ActorVertical0513& prefix) {
    if(prefix.exit!=ActorVerticalExit0513::TransferToRaw8843 ||
       prefix.x<1 || prefix.x>12 || (ram[0x65]&0x80u)==0)
        throw std::invalid_argument("$8843 only accepts original vertical transfer");
    auto p=prefix.p;
    auto a=ram[0x6b];p=nz(p,a);
    if(a==0) return {ActorVerticalExit0513::ReturnToFixedFDFB,a,prefix.x,prefix.y,p,prefix.removed};
    a=ram[0x054eu+prefix.x];p=nz(p,a);
    cmp(a,0x3bu,p);
    if(a!=0x3bu) return {ActorVerticalExit0513::ReturnToFixedFDFB,a,prefix.x,prefix.y,p,prefix.removed};
    std::uint8_t y=0;p=nz(p,y);
    a=ram[0x65];p=nz(p,a);
    a=static_cast<std::uint8_t>(a&1u);p=nz(p,a);
    if(a!=0){y=0xff;p=nz(p,y);}
    ram[4]=y;
    p=static_cast<std::uint8_t>(p&~1u); // CLC $885A
    a=ram[0x0606u+prefix.x];p=nz(p,a);
    a=adc(a,ram[0x6b],p);ram[0x0606u+prefix.x]=a;
    a=ram[0x061du+prefix.x];p=nz(p,a);
    a=adc(a,ram[4],p);ram[0x061du+prefix.x]=a;
    return {ActorVerticalExit0513::ReturnToFixedFDFB,a,prefix.x,y,p,prefix.removed};
}
ActorVertical0513 apply_prg0b_actor_displacement_80e3_vertical_complete(
        std::array<std::uint8_t,0x800>& ram,std::uint8_t x,std::uint8_t initial_p){
    auto result=apply_prg0b_actor_displacement_80e3_vertical(ram,x,initial_p);
    if(result.exit==ActorVerticalExit0513::TransferToRaw8843)
        return apply_prg0b_actor_8843_continuation(ram,result);
    return result;
}
} // namespace cv3
