/* JP0817 original raw0A:$84EA-$8500 event-slot witness and
 * raw0A:$83D1-$840F coordinate update, observer-only.
 * A nonzero $07C2 row triggers $8501/$83D1. The handler may not
 * allocate any actors: $8CDD guard is conditional on handler choice.
 * No guest RAM writes or invented offscreen actors. */
#ifndef CVIII_HORIZONTAL_ACTIVATION_0817_H
#define CVIII_HORIZONTAL_ACTIVATION_0817_H
#include <stdint.h>
enum { CVIII_SOURCE_SLOTS_0817=6 };
typedef struct {
    uint8_t slot,row,event_byte,page_bit,position_x,position_y;
    uint8_t will_dispatch,common_8cdd_gate,first_free_1_12;
} CviiiHorizontalLive0817;
typedef struct {
    uint8_t source_row_after,page_after,x_after,y_after;
    uint8_t crosses_page,will_run;
} CviiiHorizontalMotion0817;
static inline CviiiHorizontalLive0817 cviii_horizontal_live_0817(
    const uint8_t ram[2048],unsigned x)
{
    CviiiHorizontalLive0817 r={0};
    if(!ram || x>=CVIII_SOURCE_SLOTS_0817)return r;
    r.slot=(uint8_t)x;
    r.row=ram[0x07c2u+x];
    r.event_byte=ram[0x07c8u+x];
    r.page_bit=ram[0x07e0u+x]&1u;
    r.position_x=ram[0x07dau+x];
    r.position_y=ram[0x07d4u+x];
    r.will_dispatch=r.row!=0u; /* original $84EF BEQ */
    r.common_8cdd_gate=(r.will_dispatch &&
        ram[0x53u]==0u && ram[0x07e0u+x]==0u);
    r.first_free_1_12=0xffu;
    for(unsigned y=1u;y<=12u;y++){
        if(ram[0x054eu+y]==0u){
            r.first_free_1_12=(uint8_t)y;break;
        }
    }
    return r;
}
static inline CviiiHorizontalMotion0817 cviii_horizontal_motion_0817(
    const uint8_t ram[2048],unsigned x)
{
    CviiiHorizontalMotion0817 o={0};
    if(!ram || x>=CVIII_SOURCE_SLOTS_0817)return o;
    const uint8_t row=ram[0x07c2u+x];
    o.source_row_after=row;
    o.page_after=ram[0x07e0u+x]&1u;
    o.x_after=ram[0x07dau+x];
    o.y_after=ram[0x07d4u+x];
    if(!row)return o; /* $84EA bypasses $83D1 */
    o.will_run=1u;
    const unsigned delta=ram[0x6bu];
    const unsigned sign=(delta&0x80u)?255u:0u;
    if(!(ram[0x65u]&0x80u)){
        /* $83DD-$83F2 SEC; $07DA -= $6B; $07E0 -= sign+borrow. */
        const unsigned low=ram[0x07dau+x];
        o.x_after=(uint8_t)(low-delta);
        const unsigned borrow=low<delta;
        o.page_after=(uint8_t)((ram[0x07e0u+x]-sign-borrow)&1u);
    } else {
        /* $83F3-$840F CLC; $07D4 += $6B; high += sign+carry.
         * Crossing into page bit1 clears original event source row. */
        const unsigned low=ram[0x07d4u+x];
        o.y_after=(uint8_t)(low+delta);
        const unsigned carry=low+delta>255u;
        o.page_after=(uint8_t)((ram[0x07e0u+x]+sign+carry)&1u);
        if(o.page_after)o.source_row_after=0u;
    }
    o.crosses_page=o.page_after!=(ram[0x07e0u+x]&1u);
    return o;
}
#endif
