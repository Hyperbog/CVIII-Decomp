// Executes statically compiled physical-PRG instruction sites from reset to
// first NMI return under the exact, disclosed 0548 scripted hardware policy.
// Does NOT run a 6502 opcode-fetch interpreter or any ROM-derived .byte fallback.
#include "static_6502.hpp"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cstring>
using namespace jpstatic;
namespace jpstatic { StepResult compiled_boot_step(Cpu&); }
static uint64_t ramhash(const Bus& b) {
 uint64_t v=0xcbf29ce484222325ull;
 for(uint8_t byte:b.ram){v^=byte;v*=0x100000001b3ull;}
 return v;
}
static void emit_room(const Cpu& cpu,const Bus& bus,int idx,int seed) {
 std::cout<<"ROOM,"<<idx<<','<<seed<<','<<int(cpu.a)<<','<<int(cpu.x)<<','<<int(cpu.y)
          <<','<<int(cpu.p)<<','<<int(cpu.s)<<','<<int(bus.bank)<<','<<bus.mapper_writes.size()<<','<<bus.mapped_reads.size()<<',';
 for(auto entry:bus.mapped_reads)std::cout<<entry.first<<':'<<int(entry.second)<<';';
 std::cout<<',';
 for(uint8_t value:bus.ram)std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<unsigned(value);
 std::cout<<std::dec<<"\n";
}
static void check_room(const std::array<uint8_t,393232>& image) {
 for(int idx=0;idx<5;++idx)for(int seed=0;seed<256;++seed) {
  Bus b;b.whole_prg=true;b.bank=10;
  std::memcpy(b.prg.data(),image.data()+16,b.prg.size());
  b.ram[0x7a0]=uint8_t(idx);b.ram[0x23]=10;
  Cpu cpu(b);cpu.pc=0xb7f7;cpu.s=0xfd;
  cpu.a=uint8_t(seed*13);cpu.x=uint8_t(seed*5);cpu.y=uint8_t(seed*7);
  cpu.set(1,(seed&1)!=0);cpu.set(2,(seed&2)!=0);cpu.set(0x80,(seed&4)!=0);
  cpu.push(0x8f);cpu.push(0xff);
  bool returned=false;
  for(int steps=0;steps<20000;++steps) {
    if(cpu.pc==0x9000){returned=true;break;}
    if(cpu.bounded_external())continue;
    if(compiled_step(cpu)!=StepResult::executed)throw std::runtime_error("uncompiled native room PC "+std::to_string(cpu.pc));
  }
  if(!returned || cpu.s!=0xfd || b.bank!=10)throw std::runtime_error("native room return/mapper failure");
  emit_room(cpu,b,idx,seed);
 }
}
int main(int argc,char**argv){
 try {
  if(argc==2 && std::strcmp(argv[1],"--self-test")==0) {
   Bus b; b.whole_prg=true; Cpu c(b);c.pc=0x8000;
   if(compiled_boot_step(c)!=StepResult::unresolved)throw std::runtime_error("unknown boot code allowed");
   if(compiled_step(c)!=StepResult::unresolved)throw std::runtime_error("unknown room code allowed");
   std::cout<<"PASS native compiled-boot fail-closed dispatch\n";return 0;
  }
  bool room_mode=argc==3 && std::strcmp(argv[1],"--room")==0;
  if((!room_mode && argc!=2) || (room_mode && argc!=3))throw std::runtime_error("usage: native_boot [--room] original_jp_rom.nes");
  std::ifstream f(room_mode?argv[2]:argv[1],std::ios::binary);
  if(!f)throw std::runtime_error("original Japanese ROM file missing");
  std::array<uint8_t,393232> image{};
  f.read(reinterpret_cast<char*>(image.data()),image.size());
  if(f.gcount()!=static_cast<std::streamsize>(image.size()) || f.peek()!=EOF)throw std::runtime_error("ROM length mismatch");
  if(image[0]!='N'||image[1]!='E'||image[2]!='S'||image[3]!=0x1a)throw std::runtime_error("invalid iNES header");
  if(room_mode){check_room(image);return 0;}
  Bus bus;bus.whole_prg=true;bus.bank=0;
  std::memcpy(bus.prg.data(),image.data()+16,bus.prg.size());
  Cpu cpu(bus);cpu.p=0x24;cpu.s=0xfd;cpu.pc=bus.word(0xfffc);
  if(cpu.pc!=0xe00b)throw std::runtime_error("reset vector not at $E00B");
  bool injected=false,returned=false,prev_rti=false;
  unsigned steps=0;
  for(;steps<100000;){
   if(cpu.pc==0xe04b && !injected){cpu.nmi();injected=true;}
   if(cpu.pc==0xe04b && injected && prev_rti){returned=true;break;}
   std::cout<<steps<<','<<cpu.pc<<','<<unsigned(bus.bank)<<','<<unsigned(cpu.a)<<','<<unsigned(cpu.x)
            <<','<<unsigned(cpu.y)<<','<<unsigned(cpu.s)<<','<<unsigned(cpu.p)<<','<<bus.mapper_writes.size()
            <<','<<bus.status_polls<<','<<unsigned(injected)<<','<<ramhash(bus)<<'\n';
   // "prev_rti" is determined from the ORIGINAL opcode at the current PC,
   // not a fabricated signal from a translated high-level routine.
   bool rti=(bus.read(cpu.pc)==0x40);
   auto r=compiled_boot_step(cpu);
   if(r!=StepResult::executed)throw std::runtime_error("uncompiled physical instruction PC "+std::to_string(cpu.pc));
   prev_rti=rti;++steps;
  }
  if(!returned)throw std::runtime_error("original reset/NMI return not reached");
  std::cout<<"FINAL,"<<steps<<','<<cpu.pc<<','<<unsigned(bus.bank)<<','<<unsigned(cpu.a)<<','<<unsigned(cpu.x)
           <<','<<unsigned(cpu.y)<<','<<unsigned(cpu.s)<<','<<unsigned(cpu.p)<<','<<bus.mapper_writes.size()
           <<','<<bus.status_polls<<'\n';
  std::cout<<"IO,";
  for(auto [a,v]:bus.io_writes)std::cout<<a<<':'<<unsigned(v)<<';';
  std::cout<<"\n";
  std::cout<<"RAM,";
  for(uint8_t v:bus.ram)std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<unsigned(v);
  std::cout<<std::dec<<"\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 2;}
}
