/* JP0818 original row32 parent-child witness; fabricated RAM only. */
#include "cviii_horizontal_child_0818.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void ok(int yes,const char *label){
 if(!yes){fprintf(stderr,"FAIL JP0818 child: %s\n",label);exit(1);}
}
int main(void){
 uint8_t ram[2048]={0};
 const unsigned child=2u,source=4u;
 ram[0x07c2u+source]=0x32u;
 ram[0x07c8u+source]=0x11u;
 ram[0x054eu+child]=0x3du;
 ram[0x0470u+child]=0x04u;
 ram[0x0645u+child]=(uint8_t)source;
 ram[0x0400u+child]=1u;
 CviiiHorizontalChild0818 r=cviii_horizontal_child_0818(ram,child);
 ok(r.allocated && r.slot==child && r.parent_source==source &&
    r.source_row_is_32 && r.event_phase==0x11u &&
    r.sprite_candidate,"original 8B50 child parent source verified");
 ram[0x07c2u+source]=0;
 r=cviii_horizontal_child_0818(ram,child);
 ok(r.allocated && !r.source_row_is_32,
    "source-row slot may be recycled while child remains allocated");
 ram[0x0470u+child]=0x84u;
 r=cviii_horizontal_child_0818(ram,child);
 ok(r.allocated && !r.sprite_candidate,
    "hidden but allocated actor remains original CPU lineage");
 ram[0x054eu+child]=0;
 r=cviii_horizontal_child_0818(ram,child);
 ok(!r.allocated,"original type-zero deallocates tracked parent link");
 ram[0x054eu+child]=0x3du;
 ram[0x0470u+child]=0;
 r=cviii_horizontal_child_0818(ram,child);
 ok(!r.allocated,"type alone never claims source ancestry");
 ram[0x0470u+child]=4;
 ram[0x0645u+child]=6;
 r=cviii_horizontal_child_0818(ram,child);
 ok(!r.allocated,"parent index outside six source slots is invalid");
 ok(!cviii_horizontal_child_0818(NULL,child).allocated &&
    !cviii_horizontal_child_0818(ram,0).allocated &&
    !cviii_horizontal_child_0818(ram,13).allocated,
    "unsupported CPU snapshot or actor slot");
 puts("PASS JP0818 original row32 parent/child witness and hidden-slot bounds");
 return 0;
}
