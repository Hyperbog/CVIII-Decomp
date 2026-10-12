// Original ROM binaries are loaded at runtime and never embedded or distributed.
// Test CLI for native static-compiled bank0A instructions with a bounded FB96 helper.
#include "static_6502.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <cstring>
using namespace jpstatic;
static std::array<uint8_t,16384> load(const std::string& filename) {
 std::ifstream input(filename,std::ios::binary);
 if(!input)throw std::runtime_error("no bank image");
 std::array<uint8_t,16384> out{};
 input.read(reinterpret_cast<char*>(out.data()),out.size());
 if(input.gcount()!=static_cast<std::streamsize>(out.size())||input.peek()!=EOF)
  throw std::runtime_error("bank image must be exactly 16KiB");
 return out;
}
static void emit(const Cpu& cpu,const Bus& b,int idx,int seed){
 std::cout<<"{\"room\":"<<idx<<",\"seed\":"<<seed
 <<",\"x\":"<<int(cpu.x)<<",\"y\":"<<int(cpu.y)
 <<",\"a\":"<<int(cpu.a)<<",\"p\":"<<int(cpu.p)
 <<",\"sp\":"<<int(cpu.s)<<",\"mapper\":"<<int(b.bank)
 <<",\"mapped_reads\":[";
 for(size_t k=0;k<b.mapped_reads.size();++k){
  if(k)std::cout<<',';
  std::cout<<'['<<b.mapped_reads[k].first<<','<<int(b.mapped_reads[k].second)<<']';
 }
 std::cout<<"],\"mapper_writes\":"<<b.mapper_writes.size()<<",\"ram\":[";
 // Entire 2KiB RAM comparison proves the native compiled instructions' real writes,
 // including original 6502 stack operations and mapper helper side effects.
 for(size_t i=0;i<b.ram.size();++i){if(i)std::cout<<',';std::cout<<int(b.ram[i]);}
 std::cout<<"]}\n";
}
int main(int argc,char**argv){
 try{
  if(argc==2 && std::strcmp(argv[1],"--self-test")==0){
   Bus bus;Cpu cpu(bus);
   cpu.pc=0x8000;
   if(compiled_step(cpu)!=StepResult::unresolved)throw std::runtime_error("unknown address allowed");
   cpu.pc=0x8001;
   if(compiled_step(cpu)!=StepResult::candidate_blocked)throw std::runtime_error("candidate enabled by default");
   cpu.pc=0x801e;
   if(compiled_step(cpu,true)!=StepResult::executed)throw std::runtime_error("conditional candidate failed to dispatch");
   cpu.pc=0xb7f7;
   if(compiled_step(cpu)!=StepResult::executed)throw std::runtime_error("audited instruction not compiled");
   std::cout<<"PASS fail-closed unresolved/candidate gating and audited dispatch\n";
   return 0;
  }
  if(argc<3 || argc>4)throw std::runtime_error("usage: static0a BANK0A.bin BANK0E.bin [selector_cases.csv]");
  const auto a=load(argv[1]),e=load(argv[2]);
  if(argc==4){
   std::ifstream input(argv[3]);
   if(!input)throw std::runtime_error("no bounded selector-case file");
   int x,y,z;char comma1,comma2;
   int total=0;
   while(input>>x>>comma1>>y>>comma2>>z){
    if(comma1!=',' || comma2!=',' || x<0 || x>=15 || y<0 || y>=32 || z<0 || z>=16)
     throw std::runtime_error("invalid bounded selector triple");
    Bus b;b.bank0a=a;b.bank0e=e;Cpu cpu(b);
    cpu.pc=0x801e;cpu.s=0xfd;
    b.ram[0x34]=uint8_t(x);b.ram[0x35]=uint8_t(y);b.ram[0x36]=uint8_t(z);
    cpu.push(0x8f);cpu.push(0xff);
    bool ok=false;
    for(int n=0;n<100;++n){
      if(cpu.pc==0x9000){ok=true;break;}
      if(compiled_step(cpu,true)!=StepResult::executed)
        throw std::runtime_error("unknown conditional selector instruction");
    }
    if(!ok)throw std::runtime_error("conditional selector did not return");
    std::cout<<x<<','<<y<<','<<z<<','<<int(b.ram[6]|b.ram[7]<<8)
     <<','<<int(b.ram[4]|b.ram[5]<<8)<<','<<int(b.ram[0x95]|b.ram[0x96]<<8)<<'\n';
    ++total;
   }
   if(total==0 || !input.eof())throw std::runtime_error("empty or malformed selector inputs");
   return 0;
  }
  if(argc!=3)throw std::runtime_error("invalid CLI arguments");
  for(int idx=0;idx<5;++idx)for(int seed=0;seed<256;++seed){
   Bus b;b.bank0a=a;b.bank0e=e;b.ram[0x7a0]=uint8_t(idx);b.ram[0x23]=10;
   Cpu cpu(b);cpu.pc=0xb7f7;cpu.s=0xfd;
   cpu.a=uint8_t(seed*13);cpu.x=uint8_t(seed*5);cpu.y=uint8_t(seed*7);
   cpu.set(1,(seed&1)!=0);cpu.set(2,(seed&2)!=0);cpu.set(0x80,(seed&4)!=0);
   cpu.push(0x8f);cpu.push(0xff);
   bool returned=false;
   for(int steps=0;steps<20000;++steps){
    if(cpu.pc==0x9000){returned=true;break;}
    if(cpu.bounded_external())continue;
    auto result=compiled_step(cpu);
    if(result!=StepResult::executed){
     std::ostringstream os;os<<"original ROM entered uncompiled PC $"<<std::hex<<cpu.pc;
     throw std::runtime_error(os.str());
    }
   }
   if(!returned || b.bank!=10 || cpu.s!=0xfd)
     throw std::runtime_error("compiled room routine failed to return and restore mapper");
   emit(cpu,b,idx,seed);
  }
  return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 2;}
}
