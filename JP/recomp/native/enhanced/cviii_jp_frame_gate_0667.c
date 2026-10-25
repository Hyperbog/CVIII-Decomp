#include "cviii_jp_frame_gate_0667.h"
bool cviii_jp_frame_gate_0667(const CviiiJpFrameInput *in,
                               CviiiJpFrameResult *out)
{
    if(!in || !out || in->slot>=9u || in->sound_id==0u)return false;
    CviiiJpFrameResult result={0};
    result.countdown_after=in->countdown_0100;
    result.parser_mode_main=(uint8_t)(in->flags_011b&1u);
    /* $8A7C: $08 can bypass pause only when original $0109 >= $06. */
    if(in->global_01bf!=0u &&
       (in->slot==8u ? in->sound_id<6u : !(in->flags_011b&1u))) {
        result.decision=CVIII_JP_FRAME_SUSPENDED;
    }else{
        result.countdown_after=(uint8_t)(in->countdown_0100-1u);
        result.decision=result.countdown_after==0u?
             CVIII_JP_FRAME_STREAM_DUE:CVIII_JP_FRAME_COUNTING;
    }
    *out=result;
    return true;
}
