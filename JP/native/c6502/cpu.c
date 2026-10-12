/* JP C11 2A03 semantics, exact VRC6a PRG-ROM addressing and fallback.
 * $8000-$BFFF selects 16KiB, $C000-$DFFF independently selects 8KiB,
 * $E000-$FFFF is the physical last 8KiB PRG bank.
 * Other mapper, PPU, APU, DMA and cycle behavior still fail closed.
 */
#include "cpu.h"
#include <string.h>
enum { CF=1, ZF=2, IF=4, DF=8, BF=16, UF=32, VF=64, NF=128 };
void jp_cpu_init(JpCpu *c,JpBus *b) {
 memset(c,0,sizeof(*c));c->bus=b;c->s=0xfd;c->p=IF|UF;
 c->fault=JP_STEP_EXECUTED;
}
JpStep jp_bus_physical_offset(const JpBus *b,uint16_t at,unsigned *physical) {
 if(!b || !physical || at<0x8000 || !b->prg || b->prg_size!=262144)
  return JP_STEP_UNSUPPORTED;
 if(at<0xc000) {
  if(b->bank>=16)return JP_STEP_UNSUPPORTED;
  *physical=(unsigned)b->bank*16384u+(unsigned)(at-0x8000u);
 } else if(at<0xe000) {
  if(b->bank8>=32)return JP_STEP_UNSUPPORTED;
  *physical=(unsigned)b->bank8*8192u+(unsigned)(at-0xc000u);
 } else *physical=31u*8192u+(unsigned)(at-0xe000u);
 return *physical<262144u?JP_STEP_EXECUTED:JP_STEP_UNSUPPORTED;
}
JpStep jp_bus_read(JpBus *b,uint16_t at,uint8_t *v) {
 unsigned physical;
 if(!b || !v)return JP_STEP_UNSUPPORTED;
 if(at<0x2000) {*v=b->ram[at&0x7ff];return JP_STEP_EXECUTED;}
 if(jp_bus_physical_offset(b,at,&physical)!=JP_STEP_EXECUTED)
  return JP_STEP_UNSUPPORTED;
 *v=b->prg[physical];
 return JP_STEP_EXECUTED;
}
JpStep jp_bus_write(JpBus *b,uint16_t at,uint8_t v) {
 if(!b)return JP_STEP_UNSUPPORTED;
 if(at<0x2000){b->ram[at&0x7ff]=v;return JP_STEP_EXECUTED;}
 /* VRC6a mirrors A2-A11 away; there are no PRG bus conflicts.
    Other VRC6 audio/CHR/WRAM/IRQ register writes remain unsupported. */
 switch(at&0xf003u) {
 case 0x8000:case 0x8001:case 0x8002:case 0x8003:
  b->bank=(uint8_t)(v&0x0fu);return JP_STEP_EXECUTED;
 case 0xc000:case 0xc001:case 0xc002:case 0xc003:
  b->bank8=(uint8_t)(v&0x1fu);return JP_STEP_EXECUTED;
 default:return JP_STEP_UNSUPPORTED;
 }
}
static void flag(JpCpu*c,unsigned mask,int yes) {
 c->p=(uint8_t)((yes?(c->p|mask):(c->p&~mask))|UF);
}
static void nz(JpCpu*c,uint8_t v){flag(c,ZF,v==0);flag(c,NF,(v&0x80)!=0);}
static int rd(JpCpu*c,uint16_t a,uint8_t*v) {
 JpStep s=jp_bus_read(c->bus,a,v);
 if(s!=JP_STEP_EXECUTED)c->fault=s;
 return s==JP_STEP_EXECUTED;
}
static int wr(JpCpu*c,uint16_t a,uint8_t v) {
 JpStep s=jp_bus_write(c->bus,a,v);
 if(s!=JP_STEP_EXECUTED)c->fault=s;
 return s==JP_STEP_EXECUTED;
}
static int zpword(JpCpu*c,uint8_t a,uint16_t*v) {
 uint8_t lo,hi;
 if(!rd(c,a,&lo)||!rd(c,(uint8_t)(a+1),&hi))return 0;
 *v=(uint16_t)(lo | ((uint16_t)hi<<8));return 1;
}
static int address(JpCpu*c,JpMode m,uint16_t arg,uint16_t*out) {
 uint16_t base;uint8_t lo,hi;
 switch(m) {
 case JP_MODE_ZP:*out=(uint8_t)arg;return 1;
 case JP_MODE_ZPX:*out=(uint8_t)(arg+c->x);return 1;
 case JP_MODE_ZPY:*out=(uint8_t)(arg+c->y);return 1;
 case JP_MODE_ABS:*out=arg;return 1;
 case JP_MODE_ABSX:*out=(uint16_t)(arg+c->x);return 1;
 case JP_MODE_ABSY:*out=(uint16_t)(arg+c->y);return 1;
 case JP_MODE_INDX:return zpword(c,(uint8_t)(arg+c->x),out);
 case JP_MODE_INDY:
  if(!zpword(c,(uint8_t)arg,&base))return 0;
  *out=(uint16_t)(base+c->y);return 1;
 case JP_MODE_IND:
  if(!rd(c,arg,&lo)||!rd(c,(uint16_t)((arg&0xff00u)|(uint8_t)(arg+1)),&hi))return 0;
  *out=(uint16_t)(lo|((uint16_t)hi<<8));return 1;
 default:c->fault=JP_STEP_UNSUPPORTED;return 0;
 }
}
static int value(JpCpu*c,JpMode m,uint16_t arg,uint8_t *v) {
 uint16_t a;
 if(m==JP_MODE_IMM){*v=(uint8_t)arg;return 1;}
 if(m==JP_MODE_ACC){*v=c->a;return 1;}
 return address(c,m,arg,&a)&&rd(c,a,v);
}
static int push(JpCpu*c,uint8_t v) {
 if(!wr(c,(uint16_t)(0x100u|c->s),v))return 0;
 --c->s;return 1;
}
static int pop(JpCpu*c,uint8_t*v){++c->s;return rd(c,(uint16_t)(0x100u|c->s),v);}
static void compare(JpCpu*c,uint8_t a,uint8_t b){
 flag(c,CF,a>=b);nz(c,(uint8_t)(a-b));
}
static void adc(JpCpu*c,uint8_t v){
 unsigned r=(unsigned)c->a+v+((c->p&CF)!=0);
 uint8_t a=c->a,b=(uint8_t)r;
 flag(c,CF,r>255);
 flag(c,VF,((~(a^v)&(a^b))&128u)!=0);
 c->a=b;nz(c,c->a); /* 2A03 arithmetic ignores decimal flag. */
}
JpStep jp_cpu_exec(JpCpu*c,uint8_t opcode,uint16_t arg,uint16_t next) {
 const JpDecoded d=jp_opcodes[opcode];
 uint16_t ea=0,ret;uint8_t v=0,lo=0,hi=0;
 int taken=0;
 if(!c || !c->bus || !d.size || d.op==JP_OP_INVALID)return JP_STEP_UNSUPPORTED;
 c->fault=JP_STEP_EXECUTED;
 c->pc=next;
 switch(d.op) {
 case JP_OP_LDA:case JP_OP_LDX:case JP_OP_LDY:
  if(!value(c,d.mode,arg,&v))break;
  if(d.op==JP_OP_LDA)c->a=v;
  else if(d.op==JP_OP_LDX)c->x=v;
  else c->y=v;
  nz(c,v);break;
 case JP_OP_STA:case JP_OP_STX:case JP_OP_STY:
  if(address(c,d.mode,arg,&ea))
   (void)wr(c,ea,d.op==JP_OP_STA?c->a:d.op==JP_OP_STX?c->x:c->y);
  break;
 case JP_OP_ADC:case JP_OP_SBC:
  if(value(c,d.mode,arg,&v))adc(c,d.op==JP_OP_SBC?(uint8_t)~v:v);
  break;
 case JP_OP_AND:case JP_OP_ORA:case JP_OP_EOR:
  if(!value(c,d.mode,arg,&v))break;
  c->a=d.op==JP_OP_AND?(uint8_t)(c->a&v):
        d.op==JP_OP_ORA?(uint8_t)(c->a|v):(uint8_t)(c->a^v);
  nz(c,c->a);break;
 case JP_OP_CMP:case JP_OP_CPX:case JP_OP_CPY:
  if(value(c,d.mode,arg,&v))
   compare(c,d.op==JP_OP_CMP?c->a:d.op==JP_OP_CPX?c->x:c->y,v);
  break;
 case JP_OP_BIT:
  if(value(c,d.mode,arg,&v)){
   flag(c,ZF,(c->a&v)==0);flag(c,VF,(v&VF)!=0);flag(c,NF,(v&NF)!=0);
  }break;
 case JP_OP_ASL:case JP_OP_LSR:case JP_OP_ROL:case JP_OP_ROR:
 case JP_OP_INC:case JP_OP_DEC:
  if(!value(c,d.mode,arg,&v))break;
  if(d.op==JP_OP_ASL){flag(c,CF,(v&128)!=0);v=(uint8_t)(v<<1);}
  else if(d.op==JP_OP_LSR){flag(c,CF,(v&1)!=0);v=(uint8_t)(v>>1);}
  else if(d.op==JP_OP_ROL){unsigned carry=(c->p&CF)!=0;flag(c,CF,(v&128)!=0);v=(uint8_t)((v<<1)|carry);}
  else if(d.op==JP_OP_ROR){unsigned carry=(c->p&CF)!=0;flag(c,CF,(v&1)!=0);v=(uint8_t)((v>>1)|(carry<<7));}
  else if(d.op==JP_OP_INC)v=(uint8_t)(v+1);
  else v=(uint8_t)(v-1);
  nz(c,v);
  if(d.mode==JP_MODE_ACC)c->a=v;
  else if(address(c,d.mode,arg,&ea))(void)wr(c,ea,v);
  break;
 case JP_OP_JMP:
  if(d.mode==JP_MODE_IND){if(address(c,d.mode,arg,&ea))c->pc=ea;}
  else c->pc=arg;
  break;
 case JP_OP_JSR:
  ret=(uint16_t)(next-1);
  if(push(c,(uint8_t)(ret>>8)) && push(c,(uint8_t)ret))c->pc=arg;
  break;
 case JP_OP_RTS:
  if(pop(c,&lo)&&pop(c,&hi))c->pc=(uint16_t)((lo|((uint16_t)hi<<8))+1);
  break;
 case JP_OP_RTI:
  if(pop(c,&v)&&pop(c,&lo)&&pop(c,&hi)){
   c->p=(uint8_t)(v|UF);
   c->pc=(uint16_t)(lo|((uint16_t)hi<<8));
  }break;
 case JP_OP_BRK:
  c->fault=JP_STEP_UNSUPPORTED;break;
 case JP_OP_PHA:(void)push(c,c->a);break;
 case JP_OP_PHP:(void)push(c,(uint8_t)(c->p|UF|BF));break;
 case JP_OP_PLA:if(pop(c,&v)){c->a=v;nz(c,v);}break;
 case JP_OP_PLP:if(pop(c,&v))c->p=(uint8_t)(v|UF);break;
 case JP_OP_BPL:taken=!(c->p&NF);break;
 case JP_OP_BMI:taken=!!(c->p&NF);break;
 case JP_OP_BVC:taken=!(c->p&VF);break;
 case JP_OP_BVS:taken=!!(c->p&VF);break;
 case JP_OP_BCC:taken=!(c->p&CF);break;
 case JP_OP_BCS:taken=!!(c->p&CF);break;
 case JP_OP_BNE:taken=!(c->p&ZF);break;
 case JP_OP_BEQ:taken=!!(c->p&ZF);break;
 case JP_OP_CLC:flag(c,CF,0);break;
 case JP_OP_SEC:flag(c,CF,1);break;
 case JP_OP_CLI:flag(c,IF,0);break;
 case JP_OP_SEI:flag(c,IF,1);break;
 case JP_OP_CLV:flag(c,VF,0);break;
 case JP_OP_CLD:flag(c,DF,0);break;
 case JP_OP_SED:flag(c,DF,1);break;
 case JP_OP_INX:++c->x;nz(c,c->x);break;
 case JP_OP_INY:++c->y;nz(c,c->y);break;
 case JP_OP_DEX:--c->x;nz(c,c->x);break;
 case JP_OP_DEY:--c->y;nz(c,c->y);break;
 case JP_OP_TAX:c->x=c->a;nz(c,c->x);break;
 case JP_OP_TAY:c->y=c->a;nz(c,c->y);break;
 case JP_OP_TXA:c->a=c->x;nz(c,c->a);break;
 case JP_OP_TYA:c->a=c->y;nz(c,c->a);break;
 case JP_OP_TSX:c->x=c->s;nz(c,c->x);break;
 case JP_OP_TXS:c->s=c->x;break;
 case JP_OP_NOP:break;
 default:c->fault=JP_STEP_UNSUPPORTED;break;
 }
 if(d.mode==JP_MODE_REL && taken)c->pc=arg;
 return c->fault;
}
JpStep jp_cpu_interpret_one(JpCpu*c){
 uint8_t opcode=0,lo=0,hi=0;uint16_t arg=0;
 if(jp_bus_read(c->bus,c->pc,&opcode)!=JP_STEP_EXECUTED)return JP_STEP_UNSUPPORTED;
 const JpDecoded d=jp_opcodes[opcode];
 if(!d.size)return JP_STEP_UNSUPPORTED;
 if(d.size>1 && jp_bus_read(c->bus,(uint16_t)(c->pc+1),&lo)!=JP_STEP_EXECUTED)
  return JP_STEP_UNSUPPORTED;
 if(d.size>2 && jp_bus_read(c->bus,(uint16_t)(c->pc+2),&hi)!=JP_STEP_EXECUTED)
  return JP_STEP_UNSUPPORTED;
 arg=(uint16_t)(lo|((uint16_t)hi<<8));
 const uint16_t next=(uint16_t)(c->pc+d.size);
 if(d.mode==JP_MODE_REL)arg=(uint16_t)(next+(int8_t)lo);
 JpStep result=jp_cpu_exec(c,opcode,arg,next);
 if(result==JP_STEP_EXECUTED)++c->interpreted_instructions;
 return result;
}
JpStep jp_cpu_step(JpCpu*c,JpCompiledStep compiled) {
 if(!c || !c->bus)return JP_STEP_UNSUPPORTED;
 JpStep result=JP_STEP_UNRESOLVED;
 if(compiled)result=compiled(c);
 if(result==JP_STEP_EXECUTED){++c->compiled_instructions;return result;}
 if(result==JP_STEP_UNSUPPORTED)return result;
 if(!c->allow_fallback)return result;
 return jp_cpu_interpret_one(c);
}
