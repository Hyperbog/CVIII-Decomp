/* JP0827: reentrant, restricted original 2A03/6502 execution context.
 * Executes REAL owner-authenticated raw PRG0B opcodes inside a PRIVATE
 * 2KiB RAM image. No reads/writes of the running NES machine, PPU,
 * sound bus, CPU stack, savestate, mapper or cartridge.
 *
 * Current proven execution whitelist: $B486-$B4D6 and $B525-$B53E.
 * E249/E75A/B47B/B525 continuation handlers beyond $B53C are
 * explicit stops. This is a real opcode interpreter for a BOUNDED
 * subset, not independent complete enemy AI or full offscreen combat.
 *
 * NES 2A03 uses BINARY ADC/SBC even when P.D is set. Unhandled opcodes,
 * all unapproved call destinations, out-of-ROM buses and deadlines
 * STOP closed. Bank0B must have original SHA checked by the caller.
 */
#ifndef CVIII_ACTOR_VM_0827_H
#define CVIII_ACTOR_VM_0827_H
#include <stdint.h>
#include <string.h>
enum {
 CVIII_VM_STOP_NONE_0827=0, CVIII_VM_STOP_RTS_0827=1,
 CVIII_VM_STOP_EXTERNAL_0827=2, CVIII_VM_STOP_BOUNDARY_0827=3,
 CVIII_VM_STOP_OPCODE_0827=4, CVIII_VM_STOP_BUS_0827=5,
 CVIII_VM_STOP_BUDGET_0827=6
};
enum {
 CVIII_VM_FLAG_C_0827=1, CVIII_VM_FLAG_Z_0827=2,
 CVIII_VM_FLAG_I_0827=4, CVIII_VM_FLAG_D_0827=8,
 CVIII_VM_FLAG_V_0827=64, CVIII_VM_FLAG_N_0827=128
};
typedef struct {
 uint8_t ram[2048];
 uint8_t a,x,y,p,sp,depth,stop_kind,last_opcode;
 uint16_t pc,stop_pc,external_target,entry_pc;
 uint32_t instructions,ram_writes;
} CviiiActorVM0827;
static inline int cviii_vm_allowed_0827(uint16_t pc){
 /* The ORIGINAL $FE51 per-actor movement JSR selects raw PRG0B
  * at $8000 and enters $8001. Only its $8001-$804A instructions
  * may execute here; other actor dispatches still stop closed. */
 return (pc>=0x8001u && pc<=0x804au) ||
        (pc>=0xb486u && pc<=0xb4d6u) ||
        (pc>=0xb525u && pc<=0xb53eu);
}
static inline void cviii_vm_zn_0827(CviiiActorVM0827 *v,uint8_t x){
 v->p=(uint8_t)((v->p&~(CVIII_VM_FLAG_Z_0827|
           CVIII_VM_FLAG_N_0827)) |
         (x==0u?CVIII_VM_FLAG_Z_0827:0u) |
         (x&0x80u));
}
static inline int cviii_vm_read_0827(
 const CviiiActorVM0827 *v,const uint8_t bank[16384],
 uint16_t address,uint8_t *out)
{
 if(!v || !out)return 0;
 if(address<0x2000u){*out=v->ram[address&0x7ffu];return 1;}
 if(address>=0x8000u && address<0xc000u && bank){
    *out=bank[address-0x8000u];return 1;
 }
 return 0;
}
static inline int cviii_vm_write_0827(
 CviiiActorVM0827 *v,uint16_t address,uint8_t value)
{
 if(!v || address>=0x2000u)return 0;
 v->ram[address&0x7ffu]=value;
 if(v->ram_writes!=UINT32_MAX)v->ram_writes++;
 return 1;
}
static inline int cviii_vm_fetch_0827(CviiiActorVM0827 *v,
 const uint8_t bank[16384],uint8_t *out)
{
 if(v->pc<0x8000u || v->pc>=0xc000u)return 0;
 *out=bank[v->pc-0x8000u];v->pc++;return 1;
}
static inline int cviii_vm_word_0827(CviiiActorVM0827 *v,
 const uint8_t bank[16384],uint16_t *out)
{
 uint8_t lo=0,hi=0;
 if(!cviii_vm_fetch_0827(v,bank,&lo) ||
    !cviii_vm_fetch_0827(v,bank,&hi))return 0;
 *out=(uint16_t)(lo | (uint16_t)hi<<8u);return 1;
}
static inline int cviii_vm_push_0827(CviiiActorVM0827 *v,uint8_t x){
 if(v->sp==0u)return 0;
 v->ram[0x100u+v->sp]=x;v->sp--;
 return 1;
}
static inline int cviii_vm_pop_0827(CviiiActorVM0827 *v,uint8_t *x){
 if(v->sp==0xffu)return 0;
 v->sp++;*x=v->ram[0x100u+v->sp];return 1;
}
static inline void cviii_vm_stop_0827(CviiiActorVM0827 *v,
 int status,uint16_t pc){
 v->stop_kind=(uint8_t)status;v->stop_pc=pc;
 v->pc=pc;
}
/* Original input registers of this known caller: X is actor index.
 * A,Y at $B486/$B525 are overwritten before being used by the
 * supported instructions, so private initial A,Y=0 is valid there. */
static inline int cviii_vm_init_0827(CviiiActorVM0827 *v,
 const uint8_t original_ram[2048],unsigned x,uint16_t entry)
{
 if(!v || !original_ram || x<1u || x>18u ||
    (entry!=0x8001u && entry!=0xb486u && entry!=0xb525u))return 0;
 memset(v,0,sizeof *v);
 memcpy(v->ram,original_ram,2048u);
 v->pc=entry;v->entry_pc=entry;v->x=(uint8_t)x;
 v->p=0x24u;v->sp=0xfdu;
 return 1;
}
static inline int cviii_vm_step_0827(
 CviiiActorVM0827 *v,const uint8_t bank[16384])
{
 uint8_t op=0,imm=0;
 uint16_t address=0;
 uint8_t n=0;
 if(!v || !bank || v->stop_kind)return 0;
 const uint16_t at=v->pc;
 if(!cviii_vm_allowed_0827(at)){
    cviii_vm_stop_0827(v,CVIII_VM_STOP_BOUNDARY_0827,at);
    return 0;
 }
 if(!cviii_vm_fetch_0827(v,bank,&op)){
    cviii_vm_stop_0827(v,CVIII_VM_STOP_BUS_0827,at);
    return 0;
 }
 v->last_opcode=op;
 switch(op){
  case 0xbdu: /* LDA absolute,X */
  case 0xbcu: /* LDY absolute,X */
  case 0x9du: /* STA absolute,X */
    if(!cviii_vm_word_0827(v,bank,&address))goto bus;
    address=(uint16_t)(address+v->x);
    if(op==0x9du){
      if(!cviii_vm_write_0827(v,address,v->a))goto bus;
    }else{
      if(!cviii_vm_read_0827(v,bank,address,&n))goto bus;
      if(op==0xbdu)v->a=n;else v->y=n;
      cviii_vm_zn_0827(v,n);
    }break;
  case 0x7du: /* ADC absolute,X (2A03 binary) */
    if(!cviii_vm_word_0827(v,bank,&address))goto bus;
    address=(uint16_t)(address+v->x);
    if(!cviii_vm_read_0827(v,bank,address,&n))goto bus;
    {
      const uint8_t old=v->a;
      const uint16_t sum=(uint16_t)old+(uint16_t)n+
                  (unsigned)((v->p&CVIII_VM_FLAG_C_0827)!=0u);
      v->a=(uint8_t)sum;
      v->p=(uint8_t)((v->p&~(CVIII_VM_FLAG_C_0827|
                     CVIII_VM_FLAG_V_0827)) |
                   (sum>255u?CVIII_VM_FLAG_C_0827:0u) |
                   ((~(old^n)&(old^v->a)&0x80u)?
                       CVIII_VM_FLAG_V_0827:0u));
      cviii_vm_zn_0827(v,v->a);
    }break;
  case 0xa0u: /* LDY immediate */
    if(!cviii_vm_fetch_0827(v,bank,&imm))goto bus;
    v->y=imm;cviii_vm_zn_0827(v,v->y);break;
  case 0x88u: /* DEY */
    v->y--;cviii_vm_zn_0827(v,v->y);break;
  case 0x84u: /* STY zero page */
    if(!cviii_vm_fetch_0827(v,bank,&imm) ||
       !cviii_vm_write_0827(v,imm,v->y))goto bus;
    break;
  case 0x05u: /* ORA zero page */
  case 0x65u: /* ADC zero page (2A03 binary) */
    if(!cviii_vm_fetch_0827(v,bank,&imm))goto bus;
    n=v->ram[imm];
    if(op==0x05u){v->a|=n;cviii_vm_zn_0827(v,v->a);}
    else{
       const uint8_t old=v->a;
       const uint16_t sum=(uint16_t)old+(uint16_t)n+
                 (unsigned)((v->p&CVIII_VM_FLAG_C_0827)!=0u);
       v->a=(uint8_t)sum;
       v->p=(uint8_t)((v->p&~(CVIII_VM_FLAG_C_0827|
                      CVIII_VM_FLAG_V_0827)) |
                    (sum>255u?CVIII_VM_FLAG_C_0827:0u) |
                    ((~(old^n)&(old^v->a)&0x80u)?
                      CVIII_VM_FLAG_V_0827:0u));
       cviii_vm_zn_0827(v,v->a);
    }break;
  case 0x85u: /* STA zero page */
    if(!cviii_vm_fetch_0827(v,bank,&imm) ||
       !cviii_vm_write_0827(v,imm,v->a))goto bus;
    break;
  case 0xa5u: /* LDA zero page */
    if(!cviii_vm_fetch_0827(v,bank,&imm))goto bus;
    v->a=v->ram[imm];cviii_vm_zn_0827(v,v->a);break;
  case 0xe5u: /* SBC zero page, 2A03 binary semantics */
    if(!cviii_vm_fetch_0827(v,bank,&imm))goto bus;
    n=v->ram[imm];
    {
      const uint8_t old=v->a;
      const uint16_t sum=(uint16_t)old+
            ((uint16_t)(n^0xffu))+
            (unsigned)((v->p&CVIII_VM_FLAG_C_0827)!=0u);
      v->a=(uint8_t)sum;
      v->p=(uint8_t)((v->p&~(CVIII_VM_FLAG_C_0827|
                   CVIII_VM_FLAG_V_0827)) |
                   (sum>255u?CVIII_VM_FLAG_C_0827:0u) |
                   (((old^v->a)&(old^n)&0x80u)?
                    CVIII_VM_FLAG_V_0827:0u));
      cviii_vm_zn_0827(v,v->a);
    }break;
  case 0x29u: /* AND immediate */
  case 0xa9u: /* LDA immediate */
  case 0xc9u: /* CMP immediate */
  case 0xc0u: /* CPY immediate */
    if(!cviii_vm_fetch_0827(v,bank,&imm))goto bus;
    if(op==0x29u){v->a&=imm;cviii_vm_zn_0827(v,v->a);}
    else if(op==0xa9u){v->a=imm;cviii_vm_zn_0827(v,v->a);}
    else {
      const unsigned value=op==0xc0u?v->y:v->a;
      const uint8_t sub=(uint8_t)(value-imm);
      v->p=(uint8_t)((v->p&~CVIII_VM_FLAG_C_0827) |
          (value>=imm?CVIII_VM_FLAG_C_0827:0u));
      cviii_vm_zn_0827(v,sub);
    }break;
  case 0x4au: /* LSR accumulator */
    v->p=(uint8_t)((v->p&~CVIII_VM_FLAG_C_0827)|
                    (v->a&1u));
    v->a=(uint8_t)(v->a>>1u);
    cviii_vm_zn_0827(v,v->a);
    break;
  case 0x38u: v->p|=CVIII_VM_FLAG_C_0827;break; /* SEC */
  case 0x18u: v->p&=(uint8_t)~CVIII_VM_FLAG_C_0827;break;
  case 0xf0u: /* BEQ */
  case 0xd0u: /* BNE */
  case 0x90u: /* BCC */
  case 0xb0u: /* BCS */
  case 0x30u: /* BMI */
  case 0x10u: /* BPL */
    if(!cviii_vm_fetch_0827(v,bank,&imm))goto bus;
    {
      const int yes=op==0xf0u ? !!(v->p&CVIII_VM_FLAG_Z_0827):
                    op==0xd0u ? !(v->p&CVIII_VM_FLAG_Z_0827):
                    op==0x90u ? !(v->p&CVIII_VM_FLAG_C_0827):
                    op==0xb0u ? !!(v->p&CVIII_VM_FLAG_C_0827):
                    op==0x30u ? !!(v->p&CVIII_VM_FLAG_N_0827):
                    !(v->p&CVIII_VM_FLAG_N_0827);
      if(yes)v->pc=(uint16_t)(v->pc+(int8_t)imm);
    }break;
  case 0x4cu: /* JMP absolute, still bound to the approved ROM set */
  case 0x20u: /* JSR private stack if callee is in approved source */
    if(!cviii_vm_word_0827(v,bank,&address))goto bus;
    if(!cviii_vm_allowed_0827(address)){
      if(op==0x20u)v->external_target=address;
      cviii_vm_stop_0827(v,
         op==0x20u?CVIII_VM_STOP_EXTERNAL_0827:
                   CVIII_VM_STOP_BOUNDARY_0827,at);
      return 0;
    }
    if(op==0x20u){
       const uint16_t ret=(uint16_t)(v->pc-1u);
       if(v->depth>=8u || !cviii_vm_push_0827(v,(uint8_t)(ret>>8u)) ||
                             !cviii_vm_push_0827(v,(uint8_t)ret))goto bus;
       v->depth++;
    }
    v->pc=address;
    break;
  case 0x60u: /* RTS: private stack only. Top-level returns to caller. */
    if(!v->depth){
       cviii_vm_stop_0827(v,CVIII_VM_STOP_RTS_0827,at);return 0;
    }else{
       uint8_t lo=0,hi=0;
       if(!cviii_vm_pop_0827(v,&lo) ||
          !cviii_vm_pop_0827(v,&hi))goto bus;
       v->pc=(uint16_t)(((uint16_t)hi<<8u |lo)+1u);
       v->depth--;
    }break;
  case 0xeau:break; /* NOP */
  default:
    cviii_vm_stop_0827(v,CVIII_VM_STOP_OPCODE_0827,at);
    return 0;
 }
 if(v->instructions!=UINT32_MAX)v->instructions++;
 return 1;
bus:
 cviii_vm_stop_0827(v,CVIII_VM_STOP_BUS_0827,at);
 return 0;
}
static inline int cviii_vm_run_0827(
 CviiiActorVM0827 *v,const uint8_t bank[16384],
 unsigned instruction_budget)
{
 if(!v || !bank || !instruction_budget || instruction_budget>256u)return 0;
 while(!v->stop_kind && v->instructions<instruction_budget)
    if(!cviii_vm_step_0827(v,bank))break;
 if(!v->stop_kind)
    cviii_vm_stop_0827(v,CVIII_VM_STOP_BUDGET_0827,v->pc);
 return v->stop_kind==CVIII_VM_STOP_RTS_0827 ||
        v->stop_kind==CVIII_VM_STOP_EXTERNAL_0827 ||
        v->stop_kind==CVIII_VM_STOP_BOUNDARY_0827;
}
#endif
