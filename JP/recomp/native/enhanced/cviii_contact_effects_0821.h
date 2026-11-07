/* JP0821: ORIGINAL raw PRG0B $B6CE, $B5DF and $B486 reaction prefixes.
 *
 * Pure predicted 6502 state, not an alternative gameplay simulator.
 * No guest RAM writes, OAM writes, synthesized offscreen actor, damage,
 * pickup, sound or score. Original CPU remains authoritative.
 *
 * Original source:
 *   $B6CE-$B706 actor attribute response (including type $49 sweep)
 *   $B5DF-$B628 slot23 effect installation
 *   $B486-$B4D4 actor reaction gate, stop at external helper
 *
 * Stable symbolic entry labels are internal, NOT future mod IDs.
 */
#ifndef CVIII_CONTACT_EFFECTS_0821_H
#define CVIII_CONTACT_EFFECTS_0821_H
#include <stdint.h>
#include <stddef.h>
enum {
 CVIII_EFFECT_STOP_NONE_0821=0, CVIII_EFFECT_STOP_RTS_0821=1,
 CVIII_EFFECT_STOP_EXTERNAL_0821=2
};
typedef struct {
 uint8_t actor_slot,modified_mask; /* 1..8 original actor slots for type49 */
 uint8_t next_flags[9],next_state[9]; /* only indices in modified_mask valid */
 uint16_t stop_pc;
 uint8_t supported, returned_x; /* type49 sweep exits at X=$09 */
} CviiiB6ceEffect0821;
/* The original type49 path iterates 1..8, not 1..18; it does not
 * require each child's current type >=$30 inside that loop. */
static inline int cviii_effect_b6ce_0821(
    const uint8_t ram[2048],unsigned x,CviiiB6ceEffect0821 *out)
{
 if(!ram || !out || x<1u || x>18u)return 0;
 CviiiB6ceEffect0821 r={0};
 r.actor_slot=(uint8_t)x;r.supported=1u;
 r.stop_pc=0xb6f4u;r.returned_x=(uint8_t)x;
 const uint8_t type=ram[0x054eu+x];
 const unsigned start=type==0x49u ? 1u:x;
 const unsigned end=type==0x49u ? 8u:x;
 if(type==0x49u){
   r.returned_x=9u; /* $B6F5 LD X=1 ... CPX #9 / RTS at $B706 */
   r.stop_pc=0xb706u;
 }
 if(type<0x30u || type>=0x58u){*out=r;return 1;}
 for(unsigned y=start;y<=end;y++){
   const uint8_t old=ram[0x0470u+y];
   if(old&2u)continue;
   r.modified_mask|=(uint8_t)(1u<<(type==0x49u ? y-1u : 0u));
   if(type!=0x49u)r.modified_mask=1u; /* single actor X */
   const unsigned index=type==0x49u ? y:0u;
   r.next_flags[index]=(uint8_t)(old|2u);
   r.next_state[index]=(uint8_t)(ram[0x0565u+y]&0x3fu);
 }
 *out=r;return 1;
}
typedef struct {
 uint8_t accepted,effect_slot,source_actor,original_partner;
 uint8_t source_x,partner_y,restore_actor_slot,flag89;
 uint8_t effect_flags,effect_frame,effect_selector;
 uint16_t stop_pc;
} CviiiB5dfEffect0821;
/* $B5DF checks only $0400+$17; $054E+$17 is not the free predicate.
 * The helper deliberately does not set $054E+$17. */
static inline int cviii_effect_b5df_0821(
    const uint8_t ram[2048],unsigned x,unsigned partner,
    CviiiB5dfEffect0821 *out)
{
 if(!ram || !out || x<1u || x>18u ||
    partner<20u || partner>22u)return 0;
 CviiiB5dfEffect0821 r={0};
 r.effect_slot=23u;r.source_actor=(uint8_t)x;
 r.original_partner=(uint8_t)partner;
 r.stop_pc=0xb628u;
 if(ram[0x0400u+23u]){*out=r;return 1;}
 r.accepted=1u;
 r.source_x=ram[0x0438u+x];
 r.partner_y=ram[0x041cu+partner];
 r.restore_actor_slot=ram[0x69u];
 r.effect_flags=0x20u;
 r.effect_frame=0x12u;
 r.effect_selector=0x0eu;
 r.flag89=8u;
 *out=r;return 1;
}
enum {
 CVIII_B486_SKIP_0821=0,
 CVIII_B486_OTHER_TYPE_0821=1,
 CVIII_B486_NO_CHANGE_0821=2,
 CVIII_B486_DEFER_E75A_0821=3,
 CVIII_B486_DEFER_E249_0821=4,
 CVIII_B486_DEFER_B525_0821=5
};
typedef struct {
 uint8_t actor_slot,original_type,decision,upper_nibble;
 uint8_t new_0669, new_067b,write_0669,write_067b;
 uint16_t stop_pc; /* first instruction of unmodeled response */
} CviiiB486Effect0821;
static inline int cviii_effect_b486_prefix_0821(
    const uint8_t ram[2048],unsigned x,CviiiB486Effect0821 *out)
{
 if(!ram || !out || x<1u || x>18u)return 0;
 CviiiB486Effect0821 r={0};
 r.actor_slot=(uint8_t)x;
 r.original_type=ram[0x054eu+x];
 r.new_0669=ram[0x0669u+x];
 r.new_067b=ram[0x067bu+x];
 if(r.original_type<0x30u){
   r.decision=CVIII_B486_SKIP_0821;r.stop_pc=0xb4d4u;
 }else if(r.original_type>=0x58u){
   r.decision=CVIII_B486_OTHER_TYPE_0821;r.stop_pc=0xb47bu;
 }else if(!(r.new_0669&0xf0u)){
   r.decision=CVIII_B486_NO_CHANGE_0821;r.stop_pc=0xb4d4u;
 }else{
   r.upper_nibble=(uint8_t)(r.new_0669>>4u);
   r.new_0669=(uint8_t)(r.new_0669&0x0fu);
   r.write_0669=1u;
   if(ram[0x0470u+x]&2u){
     r.decision=CVIII_B486_DEFER_E75A_0821;r.stop_pc=0xb4d7u;
   }else{
     r.write_067b=1u;
     r.new_067b=(uint8_t)(r.new_067b-r.upper_nibble);
     if(r.new_067b==0u || (r.new_067b&0x80u)){
       r.decision=CVIII_B486_DEFER_B525_0821;r.stop_pc=0xb525u;
     }else{
       r.decision=CVIII_B486_DEFER_E249_0821;r.stop_pc=0xb4bcu;
     }
   }
 }
 *out=r;
 return 1;
}
/* Source-authenticated $B5DF visual-installation postcondition.
 * This is NOT proof the original CPU executed B5DF in this frame;
 * a matching guest snapshot establishes only a currently live
 * visual-effect signature. Original $054E+23 may still be zero. */
typedef struct {
 uint8_t matched,draw_candidate,frame,selector,flags,type23,x,y;
} CviiiEffect23Witness0821;
static inline CviiiEffect23Witness0821 cviii_effect23_witness_0821(
     const uint8_t ram[2048])
{
 CviiiEffect23Witness0821 w={0};
 if(!ram)return w;
 w.frame=ram[0x0400u+23u];
 w.selector=ram[0x048cu+23u];
 w.flags=ram[0x0470u+23u];
 w.type23=ram[0x054eu+23u];
 w.x=ram[0x0438u+23u];
 w.y=ram[0x041cu+23u];
 w.matched=(w.frame==0x12u && w.selector==0x0eu &&
            w.flags==0x20u);
 w.draw_candidate=w.matched && !(w.flags&0x80u);
 return w;
}

#endif
