/* JP0825 native wide-world source admission: *original* row32/type3D.
 * A source record is NOT an enemy until original CPU $8B50 allocates a
 * matching child. Independent source lifetimes survive the camera edge.
 * No speculative collision, weapon, defeat or drop is authorized.
 * The two original room(0,1,0) records are proven against natural
 * Mesen 2.1.1 frame3092: phase3 (160,80), phase4 (192,176).
 *
 * Caller must SHA-authenticate the private original physical bank0A.
 * No copyrighted ROM code/data are compiled into the executable.
 */
#ifndef CVIII_WIDE_SOURCE_ADMISSION_0825_H
#define CVIII_WIDE_SOURCE_ADMISSION_0825_H
#include "cviii_horizontal_sources_0816.h"
#include <stdint.h>
#include <string.h>
enum {
 CVIII_WIDE_SOURCE_COUNT_0825=2,
 CVIII_WIDE_READY_0825=1,
 CVIII_WIDE_CPU_OWNED_0825=2,
 CVIII_WIDE_SOURCE_UNVERIFIED_0825=3
};
typedef struct {
 uint16_t event_cpu, cell_cpu;
 int32_t room_x,room_y,last_world_x;
 uint8_t phase, original_type,script, original_source_slot;
 uint8_t state,guest_slot,guest_frame,guest_flags;
 uint32_t cpu_observations,orphan_epochs;
} CviiiWideSource0825;
typedef struct {
 CviiiWideSource0825 source[CVIII_WIDE_SOURCE_COUNT_0825];
 uint32_t admission_epoch,frame_epoch,identity_breaks;
 uint8_t resident,live_verified;
} CviiiWideSources0825;
static inline int cviii_wide_admit_original_0825(
  CviiiWideSources0825 *w,const CviiiHorizontalRoom0816 *room,
  const uint8_t raw0a[16384],unsigned n)
{
 if(!w || !room || !room->valid || room->count!=6u ||
    !raw0a || n!=16384u)return 0;
 CviiiWideSources0825 next={0};
 /* Original source $8D5E: row32 script $13, actor type $3D. */
 if(raw0a[0x91c6u-0x8000u]!=0x13u ||
    raw0a[0x921eu-0x8000u]!=0x3du)return 0;
 for(unsigned k=0;k<CVIII_WIDE_SOURCE_COUNT_0825;k++){
    unsigned phase=k+3u;
    const CviiiHorizontalPair0816 *p=&room->pairs[phase];
    const unsigned pc=p->event_record_cpu[0];
    if((phase==3u && (p->event_id!=0xa0u || pc!=0xa444u)) ||
       (phase==4u && (p->event_id!=0x9fu || pc!=0xa43fu)) ||
       p->event_row[0]!=0x32u || pc<0x8000u || pc>0xbffbu)
         return 0;
    const uint8_t *rec=&raw0a[pc-0x8000u];
    if(rec[0]!=0x32u || rec[3] || rec[4])return 0;
    CviiiWideSource0825 *s=&next.source[k];
    s->phase=(uint8_t)phase;s->original_source_slot=(uint8_t)phase;
    s->event_cpu=(uint16_t)pc;s->cell_cpu=p->cell_cpu;
    s->original_type=0x3du;s->script=0x13u;
    /* Original cell phase origin, verified only for THESE two
     * naturally created actors. No extrapolation to other rooms. */
    s->room_x=(int32_t)((phase-1u)*64u+rec[1]);
    s->room_y=rec[2];
    if((phase==3u && (s->room_x!=160 || s->room_y!=80)) ||
       (phase==4u && (s->room_x!=192 || s->room_y!=176)))return 0;
    s->state=CVIII_WIDE_READY_0825;
 }
 next.resident=1u;next.admission_epoch=1u;
 *w=next;return 1;
}
/* Source survives after actor leaves original visibility; a guest
 * child can only be owned with original $054E/$0470/$0645 witnesses.
 * Deallocated guest does NOT create a replacement native enemy.
 * Returns number of original CPU-owned actor links. */
static inline int cviii_wide_sample_original_0825(
    CviiiWideSources0825 *w,const uint8_t ram[2048],
    const uint8_t room_key[3],int32_t camera_x)
{
 if(!w || !w->resident || !ram || !room_key ||
    room_key[0]!=0 || room_key[1]!=1 || room_key[2]!=0 ||
    camera_x<0 || camera_x>512)return -1;
 unsigned active=0;
 for(unsigned k=0;k<CVIII_WIDE_SOURCE_COUNT_0825;k++){
    CviiiWideSource0825 *s=&w->source[k];
    int found=0;
    for(unsigned x=1u;x<=12u;x++){
        if(ram[0x54eu+x]!=0x3du ||
           !(ram[0x470u+x]&4u) ||
           ram[0x645u+x]!=s->original_source_slot)
            continue;
        /* A real child may have been added after leaving the view.
         * Do not equate a script record with an active actor. */
        const int32_t screen=ram[0x438u+x];
        const int32_t candidate=camera_x+screen;
        if(s->state==CVIII_WIDE_READY_0825 &&
           candidate-s->room_x>32)continue;
        if(s->state==CVIII_WIDE_READY_0825 &&
           s->room_x-candidate>32)continue;
        if(found){found=-1;break;} /* slot alias ambiguity */
        found=(int)x;
    }
    if(found>0){
        const unsigned x=(unsigned)found;
        if(s->state==CVIII_WIDE_CPU_OWNED_0825 &&
           s->guest_slot!=x && w->identity_breaks!=UINT32_MAX)
           w->identity_breaks++;
        s->state=CVIII_WIDE_CPU_OWNED_0825;
        s->guest_slot=(uint8_t)x;
        s->guest_frame=ram[0x400u+x];
        s->guest_flags=ram[0x470u+x];
        s->last_world_x=camera_x+(int32_t)ram[0x438u+x];
        if(s->cpu_observations!=UINT32_MAX)s->cpu_observations++;
        active++;
    }else{
        if(s->state==CVIII_WIDE_CPU_OWNED_0825){
            s->state=CVIII_WIDE_SOURCE_UNVERIFIED_0825;
            if(s->orphan_epochs!=UINT32_MAX)s->orphan_epochs++;
        }
        s->guest_slot=0;
    }
 }
 if(w->frame_epoch!=UINT32_MAX)w->frame_epoch++;
 w->live_verified=(uint8_t)(active>0u);
 return (int)active;
}
/* Authoritative actions are *not* permitted for inferred source objects.
 * Those actions require source-backed CPU AI and effect-write parity
 * still missing from the current wide-viewport implementation. */
static inline int cviii_wide_interaction_allowed_0825(
 const CviiiWideSource0825 *s)
{
 (void)s;return 0;
}
#endif
