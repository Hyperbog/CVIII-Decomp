#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void check(bool ok,const char* reason){if(!ok)throw std::runtime_error(reason);}
static void check_cycles(const Cpu& cpu,uint64_t expected,const char* where){
 check(cpu.cycles==expected,where);
 check(cpu.ppu_clock.cpu_cycles()==expected,"PPU clock CPU cycles differ");
 check(cpu.ppu_clock.ppu_dots()==expected*3,"3:1 CPU-to-PPU timing drift");
}
int main(){
 try {
  auto b=std::make_unique<Bus>(); Cpu c(*b);
  c.exec<Op::LDA,Mode::imm>(0x42,0x8002);
  check(c.a==0x42 && c.pc==0x8002,"immediate load");
  check_cycles(c,2,"LDA immediate base 2");
  c.x=1; b->ram[0x100]=0x63;
  c.exec<Op::LDA,Mode::absx>(0x00ff,0x8005);
  check(c.a==0x63,"indexed read crossed target");
  check_cycles(c,7,"indexed read page crossing +1");
  b->ram[0x101]=0x3e;
  c.exec<Op::LDA,Mode::absx>(0x0100,0x8008);
  check(c.a==0x3e,"indexed read no-cross target");
  check_cycles(c,11,"indexed read no crossing +0");
  c.a=0x71;
  c.exec<Op::STA,Mode::absx>(0x00ff,0x800b);
  check(b->ram[0x100]==0x71,"indexed store target");
  check_cycles(c,16,"indexed store fixed 5 cycles");
  c.p=0x20; // BNE taken; next=80FE, target=8102 -> page-cross.
  c.exec<Op::BNE,Mode::rel>(0x8102,0x80fe);
  check(c.pc==0x8102,"taken branch PC");
  check_cycles(c,20,"branch taken page crossing +2");
  c.p=0x22; // BNE not taken.
  c.exec<Op::BNE,Mode::rel>(0x8010,0x8104);
  check(c.pc==0x8104,"untaken branch PC");
  check_cycles(c,22,"branch not taken base 2");
  c.p=0x20;
  c.exec<Op::BNE,Mode::rel>(0x8110,0x8106);
  check_cycles(c,25,"taken branch same page +1");
  b->ram[0x20]=0xff;b->ram[0x21]=0x01;b->ram[0x200]=0x84;c.y=1;
  c.exec<Op::LDA,Mode::indy>(0x20,0x8112);
  check(c.a==0x84,"indirect-indexed read target");
  check_cycles(c,31,"indirect-indexed crossed read +1");
  c.exec<Op::STA,Mode::indy>(0x20,0x8114);
  check_cycles(c,37,"indirect-indexed store fixed 6");
  c.x=1; b->ram[0x200]=0x1f;
  c.exec<Op::INC,Mode::absx>(0x01ff,0x8117);
  check(b->ram[0x200]==0x20,"RMW indexed absolute");
  check_cycles(c,44,"RMW indexed absolute fixed 7");
  c.exec<Op::JSR,Mode::abs>(0x9000,0x811a);
  check(c.pc==0x9000,"JSR jump");
  check_cycles(c,50,"JSR six cycles");
  c.exec<Op::RTS,Mode::imp>(0,0x9001);
  check(c.pc==0x811a,"RTS return");
  check_cycles(c,56,"RTS six cycles");
  b->whole_prg=true;
  b->prg[31*8192+(0xfffa-0xe000)]=0x57;
  b->prg[31*8192+(0xfffb-0xe000)]=0xe0;
  c.pc=0x811a;c.nmi();
  check(c.pc==0xe057,"NMI vector");
  check_cycles(c,63,"NMI entry overhead seven cycles");
  c.exec<Op::RTI,Mode::imp>(0,0xe05a);
  check(c.pc==0x811a,"NMI return PC");
  check_cycles(c,69,"RTI six cycles");
  std::cout<<"PASS JP0554 official 6502 base, branch, indexed, stack, NMI cycles and 3:1 PPU ticks\n";
 }catch(const std::exception&e){std::cerr<<"FAIL JP0554 "<<e.what()<<'\n';return 1;}
}
