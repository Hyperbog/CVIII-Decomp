/* JP0828: ORIGINAL B447 special partner-hit input projection.
 * Use full world-space X for the 426px viewport rather than
 * wrapping an offscreen actor into the 256px guest screen.
 * Only original table dimensions and eligible original
 * partner actors 20..22 are accepted. Unknown page/special
 * type05/$B7 states STOP before any contact side effects.
 *
 * This is a verified proximity INPUT oracle, not permission to
 * apply damage, weapon consumption, score, defeat or loot.
 */
#ifndef CVIII_VIRTUAL_COLLISION_0828_H
#define CVIII_VIRTUAL_COLLISION_0828_H
#include "cviii_virtual_3d_0828.h"
#include <stdint.h>
enum {
 CVIII_VCOL_UNVERIFIED_0828=0,
 CVIII_VCOL_FAR_0828=1,
 CVIII_VCOL_NEAR_0828=2,
 CVIII_VCOL_MASKED_0828=3
};
typedef struct {
 uint8_t outcome,partner,mask,original_type;
 uint16_t actor_distance_x,actor_distance_y;
 uint8_t radius_x,radius_y;
} CviiiVirtualCollision0828;
static inline int cviii_virtual_partner_input_0828(
 const CviiiVirtual3D0828 *a,const uint8_t guest[2048],
 const uint8_t raw0b[16384],int32_t room_camera,
 unsigned partner,CviiiVirtualCollision0828 *out)
{
 if(!a || !guest || !raw0b || !out ||
    a->state!=CVIII_VIRTUAL_0828_DETACHED ||
    a->original_slot<1u || a->original_slot>12u ||
    a->cpu.ram[0x054eu+a->original_slot]!=0x3du ||
    room_camera<0 || room_camera>512 ||
    partner<20u || partner>22u)return 0;
 CviiiVirtualCollision0828 r={0};
 r.partner=(uint8_t)partner;
 r.mask=(uint8_t)(2u<<(partner-20u));
 r.original_type=guest[0x054eu+partner];
 if(!r.original_type){
    r.outcome=CVIII_VCOL_FAR_0828;
    *out=r;return 1;
 }
 if(a->cpu.ram[0x068du+a->original_slot]&r.mask){
    r.outcome=CVIII_VCOL_MASKED_0828;
    *out=r;return 1;
 }
 /* Bank0B:B447 applies special $0593,X for type05 and B7 external
  * helper for altered collision. Neither can be inferred. */
 if(r.original_type==5u || r.original_type>=11u ||
    guest[0xb7u] || (guest[0x0470u+partner]&1u)){
    r.outcome=CVIII_VCOL_UNVERIFIED_0828;
    *out=r;return 1;
 }
 const int32_t partner_world=room_camera+
     (int32_t)guest[0x0438u+partner];
 int64_t dx=(int64_t)a->world_x-(int64_t)partner_world;
 if(dx<0)dx=-dx;
 int64_t dy=(int64_t)a->world_y-
      (int64_t)guest[0x041cu+partner];
 if(dy<0)dy=-dy;
 r.actor_distance_x=(uint16_t)(dx>65535?65535:dx);
 r.actor_distance_y=(uint16_t)(dy>65535?65535:dy);
 r.radius_x=(uint8_t)(
     raw0b[0xbb80u+0x3du-0x8000u]+
     raw0b[0xbb60u+r.original_type-0x8000u]);
 r.radius_y=(uint8_t)(
     raw0b[0xbc08u+0x3du-0x8000u]+
     raw0b[0xbb6bu+r.original_type-0x8000u]);
 r.outcome=(r.actor_distance_x<r.radius_x &&
            r.actor_distance_y<r.radius_y)?
           CVIII_VCOL_NEAR_0828:CVIII_VCOL_FAR_0828;
 *out=r;return 1;
}
#endif
