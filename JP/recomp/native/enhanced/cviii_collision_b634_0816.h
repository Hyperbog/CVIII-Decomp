/* JP0816: original raw0B:$B634-$B672 first proximity gate only.
 * Includes original raw0B:$80B3 and $B707 absolute-byte arithmetic.
 * Does NOT simulate B115/B18A responses, damage, pickups, collision
 * callbacks or touch guest machine state. Original bank fingerprint
 * must have been validated by caller before supplying bank bytes. */
#ifndef CVIII_COLLISION_B634_0816_H
#define CVIII_COLLISION_B634_0816_H
#include "cviii_collision_route_0816.h"
#include <stdint.h>
enum { CVIII_B634_TO_B115_0816=0xb115,
       CVIII_B634_TO_B18A_0816=0xb18a };
typedef struct {
    uint16_t next_pc;
    uint8_t x_distance,y_distance,measured_y;
    uint8_t scratch0e,scratch10,scratch11; /* original $0E/$10/$11 */
    uint8_t carry;
} CviiiB634Gate0816;
static inline unsigned cviii_abs_unsigned_byte_0816(unsigned a,unsigned b)
{
    return a>=b?a-b:b-a; /* NMOS $80B3 and $B707: no circular shortcut */
}
static inline int cviii_b634_gate_0816(
    const uint8_t ram[2048],const uint8_t raw0b[16384],
    unsigned actor,CviiiB634Gate0816 *out)
{
    if(!ram || !raw0b || !out || actor<1u || actor>18u)return 0;
    const unsigned type=ram[0x054eu+actor];
    const unsigned group=ram[0x7fu];
    if(group>=9u ||
       cviii_b1f8_route_0816((uint8_t)type,ram[0x0470u+actor],
            ram[0x0400u+actor],ram[0x7eu],ram[0x7du])!=0xb634u)
        return 0; /* cannot reach B634 from the modeled B1F8 entry */
    CviiiB634Gate0816 r={0};
    r.x_distance=(uint8_t)cviii_abs_unsigned_byte_0816(
        ram[0x0438u+actor],ram[0x0438u]);
    r.scratch0e=r.x_distance;
    /* $B63C LDA $BB80,Y; $B641 CLC; $B642 ADC $BB05,Y;
     * $B645 CMP $0E; $B647 BCC $B632: SEC/RTS.
     * Addition wraps as an original 8-bit accumulator. */
    const uint8_t allowed_x=(uint8_t)(
        raw0b[0xbb80u+type-0x8000u] +
        raw0b[0xbb05u+group-0x8000u]);
    if(allowed_x < r.x_distance){
        r.carry=1u;
        r.next_pc=CVIII_B634_TO_B115_0816;
        *out=r;return 1;
    }
    /* $B656..$B670 then $B707: vertical comparison and CMP #$0C. */
    r.measured_y=1u;
    r.scratch10=(uint8_t)(
        raw0b[0xb673u+group-0x8000u]+ram[0x041cu]);
    r.scratch11=(uint8_t)(
        ram[0x041cu+actor]-raw0b[0xbc08u+type-0x8000u]);
    r.y_distance=(uint8_t)cviii_abs_unsigned_byte_0816(
         r.scratch11,r.scratch10);
    r.carry=r.y_distance>=12u;
    r.next_pc=r.carry?CVIII_B634_TO_B115_0816:
                            CVIII_B634_TO_B18A_0816;
    *out=r;return 1;
}
#endif
