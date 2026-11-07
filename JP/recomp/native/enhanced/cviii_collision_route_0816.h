/* JP0816: original raw0B:$B1F8-$B231 and $B162-$B182 route only.
 * Branch destination, NOT a collision or gameplay response.
 * Original type >=$80 bypasses $B162 at $B20B. Do not attach
 * a generic actor hitbox, pickups, or external offscreen AI. */
#ifndef CVIII_COLLISION_ROUTE_0816_H
#define CVIII_COLLISION_ROUTE_0816_H
#include <stdint.h>
static inline uint16_t cviii_b162_dispatch_0816(uint8_t type)
{
    /* Exact $B162 compare/JMP special cases, before $B182 JSR $B634.
     * This helper models no carry, scratch RAM or B634 distance check. */
    if(type==0x73u)return 0xb227u;
    if(type==0x75u)return 0xb1d1u;
    if(type==0x6au)return 0xb106u;
    if(type==0x6fu)return 0xb10cu;
    if(type==0x70u)return 0xb109u;
    return 0xb634u; /* call-site transfer, not executed here */
}
static inline uint16_t cviii_b1f8_route_0816(
    uint8_t type,uint8_t flags_0470,uint8_t frame_0400,
    uint8_t scratch_7e,uint8_t scratch_7d)
{
    if(flags_0470&0x11u || !frame_0400 || type>=0x83u)
        return 0xb1f7u;
    if(type>=0x80u)return 0xb258u; /* $B20B BCS */
    if(type>=0x58u && type<0x61u)return 0xb1f7u;
    if(scratch_7e&0xf0u)return 0xb258u; /* $B217 */
    if(type>=0x69u)return cviii_b162_dispatch_0816(type);
    if(flags_0470&2u)return 0xb1d8u;
    if(scratch_7d)return 0xb258u;
    return 0xb232u; /* call to original $B339, not included */
}
#endif
