/* JP0815: read-only Stage1 source projection and interaction-policy probe.
 * The +$37 chapel vertical origin comes from raw0A:$8248; the NES
 * 256px gameplay image and original CPU interaction remain authoritative.
 * These pure functions never allocate game actors, move them or grant hits. */
#ifndef CVIII_SOURCE_OFFSCREEN_0815_H
#define CVIII_SOURCE_OFFSCREEN_0815_H
#include <stdint.h>
#include <limits.h>
enum {
    CVIII_PROBE_OUTSIDE_0815=0,
    CVIII_PROBE_NATIVE_0815=1,
    CVIII_PROBE_MARGIN_0815=2
};
enum {
    CVIII_INTERACTION_NOT_ACTOR_0815=0,     /* source row $0D */
    CVIII_INTERACTION_ALLOCATION_UNVERIFIED_0815=1,   /* no current original slot proof; not a despawn */
    CVIII_INTERACTION_TYPE80_B258_0816=2,  /* eligible $80 bypasses B162 at B20B; no interaction modeled */
    CVIII_INTERACTION_UNSUPPORTED_0815=3
};
typedef struct {
    int32_t screen_x,screen_y;
    uint8_t point_region;
} CviiiSourceProjection0815;
/* Geometry is in signed 64-bit to avoid overflow when traversing the
 * authenticated world graph. A point classification is NOT sprite
 * bounding-box visibility: original compressed PRG26 pieces are authoritative. */
static inline CviiiSourceProjection0815 cviii_source_project_0815(
    int64_t object_world_x,int64_t object_world_y,
    int64_t camera_world_x,int64_t camera_world_y,
    int native_left,int wide_width,int tall_height)
{
    CviiiSourceProjection0815 out={0,0,CVIII_PROBE_OUTSIDE_0815};
    if(native_left<0 || wide_width<256 || native_left>wide_width-256 ||
       tall_height!=240)return out;
    int64_t x=object_world_x-camera_world_x+native_left;
    int64_t y=object_world_y-camera_world_y;
    if(x<INT32_MIN || x>INT32_MAX || y<INT32_MIN || y>INT32_MAX)
        return out;
    out.screen_x=(int32_t)x;
    out.screen_y=(int32_t)y;
    if(y<48 || y>=240 || x<0 || x>=wide_width)return out;
    out.point_region=(x>=native_left && x<native_left+256) ?
        CVIII_PROBE_NATIVE_0815:CVIII_PROBE_MARGIN_0815;
    return out;
}
/* Native seven-byte chapel source Y uses the original $37 offset;
 * the original loader outputs a wrapped byte for the emulated actor.
 * A source-only shadow keeps the full world-axis Y and does not borrow
 * the 8-bit screen wrap to invent another room or object. */
static inline int64_t cviii_chapel_visual_world_y_0815(
    int64_t room_y,uint16_t original_axis)
{
    return room_y+(int64_t)original_axis+0x37;
}
/* Authentic PRG26 selector/frame pointer resolution, matching the
 * existing JP0807 renderer. 'selector' and 'frame' are byte OFFSETS
 * into pointer tables, not ordinal sprite IDs. Full bank SHA is
 * verified by the existing ROM-at-launch importer before this call.
 * No pixel identity is claimed without live CHR/palette mapping. */
typedef struct {
    uint16_t descriptor_cpu;
    uint8_t pieces,valid;
} CviiiSourceVisual0815;
static inline CviiiSourceVisual0815 cviii_source_visual_0815(
    const uint8_t *authenticated_prg26,uint8_t selector,uint8_t frame)
{
    CviiiSourceVisual0815 out={0,0,0};
    if(!authenticated_prg26)return out;
    const unsigned table=0x817fu+(unsigned)selector;
    if(table+1u>0xbfffu)return out;
    const unsigned i=table-0x8000u;
    const unsigned set=(unsigned)authenticated_prg26[i] |
        ((unsigned)authenticated_prg26[i+1u]<<8u);
    if(set<0x8000u || set>0xbfffu)return out;
    const unsigned at=set+(unsigned)frame;
    if(at+1u>0xbfffu)return out;
    const unsigned off=at-0x8000u;
    const unsigned descriptor=(unsigned)authenticated_prg26[off] |
        ((unsigned)authenticated_prg26[off+1u]<<8u);
    if(descriptor<0x8000u || descriptor>0xbfffu)return out;
    const unsigned count=authenticated_prg26[descriptor-0x8000u];
    if(count>27u)return out;
    out.valid=1u;
    out.descriptor_cpu=(uint16_t)descriptor;
    out.pieces=(uint8_t)count;
    return out;
}
/* JP0816 correction from actual raw0B $B1F8-$B20D:
 * If flags/frame permit reaching $B20B, type $80 branches to $B258
 * before $B217/$B162. Thus it is WRONG to route type $80 into $B634
 * or attribute a generic hitbox/damage/pickup to $B162. Other original
 * game callbacks may still operate; this policy grants no interaction.
 * Original $0D is an EVENT SOURCE, not a direct actor. */
static inline unsigned cviii_source_interaction_0815(
    uint8_t source_type,int original_actor_confirmed)
{
    if(source_type==0x0du)return CVIII_INTERACTION_NOT_ACTOR_0815;
    if(source_type==0x80u)
        return original_actor_confirmed ?
            CVIII_INTERACTION_TYPE80_B258_0816 :
            CVIII_INTERACTION_ALLOCATION_UNVERIFIED_0815;
    return CVIII_INTERACTION_UNSUPPORTED_0815;
}
#endif
