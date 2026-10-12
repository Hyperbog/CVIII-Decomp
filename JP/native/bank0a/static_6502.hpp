#pragma once
// Native 6502 semantic core for a *statically emitted* instruction dispatch.
// Bounded compiled 2A03 core. Optional direct PPU-register accesses are timed;
// full CPU bus phases, PPU rendering, mapper IRQ, DMA and APU remain unresolved.
// Optional PPU NMI and externally driven level IRQ arbitration is available.
#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include <type_traits>
#include "../boot/ntsc_ppu_clock_0554.hpp"
#include "../boot/ppu_register_bus_0554.hpp"
#include "../boot/vrc6_irq_0554.hpp"
#include "../boot/oam_dma_0554.hpp"

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
 ClockedPpuRegisters* timed_ppu_io=nullptr; // null: preserve 0553 scripted policy
 Vrc6IrqCounter* timed_vrc6_irq=nullptr;
 bool vrc6_write_armed=false;
 RamOamDma* timed_oam_dma=nullptr;
 bool oam_dma_write_armed=false;
 std::vector<std::pair<uint16_t,uint8_t>> io_writes;
 std::vector<std::pair<uint16_t,uint8_t>> mapped_reads;
 std::vector<uint8_t> mapper_writes;
 uint8_t read(uint16_t at) {
  if(at<0x2000) return ram[at&0x7ff];
  if(at<0x4000 && timed_ppu_io)return timed_ppu_io->read(at);
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
  if(at==0x4014 && timed_oam_dma) {
   if(!oam_dma_write_armed)throw std::runtime_error("OAMDMA $4014 lacks supported final CPU bus cycle");
   timed_oam_dma->request(value);
   io_writes.emplace_back(at,value);
   return;
  }
  if(at>=0xf000 && at<=0xf002 && timed_vrc6_irq) {
   if(!vrc6_write_armed)throw std::runtime_error("VRC6 IRQ register write lacks supported final CPU bus cycle");
   timed_vrc6_irq->write(at,value);
   io_writes.emplace_back(at,value);
   return;
  }
  if(at<0x4000 && timed_ppu_io) {
   timed_ppu_io->write(at,value);
   io_writes.emplace_back(at,value);
   return;
  }
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
enum class InterruptKind { none, nmi, irq };
struct Cpu {
 Bus &bus;
 NtscPpuClock ppu_clock{};
 ClockedPpuRegisters ppu_io{ppu_clock};
 Vrc6IrqCounter vrc6_irq{};
 bool vrc6_irq_enabled_=false;
 RamOamDma oam_dma{};
 bool oam_dma_enabled_=false;
 void enable_timed_ppu_registers() {bus.timed_ppu_io=&ppu_io;}
 void enable_vrc6_irq(bool enabled=true) {
  vrc6_irq_enabled_=enabled;
  bus.timed_vrc6_irq=enabled?&vrc6_irq:nullptr;
  bus.vrc6_write_armed=false;
 }
 void enable_ram_oam_dma(unsigned get_cycle_parity) {
  oam_dma.set_get_cycle_parity(get_cycle_parity);
  oam_dma_enabled_=true;
  bus.timed_oam_dma=&oam_dma;
 }
 void advance_cycles(unsigned n) {
  cycles+=n;ppu_clock.advance_cpu_cycles(n);
  if(vrc6_irq_enabled_)vrc6_irq.clock_cpu_cycles(n);
 }
 uint64_t cycles=0;
 bool address_page_cross_=false;
 bool automatic_interrupts_=false, external_irq_line_=false;
 bool delayed_irq_mask_valid_=false, delayed_irq_mask_=true;
 bool skip_next_interrupt_poll_=false;
 uint16_t pc=0;
 uint8_t a=0,x=0,y=0,s=0xfd,p=0x20;
 explicit Cpu(Bus& b):bus(b){}
 bool flag(int v) const{return (p&v)!=0;}
 void set(int v,bool b) {p=uint8_t(b?(p|v):(p&~v));p|=0x20;}
 void nz(uint8_t v) {set(2,v==0);set(0x80,(v&128)!=0);}
 void push(uint8_t v) {bus.write(uint16_t(0x100|s),v);--s;}
 uint8_t pop() {return bus.read(uint16_t(0x100|uint8_t(++s)));}
 void enter_interrupt(uint16_t vector) {
  push(uint8_t(pc>>8));push(uint8_t(pc));
  push(uint8_t((p&~0x10u)|0x20u)); // Hardware B=0; bit 5 stays set.
  set(4,true);pc=bus.word(vector);
  advance_cycles(7); // Entry cost only; bus micro-phases not modeled.
 }
 void nmi() {enter_interrupt(0xfffa);}
 void irq() {enter_interrupt(0xfffe);}
 // Explicit opt-in; shipped 0553 replay does not enable this scheduler.
 void enable_boundary_interrupts(bool enabled=true) {
  automatic_interrupts_=enabled;
  delayed_irq_mask_valid_=false;
  skip_next_interrupt_poll_=false;
 }
 void set_external_irq_line(bool asserted){external_irq_line_=asserted;}
 // Call once immediately BEFORE each statically dispatched instruction.
 // PPU NMI edge has priority; external IRQ is level-sensitive and I-masked.
 // CLI/SEI/PLP use their previous I bit at the following boundary; RTI
 // immediately restores the mask. This is NOT cycle-exact IRQ polling.
 InterruptKind service_interrupt_boundary() {
  if(!automatic_interrupts_)return InterruptKind::none;
  const bool mask=delayed_irq_mask_valid_?delayed_irq_mask_:flag(4);
  delayed_irq_mask_valid_=false;
  if(skip_next_interrupt_poll_){skip_next_interrupt_poll_=false;return InterruptKind::none;}
  if(ppu_clock.take_nmi()) {
   nmi();skip_next_interrupt_poll_=true;return InterruptKind::nmi;
  }
  if((external_irq_line_ || (vrc6_irq_enabled_ && vrc6_irq.irq_line())) && !mask) {
   irq();skip_next_interrupt_poll_=true;return InterruptKind::irq;
  }
  return InterruptKind::none;
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
  [[maybe_unused]] const bool old_irq_mask=flag(4);
  pc=next;
  address_page_cross_=false;
  unsigned branch_penalty=0;
  // Opt-in final-access phase for direct absolute 2C02 memory operations.
  // Other PPU addressing shapes fail closed until their bus phases are modeled.
  bool timed_final_access=false;
  unsigned cycles_before_access=0;
  bool timed_vrc6_write=false;
  bool timed_oam_dma_write=false;
  if(bus.timed_ppu_io || bus.timed_vrc6_irq || bus.timed_oam_dma) {
   if constexpr(M==Mode::abs || M==Mode::absx || M==Mode::absy) {
    constexpr bool read_ppu=(O==Op::LDA || O==Op::LDX || O==Op::LDY || O==Op::BIT);
    constexpr bool write_ppu=(O==Op::STA || O==Op::STX || O==Op::STY);
    if constexpr(read_ppu || write_ppu) {
     const uint16_t eff=uint16_t(operand+
       (M==Mode::absx ? unsigned(x) : (M==Mode::absy ? unsigned(y) : 0u)));
     const bool direct_ppu=bus.timed_ppu_io && eff>=0x2000 && eff<0x4000;
     const bool direct_vrc6=bus.timed_vrc6_irq &&
       eff>=0xf000 && eff<=0xf002 && write_ppu;
     const bool direct_dma=bus.timed_oam_dma && eff==0x4014 && write_ppu;
     if((direct_ppu && (read_ppu || write_ppu)) || direct_vrc6 || direct_dma) {
      const bool crossed=(operand&0xff00u)!=(eff&0xff00u);
      const unsigned penalty=indexed_read_penalty_0554<O,M>() && crossed ? 1u : 0u;
      cycles_before_access=base_cycles+penalty-1u;
      advance_cycles(cycles_before_access);
      if(direct_ppu)bus.timed_ppu_io->arm_final_cycle();
      if(direct_vrc6){bus.vrc6_write_armed=true;timed_vrc6_write=true;}
      if(direct_dma){bus.oam_dma_write_armed=true;timed_oam_dma_write=true;}
      timed_final_access=true;
     }
    }
   }
  }
  // Fail-closed PPU reads/writes can throw. Always clear the temporary
  // access permission even if a modeled direct register operation rejects.
  struct PpuAccessCleanup {
   ClockedPpuRegisters* io;
   Bus& bus;
   ~PpuAccessCleanup(){
    if(io)io->disarm();
    bus.vrc6_write_armed=false;
    bus.oam_dma_write_armed=false;
   }
  } ppu_cleanup{timed_final_access ? bus.timed_ppu_io : nullptr,bus};
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
  if(timed_final_access) {
   if(bus.timed_ppu_io)bus.timed_ppu_io->disarm();
   if(timed_vrc6_write)bus.vrc6_write_armed=false;
   if(timed_oam_dma_write)bus.oam_dma_write_armed=false;
   if(added!=cycles_before_access+1u)
    throw std::runtime_error("timed PPU access cycle-accounting mismatch");
   advance_cycles(1);
  } else advance_cycles(added);
  // DMA halts after the $4014 write instruction's final CPU cycle.
  // No DMC overlap or CPU read-halt retries are modeled.
  if(oam_dma_enabled_ && oam_dma.pending())
   oam_dma.complete(cycles,bus.ram,[this](unsigned count){advance_cycles(count);});
  if constexpr(O==Op::CLI || O==Op::SEI || O==Op::PLP) {
   // IRQ mask is sampled before these instructions change I.
   delayed_irq_mask_=old_irq_mask;
   delayed_irq_mask_valid_=true;
  }
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
