#include "cviii_jp_chip_0665.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
static void check(int b){if(!b){fputs("JP0665 chip smoke failure\n",stderr);exit(1);}}
int main(void){
    for(int k=0;k<=5;++k){
        CviiiJpChipVoice v;check(cviii_jp_chip_init(&v,(CviiiJpChipKind)k,44100));
        check(!cviii_jp_chip_write(&v,0x8765,8));
        if(k<=2){
            check(cviii_jp_chip_write(&v,0x4015,15));
            if(k<=1){
                unsigned base=k==0?0x4000:0x4004;
                check(cviii_jp_chip_write(&v,(uint16_t)base,0xbf));
                check(cviii_jp_chip_write(&v,(uint16_t)(base+2),0x55));
                check(cviii_jp_chip_write(&v,(uint16_t)(base+3),1));
            }else{
                check(cviii_jp_chip_write(&v,0x400c,0x1f));
                check(cviii_jp_chip_write(&v,0x400e,6));
            }
        }else{
            unsigned base=k==3?0x9000:k==4?0xa000:0xb000;
            check(cviii_jp_chip_write(&v,(uint16_t)base,0x3f));
            check(cviii_jp_chip_write(&v,(uint16_t)(base+1),0x20));
            check(cviii_jp_chip_write(&v,(uint16_t)(base+2),0x81));
        }
        int64_t sum=0;int16_t min=32767,max=-32768;
        for(int i=0;i<8820;++i){int16_t x=0;check(cviii_jp_chip_sample(&v,&x)==1);
            sum+=x;if(x<min)min=x;if(x>max)max=x;}
        check(v.sample_count==8820 && min<max);
        check(sum<((int64_t)8820*INT16_MAX) && sum>((int64_t)8820*INT16_MIN));
    }
    check(!cviii_jp_chip_init(NULL,CVIII_JP_CHIP_VRC6_SAW,44100));
    puts("PASS JP0665 detached six-voice preview oscillator C11 smoke");return 0;
}
