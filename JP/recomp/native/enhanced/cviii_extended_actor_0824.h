/* JP0824 original CPU actor adjacent-page continuation, NOT another AI.
 * Original raw0B $80E3 camera compensation maintains page bit $0470&1;
 * $8161 can set bit7 when outside original 256px OAM viewport while
 * $054E still owns the actor and original CPU AI continues. Only a
 * genuine row32 source child type$3D with original parent $0645
 * may be projected. All interaction effects remain original CPU-owned.
 */
#ifndef CVIII_EXTENDED_ACTOR_0824_H
#define CVIII_EXTENDED_ACTOR_0824_H
#include <stdint.h>
typedef struct {
    uint8_t eligible,side,real_original,original_slot;
    int32_t viewport_x;
} CviiiGuestPageActor0824;
static inline CviiiGuestPageActor0824 cviii_guest_page_actor_0824(
    const uint8_t ram[2048],unsigned slot)
{
    CviiiGuestPageActor0824 p={0};
    if(!ram || slot<1u || slot>12u)return p;
    const uint8_t frame=ram[0x400u+slot],type=ram[0x54eu+slot];
    const uint8_t flag=ram[0x470u+slot];
    /* Original $8B50 source flag $04, original $80E3 page bit $01. */
    if(!frame || type!=0x3du || (flag&0x05u)!=0x05u ||
       ram[0x645u+slot]>=6u)return p;
    const unsigned local=ram[0x438u+slot];
    p.real_original=1u;
    p.original_slot=(uint8_t)slot;
    /* With one-bit page1, the only visible candidate is +256 on
     * the right or -256 on the left. Mid-page cannot reach 85px
     * margins, so don't invent visible actors in that region. */
    if(local<=92u){p.side=2u;p.viewport_x=(int32_t)local+256;}
    else if(local>=164u){p.side=1u;p.viewport_x=(int32_t)local-256;}
    else return p;
    p.eligible=1u;
    return p;
}
/* JP0824b: a previously seen authentic CPU actor can cross a 256px
 * edge even if it has no type3D row32 source tag. Prove CONTINUITY
 * instead: caller must verify the unchanged original actor slot,
 * original allocator TYPE and sprite descriptor, in the same room.
 * $80E3 acts on these ordinary slots during original FDE4 CPU loop.
 * Only original page1/OAM-cull state and a <=32px physical
 * per-frame displacement permit retaining the already-live actor. */
static inline CviiiGuestPageActor0824 cviii_guest_page_continue_0824(
    const uint8_t ram[2048],unsigned slot,int32_t prior_local_world,
    int32_t current_local_camera)
{
    CviiiGuestPageActor0824 p={0};
    if(!ram || slot<1u || slot>18u || !ram[0x400u+slot] ||
       !ram[0x54eu+slot] || ram[0x54eu+slot]>=0x83u ||
       (ram[0x470u+slot]&0x81u)!=0x81u)return p;
    const unsigned low=ram[0x438u+slot];
    if(low<=92u){p.side=2u;p.viewport_x=(int32_t)low+256;}
    else if(low>=164u){p.side=1u;p.viewport_x=(int32_t)low-256;}
    else return p;
    const int64_t candidate=(int64_t)current_local_camera+p.viewport_x;
    const int64_t displacement=candidate-prior_local_world;
    if(displacement < -32 || displacement > 32)return p;
    p.eligible=1u;p.real_original=1u;p.original_slot=(uint8_t)slot;
    return p;
}
#endif
