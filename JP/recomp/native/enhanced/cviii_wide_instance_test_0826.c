/* JP0826: authentic source-instancing and bounded original B525.
 * All fixtures use synthetic RAM/ROM data with original 6502 semantics.
 * This cannot certify offscreen weapon/hit/defeat/drop equivalence. */
#include "cviii_wide_instance_0826.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void ensure(int x,const char *why){
 if(!x){fprintf(stderr,"JP0826 FAIL: %s\n",why);exit(1);}
}
int main(void){
 static uint8_t bank[16384],ram[2048];
 CviiiHorizontalRoom0816 source={0};
 source.valid=1;source.count=6;
 source.pairs[3].event_id=0xa0u;
 source.pairs[3].event_record_cpu[0]=0xa444u;
 source.pairs[3].event_row[0]=0x32u;
 source.pairs[4].event_id=0x9fu;
 source.pairs[4].event_record_cpu[0]=0xa43fu;
 source.pairs[4].event_row[0]=0x32u;
 bank[0x91c6u-0x8000u]=0x13u;
 bank[0x921eu-0x8000u]=0x3du;
 bank[0xa444u-0x8000u]=0x32u;
 bank[0xa445u-0x8000u]=0x20u;
 bank[0xa446u-0x8000u]=0x50u;
 bank[0xa43fu-0x8000u]=0x32u;
 bank[0xa440u-0x8000u]=0u;
 bank[0xa441u-0x8000u]=0xb0u;
 CviiiWideSources0825 resident={0};
 ensure(cviii_wide_admit_original_0825(&resident,&source,
                 bank,sizeof bank) && resident.resident &&
        resident.source[0].room_x==160 &&
        resident.source[1].room_x==192 &&
        resident.source[0].room_y==80 &&
        resident.source[1].room_y==176,
        "original 2 row32 sources initialize correct room positions");
 CviiiWideRuntime0826 w={0};
 cviii_wide_runtime_init_0826(&w,&resident);
 ensure(w.initialized && w.actor[0].state==CVIII_INSTANCE_RESIDENT_0826 &&
        w.actor[1].state==CVIII_INSTANCE_RESIDENT_0826,
        "native sources persist before original CPU allocation");
 const uint8_t key[3]={0,1,0};
 ram[0x54f]=0x3du;ram[0x550]=0x3du;
 ram[0x471]=4u;ram[0x472]=4u;
 ram[0x646]=3u;ram[0x647]=4u;
 ram[0x439]=160u;ram[0x43a]=192u;
 ram[0x41d]=80u;ram[0x41e]=176u;
 ram[0x401]=0x94u;ram[0x402]=0x94u;
 ensure(cviii_wide_runtime_tick_0826(&w,&resident,ram,key,0)==2 &&
        w.actor[0].state==CVIII_INSTANCE_LIVE_0826 &&
        w.actor[1].state==CVIII_INSTANCE_LIVE_0826 &&
        w.actor[0].guest_slot==1u &&
        w.actor[1].guest_slot==2u &&
        w.actor[0].world_x==160 &&
        w.actor[1].world_y==176 &&
        w.actor[0].frames==1 &&
        w.actor[0].original_frames==1 &&
        !cviii_wide_native_combat_ready_0826(&w.actor[0]),
        "independent entity clock, real original allocator provenance");
 ram[0x439]=162u;ram[0x43a]=190u;
 ensure(cviii_wide_runtime_tick_0826(&w,&resident,ram,key,0)==2 &&
        w.actor[0].world_x==162 && w.actor[1].world_x==190 &&
        w.actor[0].frames==2 &&
        w.actor[1].original_frames==2,
        "per-frame updated native instance follows genuine CPU actor");
 ram[0x54f]=0;
 ensure(cviii_wide_runtime_tick_0826(&w,&resident,ram,key,0)==1 &&
        w.actor[0].state==CVIII_INSTANCE_LOST_0826 &&
        w.actor[0].guest_slot==0u &&
        w.actor[1].state==CVIII_INSTANCE_LIVE_0826 &&
        w.losses==1u && !cviii_wide_native_combat_ready_0826(&w.actor[0]),
        "original allocator disappearing retires only the linked instance");
 ram[0x54f]=0x3du;ram[0x439]=160u;
 ensure(cviii_wide_runtime_tick_0826(&w,&resident,ram,key,0)==1 &&
        w.actor[0].state==CVIII_INSTANCE_LOST_0826 &&
        w.actor[0].guest_slot==0u,
        "numeric slot recycled cannot resurrect old source instance");
 ensure(cviii_wide_runtime_tick_0826(&w,&resident,ram,
               (const uint8_t[]){0,2,0},0)==-1 &&
        w.actor[1].frames==4u,
        "wrong original room must not update a source instance");
 CviiiB525Prefix0826 e={0};
 ram[0x54f]=0x3du;
 ensure(cviii_b525_prefix_0826(ram,1u,&e) &&
        e.sound_id==0x27u && e.stop_pc==0xb53cu &&
        e.external_sound_required,
        "original B525 type3D first effect is sound27 at E249");
 for(unsigned type=0;type<256u;type++){
    ram[0x54f]=(uint8_t)type;
    ensure(cviii_b525_prefix_0826(ram,1u,&e) &&
          e.sound_id==((type==0x3du||type==0x3eu||
                        type==0x4bu||type==0x47u)?0x27u:0x32u),
          "all type IDs follow original B525 selection");
 }
 ram[0x54f]=0x3du;ram[0x669u+1u]=0x30u;
 ram[0x67bu+1u]=2u;
 CviiiB486Effect0821 first={0};
 ensure(cviii_effect_b486_prefix_0821(ram,1u,&first) &&
        first.decision==CVIII_B486_DEFER_B525_0821 &&
        first.new_067b==0xffu && first.stop_pc==0xb525u &&
        !cviii_wide_native_combat_ready_0826(&w.actor[1]),
        "B486 arithmetic reaches B525 but guest-effect parity not granted");
 puts("PASS JP0826 two original sources, native instance ticks, lost-slot guard, B525/B486 boundaries");
 return 0;
}
