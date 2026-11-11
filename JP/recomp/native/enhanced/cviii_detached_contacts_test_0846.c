/* JP0846 synthetic original B447 partner inputs; no ROM dependency. */
#include "cviii_detached_contacts_0846.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void ck(int ok,const char *why){
 if(!ok){fprintf(stderr,"JP0846 FAIL: %s\n",why);exit(1);}
}
int main(void){
 uint8_t guest[2048]={0},bank[16384]={0};
 uint8_t prev[2048];
 const uint8_t room[]={0,1,0},wrong[]={0,1,1};
 CviiiWideSources0825 source={0};
 CviiiVirtualActors0828 vm={0};
 CviiiDetachedContacts0846 c={0};
 source.resident=1;
 source.source[0].event_cpu=0xa444u;
 source.source[0].original_source_slot=3u;
 source.source[0].original_type=0x3du;
 source.source[0].state=CVIII_WIDE_SOURCE_UNVERIFIED_0825;
 cviii_virtual_reset_0828(&vm,&source);
 CviiiVirtual3D0828 *a=&vm.actor[0];
 a->state=CVIII_VIRTUAL_0828_DETACHED;
 a->original_slot=1u;a->original_flags=0x81u;
 a->detached_frames=2u;a->world_x=-8;a->world_y=80;
 a->cpu.ram[0x54fu]=0x3du;a->cpu.ram[0x646u]=3u;
 guest[0x54eu+20u]=2u;
 guest[0x438u+20u]=10u;guest[0x41cu+20u]=80u;
 /* Invented radii, following original physical bank0B B447 table shape. */
 bank[0xbb80u+0x3du-0x8000u]=15u;
 bank[0xbb60u+2u-0x8000u]=5u;
 bank[0xbc08u+0x3du-0x8000u]=4u;
 bank[0xbb6bu+2u-0x8000u]=3u;
 memcpy(prev,guest,sizeof guest);
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==1 &&
    c.sampled[0]==14u && c.near[0]==2u &&
    c.contact[0][0].outcome==CVIII_VCOL_NEAR_0828 &&
    c.frames==1u && c.near_inputs==1u &&
    !cviii_virtual_can_apply_effect_0828(a) &&
    !memcmp(prev,guest,sizeof guest),
    "genuine detached candidate changes only private contacts");
 a->state=CVIII_VIRTUAL_0828_LINKED;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==0 && !c.near[0] && !c.sampled[0],
    "linked real actor never duplicated");
 a->state=CVIII_VIRTUAL_0828_DETACHED;a->source_cpu=0xa43fu;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==0 && !c.near[0],
    "wrong source CPU identity rejected");
 a->source_cpu=0xa444u;a->world_x=4;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==0 && !c.near[0],
    "private actor inside NES strip cannot interact");
 a->world_x=-8;guest[0x54fu]=0x3du;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==0 && !c.near[0],
    "guest type3D allocator reuse takes priority");
 guest[0x54fu]=0;a->cpu.ram[0x68eu]=2u;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==0 && c.masked[0]==2u,
    "original private B447 mask honored");
 a->cpu.ram[0x68eu]=0;guest[0xb7u]=1u;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,room,0)==0 && c.unknown[0]==2u &&
    c.unknown_inputs==1u,
    "unsupported helper cannot enable guessed hit");
 guest[0xb7u]=0;
 ck(cviii_detached_contacts_tick_0846(&c,&vm,&source,
      guest,bank,wrong,0)==-1 && !c.near[0] && !c.sampled[0],
    "room mismatch clears live inputs");
 cviii_detached_contacts_clear_0846(&c);
 ck(!c.frames && !c.near_inputs && !c.unknown_inputs,
    "reset clears savestate-unsafe native epochs");
 puts("PASS JP0846 detached actor B447 live input candidates (no effects)");
 return 0;
}
