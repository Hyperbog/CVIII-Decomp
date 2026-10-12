#include "cpu.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"C11 test failed: %s at %d\n",#x,__LINE__);return 1;}}while(0)
static JpStep example_static(JpCpu *c){
 switch(c->pc) {
 case 0x8000: return jp_cpu_exec(c,0xa9,0x0005,0x8002); /* LDA #5 */
 case 0x8002: return jp_cpu_exec(c,0x85,0x0010,0x8004); /* STA $10 */
 case 0xe000: return jp_cpu_exec(c,0xa9,0x007f,0xe002); /* fixed31 LDA #$7F */
 case 0x8004:
  if(!c->allow_candidate_static)return JP_STEP_CANDIDATE;
  return jp_cpu_exec(c,0xa2,0x0009,0x8006); /* LDX #9 */
 default:return JP_STEP_UNRESOLVED;
 }
}
int main(void){
 static uint8_t prg[262144];
 JpBus bus;JpCpu c;uint8_t v=0;
 memset(&bus,0,sizeof(bus));bus.prg=prg;bus.prg_size=sizeof(prg);bus.bank=10;
 jp_cpu_init(&c,&bus);c.pc=0x8000;
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_EXECUTED&&c.a==5);
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_EXECUTED&&bus.ram[0x10]==5);
 CHECK(c.compiled_instructions==2);
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_CANDIDATE);
 CHECK(c.pc==0x8004 && c.interpreted_instructions==0);
 /* Runtime reachability, not static certification, permits fallback execution. */
 prg[10*16384+4]=0xa2;prg[10*16384+5]=9;
 c.allow_fallback=1;
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_EXECUTED&&c.x==9);
 CHECK(c.interpreted_instructions==1 && c.compiled_instructions==2);
 CHECK(c.pc==0x8006);
 prg[10*16384+6]=0xe8; /* INX interpreted */
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_EXECUTED&&c.x==10);
 c.pc=0xe000;
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_EXECUTED&&c.a==0x7f &&
       c.compiled_instructions==3);
 CHECK(jp_bus_write(&bus,0x8000,14)==JP_STEP_EXECUTED&&bus.bank==14);
 CHECK(jp_bus_read(&bus,0x8000,&v)==JP_STEP_EXECUTED);
 CHECK(jp_cpu_step(&c,example_static)==JP_STEP_UNSUPPORTED);
 CHECK(jp_bus_read(&bus,0x2002,&v)==JP_STEP_UNSUPPORTED);
 CHECK(jp_bus_write(&bus,0x2000,0x80)==JP_STEP_UNSUPPORTED);
 CHECK(jp_bus_write(&bus,0x8000,16)==JP_STEP_UNSUPPORTED);
 CHECK(jp_bus_write(&bus,0x1fff,0xab)==JP_STEP_EXECUTED && bus.ram[0x7ff]==0xab);
 CHECK(jp_bus_read(&bus,0x07ff,&v)==JP_STEP_EXECUTED && v==0xab);
 /* Verify interpreter correctly follows branch, JSR, RTS, and stack. */
 bus.bank=10;c.pc=0x8010;c.p=0x20;c.s=0xfd;
 const unsigned off=10*16384;
 prg[off+0x10]=0xa9;prg[off+0x11]=0x00; /* LDA #0 -> Z */
 prg[off+0x12]=0xf0;prg[off+0x13]=0x02; /* BEQ $8016 */
 prg[off+0x16]=0x20;prg[off+0x17]=0x20;prg[off+0x18]=0x80;
 prg[off+0x20]=0xe8;prg[off+0x21]=0x60; /* INX; RTS */
 CHECK(jp_cpu_interpret_one(&c)==JP_STEP_EXECUTED&&c.pc==0x8012&&(c.p&2));
 CHECK(jp_cpu_interpret_one(&c)==JP_STEP_EXECUTED&&c.pc==0x8016);
 CHECK(jp_cpu_interpret_one(&c)==JP_STEP_EXECUTED&&c.pc==0x8020&&c.s==0xfb);
 CHECK(jp_cpu_interpret_one(&c)==JP_STEP_EXECUTED&&c.pc==0x8021&&c.x==11);
 CHECK(jp_cpu_interpret_one(&c)==JP_STEP_EXECUTED&&c.pc==0x8019&&c.s==0xfd);
 c.pc=0x8080;prg[off+0x80]=0x02; /* unofficial opcode */
 CHECK(jp_cpu_interpret_one(&c)==JP_STEP_UNSUPPORTED);
 printf("PASS JP0562 C11 CPU compiled dispatch, runtime fallback, mapper and fail-closed I/O\n");
 return 0;
}
