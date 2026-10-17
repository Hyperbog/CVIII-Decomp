#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void ok(bool yes,const char* msg){if(!yes)throw std::runtime_error(msg);}
static void vectors(Bus& b){
 b.whole_prg=true;
 b.prg[31*8192+(0xfffe-0xe000)]=0x80;
 b.prg[31*8192+(0xffff-0xe000)]=0xe0;
 b.prg[31*8192+(0xfffa-0xe000)]=0x57;
 b.prg[31*8192+(0xfffb-0xe000)]=0xe0;
}
static void cycle_device_and_service(){
 auto b=std::make_unique<Bus>();vectors(*b);
 Cpu c(*b);c.p=0x20;c.pc=0x8000;c.enable_vrc6_irq();
 c.enable_boundary_interrupts();
 c.a=0xfe;
 c.exec<Op::STA,Mode::abs>(0xf000,0x8003);
 ok(c.vrc6_irq.latch()==0xfe && c.cycles==4 &&
    c.vrc6_irq.cpu_cycles()==4,"latch cycle accounting");
 c.a=0x06; // Mode M=cycle; E=1; ack enable A=0.
 c.exec<Op::STA,Mode::abs>(0xf001,0x8006);
 ok(c.cycles==8 && c.vrc6_irq.counter()==0xff &&
    !c.vrc6_irq.irq_line(),"last-cycle control register must tick once");
 c.exec<Op::NOP,Mode::imp>(0,0x8007);
 ok(c.cycles==10 && c.vrc6_irq.irq_line(),"IRQ overflow from CPU cycles");
 ok(c.service_interrupt_boundary()==InterruptKind::irq,
    "VRC6 must feed IRQ boundary arbiter");
 ok(c.pc==0xe080 && c.s==0xfa && c.cycles==17 &&
    c.vrc6_irq.cpu_cycles()==17,"IRQ vector, stack and seven device clocks");
 ok(c.service_interrupt_boundary()==InterruptKind::none,
    "handler must dispatch before next boundary service");
 c.a=0;
 c.exec<Op::STA,Mode::abs>(0xf002,0xe083);
 ok(!c.vrc6_irq.irq_line() && !c.vrc6_irq.enabled() &&
    c.vrc6_irq.cpu_cycles()==21,"ack on last cycle and A=0 disables");
 ok(b->io_writes.size()==3 && b->io_writes.back().first==0xf002,
    "original address and values retained for IRQ writes");
 c.exec<Op::RTI,Mode::imp>(0,0xe084);
 ok(c.pc==0x8007 && !c.flag(4),"RTI restores IRQ PC and I");
 ok(c.service_interrupt_boundary()==InterruptKind::none,"IRQ line cleared");
}
static void absolute_indexed_and_isolation(){
 auto b=std::make_unique<Bus>();vectors(*b);
 Cpu c(*b);
 c.enable_vrc6_irq();
 c.x=1;c.a=0xff;
 c.exec<Op::STA,Mode::absx>(0xefff,0x8103); // $F000 write, crosses CPU page
 ok(c.cycles==5 && c.vrc6_irq.latch()==0xff,
    "indexed mapper STA fixed five cycles");
 bool rejected=false;
 try {b->write(0xf001,0x06);}
 catch(const std::runtime_error&){rejected=true;}
 ok(rejected,"unpositioned mapper IRQ register write must fail closed");
 b->ram[0x10]=0x01;b->ram[0x11]=0xf0;c.a=0x07;
 rejected=false;
 try {c.exec<Op::STA,Mode::indy>(0x10,0x8105);}
 catch(const std::runtime_error&){rejected=true;}
 ok(rejected,"indirect-to-IRQ write without bus schedule must fail");
 rejected=false;
 try {b->write(0xf001,0x07);}
 catch(const std::runtime_error&){rejected=true;}
 ok(rejected,"rejected indirect access must not retain write permission");
 c.enable_vrc6_irq(false);
 b->write(0xf001,0x07); // legacy 0553 bus policy, no IRQ device effect.
 ok(!c.vrc6_irq.enabled() && !c.vrc6_irq.irq_line(),
    "disabled IRQ opt-in must not change original bus policy");
 ok(b->io_writes.back().first==0xf001,"legacy original write trace");
}
static void nmi_priority(){
 auto b=std::make_unique<Bus>();vectors(*b);
 Cpu c(*b);c.p=0x20;c.enable_vrc6_irq();c.enable_boundary_interrupts();
 c.a=0xff;c.exec<Op::STA,Mode::abs>(0xf000,0x9003);
 c.a=0x06;c.exec<Op::STA,Mode::abs>(0xf001,0x9006);
 ok(c.vrc6_irq.irq_line(),"IRQ asserted on control last cycle");
 c.ppu_clock.write_control(0x80);
 c.ppu_clock.advance_ppu_dots(241ull*341+2);
 ok(c.service_interrupt_boundary()==InterruptKind::nmi &&
    c.pc==0xe057,"latched NMI takes priority over VRC6 IRQ");
 ok(c.vrc6_irq.irq_line(),"NMI must not spuriously acknowledge VRC6 IRQ");
}
int main(){
 try{
  cycle_device_and_service();
  absolute_indexed_and_isolation();
  nmi_priority();
  std::cout<<"PASS JP0554 VRC6 CPU clock, final-cycle mapper writes, NMI/IRQ integration\n";
 }catch(const std::exception&e){std::cerr<<"FAIL JP0554 phase 4C "<<e.what()<<'\n';return 1;}
}
