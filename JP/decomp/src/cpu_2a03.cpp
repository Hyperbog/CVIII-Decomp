#include "cpu_2a03.hpp"
#include <array>
#include <cstdio>
#include <stdexcept>

namespace cv3 {
namespace {
constexpr std::uint8_t C=1, Z=2, I=4, D=8, B=16, U=32, V=64, N=128;
enum Mn : std::uint8_t {
 ADC,AND,ASL,BCC,BCS,BEQ,BIT,BMI,BNE,BPL,BRK,BVC,BVS,CLC,CLD,CLI,CLV,
 CMP,CPX,CPY,DEC,DEX,DEY,EOR,INC,INX,INY,JMP,JSR,LDA,LDX,LDY,LSR,NOP,
 ORA,PHA,PHP,PLA,PLP,ROL,ROR,RTI,RTS,SBC,SEC,SED,SEI,STA,STX,STY,TAX,TAY,
 TSX,TXA,TXS,TYA,INVALID
};
enum Mode : std::uint8_t {IMP,ACC,ZP,ZPX,ZPY,INDX,INDY,IMM,ABS,ABSX,ABSY,IND,REL};
struct Desc { Mn mn=INVALID; Mode mode=IMP; std::uint8_t cycles=0; };
std::array<Desc,256> make_table() {
    std::array<Desc,256> t{};
    // Generated from the 151 official NMOS 6502 opcode/mode pairs in the
    // SharedNES table. Base cycles from MOS 6500 and NESdev; only branch and
    // indexed READ modes can add conditional cycles.
    t[0x00]={BRK,IMP,7};
    t[0x01]={ORA,INDX,6};
    t[0x05]={ORA,ZP,3};
    t[0x06]={ASL,ZP,5};
    t[0x08]={PHP,IMP,3};
    t[0x09]={ORA,IMM,2};
    t[0x0A]={ASL,ACC,2};
    t[0x0D]={ORA,ABS,4};
    t[0x0E]={ASL,ABS,6};
    t[0x10]={BPL,REL,2};
    t[0x11]={ORA,INDY,5};
    t[0x15]={ORA,ZPX,4};
    t[0x16]={ASL,ZPX,6};
    t[0x18]={CLC,IMP,2};
    t[0x19]={ORA,ABSY,4};
    t[0x1D]={ORA,ABSX,4};
    t[0x1E]={ASL,ABSX,7};
    t[0x20]={JSR,ABS,6};
    t[0x21]={AND,INDX,6};
    t[0x24]={BIT,ZP,3};
    t[0x25]={AND,ZP,3};
    t[0x26]={ROL,ZP,5};
    t[0x28]={PLP,IMP,4};
    t[0x29]={AND,IMM,2};
    t[0x2A]={ROL,ACC,2};
    t[0x2C]={BIT,ABS,4};
    t[0x2D]={AND,ABS,4};
    t[0x2E]={ROL,ABS,6};
    t[0x30]={BMI,REL,2};
    t[0x31]={AND,INDY,5};
    t[0x35]={AND,ZPX,4};
    t[0x36]={ROL,ZPX,6};
    t[0x38]={SEC,IMP,2};
    t[0x39]={AND,ABSY,4};
    t[0x3D]={AND,ABSX,4};
    t[0x3E]={ROL,ABSX,7};
    t[0x40]={RTI,IMP,6};
    t[0x41]={EOR,INDX,6};
    t[0x45]={EOR,ZP,3};
    t[0x46]={LSR,ZP,5};
    t[0x48]={PHA,IMP,3};
    t[0x49]={EOR,IMM,2};
    t[0x4A]={LSR,ACC,2};
    t[0x4C]={JMP,ABS,3};
    t[0x4D]={EOR,ABS,4};
    t[0x4E]={LSR,ABS,6};
    t[0x50]={BVC,REL,2};
    t[0x51]={EOR,INDY,5};
    t[0x55]={EOR,ZPX,4};
    t[0x56]={LSR,ZPX,6};
    t[0x58]={CLI,IMP,2};
    t[0x59]={EOR,ABSY,4};
    t[0x5D]={EOR,ABSX,4};
    t[0x5E]={LSR,ABSX,7};
    t[0x60]={RTS,IMP,6};
    t[0x61]={ADC,INDX,6};
    t[0x65]={ADC,ZP,3};
    t[0x66]={ROR,ZP,5};
    t[0x68]={PLA,IMP,4};
    t[0x69]={ADC,IMM,2};
    t[0x6A]={ROR,ACC,2};
    t[0x6C]={JMP,IND,5};
    t[0x6D]={ADC,ABS,4};
    t[0x6E]={ROR,ABS,6};
    t[0x70]={BVS,REL,2};
    t[0x71]={ADC,INDY,5};
    t[0x75]={ADC,ZPX,4};
    t[0x76]={ROR,ZPX,6};
    t[0x78]={SEI,IMP,2};
    t[0x79]={ADC,ABSY,4};
    t[0x7D]={ADC,ABSX,4};
    t[0x7E]={ROR,ABSX,7};
    t[0x81]={STA,INDX,6};
    t[0x84]={STY,ZP,3};
    t[0x85]={STA,ZP,3};
    t[0x86]={STX,ZP,3};
    t[0x88]={DEY,IMP,2};
    t[0x8A]={TXA,IMP,2};
    t[0x8C]={STY,ABS,4};
    t[0x8D]={STA,ABS,4};
    t[0x8E]={STX,ABS,4};
    t[0x90]={BCC,REL,2};
    t[0x91]={STA,INDY,6};
    t[0x94]={STY,ZPX,4};
    t[0x95]={STA,ZPX,4};
    t[0x96]={STX,ZPY,4};
    t[0x98]={TYA,IMP,2};
    t[0x99]={STA,ABSY,5};
    t[0x9A]={TXS,IMP,2};
    t[0x9D]={STA,ABSX,5};
    t[0xA0]={LDY,IMM,2};
    t[0xA1]={LDA,INDX,6};
    t[0xA2]={LDX,IMM,2};
    t[0xA4]={LDY,ZP,3};
    t[0xA5]={LDA,ZP,3};
    t[0xA6]={LDX,ZP,3};
    t[0xA8]={TAY,IMP,2};
    t[0xA9]={LDA,IMM,2};
    t[0xAA]={TAX,IMP,2};
    t[0xAC]={LDY,ABS,4};
    t[0xAD]={LDA,ABS,4};
    t[0xAE]={LDX,ABS,4};
    t[0xB0]={BCS,REL,2};
    t[0xB1]={LDA,INDY,5};
    t[0xB4]={LDY,ZPX,4};
    t[0xB5]={LDA,ZPX,4};
    t[0xB6]={LDX,ZPY,4};
    t[0xB8]={CLV,IMP,2};
    t[0xB9]={LDA,ABSY,4};
    t[0xBA]={TSX,IMP,2};
    t[0xBC]={LDY,ABSX,4};
    t[0xBD]={LDA,ABSX,4};
    t[0xBE]={LDX,ABSY,4};
    t[0xC0]={CPY,IMM,2};
    t[0xC1]={CMP,INDX,6};
    t[0xC4]={CPY,ZP,3};
    t[0xC5]={CMP,ZP,3};
    t[0xC6]={DEC,ZP,5};
    t[0xC8]={INY,IMP,2};
    t[0xC9]={CMP,IMM,2};
    t[0xCA]={DEX,IMP,2};
    t[0xCC]={CPY,ABS,4};
    t[0xCD]={CMP,ABS,4};
    t[0xCE]={DEC,ABS,6};
    t[0xD0]={BNE,REL,2};
    t[0xD1]={CMP,INDY,5};
    t[0xD5]={CMP,ZPX,4};
    t[0xD6]={DEC,ZPX,6};
    t[0xD8]={CLD,IMP,2};
    t[0xD9]={CMP,ABSY,4};
    t[0xDD]={CMP,ABSX,4};
    t[0xDE]={DEC,ABSX,7};
    t[0xE0]={CPX,IMM,2};
    t[0xE1]={SBC,INDX,6};
    t[0xE4]={CPX,ZP,3};
    t[0xE5]={SBC,ZP,3};
    t[0xE6]={INC,ZP,5};
    t[0xE8]={INX,IMP,2};
    t[0xE9]={SBC,IMM,2};
    t[0xEA]={NOP,IMP,2};
    t[0xEC]={CPX,ABS,4};
    t[0xED]={SBC,ABS,4};
    t[0xEE]={INC,ABS,6};
    t[0xF0]={BEQ,REL,2};
    t[0xF1]={SBC,INDY,5};
    t[0xF5]={SBC,ZPX,4};
    t[0xF6]={INC,ZPX,6};
    t[0xF8]={SED,IMP,2};
    t[0xF9]={SBC,ABSY,4};
    t[0xFD]={SBC,ABSX,4};
    t[0xFE]={INC,ABSX,7};
    return t;
}
const std::array<Desc,256> TABLE=make_table();
} // namespace
std::uint8_t Cpu2A03::get() { auto v=bus_.read(state_.pc); state_.pc=static_cast<std::uint16_t>(state_.pc+1); return v; }
std::uint16_t Cpu2A03::get16() {auto lo=get();return std::uint16_t(lo | (std::uint16_t(get())<<8));}
std::uint16_t Cpu2A03::read16(std::uint16_t at) {return std::uint16_t(bus_.read(at)|(std::uint16_t(bus_.read(std::uint16_t(at+1)))<<8));}
std::uint16_t Cpu2A03::readzp16(std::uint8_t at) {return std::uint16_t(bus_.read(at)|(std::uint16_t(bus_.read(std::uint8_t(at+1)))<<8));}
void Cpu2A03::push(std::uint8_t v) {bus_.write(std::uint16_t(0x100|state_.sp),v);--state_.sp;}
std::uint8_t Cpu2A03::pop() {++state_.sp;return bus_.read(std::uint16_t(0x100|state_.sp));}
void Cpu2A03::setflag(std::uint8_t f,bool x){if(x)state_.p|=f;else state_.p=std::uint8_t(state_.p&~f);}
void Cpu2A03::nz(std::uint8_t a){setflag(Z,a==0);setflag(N,bool(a&128));}
void Cpu2A03::vector(std::uint16_t at,bool brk){
    push(std::uint8_t(state_.pc>>8));push(std::uint8_t(state_.pc));
    push(std::uint8_t((state_.p|U|(brk?B:0)) & (brk?255:~B)));
    setflag(I,true);state_.pc=read16(at);cycles_+=7;
}
void Cpu2A03::reset(){state_={};state_.p=U|I;state_.sp=0xFD;state_.pc=read16(0xFFFC);instructions_=0;cycles_=7;}
void Cpu2A03::nmi(){vector(0xFFFA,false);}
void Cpu2A03::irq(){if(!flag(I))vector(0xFFFE,false);}
std::uint8_t Cpu2A03::step() {
    const std::uint16_t pc=state_.pc;
    const std::uint8_t op=get();
    auto desc=TABLE[op];
    if(desc.mn==INVALID){char buf[96];std::snprintf(buf,sizeof(buf),"unsupported 6502 opcode %02X at PC %04X",op,pc);throw std::runtime_error(buf);}
    ++instructions_;
    std::uint16_t address=0,base=0;
    std::uint8_t value=0,relative=0;
    bool page_cross=false;
    switch(desc.mode) {
    case IMP:case ACC:break;
    case IMM:value=get();break;
    case ZP:address=get();break;
    case ZPX:address=std::uint8_t(get()+state_.x);break;
    case ZPY:address=std::uint8_t(get()+state_.y);break;
    case INDX:address=readzp16(std::uint8_t(get()+state_.x));break;
    case INDY:base=readzp16(get());address=std::uint16_t(base+state_.y);page_cross=(base&0xFF00)!=(address&0xFF00);break;
    case ABS:address=get16();break;
    case ABSX:base=get16();address=std::uint16_t(base+state_.x);page_cross=(base&0xFF00)!=(address&0xFF00);break;
    case ABSY:base=get16();address=std::uint16_t(base+state_.y);page_cross=(base&0xFF00)!=(address&0xFF00);break;
    case IND:{const auto addr=get16();address=std::uint16_t(bus_.read(addr)|(std::uint16_t(bus_.read((addr&0xFF00)|std::uint8_t(addr+1)))<<8));break;}
    case REL:relative=get();break;
    }
    const Mn m=desc.mn;
    // Avoid eager mapped I/O reads for stores, JSR and JMP. For NMOS RMW,
    // read the old value and write it back before the modified byte.
    const bool memory=desc.mode!=IMP&&desc.mode!=ACC&&desc.mode!=IMM&&desc.mode!=REL;
    const bool write=(m==STA||m==STX||m==STY);
    const bool pointer=(m==JMP||m==JSR);
    if(memory&&!write&&!pointer)value=bus_.read(address);
    auto writebyte=[&](std::uint8_t v){bus_.write(address,v);};
    auto compare=[&](std::uint8_t a){setflag(C,a>=value);nz(std::uint8_t(a-value));};
    auto carry=[&](){return std::uint16_t(flag(C)?1:0);};
    switch(m) {
    case LDA:state_.a=value;nz(value);break;
    case LDX:state_.x=value;nz(value);break;
    case LDY:state_.y=value;nz(value);break;
    case STA:writebyte(state_.a);break;
    case STX:writebyte(state_.x);break;
    case STY:writebyte(state_.y);break;
    case ADC:case SBC:{
        const auto a=state_.a;
        const auto rhs=std::uint8_t(m==SBC?value^255:value);
        const std::uint16_t sum=std::uint16_t(a)+rhs+carry();
        const auto out=std::uint8_t(sum);
        state_.a=out;setflag(C,sum>255);
        setflag(V,bool((~(a^rhs)&(a^out)&128)!=0));nz(out);break;
    }
    case CMP:compare(state_.a);break;
    case CPX:compare(state_.x);break;
    case CPY:compare(state_.y);break;
    case BIT:setflag(Z,(state_.a&value)==0);setflag(N,value&128);setflag(V,value&64);break;
    case AND:state_.a=std::uint8_t(state_.a&value);nz(state_.a);break;
    case ORA:state_.a=std::uint8_t(state_.a|value);nz(state_.a);break;
    case EOR:state_.a=std::uint8_t(state_.a^value);nz(state_.a);break;
    case ASL:case LSR:case ROL:case ROR: {
        const bool acc=desc.mode==ACC;
        const auto old=acc?state_.a:value;
        const auto cin=carry();
        std::uint8_t next=0;
        if(m==ASL||m==ROL){setflag(C,old&0x80);next=std::uint8_t((old<<1)|(m==ROL?cin:0));}
        else {setflag(C,old&1);next=std::uint8_t((old>>1)|(m==ROR?(cin<<7):0));}
        if(acc)state_.a=next;
        else {writebyte(old);writebyte(next);}
        nz(next);break;
    }
    case INC:case DEC:{writebyte(value);auto out=std::uint8_t(value+(m==INC?1:-1));writebyte(out);nz(out);break;}
    case INX:state_.x=std::uint8_t(state_.x+1);nz(state_.x);break;
    case INY:state_.y=std::uint8_t(state_.y+1);nz(state_.y);break;
    case DEX:state_.x=std::uint8_t(state_.x-1);nz(state_.x);break;
    case DEY:state_.y=std::uint8_t(state_.y-1);nz(state_.y);break;
    case TAX:state_.x=state_.a;nz(state_.x);break;
    case TAY:state_.y=state_.a;nz(state_.y);break;
    case TXA:state_.a=state_.x;nz(state_.a);break;
    case TYA:state_.a=state_.y;nz(state_.a);break;
    case TSX:state_.x=state_.sp;nz(state_.x);break;
    case TXS:state_.sp=state_.x;break;
    case PHA:push(state_.a);break;
    case PHP:push(std::uint8_t(state_.p|U|B));break;
    case PLA:state_.a=pop();nz(state_.a);break;
    case PLP:state_.p=std::uint8_t((pop()|U)&~B);break;
    case JSR:{const std::uint16_t ret=std::uint16_t(state_.pc-1);push(std::uint8_t(ret>>8));push(std::uint8_t(ret));state_.pc=address;break;}
    case JMP:state_.pc=address;break;
    case RTS:state_.pc=std::uint16_t(std::uint16_t(pop())|(std::uint16_t(pop())<<8));++state_.pc;break;
    case RTI:state_.p=std::uint8_t((pop()|U)&~B);state_.pc=pop();state_.pc=std::uint16_t(state_.pc|(std::uint16_t(pop())<<8));break;
    case BRK:++state_.pc;vector(0xFFFE,true);break;
    case BCC:case BCS:case BEQ:case BNE:case BMI:case BPL:case BVC:case BVS: {
        bool take=false;
        switch(m){case BCC:take=!flag(C);break;case BCS:take=flag(C);break;case BEQ:take=flag(Z);break;
            case BNE:take=!flag(Z);break;case BMI:take=flag(N);break;case BPL:take=!flag(N);break;
            case BVC:take=!flag(V);break;case BVS:take=flag(V);break;default:break;}
        if(take){const auto before=state_.pc;state_.pc=std::uint16_t(state_.pc+static_cast<std::int8_t>(relative));
            ++desc.cycles;if((before&0xFF00)!=(state_.pc&0xFF00))++desc.cycles;}
        break;
    }
    case CLC:setflag(C,false);break;case SEC:setflag(C,true);break;
    case CLD:setflag(D,false);break;case SED:setflag(D,true);break;
    case CLI:setflag(I,false);break;case SEI:setflag(I,true);break;
    case CLV:setflag(V,false);break;
    case NOP:break;
    default:throw std::logic_error("unimplemented official mnemonic");
    }
    if(page_cross&&(m==ORA||m==AND||m==EOR||m==ADC||m==LDA||m==CMP||m==SBC||m==LDX||m==LDY))++desc.cycles;
    state_.p|=U;
    if(m!=BRK)cycles_+=desc.cycles;
    return desc.cycles;
}
} // namespace cv3
