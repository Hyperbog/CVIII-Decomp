/* JP0819: bounded original raw0B:$B3EC-$B446 preflight and
 * $B29D-$B31F partner scan, entirely read-only.
 * Caller must SHA-authenticate original raw0B and its caller.
 *
 * B3EC returns carry (far) or clear (near) only when original
 * $B7==0. With $B7 nonzero original $E5BE/$B767 decide other
 * branches, and we STOP without inventing their results.
 *
 * Partner scanning stops BEFORE $B727, $B5DF, $B486, $B6CE:
 * none of their game-state interactions are simulated.
 */
#ifndef CVIII_INTERACTION_PREFLIGHT_0819_H
#define CVIII_INTERACTION_PREFLIGHT_0819_H
#include <stdint.h>
enum {
  CVIII_0819_UNKNOWN=0, CVIII_0819_FAR=1,
  CVIII_0819_NEAR=2
};
typedef struct {
  uint16_t stop_pc;
  uint8_t decision,carry,needs_e5be;
  uint8_t x_distance,y_distance,checked_y;
  uint8_t proposed_player_x,proposed_player_y;
  uint8_t clearance_x,clearance_y;
} CviiiB3ec0819;
static inline unsigned cviii_abs8_0819(unsigned a,unsigned b){
  return a>=b?a-b:b-a;
}
static inline int cviii_b3ec_preflight_0819(
    const uint8_t ram[2048],const uint8_t raw0b[16384],
    unsigned x,CviiiB3ec0819 *out)
{
  if(!ram || !raw0b || !out || x<1u || x>18u ||
     ram[0x0561u]>3u || ram[0x7fu]>=9u)return 0;
  CviiiB3ec0819 r={0};
  r.x_distance=(uint8_t)cviii_abs8_0819(ram[0x0438u+x],
                                              ram[0x0438u]);
  if(r.x_distance>=0x80u){
    r.stop_pc=0xb446u;r.decision=CVIII_0819_FAR;r.carry=1u;
    *out=r;return 1;
  }
  const unsigned p=ram[0x0561u];
  const unsigned pose=((p<<1u)+ram[0x04a8u])&255u;
  /* The original $BB1F pose table spans eight bytes.
   * Unsupported other-state values may read adjacent tables;
   * refuse those rather than fabricate hitbox dimensions. */
  if(pose>=8u)return 0;
  const unsigned group=ram[0x7fu],type=ram[0x054eu+x];
  const uint8_t base_x=raw0b[0xbb17u+p-0x8000u];
  const uint8_t base_y=raw0b[0xbb1bu+p-0x8000u];
  r.proposed_player_x=(uint8_t)(ram[0x0438u]+
                  raw0b[0xbb1fu+pose-0x8000u]);
  r.proposed_player_y=(uint8_t)(ram[0x042fu]+
                  raw0b[0xbb27u+group-0x8000u]);
  if(ram[0xb7u]){
    r.needs_e5be=1u;r.stop_pc=0xb41fu;
    *out=r;return 1;
  }
  r.clearance_x=(uint8_t)(raw0b[0xbb80u+type-0x8000u]+base_x);
  r.x_distance=(uint8_t)cviii_abs8_0819(
           ram[0x0438u+x],r.proposed_player_x);
  if(r.x_distance>=r.clearance_x){
    r.stop_pc=0xb446u;r.decision=CVIII_0819_FAR;r.carry=1u;
    *out=r;return 1;
  }
  r.checked_y=1u;
  r.clearance_y=(uint8_t)(raw0b[0xbc08u+type-0x8000u]+base_y);
  r.y_distance=(uint8_t)cviii_abs8_0819(
           ram[0x041cu+x],r.proposed_player_y);
  r.decision=r.y_distance>=r.clearance_y ?
          CVIII_0819_FAR:CVIII_0819_NEAR;
  r.carry=(uint8_t)(r.decision==CVIII_0819_FAR);
  r.stop_pc=0xb446u;
  *out=r;return 1;
}
typedef struct {
  uint16_t stop_pc;
  uint8_t first_partner_slot;   /* 0xff when no candidate */
  uint8_t decision,mask,mask_suppressed;
  uint8_t tested_partners,skipped_empty,skipped_masked;
  uint8_t x_distance,y_distance;
} CviiiPartnerPreflight0819;
static inline int cviii_partner_scan_0819(
    const uint8_t ram[2048],const uint8_t raw0b[16384],
    unsigned x,CviiiPartnerPreflight0819 *out)
{
  if(!ram || !raw0b || !out || x<1u || x>18u)return 0;
  static const uint8_t bits[3]={2u,4u,8u};
  CviiiPartnerPreflight0819 r={0};
  r.stop_pc=0xb31fu;r.first_partner_slot=0xffu;
  const unsigned type=ram[0x054eu+x];
  for(unsigned slot=20u;slot<=22u;slot++){
    const unsigned i=slot-20u;
    const unsigned other_type=ram[0x054eu+slot];
    if(!other_type){r.skipped_empty++;continue;}
    if(ram[0x068du+x]&bits[i]){
      r.skipped_masked++;continue;
    }
    r.first_partner_slot=(uint8_t)slot;r.mask=bits[i];
    /* Original B447 type05 uses $0593,X and special $BB76
     * radius, so the generic type-table branch is not applicable. */
    if(other_type==5u || other_type>=11u || ram[0xb7u]){
      r.stop_pc=0xb447u;*out=r;return 1;
    }
    const uint8_t dx=(uint8_t)cviii_abs8_0819(
          ram[0x0438u+x],ram[0x0438u+slot]);
    const uint8_t allowed_x=(uint8_t)(
          raw0b[0xbb80u+type-0x8000u]+
          raw0b[0xbb60u+other_type-0x8000u]);
    r.tested_partners++;
    r.x_distance=dx;
    if(dx>=allowed_x)continue;
    const uint8_t dy=(uint8_t)cviii_abs8_0819(
          ram[0x041cu+x],ram[0x041cu+slot]);
    const uint8_t allowed_y=(uint8_t)(
          raw0b[0xbc08u+type-0x8000u]+
          raw0b[0xbb6bu+other_type-0x8000u]);
    r.y_distance=dy;
    if(dy>=allowed_y)continue;
    /* Original $B2B5 JSR $B727: stop before game state writes.
     * The exact next response depends on B727/B32D/B6CE/B5DF. */
    r.stop_pc=0xb2b5u;r.decision=CVIII_0819_NEAR;
    *out=r;return 1;
  }
  r.decision=CVIII_0819_FAR;
  r.first_partner_slot=0xffu;r.stop_pc=0xb31fu;
  *out=r;return 1;
}
#endif
