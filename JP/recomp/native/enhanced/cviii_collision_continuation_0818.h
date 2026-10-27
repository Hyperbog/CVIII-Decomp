/* JP0818 original raw0B:$B249-$B2A3, exact 6502 PC boundaries.
 * This is a READ-ONLY original-RAM branch predictor.
 *
 * $B249 STX $8E; compare actor X with player; STY $8D;
 * $B258 type $16/$37/$61..$7E branches to $B1F7 RTS.
 * $B1F4 DEC $068D,X is a DIFFERENT instruction and is NOT
 * reached by these $B258 branches.
 * $B26B-$B27F guards whether JSR $B3EC can be reached.
 * $B29D prepares the later original interaction loop.
 * We stop before calling $B3EC or running that loop.
 */
#ifndef CVIII_COLLISION_CONTINUATION_0818_H
#define CVIII_COLLISION_CONTINUATION_0818_H
#include <stdint.h>
enum {
    CVIII_B249_STOP_RTS_0818=0xb1f7u,
    CVIII_B249_STOP_LOOP_0818=0xb29du,
    CVIII_B249_STOP_B3EC_0818=0xb27cu
};
typedef struct {
    uint16_t stop_pc;
    uint8_t actor_slot_8e, direction_8d;
    uint8_t writes_8e_8d;      /* zero when entered directly at $B258 */
    uint8_t original_type,original_collision_bit;
    uint8_t requires_b3ec;    /* no guessed B3EC carry or effects */
} CviiiCollisionContinuation0818;
static inline int cviii_collision_continue_0818(
    const uint8_t ram[2048],unsigned actor,
    unsigned entry_pc,CviiiCollisionContinuation0818 *out)
{
    if(!ram || !out || actor<1u || actor>18u ||
       (entry_pc!=0xb249u && entry_pc!=0xb258u))return 0;
    CviiiCollisionContinuation0818 r={0};
    r.actor_slot_8e=ram[0x8eu];
    r.direction_8d=ram[0x8du];
    r.original_type=ram[0x054eu+actor];
    r.original_collision_bit=ram[0x068du+actor]&1u;
    if(entry_pc==0xb249u) {
        r.writes_8e_8d=1u;
        r.actor_slot_8e=(uint8_t)actor;
        r.direction_8d=ram[0x0438u+actor]<ram[0x0438u]?1u:0u;
    }
    /* $B25D F0 $98; $B261 F0 $94; $B269 90 $8C:
     * all three reach the $B1F7 RTS (NOT $B1F4 DEC). */
    if(r.original_type==0x16u || r.original_type==0x37u ||
       (r.original_type>=0x61u && r.original_type<0x7fu)) {
        r.stop_pc=CVIII_B249_STOP_RTS_0818;
    } else if(r.original_collision_bit ||
              ram[0x0630u]==0u || ram[0x0413u]==0u) {
        /* $B270 D0 $2B, $B275 F0 $26, $B27A F0 $21 */
        r.stop_pc=CVIII_B249_STOP_LOOP_0818;
    } else {
        /* $B27C JSR $B3EC, later $B27F BCS $B29D.
         * Stop BEFORE the helper. */
        r.stop_pc=CVIII_B249_STOP_B3EC_0818;
        r.requires_b3ec=1u;
    }
    *out=r;
    return 1;
}
#endif
