// ROM-free 0554 phase 3: direct $2000/$2001/$2002 final-cycle bus integration.
#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void require(bool ok,const char* what) {
 if(!ok)throw std::runtime_error(what);
}
static void verify_direct_access() {
 auto b=std::make_unique<Bus>();
 b->whole_prg=true;
 Cpu c(*b); c.enable_timed_ppu_registers();
 // Reaching the dot-1 VBlank boundary on the LAST CPU-cycle access.
 c.ppu_clock.advance_ppu_dots(241ull*341u-8u);
 c.exec<Op::LDA,Mode::abs>(0x2002,0x8003);
 require(c.a==0 && c.ppu_clock.vblank(),"read must precede start-of-dot-1 VBlank");
 require(c.ppu_io.events().size()==1,"first event logged");
 const auto& first=c.ppu_io.events().front();
 require(first.cpu_cycle==4 && first.ppu_dot==241ull*341u+1u,"LDA absolute final cycle timestamp");
 require(first.register_address==0x2002 && !first.is_write,"status event metadata");
 c.exec<Op::LDA,Mode::abs>(0x2002,0x8006);
 require(c.a==0x80 && !c.ppu_clock.vblank(),"read must see and clear VBlank");
 require(c.cycles==8 && c.ppu_clock.cpu_cycles()==8,"two LDA abs use 8 cycles");
 // $2008 / $2009 are CPU-side mirrors of PPUCTRL and PPUMASK.
 c.a=0x08;
 c.exec<Op::STA,Mode::abs>(0x2009,0x8009);
 require(c.ppu_io.events().back().register_address==0x2001,"mirrored PPUMASK");
 c.a=0x80;
 c.exec<Op::STA,Mode::abs>(0x2008,0x800c);
 require(!c.ppu_clock.nmi_pending(),"no NMI when VBlank already cleared");
 c.ppu_clock.advance_ppu_dots(341ull*262u);
 require(c.ppu_clock.vblank() && c.ppu_clock.nmi_pending(),"new frame NMI edge");
 require(c.ppu_clock.take_nmi(),"NMI edge latched");
 // An indexed absolute read crossing a CPU page incurs the extra cycle.
 c.x=3;
 c.exec<Op::LDA,Mode::absx>(0x1fff,0x800f); // $2002.
 require(c.a==0x80 && c.cycles==21,"indexed read extra page-cross cycle");
 require(c.ppu_io.events().back().cpu_cycle==21,"indexed status read timestamp");
 require(!c.ppu_clock.vblank(),"indexed status read clears VBlank");
 // Indexed PPU writes have fixed 5 CPU cycles, without a page penalty.
 c.a=0x80;c.x=1;
 c.exec<Op::STA,Mode::absx>(0x1fff,0x8012); // $2000.
 require(c.cycles==26 && c.ppu_io.events().back().cpu_cycle==26,
         "indexed PPU write fixed five cycles");
 require(b->io_writes.size()==3,"original-address I/O write log");
 require(b->io_writes.back().first==0x2000,"actual CPU address preserved");
}
static void verify_fail_closed() {
 auto b=std::make_unique<Bus>();b->whole_prg=true;Cpu c(*b);
 // Default behavior remains the scripted 0553 status-poll model.
 c.exec<Op::LDA,Mode::abs>(0x2002,0x8003);
 require(c.a==0 && b->status_polls==1 && c.ppu_io.events().empty(),
         "0553 legacy mode changed");
 c.enable_timed_ppu_registers();
 bool rejected=false;
 try { (void)b->read(0x2002); } catch(const std::runtime_error&) {rejected=true;}
 require(rejected,"unpositioned access must be rejected");
 rejected=false;
 try {c.exec<Op::LDA,Mode::abs>(0x2007,0x8006);}
 catch(const std::runtime_error&) {rejected=true;}
 require(rejected,"unmodeled $2007 must not be fabricated");
 rejected=false;
 try {c.exec<Op::LDA,Mode::indy>(0x10,0x8008);}
 catch(const std::runtime_error&) {rejected=true;}
 // Indirect zero-page $10 defaults to $0000: this is ordinary RAM.
 require(!rejected,"ordinary indirect RAM access must remain valid");
 b->ram[0x10]=0x02;b->ram[0x11]=0x20;
 rejected=false;
 try {c.exec<Op::LDA,Mode::indy>(0x10,0x800a);}
 catch(const std::runtime_error&) {rejected=true;}
 require(rejected,"indirect-to-PPU access without micro-cycle model must fail");
}
int main(){
 try{
  verify_direct_access();
  verify_fail_closed();
  std::cout<<"PASS JP0554 timed PPU final-cycle read/write, mirroring, parity isolation and fail-closed dependencies\n";
 }catch(const std::exception&e){
  std::cerr<<"FAIL JP0554 phase 3: "<<e.what()<<'\n';return 1;
 }
}
