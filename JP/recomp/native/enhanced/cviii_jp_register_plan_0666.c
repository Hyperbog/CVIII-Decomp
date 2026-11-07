#include "cviii_jp_register_plan_0666.h"
#include <string.h>
static unsigned read16(const uint8_t *p,unsigned addr)
{
    unsigned off=addr-0x8000u;
    return (unsigned)p[off] | ((unsigned)p[off+1u]<<8);
}
bool cviii_jp0666_note_plan(const uint8_t *rom,size_t size,
                            const CviiiJp0666Input *in,CviiiJp0666Plan *out)
{
    if(!rom || size!=CVIII_JP0666_BANK_SIZE || !in || !out ||
       in->slot>4u || in->note>=0xc0u ||
       in->octave>5u || (in->flag_06b4&0x80u)==0u ||
       (in->flag_018e&0x10u)!=0u) return false;
    CviiiJp0666Plan tmp;
    memset(&tmp,0,sizeof(tmp));
    unsigned index=(unsigned)(in->note>>4)*2u;
    bool lower_table=false;
    if(in->transpose&0x80u){
        unsigned magnitude=in->transpose&0x7fu;
        if(index<magnitude){
            index=(index-magnitude-0xe8u)&0xffu;
            lower_table=true;
        }else index-=magnitude;
    }else index=(index+in->transpose)&0xffu;
    /* No interpolation outside the two bounded, source-authenticated pitch
     * tables. The original CPU can physically read farther, but its musical
     * meaning and safe live selector domain have not been proved. */
    if(index>(lower_table?0x16u:0x2eu))return false;
    unsigned src=(in->slot==2u?(lower_table?0x875bu:0x8773u):
                                 (lower_table?0x8713u:0x872bu))+index;
    unsigned period=read16(rom,src);
    period>>=(5u-in->octave);
    tmp.period_before_detune=(uint16_t)period;
    unsigned magnitude=in->detune&0x7fu;
    if(in->detune&0x80u)period=(period+magnitude)&0xffffu;
    else period=(period-magnitude)&0xffffu;
    tmp.period_after_detune=(uint16_t)period;
    unsigned lo=period&255u, hi=period>>8;
    tmp.high_cache_after=in->high_cache;
    if(in->slot>=3u){
        /* High-period writes may be suppressed by the source's state cache,
         * pulse envelope flags, or $010E/$010F gate. See $81AD-$81D6.
         * Original $019C,X low-period cache changes even if APU gate set. */
        bool high_needed=hi!=in->high_cache;
        if(!high_needed){
            bool rearm=((in->flag_011b&0x81u)==0x81u);
            bool inhibit=(in->flag_017e&0x10u)!=0u;
            high_needed=rearm || !inhibit;
        }
        if(high_needed){
            tmp.high_cache_after=(uint8_t)hi;
            if(in->apu_gate==0u){
                tmp.writes[tmp.write_count++]=(CviiiJp0666Write){
                    (uint16_t)(in->slot==3u?0x4003u:0x4007u),
                    (uint8_t)(hi|0x08u)};
            }
        }
        tmp.stored_period_low=(uint8_t)lo;
        if(in->apu_gate==0u){
            tmp.writes[tmp.write_count++]=(CviiiJp0666Write){
                (uint16_t)(in->slot==3u?0x4002u:0x4006u),
                (uint8_t)lo};
        }
    }else{
        unsigned base=in->slot==0u?0x9000u:in->slot==1u?0xa000u:0xb000u;
        tmp.writes[0]=(CviiiJp0666Write){(uint16_t)(base+1u),(uint8_t)lo};
        tmp.writes[1]=(CviiiJp0666Write){(uint16_t)(base+2u),(uint8_t)(hi|0x80u)};
        tmp.write_count=2u;
    }
    *out=tmp;
    return true;
}
