#include "cviii_jp_chip_0665.h"
#include <limits.h>
#include <string.h>

#define CVIII_JP_NTSC_CLOCK 1789773.0
static const uint16_t noise_cycles[16] = {
  4,8,16,32,64,96,128,160,202,254,380,508,762,1016,2034,4068
};
static int valid_kind(CviiiJpChipKind k){
    return k>=CVIII_JP_CHIP_APU_PULSE1 && k<=CVIII_JP_CHIP_VRC6_SAW;
}
bool cviii_jp_chip_init(CviiiJpChipVoice *s,CviiiJpChipKind k,
                        uint32_t sample_rate)
{
    if(!s || !valid_kind(k) || sample_rate<8000u || sample_rate>192000u)
        return false;
    memset(s,0,sizeof(*s));s->kind=k;s->sample_rate=sample_rate;
    s->lfsr=1;return true;
}
bool cviii_jp_chip_write(CviiiJpChipVoice *s,uint16_t addr,uint8_t value)
{
    if(!s || !valid_kind(s->kind) || !s->sample_rate)return false;
    uint16_t base=0;
    if(s->kind==CVIII_JP_CHIP_APU_PULSE1)base=0x4000;
    else if(s->kind==CVIII_JP_CHIP_APU_PULSE2)base=0x4004;
    else if(s->kind==CVIII_JP_CHIP_APU_NOISE)base=0x400c;
    else if(s->kind==CVIII_JP_CHIP_VRC6_PULSE1)base=0x9000;
    else if(s->kind==CVIII_JP_CHIP_VRC6_PULSE2)base=0xa000;
    else base=0xb000;
    if(addr==0x4015 && s->kind<=CVIII_JP_CHIP_APU_NOISE){
        unsigned bit=s->kind==CVIII_JP_CHIP_APU_PULSE1?0u:
                     s->kind==CVIII_JP_CHIP_APU_PULSE2?1u:3u;
        s->apu_enable=(uint8_t)((value>>bit)&1u);return true;
    }
    if(addr<base || addr>=base+3u+(s->kind<=CVIII_JP_CHIP_APU_PULSE2))
        return false;
    unsigned reg=addr-base;
    /* 2A03 noise has no $400F or length implementation yet. */
    if(s->kind==CVIII_JP_CHIP_APU_NOISE && reg==1u)return false;
    if(reg==0u)s->r0=value;
    if(reg==1u)s->r1=value;
    if(reg==2u)s->r2=value;
    if(reg==3u){s->r3=value;s->phase=0;s->cycles_until_step=0;}
    return true;
}
static double period(const CviiiJpChipVoice *s)
{
    if(s->kind==CVIII_JP_CHIP_APU_NOISE)
        return noise_cycles[s->r2&15u];
    if(s->kind<=CVIII_JP_CHIP_APU_PULSE2){
        unsigned v=((unsigned)(s->r3&7u)<<8)|s->r2;
        return 2.0*(v+1u);
    }
    unsigned v=((unsigned)(s->r2&15u)<<8)|s->r1;
    return (double)(v+1u);
}
static void step(CviiiJpChipVoice *s)
{
    if(s->kind==CVIII_JP_CHIP_APU_NOISE){
        unsigned tap=(s->r2&0x80u)?6u:1u;
        unsigned fb=(s->lfsr ^ (s->lfsr>>tap))&1u;
        s->lfsr=(uint16_t)((s->lfsr>>1)|(fb<<14));
    }else if(s->kind==CVIII_JP_CHIP_VRC6_SAW){
        /* 14-step saw, add rate on alternate steps; reset at wrap. */
        if((s->phase&1u)==0u)s->saw_acc=(uint8_t)(s->saw_acc+(s->r0&63u));
        s->phase=(uint8_t)((s->phase+1u)%14u);
        if(!s->phase)s->saw_acc=0;
    }else{
        s->phase=(uint8_t)((s->phase+1u)%
                 (s->kind<=CVIII_JP_CHIP_APU_PULSE2?8u:16u));
    }
}
static int amplitude(const CviiiJpChipVoice *s)
{
    if(s->kind<=CVIII_JP_CHIP_APU_PULSE2){
        static const uint8_t widths[4]={1,2,4,6};
        unsigned width=widths[(s->r0>>6)&3u];
        unsigned timer=((unsigned)(s->r3&7u)<<8)|s->r2;
        if(!s->apu_enable || !(s->r0&0x10u) || timer<8u)return 0;
        return (s->phase<width)?(int)(s->r0&15u):0;
    }
    if(s->kind==CVIII_JP_CHIP_APU_NOISE){
        if(!s->apu_enable || !(s->r0&0x10u) || (s->lfsr&1u))return 0;
        return s->r0&15u;
    }
    if(!(s->r2&0x80u))return 0;
    if(s->kind==CVIII_JP_CHIP_VRC6_SAW)return (s->saw_acc>>3)&31u;
    if(s->r0&0x80u)return s->r0&15u;
    return (s->phase<=((s->r0>>4)&7u))?(int)(s->r0&15u):0;
}
int cviii_jp_chip_sample(void *context,int16_t *out)
{
    CviiiJpChipVoice *s=(CviiiJpChipVoice *)context;
    if(!s || !out || !valid_kind(s->kind) || s->sample_rate<8000u)
        return 0;
    /* CPU-cycle phase advances independently, even if this bus is muted.
     * This is a deterministic approximation, not an exact NES event clock. */
    double elapsed=CVIII_JP_NTSC_CLOCK/(double)s->sample_rate;
    double p=period(s);
    if(p<1.0 || p>65536.0)return 0;
    if(s->cycles_until_step<=0.0)s->cycles_until_step=p;
    while(elapsed>=s->cycles_until_step){
        elapsed-=s->cycles_until_step;
        step(s);s->cycles_until_step=p;
    }
    s->cycles_until_step-=elapsed;
    const int a=amplitude(s);
    /* Centered bounded per-voice preview. Historical analog level mixing
     * and nonlinearity are intentionally not modeled in this experiment. */
    const double raw=(double)a*128.0;
    s->dc_estimate+=(raw-s->dc_estimate)*0.002;
    const double ac=raw-s->dc_estimate;
    *out=(int16_t)(ac>32767.0?32767:ac< -32768.0?-32768:(int)ac);
    ++s->sample_count;return 1;
}
