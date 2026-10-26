/* JP0820: original B727 and B2B5 prefix, synthetic original RAM only. */
#include "cviii_b727_contact_0820.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void check(int v,const char *msg){
    if(!v){fprintf(stderr,"JP0820 FAIL: %s\n",msg);exit(1);}
}
int main(void){
    uint8_t ram[2048]={0},before[2048];
    CviiiB727Contact0820 r={0};
    const unsigned x=3u,y=21u;
    ram[0x054eu]=1u;
    ram[0x054eu+x]=0x3du;
    ram[0x054eu+y]=2u;
    ram[0x99u]=0xffu;
    ram[0x068du+x]=0x80u;
    ram[0x0606u+y]=0x21u;
    ram[0x0669u+x]=0x30u;
    ram[0x0669u+y]=0x40u;
    ram[0x0657u+x]=3u;
    memcpy(before,ram,sizeof ram);
    check(cviii_b727_predict_0820(ram,x,y,1,&r) &&
          r.new_99==0u && r.increment_99 &&
          r.new_068d==0x84u && r.mask_bit==4u &&
          r.new_0669_actor==0x53u &&
          r.new_0669_partner==0x43u &&
          r.write_0669_partner &&
          r.b32d_special_contact &&
          r.new_061d_partner==3u &&
          r.next_pc==0xb311u,
          "B727 counter wrap and B32D partner special, stop B5DF");
    check(memcmp(ram,before,sizeof ram)==0,"preview must never mutate guest RAM");
    ram[0x0657u+x]=2u;
    ram[0x0606u+y]=0xf2u;
    ram[0x0669u+x]=0x30u;
    check(cviii_b727_predict_0820(ram,x,y,1,&r) &&
          r.adc_overflow && r.new_0669_actor==0xf2u &&
          !r.write_0669_partner,"B2C8 original ADC carry saturation");
    ram[0x054eu+y]=6u;
    check(cviii_b727_predict_0820(ram,x,y,1,&r) &&
          r.next_pc==0xb30bu,"partner type6 stops before B6CE");
    ram[0x054eu]=2u;ram[0x054eu+y]=8u;
    check(cviii_b727_predict_0820(ram,x,y,1,&r) &&
          !r.increment_99 && r.new_99==0xffu,
          "B727 special player2 plus partner8 skips $99 increment");
    for(unsigned slot=20u;slot<=22u;slot++){
       ram[0x054eu+slot]=1u;
       check(cviii_b727_predict_0820(ram,x,slot,1,&r) &&
             r.mask_bit==(2u<<(slot-20u)) &&
             r.partner_slot==slot,
             "B320 original three partner masks 02/04/08");
    }
    check(!cviii_b727_predict_0820(ram,x,y,0,&r) &&
          !cviii_b727_predict_0820(ram,x,23u,1,&r) &&
          !cviii_b727_predict_0820(ram,0u,y,1,&r) &&
          !cviii_b727_predict_0820(NULL,x,y,1,&r),
          "no near proof or invalid actor/partner never grants contact");
    puts("PASS JP0820 original B727 counter, B2B5 mask/state and B32D branching");
    return 0;
}
