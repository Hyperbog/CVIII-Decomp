/* JP0821: original raw0B reaction prefixes, ROM-free artificial RAM. */
#include "cviii_contact_effects_0821.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static void ok(int yes,const char *msg){
 if(!yes){fprintf(stderr,"JP0821 FAIL: %s\n",msg);exit(1);}
}
int main(void){
 uint8_t ram[2048]={0},before[2048];
 CviiiB6ceEffect0821 a={0};
 CviiiB5dfEffect0821 b={0};
 CviiiB486Effect0821 c={0};
 const unsigned x=3u,partner=21u;
 ram[0x054eu+x]=0x3du;ram[0x0470u+x]=0x80u;
 ram[0x0565u+x]=0xf3u;
 memcpy(before,ram,sizeof ram);
 ok(cviii_effect_b6ce_0821(ram,x,&a) &&
    a.supported && a.modified_mask==1u &&
    a.next_flags[0]==0x82u && a.next_state[0]==0x33u &&
    a.stop_pc==0xb6f4u,
    "B6CE type3D marks bit2 and clears 0565 upper two");
 ok(memcmp(before,ram,sizeof ram)==0,"B6CE preview must not mutate original RAM");
 ram[0x0470u+x]=0x82u;
 ok(cviii_effect_b6ce_0821(ram,x,&a) && !a.modified_mask,
    "B6CE already-flagged actor is unchanged");
 ram[0x054eu+x]=0x29u;
 ok(cviii_effect_b6ce_0821(ram,x,&a) && !a.modified_mask,
    "B6CE type below30 untouched");
 ram[0x054eu+x]=0x58u;
 ok(cviii_effect_b6ce_0821(ram,x,&a) && !a.modified_mask,
    "B6CE type58 or higher untouched");
 ram[0x054eu+x]=0x49u;
 for(unsigned i=1;i<=8u;i++){
     ram[0x0470u+i]=0u;ram[0x0565u+i]=0xffu;
 }
 ram[0x0470u+4u]=2u;
 ok(cviii_effect_b6ce_0821(ram,x,&a) &&
    a.modified_mask==(uint8_t)(0xffu&~(1u<<(4u-1u))) &&
    a.next_flags[1u]==2u && a.next_state[1u]==0x3fu &&
    a.next_flags[8u]==2u && a.next_state[8u]==0x3fu,
    "B6CE type49 original slots1..8, skipped flagged child");
 ram[0x054eu+x]=0x3du;
 ram[0x0438u+x]=0x52u;
 ram[0x041cu+partner]=0xa4u;
 ram[0x69u]=(uint8_t)x;
 ok(cviii_effect_b5df_0821(ram,x,partner,&b) &&
    b.accepted && b.effect_slot==23u &&
    b.source_x==0x52u && b.partner_y==0xa4u &&
    b.effect_flags==0x20u && b.effect_frame==0x12u &&
    b.effect_selector==0x0eu && b.flag89==8u &&
    b.restore_actor_slot==3u && b.stop_pc==0xb628u,
    "B5DF free slot23 installs effect frame and flags, not actor type");
 ram[0x054eu+23u]=0x55u;
 ok(cviii_effect_b5df_0821(ram,x,partner,&b) && b.accepted,
    "B5DF free predicate is $0400+23, not $054E+23");
 ram[0x0400u+23u]=1u;
 ok(cviii_effect_b5df_0821(ram,x,partner,&b) && !b.accepted,
    "B5DF frame occupied prevents effect installation");
 ram[0x0400u+23u]=0u;
 ram[0x054eu+x]=0x3du;ram[0x0669u+x]=0x31u;
 ram[0x067bu+x]=0x0au;ram[0x0470u+x]=0u;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.write_0669 && c.new_0669==1u &&
    c.write_067b && c.new_067b==7u &&
    c.upper_nibble==3u &&
    c.decision==CVIII_B486_DEFER_E249_0821 && c.stop_pc==0xb4bcu,
    "B486 subtracts event high nibble before deferred sound");
 ram[0x067bu+x]=3u;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.new_067b==0u &&
    c.decision==CVIII_B486_DEFER_B525_0821,
    "B486 depleted actor counter enters kill/response helper");
 ram[0x067bu+x]=1u;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.new_067b==0xfeu &&
    c.decision==CVIII_B486_DEFER_B525_0821,
    "B486 negative 8-bit subtraction uses BMI response");
 ram[0x0470u+x]=2u;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.write_0669 && !c.write_067b &&
    c.decision==CVIII_B486_DEFER_E75A_0821 &&
    c.stop_pc==0xb4d7u,
    "B486 attribute02 takes external E75A path");
 ram[0x0669u+x]=1u;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.decision==CVIII_B486_NO_CHANGE_0821 && !c.write_0669,
    "B486 zero high nibble does not modify actor");
 ram[0x054eu+x]=0x58u;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.decision==CVIII_B486_OTHER_TYPE_0821 &&
    c.stop_pc==0xb47bu,
    "B486 type58+ defers to earlier handler");
 ram[0x054eu+x]=0x2fu;
 ok(cviii_effect_b486_prefix_0821(ram,x,&c) &&
    c.decision==CVIII_B486_SKIP_0821 && c.stop_pc==0xb4d4u,
    "B486 type below30 returns");
 ram[0x0400u+23u]=0x12u;
 ram[0x048cu+23u]=0x0eu;
 ram[0x0470u+23u]=0x20u;
 ram[0x054eu+23u]=0u;
 const CviiiEffect23Witness0821 witness=cviii_effect23_witness_0821(ram);
 ok(witness.matched && witness.draw_candidate && !witness.type23,
    "real original $B5DF special sprite need not be an allocated actor");
 ram[0x0400u+23u]=0u;
 ok(!cviii_effect23_witness_0821(ram).matched,
    "original frame-zero effect is not a visible active sprite");
 ok(!cviii_effect_b6ce_0821(ram,0,&a) &&
    !cviii_effect_b5df_0821(ram,x,19u,&b) &&
    !cviii_effect_b486_prefix_0821(ram,19u,&c),
    "original actor/partner boundaries enforced");
 puts("PASS JP0821 B6CE flag sweep, B5DF effect23, B486 state branch");
 return 0;
}
