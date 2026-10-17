// ROM-free interrupt priority and pre-dispatch scheduler contract.
#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void need(bool b,const char*why){if(!b)throw std::runtime_error(why);}
static void vectors(Bus& b) {
 b.whole_prg=true;
 b.prg[31*8192+(0xfffa-0xe000)]=0x57; // NMI = $E057
 b.prg[31*8192+(0xfffb-0xe000)]=0xe0;
 b.prg[31*8192+(0xfffe-0xe000)]=0x80; // IRQ = $E080
 b.prg[31*8192+(0xffff-0xe000)]=0xe0;
}
static void test_nmi_priority_and_opt_in() {
 auto b=std::make_unique<Bus>();vectors(*b);
 Cpu c(*b);c.pc=0x8123;c.s=0xfd;c.p=0x24;
 c.ppu_clock.write_control(0x80);
 c.ppu_clock.advance_ppu_dots(241ull*341+2);
 c.set_external_irq_line(true);
 need(c.service_interrupt_boundary()==InterruptKind::none,"default must remain inert");
 need(c.ppu_clock.nmi_pending(),"disabled scheduler lost pending edge");
 c.enable_boundary_interrupts();
 need(c.service_interrupt_boundary()==InterruptKind::nmi,"NMI must outrank masked IRQ");
 need(c.pc==0xe057 && c.s==0xfa,"NMI vector and stack");
 need(b->ram[0x1fd]==0x81 && b->ram[0x1fc]==0x23,"saved interrupted PC");
 need((b->ram[0x1fb]&0x34)==0x24 && (b->ram[0x1fb]&0x10)==0,
      "hardware status pushes bit 5, clears B");
 need(c.cycles==7 && c.ppu_clock.cpu_cycles()==7,"NMI seven-cycle entry");
 need(!c.ppu_clock.nmi_pending(),"NMI edge consumed once");
 need(c.service_interrupt_boundary()==InterruptKind::none,
      "handler must execute an instruction before further interrupts");
 c.exec<Op::RTI,Mode::imp>(0,0xe058);
 need(c.pc==0x8123 && c.s==0xfd && c.flag(4),"RTI restores old PC/flags");
 need(c.cycles==13,"RTI counts six cycles");
 // An asserted IRQ remains pending but is masked after RTI restores I=1.
 need(c.service_interrupt_boundary()==InterruptKind::none,"IRQ I mask ignored");
}
static void test_irq_level_and_cli_delay() {
 auto b=std::make_unique<Bus>();vectors(*b);
 Cpu c(*b);c.pc=0x9000;c.p=0x24;c.enable_boundary_interrupts();
 c.set_external_irq_line(true);
 need(c.service_interrupt_boundary()==InterruptKind::none,"IRQ must honor I");
 c.exec<Op::CLI,Mode::imp>(0,0x9001);
 need(!c.flag(4),"CLI did not clear I");
 need(c.service_interrupt_boundary()==InterruptKind::none,"CLI must delay IRQ one instruction");
 c.exec<Op::NOP,Mode::imp>(0,0x9002);
 need(c.service_interrupt_boundary()==InterruptKind::irq,"level IRQ not delivered");
 need(c.pc==0xe080 && c.s==0xfa && c.flag(4),"IRQ entry vector or flags");
 need((b->ram[0x1fb]&0x10)==0 && (b->ram[0x1fb]&0x20)!=0,
      "IRQ stack push break flag");
 need(c.cycles==11,"CLI+NOP+IRQ cycles");
 need(c.service_interrupt_boundary()==InterruptKind::none,"IRQ interrupt chain must delay");
 c.exec<Op::RTI,Mode::imp>(0,0xe081);
 need(!c.flag(4) && c.pc==0x9002,"IRQ RTI restores flags immediately");
 need(c.service_interrupt_boundary()==InterruptKind::irq,
      "RTI must immediately permit still-asserted IRQ");
 c.set_external_irq_line(false);
 c.exec<Op::RTI,Mode::imp>(0,0xe081);
 need(c.service_interrupt_boundary()==InterruptKind::none,"deasserted IRQ repeats");
}
static void test_sei_old_mask_and_unenabled_noop() {
 auto b=std::make_unique<Bus>();vectors(*b);
 Cpu c(*b);c.pc=0x8200;c.p=0x20;c.enable_boundary_interrupts();
 c.exec<Op::SEI,Mode::imp>(0,0x8201);
 c.set_external_irq_line(true);
 need(c.service_interrupt_boundary()==InterruptKind::irq,
      "SEI uses previous mask at immediately following IRQ sample");
 c.enable_boundary_interrupts(false);
 c.ppu_clock.write_control(0x80);
 c.ppu_clock.advance_ppu_dots(241ull*341+2);
 need(c.service_interrupt_boundary()==InterruptKind::none,"legacy mode changed");
 need(c.ppu_clock.nmi_pending(),"legacy mode consumed NMI");
}
int main(){
 try{
  test_nmi_priority_and_opt_in();
  test_irq_level_and_cli_delay();
  test_sei_old_mask_and_unenabled_noop();
  std::cout<<"PASS JP0554 pre-dispatch NMI/level IRQ priority, mask latency, vectors, opt-in\n";
 }catch(const std::exception&e){
  std::cerr<<"FAIL JP0554 interrupts: "<<e.what()<<'\n';return 1;
 }
}
