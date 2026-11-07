#include "cviii_jp_music_0665.h"
#include <string.h>
#include <limits.h>

static bool get(const CviiiJp0665Voice *v, unsigned pc, unsigned width,
                const uint8_t **bytes)
{
    if(!v || !v->bank05 || !bytes || pc<0x87aeu || pc>=0x9a6bu ||
       width==0 || width>0x9a6bu-pc) return false;
    *bytes=v->bank05+(pc-0x8000u);
    return true;
}
static uint16_t little(const uint8_t *p){return (uint16_t)(p[0] | ((uint16_t)p[1]<<8));}
static uint8_t route(unsigned i){
    static const uint8_t r[CVIII_JP0665_VOICES]={0,1,2,3,4,7};
    return r[i];
}
static void add(uint64_t *t, uint16_t duration){
    /* Overflow checked in cviii_jp0665_next before use. */
    *t+=duration;
}
bool cviii_jp0665_init(const uint8_t *raw05,size_t n05,
                       const uint8_t *raw0c,size_t n0c,
                       CviiiJp0665Voice voices[CVIII_JP0665_VOICES])
{
    if(!raw05 || !raw0c || !voices || n05!=CVIII_JP0665_RAW05_SIZE ||
       n0c!=CVIII_JP0665_RAW0C_SIZE)return false;
    unsigned ptr_off=0x8f60u-0x8000u+2u*(0x51u-1u);
    unsigned descriptor=little(raw0c+ptr_off);
    if(descriptor<0x905au || descriptor+20u>0x9541u)return false;
    unsigned pos=descriptor-0x8000u;
    if(raw0c[pos]!=5u || raw0c[pos+1u]!=5u)return false;
    CviiiJp0665Voice tmp[CVIII_JP0665_VOICES]={{0}};
    for(unsigned i=0;i<CVIII_JP0665_VOICES;++i){
        unsigned entry=pos+2u+3u*i;
        unsigned root=little(raw0c+entry+1u);
        if(raw0c[entry]!=route(i) || root<0x87aeu || root>=0x9a6bu ||
           raw05[root-0x8000u]<0x10u)return false;
        tmp[i].bank05=raw05;tmp[i].route=route(i);tmp[i].pc=(uint16_t)root;
    }
    memcpy(voices,tmp,sizeof(tmp));return true;
}
int cviii_jp0665_next(CviiiJp0665Voice *v,CviiiJp0665Event *out)
{
    if(!v || !out || !v->bank05 || v->ended)return 0;
    for(unsigned step=0;step<8192u;++step){
        const uint8_t *p=NULL;
        unsigned pc=v->pc;
        if(!get(v,pc,1u,&p))goto error;
        unsigned raw=p[0], high=raw>>4, low=raw&15u;
        if(high==15u){
            if(low<=10u || low==12u){v->pc=(uint16_t)(pc+1u);continue;}
            if(low==11u){v->fb_anchor=(uint16_t)(pc+1u);v->has_anchor=true;
                v->pc=(uint16_t)(pc+1u);continue;}
            if(low==13u){
                if(!v->has_return){
                    if(!get(v,pc,3u,&p))goto error;
                    unsigned target=little(p+1);
                    if(!get(v,target,1u,&p))goto error;
                    v->fd_return=(uint16_t)(pc+3u);
                    v->has_return=true;v->pc=(uint16_t)target;
                }else{v->pc=v->fd_return;v->has_return=false;}
                continue;
            }
            if(low==14u){
                if(!get(v,pc,2u,&p))goto error;
                unsigned count=p[1];
                if(count==255u){
                    if(!get(v,pc,4u,&p))goto error;
                    unsigned target=little(p+2);
                    if(!get(v,target,1u,&p))goto error;
                    v->pc=(uint16_t)target;
                }else{
                    if(!v->has_anchor)goto error;
                    if(v->has_repeat && v->repeat_site!=pc)goto error;
                    if(!v->has_repeat){v->repeat_site=(uint16_t)pc;
                        v->has_repeat=true;v->repeat_counter=0;}
                    v->repeat_counter=(uint8_t)(v->repeat_counter+1u);
                    if(v->repeat_counter==count){
                        v->has_repeat=false;v->repeat_counter=0;
                        v->pc=(uint16_t)(pc+2u);
                    }else v->pc=v->fb_anchor;
                }
                continue;
            }
            if(low==15u){v->ended=true;return 0;}
            goto error;
        }
        if(v->route!=CVIII_JP0665_PERCUSSION){
            if(high==13u){
                if(!get(v,pc,4u,&p))goto error;
                v->unit=(uint8_t)low;
                v->pc=(uint16_t)(pc+4u);
                v->unknown_effects=true; /* three D parameters still affect timbre */
                continue;
            }
            if(high==14u){
                unsigned width;
                if(low<=5u){
                    v->octave=(uint8_t)low; width=1u;
                }else if(low==11u){
                    if(!get(v,pc,2u,&p))goto error;
                    width=p[1]==0u?2u:3u;
                }else if(low==6u || low==7u || low==8u || low==9u ||
                         low==10u || low==12u || low==13u || low==14u || low==15u)
                    width=2u;
                else goto error;
                if(!get(v,pc,width,&p))goto error;
                if(low>=6u)v->unknown_effects=true;
                v->pc=(uint16_t)(pc+width);continue;
            }
        }else if(high==13u){
            v->unit=(uint8_t)low;v->pc=(uint16_t)(pc+1u);continue;
        }
        if(v->route==CVIII_JP0665_PERCUSSION && high>=13u)goto error;
        /* $82A4-$82B8: low nibble N means (N+1) x current unit
         * modulo 256; it is an 8-bit $0100,X countdown. */
        uint16_t duration=(uint16_t)(((low+1u)*v->unit)&255u);
        if(duration==0 || UINT64_MAX-v->ticks<duration || v->events==UINT64_MAX)
            goto error;
        CviiiJp0665Event event={0};
        event.tick=v->ticks;event.route=v->route;
        event.note_byte=(uint8_t)raw;event.note_index=(uint8_t)high;
        event.duration_units=v->unit;event.duration_ticks=duration;
        event.source_pc=(uint16_t)pc;
        event.exact_register_values_verified=false;
        if(v->route==CVIII_JP0665_PERCUSSION){
            if(high<12u){
                static const uint8_t requests[12]={1,2,3,4,5,0x72,0x7b,0x6f,0x70,0x71,0x72,0x73};
                event.sound_request_id=requests[high];
                event.kind=event.sound_request_id>=0x6fu?
                    CVIII_JP0665_DPCM_REQUEST:CVIII_JP0665_NOISE_REQUEST;
            }else event.kind=CVIII_JP0665_REST;
        }else if(high<12u){
            const uint8_t *period=NULL;
            unsigned address=0x872bu+2u*high;
            if(!get(v,address,2u,&period)){
                /* Pitch lookup table is in common code, outside $87AE. */
                period=v->bank05+(address-0x8000u);
            }
            event.kind=CVIII_JP0665_NOTE;
            event.pitch_table_base_period=little(period);
            if(v->route<=CVIII_JP0665_VRC6_SAW){
                unsigned base=(v->route==0u?0x9000u:v->route==1u?0xa000u:0xb000u);
                event.destination_period_low=(uint16_t)(base+1u);
                event.destination_period_high=(uint16_t)(base+2u);
            }else{
                unsigned base=v->route==3u?0x4000u:0x4004u;
                event.destination_period_low=(uint16_t)(base+2u);
                event.destination_period_high=(uint16_t)(base+3u);
            }
        }else event.kind=CVIII_JP0665_REST;
        v->pc=(uint16_t)(pc+1u);
        add(&v->ticks,duration);++v->events;
        *out=event;return 1;
    }
error:
    v->ended=true;return -1;
}
