#include "cviii_jp_register_plan_0666.h"
#include <stdlib.h>
#define CHECK(c) do{if(!(c)){fprintf(stderr,"FAIL %s:%d: %s\n", __FILE__,__LINE__,#c);exit(1);}}while(0)
#include <stdio.h>
#include <string.h>
int main(void){
    uint8_t bank[CVIII_JP0666_BANK_SIZE]={0};
    CviiiJp0666Input in={0};
    CviiiJp0666Plan out={0};
    bank[0x872b - 0x8000]=0x34;bank[0x872c - 0x8000]=0x12;
    in.flag_06b4=0x80;in.octave=5;in.note=0;
    CHECK(cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(out.period_before_detune==0x1234 && out.write_count==2);
    CHECK(out.writes[0].address==0x9001 && out.writes[0].value==0x34);
    CHECK(out.writes[1].address==0x9002 && out.writes[1].value==0x92);
    in.slot=3;in.high_cache=0x12;in.flag_011b=0;in.flag_017e=0x10;
    CHECK(cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(out.write_count==1 && out.writes[0].address==0x4002);
    in.apu_gate=1;
    CHECK(cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(out.write_count==0 && out.stored_period_low==0x34);
    /* Bounded positive transpose moves to next 16-bit table entry. */
    in.slot=0;in.apu_gate=0;in.transpose=2;
    bank[0x872d - 0x8000]=0x78;bank[0x872e - 0x8000]=0x56;
    CHECK(cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(out.period_before_detune==0x5678);
    /* Negative two-byte transposition underflows index to the lower table. */
    in.transpose=0x82;
    bank[0x8729 - 0x8000]=0x11;bank[0x872a - 0x8000]=0x22;
    CHECK(cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(out.period_before_detune==0x2211);
    CviiiJp0666Plan prior=out;
    in.transpose=0x81; /* lower table index falls outside witness */
    CHECK(!cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(memcmp(&prior,&out,sizeof(out))==0);
    in.transpose=0;in.flag_06b4=0;
    CHECK(!cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(memcmp(&prior,&out,sizeof(out))==0);
    in.flag_06b4=0x80;in.flag_018e=0x10;
    CHECK(!cviii_jp0666_note_plan(bank,sizeof(bank),&in,&out));
    CHECK(memcmp(&prior,&out,sizeof(out))==0);
    puts("PASS JP0666 C11 synthetic register planning and unsupported-state guards");
    return 0;
}
