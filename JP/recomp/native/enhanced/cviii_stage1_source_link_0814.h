/* JP0814: source-to-original-slot installation witness, read-only.
 * This is NOT an actor spawning or collision implementation. The two
 * original raw0A:$8275 branches have disjoint slot owners:
 * source row (< $80) -> $07C2,X in X=0..5, and direct type
 * (>= $80) -> $054E,X in X=13..18.
 * Require the full observed postcondition; fail closed on ambiguity. */
#ifndef CVIII_STAGE1_SOURCE_LINK_0814_H
#define CVIII_STAGE1_SOURCE_LINK_0814_H
#include <stdint.h>
enum { CVIII_LINK_NONE_0814=0, CVIII_LINK_EVENT_0814=1,
       CVIII_LINK_DIRECT_0814=2, CVIII_LINK_AMBIGUOUS_0814=3 };
typedef struct {
    uint8_t kind, slot;
} CviiiSourceLink0814;
static inline CviiiSourceLink0814 cviii_source_link_0814(
    const uint8_t record[7],uint8_t local_axis,
    const uint8_t ram[2048])
{
    CviiiSourceLink0814 result={0,0};
    if(!record || !ram)return result;
    const uint8_t type=record[2];
    const unsigned begin=type==0x0du ? 0u : 13u;
    const unsigned end=type==0x0du ? 6u : 19u;
    /* Only types witnessed in the original Stage1 chapel source.
     * Do not guess the allocation semantics of other seven-byte tags. */
    if(type!=0x0du && type!=0x80u)return result;
    for(unsigned x=begin;x<end;x++) {
        int match=0;
        if(type==0x0du) {
            /* Original $8287-$82A8: seven-byte source initialisation.
             * $07C8 and $07E0 are zero on this exact installation. */
            match=ram[0x07c2u+x]==type &&
                  ram[0x07dau+x]==record[3] &&
                  ram[0x07e6u+x]==record[5] &&
                  ram[0x07ceu+x]==record[6] &&
                  ram[0x07d4u+x]==local_axis &&
                  ram[0x07c8u+x]==0u &&
                  ram[0x07e0u+x]==0u;
        } else {
            /* Original $82B8-$82D6 direct-object installer.
             * The $8329 script lookup yields $30 for type $80.
             * Do not infer sprite identity or current activity. */
            match=ram[0x054eu+x]==type &&
                  ram[0x0438u+x]==record[3] &&
                  ram[0x05d8u+x]==record[4] &&
                  ram[0x041cu+x]==local_axis &&
                  ram[0x05efu+x]==0x30u;
        }
        if(match) {
            if(result.kind) {
                result.kind=CVIII_LINK_AMBIGUOUS_0814;
                result.slot=0;
                return result;
            }
            result.kind=type==0x0du ?
                CVIII_LINK_EVENT_0814:CVIII_LINK_DIRECT_0814;
            result.slot=(uint8_t)x;
        }
    }
    return result;
}
#endif
