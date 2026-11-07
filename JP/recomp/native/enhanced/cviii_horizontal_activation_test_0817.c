/* JP0817: original six source-slot dispatch and $83D1 movement,
 * artificial CPU RAM and pure predicted arithmetic only. */
#include "cviii_horizontal_activation_0817.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
static void check(int ok,const char *description){
 if(!ok){fprintf(stderr,"FAIL JP0817 source: %s\n",description);exit(1);}
}
int main(void){
 uint8_t ram[2048]={0};
 for(unsigned x=1u;x<=12u;x++)ram[0x054eu+x]=0x3du;
 ram[0x054eu+7u]=0u;
 ram[0x07c2u+3u]=0x32u;
 ram[0x07c8u+3u]=0x13u;
 ram[0x07e0u+3u]=0u;
 ram[0x07dau+3u]=0u;
 ram[0x07d4u+3u]=0xfeu;
 const CviiiHorizontalLive0817 v=cviii_horizontal_live_0817(ram,3u);
 check(v.slot==3u && v.row==0x32u && v.event_byte==0x13u &&
       v.will_dispatch && v.common_8cdd_gate &&
       v.first_free_1_12==7u,
       "84EA live source and optional 8CDD + FF06 decision");
 check(!cviii_horizontal_live_0817(ram,0u).will_dispatch,
       "84EA zero-row source is skipped with no event/motion");
 ram[0x53u]=1u;
 check(!cviii_horizontal_live_0817(ram,3u).common_8cdd_gate,
       "8CDD rejects nonzero scroll, not all handlers necessarily use it");
 ram[0x53u]=0u;
 ram[0x6bu]=1u;ram[0x65u]=0u;
 CviiiHorizontalMotion0817 m=cviii_horizontal_motion_0817(ram,3u);
 check(m.will_run && m.source_row_after==0x32u &&
       m.x_after==0xffu && m.page_after==1u &&
       m.crosses_page && m.y_after==0xfeu,
       "83D1 nonnegative 65 subtracts X with original 6502 borrow");
 ram[0x6bu]=0xffu;ram[0x07dau+3u]=0x12u;
 m=cviii_horizontal_motion_0817(ram,3u);
 check(m.x_after==0x13u && m.page_after==0u && !m.crosses_page,
       "83D1 negative signed movement subtraction wraps correctly");
 ram[0x65u]=0x80u;ram[0x6bu]=5u;
 ram[0x07d4u+3u]=0xfeu;ram[0x07e0u+3u]=0u;
 m=cviii_horizontal_motion_0817(ram,3u);
 check(m.y_after==3u && m.page_after==1u &&
       m.source_row_after==0u && m.crosses_page,
       "83D1 vertical pass explicitly clears original event on page one");
 ram[0x07c2u+3u]=0u;
 m=cviii_horizontal_motion_0817(ram,3u);
 check(!m.will_run && m.source_row_after==0u && m.y_after==0xfeu,
       "84EA no 83D1 on a zero row");
 check(!cviii_horizontal_live_0817(NULL,3u).will_dispatch &&
       !cviii_horizontal_motion_0817(NULL,3u).will_run &&
       !cviii_horizontal_live_0817(ram,6u).will_dispatch,
       "invalid RAM or six-slot bounds fail closed");
 puts("PASS JP0817 six original scheduler slots and 83D1 movement arithmetic");
 return 0;
}
