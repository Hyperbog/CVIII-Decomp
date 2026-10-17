#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void require(bool v,const char*msg){if(!v)throw std::runtime_error(msg);}
static void load_ram(Bus& b){
 b.whole_prg=true;
 for(unsigned i=0;i<256;++i)b.ram[0x200+i]=uint8_t(i^0x5au);
}
static void no_alignment_and_oam_wrap(){
 auto b=std::make_unique<Bus>();load_ram(*b);
 Cpu c(*b);c.enable_ram_oam_dma(0); // CPU cycle even = get.
 c.oam_dma.set_oam_address_for_test(0xfe);
 c.a=0x02;c.exec<Op::STA,Mode::abs>(0x4014,0x8003);
 require(c.cycles==517 && c.oam_dma.last_stall_cycles()==513,
         "4-cycle STA then no-alignment 513-cycle DMA");
 require(c.ppu_clock.cpu_cycles()==c.cycles &&
         c.ppu_clock.ppu_dots()==c.cycles*3,"PPU clock advances during halt");
 require(c.oam_dma.completed_transfers()==1 && !c.oam_dma.pending(),
         "one DMA transfer");
 require(c.oam_dma.oam_address()==0xfe,"OAMADDR wraps after 256 bytes");
 require(c.oam_dma.oam()[0xfe]==0x5a &&
         c.oam_dma.oam()[0xff]==0x5b &&
         c.oam_dma.oam()[0x00]==0x58,"OAM byte order and wrap");
 const auto& reads=c.oam_dma.last_bytes();
 require(reads.size()==256 &&
         reads[0].source==0x200 && reads[0].destination==0xfe &&
         reads[0].get_cycle==6 && reads[0].put_cycle==7 &&
         reads[255].get_cycle==516 && reads[255].put_cycle==517,
         "DMA get/put CPU-cycle timestamps");
 require(b->io_writes.size()==1 && b->io_writes[0].first==0x4014 &&
         b->io_writes[0].second==2,"legacy I/O write event preserved");
}
static void alignment_and_ram_mirror(){
 auto b=std::make_unique<Bus>();load_ram(*b);
 Cpu c(*b);c.enable_ram_oam_dma(1); // CPU cycle odd = get.
 c.a=0x0a;c.exec<Op::STA,Mode::abs>(0x4014,0x8103);
 require(c.cycles==518 && c.oam_dma.last_stall_cycles()==514,
         "odd get/put alignment adds one stall cycle");
 require(c.oam_dma.last_bytes().front().get_cycle==7 &&
         c.oam_dma.last_bytes().front().put_cycle==8 &&
         c.oam_dma.last_bytes().back().put_cycle==518,
         "514-cycle DMA timestamps");
 require(c.oam_dma.oam()[0]==0x5a && c.oam_dma.oam()[255]==0xa5,
         "mirrored internal RAM source page");
}
static void irq_and_nmi_continue_clocking(){
 auto b=std::make_unique<Bus>();load_ram(*b);
 b->prg[31*8192+(0xfffa-0xe000)]=0x57;
 b->prg[31*8192+(0xfffb-0xe000)]=0xe0;
 Cpu c(*b);c.enable_ram_oam_dma(0);
 c.enable_vrc6_irq();c.enable_boundary_interrupts();
 c.a=0xff;c.exec<Op::STA,Mode::abs>(0xf000,0x9003);
 c.a=0x03;c.exec<Op::STA,Mode::abs>(0xf001,0x9006);
 require(c.vrc6_irq.enabled() && !c.vrc6_irq.irq_line(),
         "scanline VRC6 counter enabled");
 c.p=0x20;
 c.ppu_clock.write_control(0x80);
 // Advance only the PPU epoch; CPU cycles remain separately clocked.
 c.ppu_clock.advance_ppu_dots(241ull*341u-300u);
 c.a=0x02;c.exec<Op::STA,Mode::abs>(0x4014,0x9009);
 require(c.vrc6_irq.cpu_cycles()==c.cycles &&
         c.vrc6_irq.irq_line() && c.vrc6_irq.irq_events()>=1,
         "VRC6 IRQ continues across OAM DMA halt");
 require(c.ppu_clock.nmi_pending(),"NMI edge latched while CPU DMA-halted");
 require(c.service_interrupt_boundary()==InterruptKind::nmi &&
         c.pc==0xe057,"NMI priority after CPU resumes");
 require(c.vrc6_irq.irq_line(),"NMI does not acknowledge mapper IRQ");
}
static void reject_unsupported_dma_without_leaking_bus_permission(){
 auto b=std::make_unique<Bus>();load_ram(*b);
 Cpu c(*b);c.enable_ram_oam_dma(0);
 bool failed=false;
 try{b->write(0x4014,2);}
 catch(const std::runtime_error&){failed=true;}
 require(failed,"unpositioned $4014 write must fail");
 c.a=0x20;
 failed=false;
 try{c.exec<Op::STA,Mode::abs>(0x4014,0x8003);}
 catch(const std::runtime_error&){failed=true;}
 require(failed && !c.oam_dma.pending() && c.oam_dma.completed_transfers()==0,
         "unsupported page must reject before DMA side effects");
 failed=false;
 try{b->write(0x4014,2);}
 catch(const std::runtime_error&){failed=true;}
 require(failed,"rejected $4014 must not leave bus permission armed");
 c.a=0x02;
 failed=false;
 try{c.exec<Op::STA,Mode::indy>(0x10,0x8005);}
 catch(const std::runtime_error&){failed=true;}
 require(!failed,"ordinary indirect RAM stores remain supported");
 b->ram[0x10]=0x14;b->ram[0x11]=0x40;
 failed=false;
 try{c.exec<Op::STA,Mode::indy>(0x10,0x8007);}
 catch(const std::runtime_error&){failed=true;}
 require(failed,"indirect $4014 without modeled phase must fail closed");
}
static void legacy_driver_isolation(){
 auto b=std::make_unique<Bus>();load_ram(*b);
 Cpu c(*b);c.a=2;
 c.exec<Op::STA,Mode::abs>(0x4014,0x8003);
 require(c.cycles==4 && c.oam_dma.completed_transfers()==0 &&
         b->io_writes.size()==1,"disabled DMA must preserve scripted policy");
}
int main(){
 try{
  no_alignment_and_oam_wrap();
  alignment_and_ram_mirror();
  irq_and_nmi_continue_clocking();
  reject_unsupported_dma_without_leaking_bus_permission();
  legacy_driver_isolation();
  std::cout<<"PASS JP0554 RAM OAM DMA 513/514 cycles, mirrored bytes, IRQ/NMI, fail closed\n";
 }catch(const std::exception&e){std::cerr<<"FAIL JP0554 phase 4D "<<e.what()<<'\n';return 1;}
}
