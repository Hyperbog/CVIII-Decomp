/* JP 0563: execute original raw0A $801E native-C-generated selector.
 * Input: exact user-owned original Japanese iNES ROM + selector CSV.
 * This tool does not interpret unknown hardware or distribute ROM bytes.
 */
#include "cpu.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
JpStep jp_bank0a_compiled_step(JpCpu *);
static uint8_t prg[262144];
int main(int argc,char **argv){
 if(argc!=3){fprintf(stderr,"usage: c6502_raw0a JP.nes selectors.csv\n");return 2;}
 FILE *rom=fopen(argv[1],"rb");
 if(!rom){perror("ROM");return 2;}
 if(fseek(rom,16,SEEK_SET)!=0 ||
    fread(prg,1,sizeof(prg),rom)!=sizeof(prg)){
  fprintf(stderr,"missing original PRG image\n");fclose(rom);return 2;
 }
 fclose(rom);
 FILE *in=fopen(argv[2],"r");
 if(!in){perror("selectors");return 2;}
 unsigned count=0;char line[128];
 while(fgets(line,sizeof(line),in)){
  unsigned x,y,z;char extra;
  if(sscanf(line,"%u,%u,%u %c",&x,&y,&z,&extra)!=3 ||
     x>14 || y>31 || z>15){
   fprintf(stderr,"invalid selector case: %s",line);
   fclose(in);return 2;
  }
  JpBus bus;JpCpu cpu;
  memset(&bus,0,sizeof(bus));
  bus.prg=prg;bus.prg_size=sizeof(prg);bus.bank=10;
  jp_cpu_init(&cpu,&bus);
  cpu.pc=0x801e;cpu.allow_candidate_static=1;
  bus.ram[0x34]=(uint8_t)x;bus.ram[0x35]=(uint8_t)y;bus.ram[0x36]=(uint8_t)z;
  /* Simulate JSR caller return address $8FFF in two stack bytes. */
  bus.ram[0x1fd]=0x8f;bus.ram[0x1fc]=0xff;cpu.s=0xfb;
  unsigned n=0;
  while(cpu.pc!=0x9000 && n++<100){
   const JpStep result=jp_cpu_step(&cpu,jp_bank0a_compiled_step);
   if(result!=JP_STEP_EXECUTED){
    fprintf(stderr,"native-C raw0A failed at $%04X, result %d\n",cpu.pc,result);
    fclose(in);return 3;
   }
  }
  if(cpu.pc!=0x9000 || cpu.s!=0xfd || cpu.interpreted_instructions!=0){
   fprintf(stderr,"raw0A C routine did not return as fully compiled source\n");
   fclose(in);return 3;
  }
  const unsigned stage=(unsigned)bus.ram[6] | ((unsigned)bus.ram[7]<<8);
  const unsigned mid=(unsigned)bus.ram[4] | ((unsigned)bus.ram[5]<<8);
  const unsigned leaf=(unsigned)bus.ram[0x95] | ((unsigned)bus.ram[0x96]<<8);
  printf("%u,%u,%u,%u,%u,%u\n",x,y,z,stage,mid,leaf);
  ++count;
 }
 fclose(in);
 if(count==0){fprintf(stderr,"no selector cases\n");return 3;}
 return 0;
}
