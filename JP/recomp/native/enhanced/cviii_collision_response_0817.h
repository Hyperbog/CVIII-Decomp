/* JP0817: original raw0B $B115-$B155 and $B18A-$B1C8.
 * B115 invokes $B80E (separate actor proximity metric); only its
 * original carry is reproduced. B18A may clear $AC or update $7E,
 * $0669,X. This is a PREDICTION: never apply these writes to guest.
 * It stops at $B249 or $B258 before collision response callbacks. */
#ifndef CVIII_B115_B18A_RESPONSE_0817_H
#define CVIII_B115_B18A_RESPONSE_0817_H
#include "cviii_collision_route_0816.h"
#include <stdint.h>
enum {
    CVIII_RESPONSE_7E_0817=1,
    CVIII_RESPONSE_AC_0817=2,
    CVIII_RESPONSE_0669_0817=4
};
typedef struct {
    uint16_t next_pc;
    uint8_t predicted_7e,predicted_ac,predicted_0669;
    uint8_t write_mask,checked_b80e,b80e_carry;
    uint8_t b80e_x,b80e_y,b80e_checked_y;
} CviiiResponse0817;
/* $80B3: true absolute difference; B80E's negative vertical branch
 * uses EOR #$FF (without ADC #1), making the result abs(delta)-1. */
static inline unsigned cviii_abs_byte_0817(unsigned a,unsigned b){
    return a>=b?a-b:b-a;
}
static inline unsigned cviii_b80e_carry_0817(
    const uint8_t ram[2048],const uint8_t b[16384],
    unsigned x,CviiiResponse0817 *out)
{
    const unsigned type=ram[0x054eu+x],group=ram[0x7fu];
    const unsigned distance=cviii_abs_byte_0817(
            ram[0x0438u+x],ram[0x0438u]);
    const uint8_t threshold=(uint8_t)(
         b[0xbb80u+type-0x8000u]+b[0xbb05u+group-0x8000u]);
    out->checked_b80e=1u;
    out->b80e_x=(uint8_t)distance;
    if(distance>=threshold)return 1u; /* $B823 CMP; BCS $B849 */
    const uint8_t player=(uint8_t)(
          ram[0x041cu]-b[0xb97du+group-0x8000u]);
    const uint8_t actor=(uint8_t)(
          ram[0x041cu+x]+b[0xbc08u+type-0x8000u]);
    const uint8_t difference=(uint8_t)(player-actor);
    const unsigned result=player>=actor ?
          (unsigned)difference:(unsigned)(difference^0xffu);
    out->b80e_checked_y=1u;
    out->b80e_y=(uint8_t)result;
    return result>=8u;
}
/* Only original B634 callers from $B162 eligible types $69-$7F.
 * Source type $80 is rejected; this function must never be reused
 * as an Enhanced offscreen hitbox or pickup callback. */
static inline int cviii_response_b115_b18a_0817(
    const uint8_t ram[2048],const uint8_t b[16384],
    unsigned x,unsigned entry,CviiiResponse0817 *dst)
{
    if(!ram || !b || !dst || x<1u || x>18u ||
       (entry!=0xb115u && entry!=0xb18au) ||
       ram[0x7fu]>=9u)return 0;
    const uint8_t type=ram[0x054eu+x];
    if(type<0x69u || type>=0x80u ||
       cviii_b1f8_route_0816(type,ram[0x0470u+x],
           ram[0x0400u+x],ram[0x7eu],ram[0x7du])!=0xb634u)
         return 0;
    CviiiResponse0817 r={0};
    r.predicted_7e=ram[0x7eu];
    r.predicted_ac=ram[0xacu];
    r.predicted_0669=ram[0x0669u+x];
    r.next_pc=0xb249u;
    if(entry==0xb115u){
        /* $B115 LDA $7E; CMP #1; BEQ $B138 JMP $B258. */
        if(r.predicted_7e==1u)r.next_pc=0xb258u;
        else {
            r.b80e_carry=(uint8_t)cviii_b80e_carry_0817(
                  ram,b,x,&r);
            if(r.b80e_carry)r.next_pc=0xb258u;
            else if(type==0x6du){
                if(ram[0x0657u+x]){
                    r.predicted_7e=0x0cu;
                    r.write_mask|=CVIII_RESPONSE_7E_0817;
                }
            } else if(type==0x72u){
                if(ram[0x0657u+x]){
                    r.predicted_7e=ram[0x0606u+x]?0x0cu:0x1cu;
                    r.write_mask|=CVIII_RESPONSE_7E_0817;
                }
            } else {
                const unsigned y=((unsigned)(uint8_t)(type-0x69u)<<1u)&255u;
                r.predicted_7e=b[0xb0e3u+y-0x8000u];
                r.write_mask|=CVIII_RESPONSE_7E_0817;
            }
        }
    } else {
        /* $B18A: five AC ownership exceptions, then three special
         * $0657 dispatches. Clearing $AC also changes accumulator
         * to zero before the fallback source lookup at $B0E2,Y. */
        unsigned a=type;
        if(type==0x6eu || type==0x74u || type==0x76u ||
           type==0x77u || type==0x78u){
            if(r.predicted_ac && x==ram[0xb5u]){
                r.next_pc=0xb258u;
                *dst=r;return 1;
            }
            if(r.predicted_ac){
                r.predicted_ac=0u;
                r.write_mask|=CVIII_RESPONSE_AC_0817;
                a=0u;
            }
        }
        if(a==0x6du || a==0x72u || a==0x73u)
             r.predicted_7e=ram[0x0657u+x];
        else {
             const unsigned y=((a-0x69u)&255u)<<1u&255u;
             r.predicted_7e=b[0xb0e2u+y-0x8000u];
        }
        r.write_mask|=CVIII_RESPONSE_7E_0817|
                      CVIII_RESPONSE_0669_0817;
        r.predicted_0669=0x10u;
    }
    *dst=r;return 1;
}
#endif
