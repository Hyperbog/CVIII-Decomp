/* JP0828: original $8001 movement oracle and detached source CPU
 * simulation. Synthetic RAM; real owner ROM only as optional argv[1].
 * Source code includes NO commercial PRG bytes or encoded sprites. */
#include "cviii_virtual_collision_0828.h"
#include "cviii_sound_prelude_0828.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void check(int v,const char *what){
 if(!v){fprintf(stderr,"JP0828 FAIL: %s\n",what);exit(1);}
}
static void synthetic(void){
 static uint8_t bank[16384],ram[2048];
 /* Distinct synthetic implementation for private detached movement:
  * CLC; LDA $0438,X; ADC $04F2,X; STA $0438,X;
  * JMP $8036; $8036: RTS. No source ROM bytes copied. */
 const uint8_t op[]={0x18,0xbd,0x38,0x04,0x7d,0xf2,0x04,
                     0x9d,0x38,0x04,0x4c,0x36,0x80};
 memcpy(bank+1,op,sizeof op);
 bank[0x36]=0x60u;
 CviiiWideSources0825 s={0};
 s.resident=1;s.source[0].event_cpu=0xa444u;
 s.source[0].original_source_slot=3u;
 s.source[0].room_x=160;s.source[0].room_y=80;
 s.source[1].event_cpu=0xa43fu;
 s.source[1].original_source_slot=4u;
 s.source[1].room_x=192;s.source[1].room_y=176;
 CviiiVirtualActors0828 v={0};
 cviii_virtual_reset_0828(&v,&s);
 check(v.initialized && !v.actor[0].original_slot &&
       v.actor[0].world_x==160,"source resident before actual CPU actor");
 const uint8_t key[]={0,1,0};
 ram[0x54f]=0x3du;ram[0x471]=4u;ram[0x646]=3u;
 ram[0x439]=160;ram[0x41d]=80;
 ram[0x4f3]=2u;ram[0x401]=0x94u;
 s.source[0].state=CVIII_WIDE_CPU_OWNED_0825;
 s.source[0].guest_slot=1u;
 check(cviii_virtual_tick_0828(&v,&s,bank,ram,key,0)==0 &&
       v.actor[0].state==CVIII_VIRTUAL_0828_LINKED &&
       v.actor[0].original_slot==1u &&
       v.actor[0].world_x==160 &&
       !cviii_virtual_can_apply_effect_0828(&v.actor[0]),
       "native instance copied actual 6502 RAM but cannot inflict damage");
 s.source[0].state=CVIII_WIDE_SOURCE_UNVERIFIED_0825;
 s.source[0].guest_slot=0u;ram[0x54f]=0u;
 check(cviii_virtual_tick_0828(&v,&s,bank,ram,key,0)==1 &&
       v.actor[0].state==CVIII_VIRTUAL_0828_DETACHED &&
       v.actor[0].world_x==162 &&
       v.actor[0].cpu.ram[0x54f]==0x3du &&
       v.actor[0].cpu.ram[0x439]==162 &&
       ram[0x439]==160 && ram[0x54f]==0u &&
       v.detached_steps==1u,
       "original guest actor deallocated; isolated private 6502 still moves");
 check(cviii_virtual_tick_0828(&v,&s,bank,ram,key,0)==1 &&
       v.actor[0].world_x==164 &&
       v.actor[0].detached_frames==2u &&
       v.actor[0].cpu.ram[0x439]==164,
       "persistent private CPU RAM advances over multiple detached frames");
 ram[0x54f]=0x3du;
 s.source[0].state=CVIII_WIDE_CPU_OWNED_0825;
 s.source[0].guest_slot=1u;
 check(cviii_virtual_tick_0828(&v,&s,bank,ram,key,0)==1 &&
       v.actor[0].state==CVIII_VIRTUAL_0828_DETACHED &&
       v.actor[0].world_x==166,
       "reused original guest slot cannot overwrite detached virtual identity");
 /* Synthetic table radii and weapon guest inputs: same original B447
  * normal partner branch, but compare in world rather than 8-bit X. */
 ram[0x54eu+21u]=2u;
 ram[0x438u+21u]=166u;ram[0x41cu+21u]=80u;
 bank[0xbb80u+0x3du-0x8000u]=5u;
 bank[0xbb60u+2u-0x8000u]=2u;
 bank[0xbc08u+0x3du-0x8000u]=4u;
 bank[0xbb6bu+2u-0x8000u]=3u;
 CviiiVirtualCollision0828 hit={0};
 check(cviii_virtual_partner_input_0828(&v.actor[0],ram,bank,0,
                                         21u,&hit) &&
       hit.outcome==CVIII_VCOL_NEAR_0828 &&
       hit.radius_x==7u && hit.radius_y==7u &&
       !cviii_virtual_can_apply_effect_0828(&v.actor[0]),
       "verified original B447 table dimensions produce near INPUT, not hit");
 ram[0x438u+21u]=246u;
 check(cviii_virtual_partner_input_0828(&v.actor[0],ram,bank,0,
                                         21u,&hit) &&
       hit.outcome==CVIII_VCOL_FAR_0828,
       "world X distance does not wrap distant original projectile");
 ram[0xb7u]=1u;
 check(cviii_virtual_partner_input_0828(&v.actor[0],ram,bank,0,
                                         21u,&hit) &&
       hit.outcome==CVIII_VCOL_UNVERIFIED_0828,
       "original E5BE altered B447 branch cannot grant guessed hit");
 ram[0xb7u]=0;ram[0x54eu+21u]=5u;
 check(cviii_virtual_partner_input_0828(&v.actor[0],ram,bank,0,
                                         21u,&hit) &&
       hit.outcome==CVIII_VCOL_UNVERIFIED_0828,
       "type05 original special hitbox remains blocked");
 /* The real fixed-bank $E249 prelude saves original PRG bank,
  * selects $0C and reaches JSR $8850 with the sound ID untouched.
  * All sound/mapper writes remain hypothetical sandbox values. */
 uint8_t ram_before[2048];memcpy(ram_before,ram,sizeof ram);
 ram[0x23u]=0x0bu;ram[0x26u]=0x00u;
 CviiiE249Prelude0828 sound={0};
 check(cviii_e249_prelude_0828(ram,0x27u,&sound) &&
       sound.original_bank==0x0bu &&
       sound.proposed_25==0x0bu &&
       sound.proposed_26==0xffu &&
       sound.proposed_prg_bank==0x0cu &&
       sound.pending_sound==0x27u &&
       sound.stop_pc==0xe258u &&
       sound.external_target==0x8850u &&
       !sound.effects_authorized,
       "E249 real fixed-bank sound prelude stops BEFORE bank0C APU effects");
 (void)ram_before;
 cviii_virtual_reset_0828(&v,&s);
 check(v.actor[0].state==CVIII_VIRTUAL_0828_UNSPAWNED &&
       !v.detached_steps && !v.actor[0].cpu.ram[0x54fu],
       "savestate epoch reset never treats stale private CPU as current");
 puts("PASS JP0828 native original movement detach, persistent CPU, B447 candidates");
}
static void original(const char *path){
 FILE *file=fopen(path,"rb");
 check(file!=NULL,"open owner private ROM");
 static uint8_t bank[16384],ram[2048],before[2048];
 check(fseek(file,16L+11L*16384L,SEEK_SET)==0 &&
       fread(bank,1,sizeof bank,file)==sizeof bank,
       "read owner original raw PRG0B bank");
 fclose(file);
 check(bank[0x8001u-0x8000u]==0xbdu &&
       bank[0x8036u-0x8000u]==0x60u &&
       bank[0x8037u-0x8000u]==0x18u,
       "physical $8001 original X/Y movement opcode identity");
 for(unsigned n=0;n<4096u;n++){
    memset(ram,0,sizeof ram);
    const unsigned x=1u;
    const uint8_t original_flags=(uint8_t)((n&1u)|0x44u);
    const uint8_t oldx=(uint8_t)(n*29u);
    const uint8_t oldy=(uint8_t)(n*17u);
    const uint8_t fx=(uint8_t)(n*19u);
    const uint8_t fy=(uint8_t)(n*71u);
    const uint8_t speedx=(uint8_t)((n>>4u)&0xffu);
    const uint8_t speedy=(uint8_t)((n>>5u)&0xffu);
    const uint8_t frac_speedx=(uint8_t)(n*3u);
    const uint8_t frac_speedy=(uint8_t)(n*11u);
    ram[0x471u]=original_flags;
    ram[0x439u]=oldx;ram[0x41du]=oldy;
    ram[0x4c5u]=fx;ram[0x4dcu]=fy;
    ram[0x4f3u]=speedx;ram[0x521u]=speedy;
    ram[0x50au]=frac_speedx;ram[0x538u]=frac_speedy;
    memcpy(before,ram,sizeof ram);
    const unsigned sumfx=(unsigned)fx+frac_speedx;
    const unsigned newx=(unsigned)oldx+speedx+(sumfx>>8u);
    const unsigned sumfy=(unsigned)fy+frac_speedy;
    const unsigned newy=(unsigned)oldy+speedy+(sumfy>>8u);
    const uint8_t page=(uint8_t)(
       ((original_flags&1u)+(speedx>=128u?255u:0u)+
        (newx>>8u))&1u);
    CviiiActorVM0827 vm={0};
    check(cviii_vm_init_0827(&vm,ram,x,0x8001u) &&
          cviii_vm_run_0827(&vm,bank,96u) &&
          vm.stop_kind==CVIII_VM_STOP_RTS_0827 &&
          vm.stop_pc==0x8036u,
          "original $8001 opcode source executes to exact RTS");
    check(vm.ram[0x4c5u]==(uint8_t)sumfx &&
          vm.ram[0x439u]==(uint8_t)newx &&
          vm.ram[0x4dcu]==(uint8_t)sumfy &&
          vm.ram[0x41du]==(uint8_t)newy &&
          (vm.ram[0x471u]&1u)==page &&
          (vm.ram[0x471u]&0xfeu)==(original_flags&0xfeu) &&
          memcmp(ram,before,sizeof ram)==0,
          "original ROM VM X,Y,page,fraction matches independent arithmetic");
 }
 puts("PASS JP0828 4096 original-bank $8001 source differential movement cases");
}
int main(int argc,char **argv){
 synthetic();if(argc>1)original(argv[1]);return 0;
}
