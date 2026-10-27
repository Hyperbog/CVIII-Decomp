/* JP0814: invented RAM, original allocator postcondition regression. */
#include "cviii_stage1_source_link_0814.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static int eq(CviiiSourceLink0814 r,int k,int x) {
    return r.kind==(unsigned)k && r.slot==(unsigned)x;
}
int main(void) {
    uint8_t ram[2048]={0},before[2048],rec[7]={0};
    rec[2]=0x80u;rec[3]=0x28u;rec[4]=0x9eu;
    ram[0x054eu+13u]=0x80u;
    ram[0x0438u+13u]=0x28u;
    ram[0x05d8u+13u]=0x9eu;
    ram[0x041cu+13u]=0x57u;
    ram[0x05efu+13u]=0x30u;
    memcpy(before,ram,sizeof ram);
    if(!eq(cviii_source_link_0814(rec,0x57u,ram),
           CVIII_LINK_DIRECT_0814,13))return 1;
    if(memcmp(before,ram,sizeof ram))return 2;
    ram[0x05efu+13u]=0x31u;
    if(!eq(cviii_source_link_0814(rec,0x57u,ram),
           CVIII_LINK_NONE_0814,0))return 3;
    ram[0x05efu+13u]=0x30u;
    /* Two valid direct slots for the same source cannot be assigned. */
    for(unsigned base=0;base<2048;base++)
        if(base==0x054eu+13u || base==0x0438u+13u ||
           base==0x05d8u+13u || base==0x041cu+13u ||
           base==0x05efu+13u)
            ram[base+1u]=ram[base];
    if(!eq(cviii_source_link_0814(rec,0x57u,ram),
           CVIII_LINK_AMBIGUOUS_0814,0))return 4;
    memset(ram,0,sizeof ram);
    memset(rec,0,sizeof rec);
    rec[2]=0x0du;rec[3]=0xd8u;rec[5]=0x7au;rec[6]=0x4cu;
    ram[0x07c2u+3u]=0x0du;
    ram[0x07dau+3u]=0xd8u;
    ram[0x07e6u+3u]=0x7au;
    ram[0x07ceu+3u]=0x4cu;
    ram[0x07d4u+3u]=0x37u;
    if(!eq(cviii_source_link_0814(rec,0x37u,ram),
           CVIII_LINK_EVENT_0814,3))return 5;
    ram[0x07c8u+3u]=0x11u;
    if(!eq(cviii_source_link_0814(rec,0x37u,ram),
           CVIII_LINK_NONE_0814,0))return 6;
    rec[2]=0x7fu;
    if(!eq(cviii_source_link_0814(rec,0x37u,ram),
           CVIII_LINK_NONE_0814,0))return 7;
    if(!eq(cviii_source_link_0814(NULL,0x37u,ram),
           CVIII_LINK_NONE_0814,0))return 8;
    puts("PASS JP0814 original source/direct allocator RAM postconditions");
    return 0;
}
