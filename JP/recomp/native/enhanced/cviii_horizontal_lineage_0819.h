/* JP0819: source-parent lifecycle census from real original RAM.
 * Never derives a historical source-to-actor mapping from type alone.
 * One snapshot cannot prove spawn timing; parent slots are recyclable.
 * Does not schedule AI/collision/drops outside the NES viewport.
 */
#ifndef CVIII_HORIZONTAL_LINEAGE_0819_H
#define CVIII_HORIZONTAL_LINEAGE_0819_H
#include "cviii_horizontal_child_0818.h"
#include <stdint.h>
enum { CVIII_SOURCE_PARENTS_0819=6 };
typedef struct {
    uint16_t actor_slot_mask;   /* X1..12 currently linked to parent */
    uint8_t parent_source_slot,children,visible_candidates;
    uint8_t event_row,event_index,source_cleared_with_child;
} CviiiParentCensus0819;
static inline int cviii_parent_census_0819(
    const uint8_t ram[2048],CviiiParentCensus0819 parents[6])
{
    if(!ram || !parents)return -1;
    CviiiParentCensus0819 snapshot[6]={0};
    for(unsigned p=0;p<6u;p++){
        snapshot[p].parent_source_slot=(uint8_t)p;
        snapshot[p].event_row=ram[0x07c2u+p];
        snapshot[p].event_index=ram[0x07c8u+p];
    }
    int linked=0;
    for(unsigned x=1u;x<=12u;x++){
        const CviiiHorizontalChild0818 child=
             cviii_horizontal_child_0818(ram,x);
        if(!child.allocated)continue;
        CviiiParentCensus0819 *parent=&snapshot[child.parent_source];
        parent->actor_slot_mask|=(uint16_t)(1u<<x);
        parent->children++;
        parent->visible_candidates+=child.sprite_candidate!=0u;
        linked++;
    }
    for(unsigned p=0;p<6u;p++){
        if(snapshot[p].children && snapshot[p].event_row!=0x32u)
            snapshot[p].source_cleared_with_child=1u;
        parents[p]=snapshot[p];
    }
    return linked;
}
#endif
