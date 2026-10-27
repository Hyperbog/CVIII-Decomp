/* JP0813: exact synthetic source admission regression, no game bytes. */
#include "cviii_stage1_source_window_0813.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
static void ok(int expr,const char *msg){
    if(!expr){fprintf(stderr,"FAIL: %s\n",msg);exit(1);}
}
/* Independent byte/borrow arithmetic reproduction of original $8213-$8248. */
static CviiiStage1Admission0813 oracle(uint16_t world,uint16_t cam){
    unsigned a=world&255u,b=cam&255u,c=1u;
    unsigned t=(a-b-(c^1u))&511u;
    unsigned scratch2=t&255u;c=t<256u;
    a=world>>8;b=cam>>8;
    t=(a-b-(c^1u))&511u;
    unsigned scratch3=t&255u;
    CviiiStage1Admission0813 o={0,0};
    if(scratch3&128u)return o;
    a=world>>8;b=cam>>8;
    t=(a-b)&511u;a=t&255u;
    if(a){
        t=(a-1u)&511u;a=t&255u;
        if(a)return o;
        t=(scratch2-16u)&511u;c=t<256u;
        scratch2=t&255u;
        if(!c)scratch3=(scratch3-1u)&255u;
    }
    if(scratch3 || scratch2>=185u)return o;
    o.admitted=1u;o.local_axis=(uint8_t)((scratch2+55u)&255u);
    return o;
}
int main(void){
    unsigned matches=0,admitted=0;
    for(unsigned w=0;w<512u;w++)for(unsigned c=0;c<512u;c++){
        CviiiStage1Admission0813 a=
            cviii_stage1_admit_0813((uint16_t)w,(uint16_t)c);
        CviiiStage1Admission0813 b=
            oracle((uint16_t)w,(uint16_t)c);
        if(a.admitted!=b.admitted || a.local_axis!=b.local_axis){
            fprintf(stderr,"divergence source=%u camera=%u\n",w,c);
            return 1;
        }
        matches++;admitted+=a.admitted;
    }
    ok(cviii_stage1_admit_0813(0x180u,0x180u).local_axis==55u,
       "zero-delta world positioning");
    ok(!cviii_stage1_admit_0813(0x100u,0x180u).admitted,
       "behind-camera item rejected");
    printf("PASS JP0813 %u original-opcode-structure comparisons, %u admitted\n",
           matches,admitted);
    return 0;
}
