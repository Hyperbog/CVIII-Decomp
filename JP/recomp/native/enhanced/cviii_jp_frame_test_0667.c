#ifdef NDEBUG
#undef NDEBUG
#endif
#include "cviii_jp_frame_gate_0667.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 unsigned tested=0;
 for(unsigned slot=0;slot<9;slot++)for(unsigned sound=1;sound<=0x7d;sound+=31)
 for(unsigned flags=0;flags<2;flags++)for(unsigned pause=0;pause<2;pause++)
 for(unsigned tick=0;tick<3;tick++){
  CviiiJpFrameInput in={(uint8_t)slot,(uint8_t)sound,(uint8_t)flags,(uint8_t)pause,(uint8_t)tick};
  CviiiJpFrameResult out={0};
  assert(cviii_jp_frame_gate_0667(&in,&out));
  unsigned expected_suspend=pause && (slot==8 ? sound<6 : !flags);
  assert(out.decision==(expected_suspend?CVIII_JP_FRAME_SUSPENDED:
          (tick==1?CVIII_JP_FRAME_STREAM_DUE:CVIII_JP_FRAME_COUNTING)));
  assert(out.countdown_after==(expected_suspend?tick:(uint8_t)(tick-1)));
  assert(out.parser_mode_main==flags);
  ++tested;
 }
 CviiiJpFrameResult out={0};CviiiJpFrameInput bad={9,1,0,0,1};
 assert(!cviii_jp_frame_gate_0667(&bad,&out));
 printf("PASS JP0667 synthetic frame pause/timer gate %u cases\n",tested);
 return 0;
}
