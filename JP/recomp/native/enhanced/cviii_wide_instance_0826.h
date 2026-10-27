/* JP0826: a native resident instance updated once per verified room frame.
 * Original NES CPU actor is still authoritative for AI, damage and drops.
 * This is the first actual host integration for JP0825's source registry.
 *
 * The persistent source survives scrolling, but a missing original CPU
 * allocation makes the linked instance LOST, not an immortal invisible NPC.
 * No guest RAM writes or simulated weapon hits.
 */
#ifndef CVIII_WIDE_INSTANCE_0826_H
#define CVIII_WIDE_INSTANCE_0826_H
#include "cviii_wide_source_admission_0825.h"
#include "cviii_contact_effects_0821.h"
#include <stdint.h>
#include <string.h>
enum {
 CVIII_INSTANCE_RESIDENT_0826=1,
 CVIII_INSTANCE_LIVE_0826=2,
 CVIII_INSTANCE_LOST_0826=3
};
typedef struct {
 uint16_t source_cpu;
 int32_t source_x,source_y,world_x,world_y;
 uint32_t frames,original_frames;
 uint8_t state,guest_slot,guest_type,guest_frame,guest_flags;
 uint8_t has_combat_parity; /* must stay 0 until full $B486/$B525 match */
} CviiiWideInstance0826;
typedef struct {
 CviiiWideInstance0826 actor[CVIII_WIDE_SOURCE_COUNT_0825];
 uint32_t total_frames,original_links,losses;
 uint8_t initialized;
} CviiiWideRuntime0826;
static inline void cviii_wide_runtime_init_0826(
   CviiiWideRuntime0826 *w,const CviiiWideSources0825 *sources)
{
 if(!w)return;
 memset(w,0,sizeof *w);
 if(!sources || !sources->resident)return;
 for(unsigned i=0;i<CVIII_WIDE_SOURCE_COUNT_0825;i++){
    CviiiWideInstance0826 *a=&w->actor[i];
    const CviiiWideSource0825 *s=&sources->source[i];
    if(s->state!=CVIII_WIDE_READY_0825)return;
    a->source_cpu=s->event_cpu;
    a->source_x=s->room_x;a->source_y=s->room_y;
    a->world_x=s->room_x;a->world_y=s->room_y;
    a->state=CVIII_INSTANCE_RESIDENT_0826;
 }
 w->initialized=1u;
}
/* Each call is an independent native instance clock tick. Original CPU
 * confirms/updates position and sprite; this deliberately DOES NOT
 * extrapolate original type-$3D AI or create an interaction hitbox. */
static inline int cviii_wide_runtime_tick_0826(
   CviiiWideRuntime0826 *w,CviiiWideSources0825 *source,
   const uint8_t ram[2048],const uint8_t selector[3],
   int32_t camera_x)
{
 if(!w || !source || !w->initialized || !source->resident ||
    !ram || !selector || selector[0]!=0u || selector[1]!=1u ||
    selector[2]!=0u || camera_x<0 || camera_x>512)return -1;
 unsigned live=0;
 for(unsigned i=0;i<CVIII_WIDE_SOURCE_COUNT_0825;i++){
    CviiiWideInstance0826 *a=&w->actor[i];
    CviiiWideSource0825 *s=&source->source[i];
    if(a->source_cpu!=s->event_cpu || !a->source_cpu ||
       a->state==CVIII_INSTANCE_LOST_0826)continue;
    if(a->frames!=UINT32_MAX)a->frames++;
    unsigned linked=0;
    for(unsigned x=1u;x<=12u;x++){
        if(ram[0x54eu+x]!=0x3du ||
           (ram[0x470u+x]&4u)==0u ||
           ram[0x645u+x]!=s->original_source_slot)continue;
        /* A first link is admitted only at the source's original
         * spawn coordinate; a continuing link must keep the same
         * original slot to prevent ambiguous allocation reuse. */
        const int32_t px=camera_x+ram[0x438u+x];
        const int32_t prior=a->state==CVIII_INSTANCE_LIVE_0826 ?
                              a->world_x:a->source_x;
        if(px-prior>32 || prior-px>32)continue;
        if(a->state==CVIII_INSTANCE_LIVE && a->guest_slot!=x)
            continue;
        if(linked){linked=0;break;} /* ambiguous duplicate parent */
        linked=x;
    }
    if(linked){
        a->state=CVIII_INSTANCE_LIVE_0826;
        a->guest_slot=(uint8_t)linked;
        a->guest_type=ram[0x54eu+linked];
        a->guest_flags=ram[0x470u+linked];
        a->guest_frame=ram[0x400u+linked];
        a->world_x=camera_x+ram[0x438u+linked];
        a->world_y=ram[0x41cu+linked];
        if(a->original_frames!=UINT32_MAX)a->original_frames++;
        if(w->original_links!=UINT32_MAX)w->original_links++;
        s->state=CVIII_WIDE_CPU_OWNED_0825;
        s->guest_slot=(uint8_t)linked;
        s->guest_frame=a->guest_frame;
        s->guest_flags=a->guest_flags;
        s->last_world_x=a->world_x;
        if(s->cpu_observations!=UINT32_MAX)s->cpu_observations++;
        live++;
    }else if(a->state==CVIII_INSTANCE_LIVE_0826){
        a->state=CVIII_INSTANCE_LOST_0826;
        a->guest_slot=0u;
        s->state=CVIII_WIDE_SOURCE_UNVERIFIED_0825;
        s->guest_slot=0u;
        if(s->orphan_epochs!=UINT32_MAX)s->orphan_epochs++;
        if(w->losses!=UINT32_MAX)w->losses++;
    }
 }
 if(w->total_frames!=UINT32_MAX)w->total_frames++;
 if(source->frame_epoch!=UINT32_MAX)source->frame_epoch++;
 source->live_verified=(uint8_t)(live>0u);
 return (int)live;
}
/* No independent gameplay actions until the entire response/defeat
 * chain is matched; a provenance and display state alone is never
 * permission to apply source simulation damage. */
static inline int cviii_wide_native_combat_ready_0826(
     const CviiiWideInstance0826 *a)
{
 return a && a->state==CVIII_INSTANCE_LIVE_0826 &&
        a->has_combat_parity!=0u;
}
/* B525 first original CPU decision: select original sound ID before
 * JSR $E249. No alleged defeat writes are applied beyond this stop. */
typedef struct {
 uint16_t entry_pc,stop_pc;
 uint8_t original_type,sound_id;
 uint8_t external_sound_required;
} CviiiB525Prefix0826;
static inline int cviii_b525_prefix_0826(
 const uint8_t ram[2048],unsigned x,CviiiB525Prefix0826 *out)
{
 if(!ram || !out || x<1u || x>18u)return 0;
 CviiiB525Prefix0826 r={0};
 r.entry_pc=0xb525u;r.stop_pc=0xb53cu;
 r.original_type=ram[0x54eu+x];
 r.sound_id=(r.original_type==0x3du ||
             r.original_type==0x3eu ||
             r.original_type==0x4bu ||
             r.original_type==0x47u)?0x27u:0x32u;
 r.external_sound_required=1u;
 *out=r;return 1;
}
#endif
