#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void check(bool p,const char*s){if(!p)throw std::runtime_error(s);}
static void load_and_reload_phases() {
 auto b=std::make_unique<Bus>();b->whole_prg=true;
 b->prg[30*8192]=0x5a;    // CPU $C000 physical fixed PRG bank 30.
 b->prg[31*8192]=0xa5;    // CPU $E000 fixed PRG bank 31.
 Cpu c(*b);c.enable_dmc_dma(1);
 c.dmc_dma.request(0xc000,DmcFetchKind::load);
 check(c.service_dmc_dma_at_read_boundary()==3,"get-parity aligned DMC takes three cycles");
 check(c.cycles==3 && c.ppu_clock.ppu_dots()==9,"PPU clocks during DMC halt");
 const auto first=c.dmc_dma.last_fetch();
 check(first.byte==0x5a && first.source==0xc000 &&
       first.get_cycle==3 && first.stall_cycles==3 &&
       first.kind==DmcFetchKind::load,"fixed PRG bank30 sample fetch");
 check(c.service_dmc_dma_at_read_boundary()==0,"no spurious second DMC");
 c.dmc_dma.request(0xe000,DmcFetchKind::reload);
 check(c.service_dmc_dma_at_read_boundary()==4,"misaligned DMC takes four cycles");
 const auto second=c.dmc_dma.last_fetch();
 check(second.source==0xe000 && second.byte==0xa5 &&
       second.kind==DmcFetchKind::reload &&
       second.get_cycle==7 && second.stall_cycles==4,
       "fixed PRG bank31 reload and get cycle");
 check(c.cycles==7 && c.dmc_dma.completed_fetches()==2,
       "two DMC fetches total seven CPU cycles");
}
static void mapper_irq_continues_during_dmc(){
 auto b=std::make_unique<Bus>();b->whole_prg=true;
 b->prg[30*8192]=0x11;
 b->prg[31*8192+(0xfffe-0xe000)]=0x80;
 b->prg[31*8192+(0xffff-0xe000)]=0xe0;
 Cpu c(*b);c.p=0x20;c.enable_dmc_dma(1);c.enable_vrc6_irq();
 c.enable_boundary_interrupts();
 c.vrc6_irq.write(0xf000,0xff);
 c.vrc6_irq.write(0xf001,0x07);
 c.dmc_dma.request(0xc000,DmcFetchKind::load);
 check(c.service_dmc_dma_at_read_boundary()==3 &&
       c.vrc6_irq.cpu_cycles()==3 && c.vrc6_irq.irq_line(),
       "VRC6 IRQ clocks during DMC stall");
 check(c.service_interrupt_boundary()==InterruptKind::irq &&
       c.pc==0xe080,"mapper IRQ serviced after DMC read boundary");
 check(c.vrc6_irq.cpu_cycles()==10,"IRQ entry also clocks VRC6");
}
static void strict_boundaries_and_no_overlap(){
 auto b=std::make_unique<Bus>();b->whole_prg=true;
 Cpu c(*b);
 bool reject=false;
 try{c.dmc_dma.request(0xc000,DmcFetchKind::load);}
 catch(const std::runtime_error&){reject=true;}
 check(reject,"DMC parity must be configured explicitly");
 c.enable_dmc_dma(0);
 reject=false;
 try{c.dmc_dma.request(0xbfff,DmcFetchKind::load);}
 catch(const std::runtime_error&){reject=true;}
 check(reject,"non-sample DMC address must reject");
 c.dmc_dma.request(0xc000,DmcFetchKind::reload);
 reject=false;
 try{c.dmc_dma.request(0xc001,DmcFetchKind::reload);}
 catch(const std::runtime_error&){reject=true;}
 check(reject,"two unserviced DMC requests must reject");
 reject=false;
 try{c.enable_ram_oam_dma(1);}
 catch(const std::runtime_error&){reject=true;}
 check(reject,"OAM/DMC phase mismatch must reject");
 c.enable_ram_oam_dma(0);
 c.oam_dma.request(0x02);
 reject=false;
 try{(void)c.service_dmc_dma_at_read_boundary();}
 catch(const std::runtime_error&){reject=true;}
 check(reject && c.cycles==0 && c.dmc_dma.pending() && c.oam_dma.pending(),
       "overlapping DMC/OAM must fail closed before clocks/reads");
 reject=false;
 c.a=0x02;
 try{c.exec<Op::STA,Mode::abs>(0x4014,0x8003);}
 catch(const std::runtime_error&){reject=true;}
 check(reject && c.oam_dma.completed_transfers()==0,
       "DMC/OAM overlap must not simulate incorrect 513-cycle path");
}
int main(){
 try{
  load_and_reload_phases();
  mapper_irq_continues_during_dmc();
  strict_boundaries_and_no_overlap();
  std::cout<<"PASS JP0554 bounded DMC sample 3/4 CPU stalls and IRQ/PPU ticking\n";
 }catch(const std::exception&e){
  std::cerr<<"FAIL JP0554 DMC DMA: "<<e.what()<<'\n';return 1;
 }
}
