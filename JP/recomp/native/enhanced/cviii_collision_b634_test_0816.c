/* JP0816 original proximity carry; artificial tables/RAM, no ROM data. */
#include "cviii_collision_b634_0816.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
static void ok(int pred,const char *msg){
 if(!pred){fprintf(stderr,"FAIL JP0816 B634: %s\n",msg);exit(1);}
}
int main(void){
 uint8_t ram[2048]={0},bank[16384]={0};
 CviiiB634Gate0816 r={0};
 const unsigned x=3u,t=0x69u;
 ram[0x054eu+x]=(uint8_t)t;
 ram[0x0400u+x]=1u;
 ram[0x0470u+x]=0u;
 ram[0x7fu]=0u;
 ram[0x0438u]=0u;
 ram[0x0438u+x]=50u;
 bank[0xbb80u+t-0x8000u]=20u;
 bank[0xbb05u-0x8000u]=6u;
 bank[0xb673u-0x8000u]=16u;
 bank[0xbc08u+t-0x8000u]=5u;
 ram[0x041cu]=100u;
 ram[0x041cu+x]=125u;
 ok(cviii_b634_gate_0816(ram,bank,x,&r) &&
    r.x_distance==50u && !r.measured_y &&
    r.carry==1u && r.next_pc==0xb115u,
    "far horizontal branch to $B632 SEC then $B115");
 ram[0x0438u+x]=10u;
 ok(cviii_b634_gate_0816(ram,bank,x,&r) &&
    r.x_distance==10u && r.measured_y &&
    r.scratch10==116u && r.scratch11==120u &&
    r.y_distance==4u && !r.carry && r.next_pc==0xb18au,
    "near horizontal and vertical routes via B18A");
 ram[0x041cu+x]=145u;
 ok(cviii_b634_gate_0816(ram,bank,x,&r) &&
    r.y_distance==24u && r.carry==1u &&
    r.next_pc==0xb115u,"vertical far via B115");
 ram[0x054eu+x]=0x80u;
 ok(!cviii_b634_gate_0816(ram,bank,x,&r),
    "type80 bypasses B162 and B634 at B20B");
 ram[0x054eu+x]=0x75u;
 ok(!cviii_b634_gate_0816(ram,bank,x,&r),
    "type75 B162 dispatch bypasses B634");
 ram[0x054eu+x]=0x69u;ram[0x0470u+x]=0x11u;
 ok(!cviii_b634_gate_0816(ram,bank,x,&r),
    "original early actor attribute mask");
 ram[0x0470u+x]=0u;
 ram[0x7fu]=9u;
 ok(!cviii_b634_gate_0816(ram,bank,x,&r),
    "unsupported player radius table index rejected");
 puts("PASS JP0816 B634 source-bounded far/near, $80 exclusion and branch guards");
 return 0;
}
