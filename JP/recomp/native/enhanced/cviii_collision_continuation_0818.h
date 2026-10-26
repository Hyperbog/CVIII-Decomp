/* JP0818: original raw0B $B249-$B299 first reaction continuation.
 * A predictor only; do not store guest $8E/$8D/$068D or activate AI.
 * Caller supplies the ORIGINAL emulated CPU RAM snapshot.
 *
 * $B249: STX $8E, choose Y=(actorX<playerX), STY $8D.
 * $B258: branch on source type before B3EC and later collision loop.
 * $B1F5: DEC $068D,X; $B1F8 RTS.
 */
#ifndef CVIII_COLLISION_CONTINUATION_0818_H
#define CVIII_COLLISION_CONTINUATION_0818_H
#include <stdint.h>
#include <stddef.h>
enum {
    CVIII_B249_STOP_B1F5_0818=0xb1f5u,
    CVIII_B249_STOP_B29B_0818=0xb29bu,
    CVIII_B249_STOP_B3EC_0818=0xb27au
};
typedef struct {
    uint16_t stop_pc;
    uint8_t actor_slot_8e, direction_8d;
    uint8_t writes_8e_8d;       /* 0 when caller enters at $B258 */
    uint8_t decrements_068d, predicted_068d;
    uint8_t original_type, prior_068d;
    uint8_t requires_b3ec;     /* unknown original helper carry */
} CviiiCollisionContinuation0818;
static inline int cviii_collision_continue_0818(
    const uint8_t ram[2048], unsigned actor,
    unsigned entry_pc,CviiiCollisionContinuation0818 *out)
{
    if(!ram || !out || actor<1u || actor>18u ||
       (entry_pc!=0xb249u && entry_pc!=0xb258u))return 0;
    CviiiCollisionContinuation0818 r={0};
    r.actor_slot_8e=ram[0x8eu];
    r.direction_8d=ram[0x8du];
    r.original_type=ram[0x054eu+actor];
    r.prior_068d=ram[0x068du+actor];
    r.predicted_068d=r.prior_068d;
    if(entry_pc==0xb249u) {
        r.writes_8e_8d=1u;
        r.actor_slot_8e=(uint8_t)actor;
        r.direction_8d=ram[0x0438u+actor]<ram[0x0438u]?1u:0u;
    }
    /* $B258..$B269: special types $16 and $37 decrement,
     * and inclusive $61..$7E also decrement. */
    if(r.original_type==0x16u || r.original_type==0x37u ||
       (r.original_type>=0x61u && r.original_type<0x7fu)) {
        r.stop_pc=CVIII_B249_STOP_B1F5_0818;
        r.decrements_068d=1u;
        r.predicted_068d=(uint8_t)(r.prior_068d-1u);
    } else if((ram[0x068du+actor]&1u)!=0 ||
              ram[0x0630u]==0 || ram[0x0413u]==0) {
        /* $B269-$B279: existing contact-bit and two guest-state
         * prerequisites. No original $B3EC has run at this point. */
        r.stop_pc=CVIII_B249_STOP_B29B_0818;
    } else {
        /* $B27A JSR $B3EC / $B27D BCS $B29B:
         * stop BEFORE helper, its carry and effects are not guessed. */
        r.stop_pc=CVIII_B249_STOP_B3EC_0818;
        r.requires_b3ec=1u;
    }
    *out=r;
    return 1;
}
#endif
