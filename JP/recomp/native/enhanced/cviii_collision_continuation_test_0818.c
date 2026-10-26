/* JP0818: original $B249/$B258 original-ROM decision contract.
 * Invented CPU RAM; no game code/data or collision response writes. */
#include "cviii_collision_continuation_0818.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void ok(int good,const char *why){
 if(!good){fprintf(stderr,"JP0818 FAIL: %s\n",why);exit(1);}
}
static uint16_t independently_expected(uint8_t type,int prior_bit,
                                     int player_ready,int partner_ready){
 if(type==0x16u || type==0x37u ||
   (type>=0x61u && type<0x7fu))return 0xb1f5u;
 if(prior_bit || !player_ready || !partner_ready)return 0xb29bu;
 return 0xb27au;
}
int main(void){
 uint8_t ram[2048]={0};
 const unsigned slot=3u;
 unsigned tested=0u;
 ram[0x0438u]=0x60u;
 ram[0x0438u+slot]=0x10u;
 ram[0x068du+slot]=0u;
 ram[0x0630u]=1u;ram[0x0413u]=1u;
 for(unsigned type=0;type<256;type++)
 for(unsigned mask=0;mask<8;mask++){
    ram[0x054eu+slot]=(uint8_t)type;
    ram[0x068du+slot]=(uint8_t)((mask&1u)?0x03u:0u);
    ram[0x0630u]=(uint8_t)((mask&2u)?1u:0u);
    ram[0x0413u]=(uint8_t)((mask&4u)?1u:0u);
    CviiiCollisionContinuation0818 r={0};
    ok(cviii_collision_continue_0818(ram,slot,0xb249u,&r),
       "read-only B249 branch must accept valid slot");
    ok(r.stop_pc==independently_expected(
         (uint8_t)type,(mask&1u)!=0,(mask&2u)!=0,(mask&4u)!=0),
       "original type-specific B258 first-stop route");
    ok(r.writes_8e_8d && r.actor_slot_8e==slot &&
       r.direction_8d==1u,"B249 sets original left-of-player bit");
    ok(r.decrements_068d==(r.stop_pc==0xb1f5u) &&
       r.predicted_068d==(uint8_t)(ram[0x068du+slot]-
           (r.stop_pc==0xb1f5u ? 1u:0u)),
       "B1F5 8-bit decrement is a prediction");
    ok(r.requires_b3ec==(r.stop_pc==0xb27au),
       "B3EC carry never simulated or guessed");
    tested++;
 }
 ram[0x054eu+slot]=0x69u;ram[0x068du+slot]=0u;
 CviiiCollisionContinuation0818 r={0};
 ok(cviii_collision_continue_0818(ram,slot,0xb258u,&r) &&
    !r.writes_8e_8d && r.stop_pc==0xb1f5u,
    "direct B258 bypasses B249 $8E/$8D direction writes");
 ram[0x054eu+slot]=0x7fu;ram[0x0630u]=1u;ram[0x0413u]=1u;
 ok(cviii_collision_continue_0818(ram,slot,0xb258u,&r) &&
    r.stop_pc==0xb27au && r.requires_b3ec,
    "type7F reaches deferred B3EC helper, not type61-7E decrement");
 ram[0x054eu+slot]=0x69u;
 ram[0x068du+slot]=0u;
 ok(cviii_collision_continue_0818(ram,slot,0xb249u,&r) &&
    r.predicted_068d==0xffu,
    "original DEC of zero wraps to $FF");
 ram[0x0438u+slot]=ram[0x0438u];
 ok(cviii_collision_continue_0818(ram,slot,0xb249u,&r) &&
    !r.direction_8d,"actor X equal to player X uses side zero");
 ok(!cviii_collision_continue_0818(ram,0,0xb249u,&r) &&
    !cviii_collision_continue_0818(ram,19,0xb249u,&r) &&
    !cviii_collision_continue_0818(ram,slot,0xb115u,&r),
    "unsupported original slot and PC fail closed");
 printf("PASS JP0818 B249/B258 %u exhaustive type/state synthetic decisions\n",tested);
 return 0;
}
