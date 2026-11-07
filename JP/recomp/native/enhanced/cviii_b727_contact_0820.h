/* JP0820: read-only original raw0B:$B727-$B739 and
 * $B2B5-$B30A contact-effect prefix.
 *
 * Requires a carry-clear original B447 partner check. It returns
 * the exact predicted guest RAM write postconditions only; the
 * interpreter/compiled original remains authoritative. It does
 * NOT run B6CE, B5DF, B486, apply damage or award pickups.
 */
#ifndef CVIII_B727_CONTACT_0820_H
#define CVIII_B727_CONTACT_0820_H
#include <stdint.h>
enum { CVIII_B727_NEXT_B6CE_0820=0xb30bu,
       CVIII_B727_NEXT_B5DF_0820=0xb311u };
typedef struct {
    uint8_t actor_slot, partner_slot, original_partner_type;
    uint8_t increment_99, new_99, new_068d, new_0669_actor;
    uint8_t new_061d_partner, new_0669_partner;
    uint8_t write_0669_partner, adc_overflow, mask_bit;
    uint8_t b32d_special_contact;
    uint16_t next_pc;
} CviiiB727Contact0820;
/* Original $B447 carry-clear must be independently established by
 * the caller. Synthetic proximity is never gameplay authority. */
static inline int cviii_b727_predict_0820(
    const uint8_t ram[2048],unsigned actor,unsigned partner,
    int original_b447_near,CviiiB727Contact0820 *out)
{
    if(!ram || !out || !original_b447_near || actor<1u || actor>18u ||
       partner<20u || partner>22u || !ram[0x054eu+actor] ||
       !ram[0x054eu+partner])return 0;
    CviiiB727Contact0820 r={0};
    r.actor_slot=(uint8_t)actor;
    r.partner_slot=(uint8_t)partner;
    const uint8_t type=ram[0x054eu+partner];
    r.original_partner_type=type;
    /* $B727: player type2 + partner type8 avoids INC $99. */
    r.increment_99=(ram[0x054eu]!=2u || type!=8u);
    r.new_99=(uint8_t)(ram[0x99u]+r.increment_99);
    /* $B323 -> ORA $B320,Y -> STA $068D,X */
    r.mask_bit=(uint8_t)(2u<<(partner-20u));
    r.new_068d=(uint8_t)(ram[0x068du+actor]|r.mask_bit);
    /* $B2C0 CLC; $0606,Y&$F0 + $0669,X; on carry use
     * original $0669,X|$F0 instead of the ADC value. */
    const unsigned total=(unsigned)(ram[0x0606u+partner]&0xf0u)+
                         (unsigned)ram[0x0669u+actor];
    r.adc_overflow=total>255u;
    const uint8_t intermediate=(uint8_t)(r.adc_overflow ?
          (ram[0x0669u+actor]|0xf0u):(uint8_t)total);
    r.new_0669_actor=(uint8_t)((intermediate&0xf0u)|
                                 (ram[0x0606u+partner]&0x0fu));
    r.new_061d_partner=ram[0x0657u+actor];
    r.new_0669_partner=ram[0x0669u+partner];
    /* $B32D checks source $0657,X low nibble==3 and partner type2. */
    r.b32d_special_contact=((ram[0x0657u+actor]&0x0fu)==3u &&
                            type==2u);
    if(r.b32d_special_contact){
        r.write_0669_partner=1u;
        r.new_0669_partner|=3u;
        r.new_0669_actor=(uint8_t)((r.new_0669_actor&0xf0u)|3u);
    }
    /* $B304 CMP #$06; $B30B JSR $B6CE else
     * $B311 JSR $B5DF. Stop BEFORE either effect helper. */
    r.next_pc=type==6u ? CVIII_B727_NEXT_B6CE_0820:
                         CVIII_B727_NEXT_B5DF_0820;
    *out=r;
    return 1;
}
#endif
