/* JP0819 original source-parent lifecycle census, RAM fixtures only. */
#include "cviii_horizontal_lineage_0819.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static void ok(int x,const char *why){
 if(!x){fprintf(stderr,"FAIL JP0819 lineage: %s\n",why);exit(1);}
}
int main(void){
 uint8_t ram[2048]={0};
 CviiiParentCensus0819 parents[CVIII_SOURCE_PARENTS_0819];
 ram[0x07c2u+3u]=0x32u;
 ram[0x07c8u+3u]=0x11u;
 ram[0x054eu+2u]=0x3du;
 ram[0x0470u+2u]=4u;
 ram[0x0645u+2u]=3u;
 ram[0x0400u+2u]=1u;
 ram[0x054eu+5u]=0x3du;
 ram[0x0470u+5u]=0x84u;
 ram[0x0645u+5u]=3u;
 ram[0x0400u+5u]=1u;
 ok(cviii_parent_census_0819(ram,parents)==2 &&
    parents[3].actor_slot_mask==((1u<<2)|(1u<<5)) &&
    parents[3].children==2u &&
    parents[3].visible_candidates==1u &&
    parents[3].event_row==0x32u &&
    parents[3].event_index==0x11u &&
    !parents[3].source_cleared_with_child,
    "two original children share source slot but one is hidden");
 ram[0x07c2u+3u]=0u;
 ok(cviii_parent_census_0819(ram,parents)==2 &&
    parents[3].children==2u && parents[3].source_cleared_with_child,
    "source row freed without original allocated child disappearing");
 ram[0x054eu+2u]=0u;
 ok(cviii_parent_census_0819(ram,parents)==1 &&
    parents[3].actor_slot_mask==(1u<<5) &&
    parents[3].visible_candidates==0u,
    "slot2 original deallocation does not deallocate hidden slot5");
 ram[0x054eu+5u]=0u;
 ok(cviii_parent_census_0819(ram,parents)==0 &&
    !parents[3].actor_slot_mask &&
    !parents[3].source_cleared_with_child,
    "both original slots type0: source is resident, no live children");
 ok(cviii_parent_census_0819(NULL,parents)==-1 &&
    cviii_parent_census_0819(ram,NULL)==-1,
    "unsupported pointers reject, no synthetic lifetime");
 puts("PASS JP0819 source parent/sibling allocation, hidden sprites, row reset");
 return 0;
}
