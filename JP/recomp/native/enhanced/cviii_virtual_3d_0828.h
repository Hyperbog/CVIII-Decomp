/* JP0828: persistent, independently stepped original-6502 type3D
 * actor movement AFTER its original guest CPU slot detaches.
 * The movement at bank0B:$8001-$804A is source-authenticated and
 * natural-Mesen traced. Animation, reactions, damage, loot and
 * projectile contacts are NOT authorized by this partial executor.
 *
 * Virtual RAM is private to every instance and survives loss of the
 * original allocator slot. No execution can write the real NES CPU,
 * PPU, APU, mapper, guest OAM or game/savestate memory.
 */
#ifndef CVIII_VIRTUAL_3D_0828_H
#define CVIII_VIRTUAL_3D_0828_H
#include "cviii_actor_vm_0827.h"
#include "cviii_wide_instance_0826.h"
#include <stdint.h>
#include <string.h>
enum {
 CVIII_VIRTUAL_0828_UNSPAWNED=0,
 CVIII_VIRTUAL_0828_LINKED=1,
 CVIII_VIRTUAL_0828_DETACHED=2,
 CVIII_VIRTUAL_0828_FAULTED=3
};
typedef struct {
 CviiiActorVM0827 cpu;
 uint16_t source_cpu;
 int32_t world_x,world_y;
 uint32_t attached_frames,detached_frames;
 uint8_t state,original_slot,original_parent;
 uint8_t original_frame,original_flags;
 uint8_t collision_parity,interaction_authorized;
} CviiiVirtual3D0828;
typedef struct {
 CviiiVirtual3D0828 actor[CVIII_WIDE_SOURCE_COUNT_0825];
 uint32_t native_ticks,detached_steps,faults;
 uint8_t initialized;
} CviiiVirtualActors0828;
static inline void cviii_virtual_reset_0828(CviiiVirtualActors0828 *v,
     const CviiiWideSources0825 *source)
{
 if(!v)return;
 memset(v,0,sizeof *v);
 if(!source || !source->resident)return;
 for(unsigned i=0;i<CVIII_WIDE_SOURCE_COUNT_0825;i++){
    v->actor[i].source_cpu=source->source[i].event_cpu;
    v->actor[i].original_parent=
        source->source[i].original_source_slot;
    v->actor[i].world_x=source->source[i].room_x;
    v->actor[i].world_y=source->source[i].room_y;
 }
 v->initialized=1u;
}
static inline int cviii_virtual_tick_0828(
     CviiiVirtualActors0828 *v,const CviiiWideSources0825 *source,
     const uint8_t raw0b[16384],const uint8_t ram[2048],
     const uint8_t key[3],int32_t camera_x)
{
 if(!v || !v->initialized || !source || !source->resident ||
    !raw0b || !ram || !key ||
    key[0]!=0u || key[1]!=1u || key[2]!=0u ||
    camera_x<0 || camera_x>512)return -1;
 unsigned detached=0;
 for(unsigned i=0;i<CVIII_WIDE_SOURCE_COUNT_0825;i++){
    CviiiVirtual3D0828 *a=&v->actor[i];
    const CviiiWideSource0825 *s=&source->source[i];
    if(!a->source_cpu || a->source_cpu!=s->event_cpu ||
       a->state==CVIII_VIRTUAL_0828_FAULTED)continue;
    const unsigned x=s->guest_slot;
    const int linked=s->state==CVIII_WIDE_CPU_OWNED_0825 &&
       x>=1u && x<=12u &&
       ram[0x054eu+x]==0x3du &&
       (ram[0x0470u+x]&4u) &&
       ram[0x0645u+x]==a->original_parent;
    if(linked && a->state!=CVIII_VIRTUAL_0828_DETACHED){
        /* Original guest remains authoritative while linked.
         * Snapshot the guest RAM after its *real* CPU update, to
         * seed a later isolated movement frame if it detaches. */
        if(a->state==CVIII_VIRTUAL_0828_UNSPAWNED ||
           a->original_slot==x){
            if(!cviii_vm_init_0827(&a->cpu,ram,x,0x8001u)){
                a->state=CVIII_VIRTUAL_0828_FAULTED;v->faults++;
                continue;
            }
            a->state=CVIII_VIRTUAL_0828_LINKED;
            a->original_slot=(uint8_t)x;
            a->original_frame=ram[0x0400u+x];
            a->original_flags=ram[0x0470u+x];
            /* Original page bit0 distinguishes the adjacent 256px
             * page; choose nearest of +/-256 from the previously
             * witnessed absolute world location, not a screen-wrap
             * teleport. A center-page actor uses its ordinary X. */
            const int32_t local=camera_x+(int32_t)ram[0x0438u+x];
            int32_t projected=local;
            if(ram[0x0470u+x]&1u){
                const int32_t right=local+256;
                const int32_t left=local-256;
                const int64_t dr=(int64_t)right-a->world_x;
                const int64_t dl=(int64_t)left-a->world_x;
                const uint64_t ar=(uint64_t)(dr<0?-dr:dr);
                const uint64_t al=(uint64_t)(dl<0?-dl:dl);
                projected=ar<=al?right:left;
            }
            /* Guest-owned movement remains authoritative; allow it
             * to move through original-page rollover only when
             * the original actor's identity/position are continuous. */
            if(a->attached_frames &&
               (projected-a->world_x>32 ||
                a->world_x-projected>32)){
                a->state=CVIII_VIRTUAL_0828_FAULTED;
                if(v->faults!=UINT32_MAX)v->faults++;
                continue;
            }
            a->world_x=projected;
            a->world_y=ram[0x041cu+x];
            if(a->attached_frames!=UINT32_MAX)a->attached_frames++;
        }else{
            a->state=CVIII_VIRTUAL_0828_FAULTED;
            if(v->faults!=UINT32_MAX)v->faults++;
        }
        continue;
    }
    if(a->state==CVIII_VIRTUAL_0828_UNSPAWNED)
        continue; /* source records alone NEVER fabricate actors */
    if(a->state==CVIII_VIRTUAL_0828_LINKED){
        /* Original type-zero is NOT proof of a harmless offscreen
         * despawn: normal in-viewport actor death must never be
         * resurrected by a stale private movement timeline.
         * Require previously witnessed adjacent-page bit0 plus
         * OAM-cull bit7 AND an absolute position outside the
         * original 256px gameplay strip. Even this is only a
         * conservative offscreen detachment CANDIDATE. */
        const int adjacent=(a->original_flags&0x81u)==0x81u;
        const int outside=a->world_x<camera_x ||
                          a->world_x>=camera_x+256;
        if(!adjacent || !outside){
            a->state=CVIII_VIRTUAL_0828_FAULTED;
            if(v->faults!=UINT32_MAX)v->faults++;
            continue;
        }
        a->state=CVIII_VIRTUAL_0828_DETACHED;
    }
    if(a->state!=CVIII_VIRTUAL_0828_DETACHED)continue;
    const unsigned slot=a->original_slot;
    if(slot<1u || slot>12u){
        a->state=CVIII_VIRTUAL_0828_FAULTED;
        if(v->faults!=UINT32_MAX)v->faults++;
        continue;
    }
    const uint8_t old_x=a->cpu.ram[0x0438u+slot];
    const uint8_t old_y=a->cpu.ram[0x041cu+slot];
    const uint8_t old_flag=a->cpu.ram[0x0470u+slot];
    CviiiActorVM0827 step={0};
    /* Preserve all private guest scratch and actor state between
     * frames, resetting only the 6502 CALL frame's registers. */
    if(!cviii_vm_init_0827(&step,a->cpu.ram,slot,0x8001u) ||
       !cviii_vm_run_0827(&step,raw0b,96u) ||
       step.stop_kind!=CVIII_VM_STOP_RTS_0827 ||
       step.stop_pc!=0x8036u){
        a->state=CVIII_VIRTUAL_0828_FAULTED;
        if(v->faults!=UINT32_MAX)v->faults++;
        continue;
    }
    /* Original bit0 in $0470 carries the 9-bit X page across 8-bit
     * position rollover. A detached original velocity cannot
     * legitimately move more than 256px in one actor tick. */
    const int before=old_x+((old_flag&1u)?256:0);
    const int after=step.ram[0x0438u+slot]+
                    ((step.ram[0x0470u+slot]&1u)?256:0);
    int dx=after-before;
    if(dx>256)dx-=512;
    if(dx< -256)dx+=512;
    const int dy0=(int)step.ram[0x041cu+slot]-(int)old_y;
    const int dy=dy0>127 ? dy0-256:
                 dy0< -128 ? dy0+256:dy0;
    if(dx>32 || dx< -32 || dy>32 || dy< -32){
       a->state=CVIII_VIRTUAL_0828_FAULTED;
       if(v->faults!=UINT32_MAX)v->faults++;
       continue;
    }
    a->world_x+=dx;
    a->world_y+=dy;
    a->cpu=step; /* all 2KiB remain instance-local */
    if(a->detached_frames!=UINT32_MAX)a->detached_frames++;
    if(v->detached_steps!=UINT32_MAX)v->detached_steps++;
    detached++;
 }
 if(v->native_ticks!=UINT32_MAX)v->native_ticks++;
 return (int)detached;
}
/* Original actor world collision is NOT enabled here. A source-linked,
 * moving native instance cannot inflict damage just because its ROM
 * movement matched. Collision/defeat effects must be separately proven. */
static inline int cviii_virtual_can_apply_effect_0828(
   const CviiiVirtual3D0828 *a)
{
 return a && a->state==CVIII_VIRTUAL_0828_DETACHED &&
        a->collision_parity && a->interaction_authorized;
}
#endif
