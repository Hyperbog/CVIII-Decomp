/* JP0846: original B447 inputs for previously genuine detached type3D.
 * Not a collision effect, AI, damage, defeat or audio implementation.
 * Nothing here writes original NES CPU/PPU/APU/mapper/OAM state.
 */
#ifndef CVIII_DETACHED_CONTACTS_0846_H
#define CVIII_DETACHED_CONTACTS_0846_H
#include "cviii_virtual_collision_0828.h"
#include <stdint.h>
#include <string.h>
typedef struct {
 CviiiVirtualCollision0828 contact[CVIII_WIDE_SOURCE_COUNT_0825][3];
 uint8_t sampled[CVIII_WIDE_SOURCE_COUNT_0825];
 uint8_t near[CVIII_WIDE_SOURCE_COUNT_0825];
 uint8_t unknown[CVIII_WIDE_SOURCE_COUNT_0825];
 uint8_t masked[CVIII_WIDE_SOURCE_COUNT_0825];
 uint32_t frames,near_inputs,unknown_inputs;
} CviiiDetachedContacts0846;
static inline void cviii_detached_contacts_clear_0846(CviiiDetachedContacts0846 *c){
 if(c)memset(c,0,sizeof *c);
}
/* Only call after a verified Stage1-02 camera and source-authenticated
 * private $8001 movement tick. Unsupported states clear current results. */
static inline int cviii_detached_contacts_tick_0846(
 CviiiDetachedContacts0846 *c,const CviiiVirtualActors0828 *v,
 const CviiiWideSources0825 *s,const uint8_t guest[2048],
 const uint8_t raw0b[16384],const uint8_t room[3],int32_t camera_x)
{
 if(!c)return -1;
 uint32_t frames=c->frames,near_inputs=c->near_inputs;
 uint32_t unknown_inputs=c->unknown_inputs;
 memset(c,0,sizeof *c);
 c->frames=frames;c->near_inputs=near_inputs;
 c->unknown_inputs=unknown_inputs;
 if(!v || !v->initialized || !s || !s->resident ||
    !guest || !raw0b || !room ||
    room[0]!=0u || room[1]!=1u || room[2]!=0u ||
    camera_x<0 || camera_x>512)return -1;
 int near=0;
 for(unsigned i=0;i<CVIII_WIDE_SOURCE_COUNT_0825;i++){
  const CviiiVirtual3D0828 *a=&v->actor[i];
  const CviiiWideSource0825 *src=&s->source[i];
  unsigned slot=a->original_slot;
  if(a->state!=CVIII_VIRTUAL_0828_DETACHED || !a->detached_frames ||
     !a->source_cpu || a->source_cpu!=src->event_cpu ||
     a->original_parent!=src->original_source_slot ||
     src->original_type!=0x3du ||
     src->state!=CVIII_WIDE_SOURCE_UNVERIFIED_0825 ||
     slot<1u || slot>12u ||
     (a->original_flags&0x81u)!=0x81u ||
     a->cpu.ram[0x054eu+slot]!=0x3du ||
     a->cpu.ram[0x0645u+slot]!=a->original_parent ||
     (a->world_x>=camera_x && a->world_x<camera_x+256) ||
     guest[0x054eu+slot]==0x3du)continue;
  for(unsigned p=20u;p<=22u;p++){
   CviiiVirtualCollision0828 r={0};
   if(!cviii_virtual_partner_input_0828(
      a,guest,raw0b,camera_x,p,&r))continue;
   c->contact[i][p-20u]=r;
   c->sampled[i]|=r.mask;
   if(r.outcome==CVIII_VCOL_NEAR_0828){
    c->near[i]|=r.mask;
    if(c->near_inputs!=UINT32_MAX)c->near_inputs++;
    near++;
   }else if(r.outcome==CVIII_VCOL_UNVERIFIED_0828){
    c->unknown[i]|=r.mask;
    if(c->unknown_inputs!=UINT32_MAX)c->unknown_inputs++;
   }else if(r.outcome==CVIII_VCOL_MASKED_0828)
    c->masked[i]|=r.mask;
  }
 }
 if(c->frames!=UINT32_MAX)c->frames++;
 return near;
}
#endif
