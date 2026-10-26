/* JP0816: authenticated original raw0A horizontal Stage1 source cells.
 * Original $801E/$80D1/$8111/$818C, READ ONLY. Source descriptor
 * != resident enemy spawn; collision, OAM and CPU are not touched.
 * Caller MUST validate original raw0A's whole-bank SHA first. */
#ifndef CVIII_HORIZONTAL_SOURCES_0816_H
#define CVIII_HORIZONTAL_SOURCES_0816_H
#include <stdint.h>
#include <stddef.h>
enum { CVIII_HORIZONTAL_ROOMS_0816=8, CVIII_HORIZONTAL_PAIRS_0816=14 };
typedef struct {
    uint16_t cell_cpu, event_record_cpu[2],aux_record_cpu;
    uint8_t event_id,aux_id,event_row[2],aux_type;
} CviiiHorizontalPair0816;
typedef struct {
    uint8_t valid, count;
    CviiiHorizontalPair0816 pairs[CVIII_HORIZONTAL_PAIRS_0816];
} CviiiHorizontalRoom0816;
typedef struct {
    uint8_t valid,room,phase,slot,source_id,aux_id,event_row,aux_type;
    uint16_t cell_cpu,event_cpu,aux_cpu;
} CviiiHorizontalSelection0816;
static inline unsigned cviii_raw0a_byte_0816(const uint8_t *b,unsigned address){
    return b[address-0x8000u];
}
static inline unsigned cviii_raw0a_word_0816(const uint8_t *b,unsigned address){
    return cviii_raw0a_byte_0816(b,address) |
        cviii_raw0a_byte_0816(b,address+1u)<<8u;
}
/* Exact ASL carry and $07F6 special $A0 fallback in $8111-$813C. */
static inline unsigned cviii_horizontal_event_ptr_0816(
    const uint8_t *bank,unsigned id,int f6)
{
    const unsigned doubled=(id<<1u)&255u;
    const int high=(id&0x80u)!=0;
    const unsigned fallback=high && !f6 && doubled>=0xa0u;
    const unsigned table=high && !fallback ? 0xa06eu:0x9f6eu;
    const unsigned at=fallback ? 0u:doubled;
    return cviii_raw0a_word_0816(bank,table+at);
}
static inline unsigned cviii_horizontal_aux_ptr_0816(
    const uint8_t *bank,unsigned id)
{
    const unsigned table=id&0x80u ? 0xa66bu:0xa56bu;
    return cviii_raw0a_word_0816(bank,table+((id<<1u)&255u));
}
/* Only seven horizontal Stage-zero room leaves. Room 2 is VERTICAL
 * seven-byte objects and must not be decoded as a pair stream. */
static inline int cviii_horizontal_build_room_0816(
    CviiiHorizontalRoom0816 *dst,unsigned room,
    uint16_t source_root,const uint8_t *payload,unsigned payload_len,
    const uint8_t *original_raw0a,size_t bank_len)
{
    static const uint16_t roots[8]={
        0x93ccu,0x93e8u,0u,0x93f4u,
        0x9410u,0x9424u,0x9440u,0x945cu
    };
    static const uint8_t sizes[8]={28u,12u,0u,28u,20u,28u,28u,28u};
    if(!dst || !payload || !original_raw0a ||
       bank_len!=16384u || room>=8u || room==2u ||
       source_root!=roots[room] || payload_len!=sizes[room])
       return 0;
    CviiiHorizontalRoom0816 tmp={0};
    tmp.valid=1u;
    tmp.count=(uint8_t)(payload_len/2u);
    for(unsigned i=0;i<tmp.count;i++){
        CviiiHorizontalPair0816 *p=&tmp.pairs[i];
        p->cell_cpu=(uint16_t)(source_root+i*2u);
        p->event_id=payload[i*2u];
        p->aux_id=payload[i*2u+1u];
        for(unsigned f=0;f<2;f++){
            const unsigned pc=cviii_horizontal_event_ptr_0816(
                original_raw0a,p->event_id,(int)f);
            if(pc<0x8000u || pc>0xbffbu)return 0;
            p->event_record_cpu[f]=(uint16_t)pc;
            p->event_row[f]=(uint8_t)cviii_raw0a_byte_0816(original_raw0a,pc);
        }
        if(p->aux_id){
            const unsigned pc=cviii_horizontal_aux_ptr_0816(
                original_raw0a,p->aux_id);
            if(pc<0x8000u || pc>0xbffcu)return 0;
            p->aux_record_cpu=(uint16_t)pc;
            p->aux_type=(uint8_t)cviii_raw0a_byte_0816(original_raw0a,pc);
        }
    }
    *dst=tmp;return 1;
}
/* Original $8001 adds 2 with carry to a 16-bit camera, ASL+ROL twice
 * and $80D1 adds 5 if $62 nonzero; $8410 has only 48 real entries.
 * Return NONE, never wrap a source payload or invent another room. */
static inline CviiiHorizontalSelection0816 cviii_horizontal_select_0816(
    const CviiiHorizontalRoom0816 *source,unsigned room,
    unsigned camera_16,unsigned direction_62,int flag_07f6)
{
    CviiiHorizontalSelection0816 result={0};
    if(!source || !source->valid || room>=8u || room==2u ||
       camera_16>65535u || direction_62>255u)return result;
    const unsigned phase=(((((camera_16+2u)&65535u)>>6u)&255u)+
        (direction_62 ? 5u:0u))&255u;
    if(phase>=48u || phase>=source->count)return result;
    const CviiiHorizontalPair0816 *p=&source->pairs[phase];
    result.valid=1u;result.room=(uint8_t)room;
    result.phase=(uint8_t)phase;
    result.slot=(uint8_t)(phase%6u); /* original $8410 phase table */
    result.source_id=p->event_id;result.aux_id=p->aux_id;
    result.event_row=p->event_row[flag_07f6?1:0];
    result.aux_type=p->aux_type;
    result.cell_cpu=p->cell_cpu;
    result.event_cpu=p->event_record_cpu[flag_07f6?1:0];
    result.aux_cpu=p->aux_record_cpu;
    return result;
}
#endif
