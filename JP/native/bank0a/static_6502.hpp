#pragma once
// Native 6502 semantic core for a *statically emitted* instruction dispatch.
// This is not a game implementation, and does not model timing, PPU, IRQ or APU.
#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include <type_traits>
#include "../boot/ntsc_ppu_clock_0554.hpp"

namespace jpstatic {
enum class Mode { imp, acc, imm, zp, zpx, zpy, abs, absx, absy, indx, indy, ind, rel };
enum class Op {
 BRK, ORA, ASL, PHP, AND, BIT, ROL, PLP, RTI, EOR, LSR, PHA,
 ADC, ROR, PLA, JMP, JSR, BPL, BMI, BVC, BVS, BCC, BCS, BNE, BEQ,
 CLC, SEC, CLI, SEI, CLV, CLD, SED, RTS, DEY, INY, DEX, INX,
 STA, STX, STY, TYA, TXA, TAY, TAX, TXS, TSX, LDA, LDX, LDY,
 CMP, CPX, CPY, DEC, INC, SBC, NOP
};
#include "cpu_cycle_0554.hpp"  // Timing traits inside namespace jpstatic.
struct Bus {
 std::array<uint8_t,2048> ram{};
 std::array<uint8_t,16384> bank0a{},bank0e{};
 uint8_t bank=10;
 bool whole_prg=false;
 std::array<uint8_t,262144> prg{};
 std::array<uint8_t,65536> extra{};
 unsigned status_polls=0, ppu_data_reads=0;
 uint8_t controller_strobe=0;
 std::vector<std::pair<uint16_t,uint8_t>> io_writes;
 std::vector<std::pair<uint16_t,uint8_t>> mapped_reads;
 std::vector<uint8_t> mapper_writes;
 uint8_t read(uint16_t at) {
  if(at<0x2000) return ram[at&0x7ff];
  if(whole_prg) {
   if(at<0x4000) {
    uint16_t reg=uint16_t(0x2000+(at&7));
    if(reg==0x2002)return (++status_polls>=2)?0x80:0;
    if(reg==0x2007){++ppu_data_reads;return 0;}
    return 0;
   }
   if(at==0x4016 || at==0x4017)return 0;
   if(at<0x8000)return extra[at];
   if(at<0xc000) {
    if(bank>15)throw std::runtime_error("invalid VRC6 PRG bank");
    return prg[unsigned(bank)*16384+(at-0x8000)];
   }
   if(at<0xe000)return prg[30*8192+(at-0xc000)];
   return prg[31*8192+(at-0xe000)];
  }
  if(at>=0x8000 && at<0xc000) {
   if(bank==14) return bank0e[at-0x8000];
   if(bank==10) return bank0a[at-0x8000];
   throw std::runtime_error("unexpected physical VRC6 bank");
  }
  throw std::runtime_error("external 6502 hardware/ROM dependency at "+std::to_string(at));
 }
 void write(uint16_t at,uint8_t value) {
  if(at<0x2000) {ram[at&0x7ff]=value;return;}
  if(whole_prg) {
   if(at==0x8000) {bank=value;mapper_writes.push_back(value);return;}
   if(at==0x4016){controller_strobe=value;return;}
   if((at>=0x2000 && at<0x6000) || at>=0x8000) {io_writes.emplace_back(at,value);return;}
   extra[at]=value;return;
  }
  if(at==0x8000 && (value==10 || value==14)) {
   bank=value;mapper_writes.push_back(value);return;
  }
  throw std::runtime_error("unresolved VRC6 write at "+std::to_string(at));
 }
 uint16_t word(uint16_t p) {auto a=read(p);return uint16_t(a|(uint16_t(read(uint16_t(p+1)))<<8));}
 uint16_t zpword(uint8_t p) {auto a=read(p);return uint16_t(a|(uint16_t(read(uint8_t(p+1)))<<8));}
};
template <Op O> struct UnhandledOpcode : std::false_type {};
struct Cpu {
 Bus &bus;
 NtscPpuClock ppu_clock{};  // Observes instruction totals, not individual bus phases.
 uint64_t cycles=0;
 bool address_page_cross_=false;
 uint16_t pc=0;
 uint8_t a=0,x=0,y=0,s=0xfd,p=0x20;
 explicit Cpu(Bus& b):bus(b){}
 bool flag(int v) const{return (p&v)!=0;}
 void set(int v,bool b) {p=uint8_t(b?(p|v):(p&~v));p|=0x20;}
 void nz(uint8_t v) {set(2,v==0);set(0x80,(v&128)!=0);}
 void push(uint8_t v) {bus.write(uint16_t(0x100|s),v);--s;}
 uint8_t pop() {return bus.read(uint16_t(0x100|uint8_t(++s)));}
 void nmi() {
  push(uint8_t(pc>>8));push(uint8_t(pc));push(uint8_t((p&~0x10)|0x20));
  set(4,true);pc=bus.word(0xfffa);
  cycles+=7;ppu_clock.advance_cpu_cycles(7); // NMOS 6502 interrupt entry.
 }
 void rts() {uint16_t low=pop(),hi=pop();pc=uint16_t((hi<<8|low)+1);}
 uint16_t address(Mode m,uint16_t operand) {
  switch(m) {
   case Mode::zp:return uint8_t(operand);
   case Mode::zpx:return uint8_t(operand+x);
   case Mode::zpy:return uint8_t(operand+y);
   case Mode::abs:return operand;
   case Mode::absx:{const auto at=uint16_t(operand+x);address_page_cross_=(operand&0xff00)!=(at&0xff00);return at;}
   case Mode::absy:{const auto at=uint16_t(operand+y);address_page_cross_=(operand&0xff00)!=(at&0xff00);return at;}
   case Mode::indx:return bus.zpword(uint8_t(operand+x));
   case Mode::indy:{const auto base=bus.zpword(uint8_t(operand));const auto at=uint16_t(base+y);address_page_cross_=(base&0xff00)!=(at&0xff00);return at;}
   case Mode::ind:{const uint16_t lo=bus.read(operand);
       const uint16_t hi=bus.read(uint16_t((operand&0xff00)|uint8_t(operand+1)));
       return uint16_t(lo|(hi<<8));}
   default: throw std::runtime_error("invalid address mode");
  }
 }
 uint8_t value(Mode m,uint16_t operand) {
  if(m==Mode::imm)return uint8_t(operand);
  if(m==Mode::acc)return a;
  return bus.read(address(m,operand));
 }
 void compare(uint8_t lhs,uint8_t rhs){auto v=uint8_t(lhs-rhs);set(1,lhs>=rhs);nz(v);}
 void adc(uint8_t rhs){auto t=uint16_t(a)+rhs+(flag(1)?1:0);auto v=uint8_t(t);
  set(1,t>255);set(0x40,((~(a^rhs)&(a^v))&128)!=0);a=v;nz(a);}
 void sbc(uint8_t rhs){adc(uint8_t(~rhs));}
 template <Op O,Mode M> void exec(uint16_t operand,uint16_t next) {
  constexpr unsigned base_cycles=base_cpu_cycles_0554<O,M>();
  static_assert(base_cycles!=0,"unsupported original opcode/address-mode timing");
  pc=next;
  address_page_cross_=false;
  unsigned branch_penalty=0;
  if constexpr(O==Op::LDA){a=value(M,operand);nz(a);}
  else if constexpr(O==Op::LDX){x=value(M,operand);nz(x);}
  else if constexpr(O==Op::LDY){y=value(M,operand);nz(y);}
  else if constexpr(O==Op::STA)bus.write(address(M,operand),a);
  else if constexpr(O==Op::STX)bus.write(address(M,operand),x);
  else if constexpr(O==Op::STY)bus.write(address(M,operand),y);
  else if constexpr(O==Op::ADC)adc(value(M,operand));
  else if constexpr(O==Op::SBC)sbc(value(M,operand));
  else if constexpr(O==Op::AND){a=uint8_t(a&value(M,operand));nz(a);}
  else if constexpr(O==Op::ORA){a=uint8_t(a|value(M,operand));nz(a);}
  else if constexpr(O==Op::EOR){a=uint8_t(a^value(M,operand));nz(a);}
  else if constexpr(O==Op::CMP)compare(a,value(M,operand));
  else if constexpr(O==Op::CPX)compare(x,value(M,operand));
  else if constexpr(O==Op::CPY)compare(y,value(M,operand));
  else if constexpr(O==Op::BIT){auto v=value(M,operand);set(2,(a&v)==0);set(0x40,(v&0x40)!=0);set(0x80,(v&0x80)!=0);}
  else if constexpr(O==Op::ASL || O==Op::LSR || O==Op::ROL || O==Op::ROR || O==Op::INC || O==Op::DEC) {
   uint16_t ad=0; uint8_t v;
   if constexpr(M==Mode::acc)v=a;
   else {ad=address(M,operand);v=bus.read(ad);}
   if constexpr(O==Op::ASL){set(1,(v&0x80)!=0);v=uint8_t(v<<1);}
   if constexpr(O==Op::LSR){set(1,(v&1)!=0);v=uint8_t(v>>1);}
   if constexpr(O==Op::ROL){auto carry=flag(1);set(1,(v&0x80)!=0);v=uint8_t((v<<1)|(carry?1:0));}
   if constexpr(O==Op::ROR){auto carry=flag(1);set(1,(v&1)!=0);v=uint8_t((v>>1)|(carry?128:0));}
   if constexpr(O==Op::INC)v=uint8_t(v+1);
   if constexpr(O==Op::DEC)v=uint8_t(v-1);
   nz(v);
   if constexpr(M==Mode::acc)a=v;
   else bus.write(ad,v);
  }
  else if constexpr(O==Op::BPL||O==Op::BMI||O==Op::BVC||O==Op::BVS||O==Op::BCC||O==Op::BCS||O==Op::BNE||O==Op::BEQ){
   bool taken=false;
   if constexpr(O==Op::BPL)taken=!flag(0x80);
   if constexpr(O==Op::BMI)taken=flag(0x80);
   if constexpr(O==Op::BVC)taken=!flag(0x40);
   if constexpr(O==Op::BVS)taken=flag(0x40);
   if constexpr(O==Op::BCC)taken=!flag(1);
   if constexpr(O==Op::BCS)taken=flag(1);
   if constexpr(O==Op::BNE)taken=!flag(2);
   if constexpr(O==Op::BEQ)taken=flag(2);
   if(taken){branch_penalty=1u+(((next^operand)&0xff00u)?1u:0u);pc=operand;}
  }
  else if constexpr(O==Op::JSR){auto ret=uint16_t(next-1);push(uint8_t(ret>>8));push(uint8_t(ret));pc=operand;}
  else if constexpr(O==Op::JMP){if constexpr(M==Mode::ind)pc=address(M,operand);else pc=operand;}
  else if constexpr(O==Op::RTS)rts();
  else if constexpr(O==Op::RTI){p=uint8_t(pop()|0x20);auto lo=pop();pc=uint16_t(lo|(uint16_t(pop())<<8));}
  else if constexpr(O==Op::BRK)throw std::runtime_error("BRK requires IRQ vector and PPU/CPU cycle model");
  else if constexpr(O==Op::PHA)push(a);
  else if constexpr(O==Op::PHP)push(uint8_t(p|0x30));
  else if constexpr(O==Op::PLA){a=pop();nz(a);}
  else if constexpr(O==Op::PLP){p=uint8_t(pop()|0x20);}
  else if constexpr(O==Op::CLC)set(1,false);
  else if constexpr(O==Op::SEC)set(1,true);
  else if constexpr(O==Op::CLI)set(4,false);
  else if constexpr(O==Op::SEI)set(4,true);
  else if constexpr(O==Op::CLV)set(0x40,false);
  else if constexpr(O==Op::CLD)set(8,false);
  else if constexpr(O==Op::SED)set(8,true); // 2A03 decimal mode ignored by ADC/SBC
  else if constexpr(O==Op::DEX){x=uint8_t(x-1);nz(x);}
  else if constexpr(O==Op::DEY){y=uint8_t(y-1);nz(y);}
  else if constexpr(O==Op::INX){x=uint8_t(x+1);nz(x);}
  else if constexpr(O==Op::INY){y=uint8_t(y+1);nz(y);}
  else if constexpr(O==Op::TAX){x=a;nz(x);}
  else if constexpr(O==Op::TAY){y=a;nz(y);}
  else if constexpr(O==Op::TXA){a=x;nz(a);}
  else if constexpr(O==Op::TYA){a=y;nz(a);}
  else if constexpr(O==Op::TSX){x=s;nz(x);}
  else if constexpr(O==Op::TXS)s=x;
  else if constexpr(O==Op::NOP){}
  else static_assert(UnhandledOpcode<O>::value,"unimplemented 6502 opcode");
  const unsigned added=base_cycles+branch_penalty+
      ((indexed_read_penalty_0554<O,M>() && address_page_cross_)?1u:0u);
  cycles+=added;
  ppu_clock.advance_cpu_cycles(added);
 }
 // Fixed-$FB96 is independently bounded. Other cross-bank calls FAIL CLOSED.
 bool bounded_external() {
  if(pc!=0xfb96)return false;
  // Original bytes at FB96: A9 0E; JSR E2D0; B1 08; PHA;
  // A9 0A; JSR E2D0; PLA; RTS. VRC6 mapper-write at E2D0.
  a=14;nz(a);push(0xfb);push(0x9a);
  bus.write(0x23,a);bus.write(0x8000,a);rts();
  uint16_t address=uint16_t(bus.zpword(8)+y);
  if(address<0x8000 || address>=0xc000)throw std::runtime_error("FB96 read escaped bank");
  a=bus.read(address);bus.mapped_reads.emplace_back(address,a);nz(a);push(a);
  a=10;nz(a);push(0xfb);push(0xa2);
  bus.write(0x23,a);bus.write(0x8000,a);rts();
  a=pop();nz(a);rts();return true;
 }
};
enum class StepResult { executed, unresolved, candidate_blocked };
StepResult compiled_step(Cpu& cpu,bool allow_conditional=false);
}
