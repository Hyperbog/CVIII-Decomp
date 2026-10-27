/* JP0818 original raw0A:$8B2C-$8B73: row $32 actor ancestry.
 * $8D5E indexes type from $91EC+$32 ($3D), script from
 * $9194+$32 ($13); $8B50 ORs $04 into $0470,X and copies
 * original parent source-slot $69 into $0645,X.
 *
 * This witnesses a still-allocated original actor slot, not spawn
 * timing, lifetime of offscreen AI, or the display's hitbox.
 */
#ifndef CVIII_HORIZONTAL_CHILD_0818_H
#define CVIII_HORIZONTAL_CHILD_0818_H
#include <stdint.h>
typedef struct {
    uint8_t allocated;     /* exact original type/parent/flag postconditions */
    uint8_t slot,parent_source,source_row_is_32;
    uint8_t sprite_candidate; /* stricter screen frame/flag visibility probe */
    uint8_t event_phase;
    uint8_t original_flags;
    uint8_t sprite_frame;
} CviiiHorizontalChild0818;
static inline CviiiHorizontalChild0818 cviii_horizontal_child_0818(
    const uint8_t ram[2048],unsigned x)
{
    CviiiHorizontalChild0818 out={0};
    if(!ram || x<1u || x>12u)return out;
    out.slot=(uint8_t)x;
    const uint8_t type=ram[0x054eu+x];
    const uint8_t flags=ram[0x0470u+x];
    const uint8_t parent=ram[0x0645u+x];
    out.original_flags=flags;
    out.sprite_frame=ram[0x0400u+x];
    if(type!=0x3du || !(flags&0x04u) || parent>=6u)
        return out;
    out.allocated=1u;
    out.parent_source=parent;
    out.event_phase=ram[0x07c8u+parent];
    out.source_row_is_32=ram[0x07c2u+parent]==0x32u;
    out.sprite_candidate=(out.sprite_frame!=0u && !(flags&0x80u));
    return out;
}
#endif
