/* JP0816 original horizontal source-cell/phase oracle, no ROM bytes. */
#include "cviii_horizontal_sources_0816.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static void ok(int cond,const char *msg){
    if(!cond){fprintf(stderr,"FAIL JP0816 horizontal: %s\n",msg);exit(1);}
}
static void writeword(uint8_t *b,unsigned cpu,unsigned value){
    b[cpu-0x8000u]=(uint8_t)value;
    b[cpu-0x8000u+1u]=(uint8_t)(value>>8u);
}
int main(void){
    uint8_t bank[16384]={0};
    /* Original table ABI with entirely artificial descriptor records. */
    writeword(bank,0x9f6eu,0xa120u);
    writeword(bank,0xa06eu+0xa2u,0xa220u);
    bank[0xa120u-0x8000u]=0x00u;
    bank[0xa220u-0x8000u]=0x32u;
    writeword(bank,0xa56bu+0x02u,0xa320u);
    bank[0xa320u-0x8000u]=0x80u;
    const uint8_t ids[28]={
        0,0,0,0,0,0,0,0,0,0,0xd1,1,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0
    };
    CviiiHorizontalRoom0816 room={0};
    ok(cviii_horizontal_build_room_0816(
       &room,0,0x93ccu,ids,sizeof ids,bank,sizeof bank),
       "original 14-pair opening room shape");
    ok(room.count==14u &&
       room.pairs[5].event_row[0]==0 &&
       room.pairs[5].event_row[1]==0x32u &&
       room.pairs[5].aux_type==0x80u &&
       room.pairs[5].cell_cpu==0x93d6u,
       "high-bit ID fallback / original $07F6 choice");
    CviiiHorizontalSelection0816 a=cviii_horizontal_select_0816(
        &room,0,318u,0u,1);
    ok(a.valid && a.phase==5u && a.slot==5u &&
       a.source_id==0xd1u && a.event_row==0x32u &&
       a.event_cpu==0xa220u && a.aux_cpu==0xa320u,
       "original camera+2 and ASL/ROL source selection");
    a=cviii_horizontal_select_0816(&room,0,318u,0u,0);
    ok(a.valid && !a.event_row && a.event_cpu==0xa120u,
       "$07F6 low-bank fallback rejects false stage0 spawn");
    a=cviii_horizontal_select_0816(&room,0,318u,1u,1);
    ok(a.valid && a.phase==10u && a.slot==4u &&
       a.source_id==0u,
       "nonzero $62 adds 5 source phases");
    for(unsigned cam=0;cam<768u;cam++){
        a=cviii_horizontal_select_0816(&room,0,cam,0u,0);
        const unsigned phase=(cam+2u)/64u;
        ok(a.valid && a.phase==phase && a.slot==phase%6u,
           "all opening-room camera phases matched");
    }
    ok(!cviii_horizontal_select_0816(&room,2,318u,0u,1).valid,
       "vertical room never horizontal source");
    ok(!cviii_horizontal_select_0816(&room,0,1024u,0u,1).valid,
       "room-pair bound prevents source escape");
    CviiiHorizontalRoom0816 before=room;
    ok(!cviii_horizontal_build_room_0816(
        &room,0,0x93ccu,ids,sizeof ids-2u,bank,sizeof bank) &&
        memcmp(&room,&before,sizeof room)==0,
        "failed room source preload is transactional");
    puts("PASS JP0816 horizontal source conditional selectors + 768 cameras");
    return 0;
}
