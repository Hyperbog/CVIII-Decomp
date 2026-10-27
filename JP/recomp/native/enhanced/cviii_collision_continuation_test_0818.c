/* JP0818 original B249/B258 branching, all input RAM artificial.
 * No game data, original guest writes, or inferred hitbox effects. */
#include "cviii_collision_continuation_0818.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
static void ok(int good,const char *why){
 if(!good){fprintf(stderr,"JP0818 FAIL: %s\n",why);exit(1);}
}
static uint16_t independent_stop(uint8_t type,int bit,
                                  int guard630,int guard413){
 if(type==0x16u || type==0x37u ||
    (type>=0x61u && type<0x7fu))return 0xb1f7u;
 if(bit || !guard630 || !guard413)return 0xb29du;
 return 0xb27cu;
}
int main(void){
 uint8_t ram[2048]={0};
 const unsigned slot=3u;
 unsigned tested=0;
 ram[0x0438u]=0x60u;
 ram[0x0438u+slot]=0x10u;
 for(unsigned type=0;type<256u;type++)
 for(unsigned mask=0;mask<8u;mask++){
    ram[0x054eu+slot]=(uint8_t)type;
    ram[0x068du+slot]=(uint8_t)((mask&1u)?0x03u:0u);
    ram[0x0630u]=(uint8_t)((mask&2u)?1u:0u);
    ram[0x0413u]=(uint8_t)((mask&4u)?1u:0u);
    CviiiCollisionContinuation0818 r={0};
    ok(cviii_collision_continue_0818(ram,slot,0xb249u,&r),
       "bounded $B249 entry must accept original slot");
    ok(r.stop_pc==independent_stop((uint8_t)type,
         (mask&1u)!=0,(mask&2u)!=0,(mask&4u)!=0),
       "exact original $B258 branch destination PCs");
    ok(r.writes_8e_8d && r.actor_slot_8e==slot &&
       r.direction_8d==1u,"original $B249 side/actor scratch");
    ok(r.requires_b3ec==(r.stop_pc==0xb27cu),
       "unexecuted original B3EC helper is deferred");
    tested++;
 }
 ram[0x054eu+slot]=0x69u;ram[0x068du+slot]=0u;
 CviiiCollisionContinuation0818 r={0};
 ok(cviii_collision_continue_0818(ram,slot,0xb258u,&r) &&
    !r.writes_8e_8d && r.stop_pc==0xb1f7u,
    "direct $B258 type69 exits RTS without $B249 scratch writes");
 ram[0x054eu+slot]=0x7fu;ram[0x0630u]=1u;ram[0x0413u]=1u;
 ok(cviii_collision_continue_0818(ram,slot,0xb258u,&r) &&
    r.stop_pc==0xb27cu && r.requires_b3ec,
    "type7F may call original B3EC, not B1F7");
 ram[0x054eu+slot]=0x69u;
 ram[0x068du+slot]=0xffu;
 ok(cviii_collision_continue_0818(ram,slot,0xb249u,&r) &&
    r.stop_pc==0xb1f7u,
    "type69 RTS: no inferred DEC $068D regardless of original byte");
 ram[0x0438u+slot]=ram[0x0438u];
 ok(cviii_collision_continue_0818(ram,slot,0xb249u,&r) &&
    !r.direction_8d,"actor X equal to player X sets direction zero");
 ok(!cviii_collision_continue_0818(ram,0,0xb249u,&r) &&
    !cviii_collision_continue_0818(ram,19,0xb249u,&r) &&
    !cviii_collision_continue_0818(ram,slot,0xb115u,&r),
    "unsupported actor slots and PC fail closed");
 printf("PASS JP0818 original B249/B258 %u bounded route decisions\n",tested);
 return 0;
}
