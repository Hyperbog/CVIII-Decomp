/* JP 0565: pure-C native recompiled 2A03 bounded host.
 * The generated original-JP instruction switch is compiled into this executable
 * locally after ROM authentication. No game ROM is ever embedded or bundled.
 * This is NOT a full NES PPU/APU/VRC6 runtime or playable game yet.
 */
#include "cpu.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
JpStep jp_bank0a_compiled_step(JpCpu *);
JpStep jp_fixed_compiled_step(JpCpu *);
static uint8_t cartridge[393232];
static JpStep compiled(JpCpu *c){
 JpStep s=jp_fixed_compiled_step(c);
 return s!=JP_STEP_UNRESOLVED?s:jp_bank0a_compiled_step(c);
}
static uint32_t crc32_retail(const uint8_t *p,size_t n) {
 uint32_t crc=0xffffffffu;
 for(size_t i=0;i<n;++i){
  crc^=p[i];
  for(unsigned bit=0;bit<8;++bit)
   crc=(crc>>1)^((crc&1u)?0xedb88320u:0u);
 }
 return ~crc;
}
int main(int argc,char **argv){
 if(argc<2 || argc>6){
  fprintf(stderr,"usage: jp_c6502 ROM.nes [--steps N] [--fallback] [--test-media]\n");
  return 2;
 }
 const char *rompath=argv[1];unsigned limit=10000u;
 int fallback=0,test_media=0;
 for(int i=2;i<argc;++i) {
  if(strcmp(argv[i],"--fallback")==0)fallback=1;
  else if(strcmp(argv[i],"--test-media")==0)test_media=1;
  else if(strcmp(argv[i],"--steps")==0 && i+1<argc){
   char *end=NULL;
   const unsigned long n=strtoul(argv[++i],&end,10);
   if(!end || *end || !n || n>10000000ul){
    fprintf(stderr,"invalid bounded instruction count\n");return 2;
   }
   limit=(unsigned)n;
  }else{fprintf(stderr,"unknown argument: %s\n",argv[i]);return 2;}
 }
 FILE *f=fopen(rompath,"rb");
 if(!f){perror("original Japanese ROM");return 2;}
 const size_t count=fread(cartridge,1,sizeof(cartridge),f);
 const int trailing=fgetc(f);fclose(f);
 if(count!=sizeof(cartridge) || trailing!=EOF ||
    memcmp(cartridge,"NES\032",4)!=0){
  fprintf(stderr,"cartridge must be exactly the original 393232-byte iNES shape\n");
  return 2;
 }
 if(!test_media && crc32_retail(cartridge,sizeof(cartridge))!=0x2e93ce72u){
  fprintf(stderr,"cartridge CRC32 differs from authenticated original JP retail image\n");
  return 2;
 }
 JpBus bus;JpCpu cpu;
 memset(&bus,0,sizeof(bus));
 bus.prg=cartridge+16;bus.prg_size=262144;bus.bank=0;
 jp_cpu_init(&cpu,&bus);
 cpu.allow_fallback=fallback;
 uint8_t lo,hi;
 if(jp_bus_read(&bus,0xfffc,&lo)!=JP_STEP_EXECUTED ||
    jp_bus_read(&bus,0xfffd,&hi)!=JP_STEP_EXECUTED){
  fprintf(stderr,"reset vector inaccessible\n");return 3;
 }
 cpu.pc=(uint16_t)(lo|((uint16_t)hi<<8));
 unsigned instructions=0;
 for(;instructions<limit;++instructions){
  const JpStep step=jp_cpu_step(&cpu,compiled);
  if(step!=JP_STEP_EXECUTED){
   printf("STATUS=HALTED step=%u reason=%d pc=%04X bank=%u "
          "compiled=%llu interpreted=%llu\n",
          instructions,(int)step,cpu.pc,(unsigned)bus.bank,
          (unsigned long long)cpu.compiled_instructions,
          (unsigned long long)cpu.interpreted_instructions);
   return 3;  /* fail closed; not a pretend gameplay frame. */
  }
 }
 printf("STATUS=BOUNDED step=%u pc=%04X bank=%u "
        "A=%02X X=%02X Y=%02X S=%02X P=%02X "
        "compiled=%llu interpreted=%llu ram10=%02X\n",
        instructions,cpu.pc,(unsigned)bus.bank,cpu.a,cpu.x,cpu.y,cpu.s,cpu.p,
        (unsigned long long)cpu.compiled_instructions,
        (unsigned long long)cpu.interpreted_instructions,bus.ram[0x10]);
 return 0;
}
