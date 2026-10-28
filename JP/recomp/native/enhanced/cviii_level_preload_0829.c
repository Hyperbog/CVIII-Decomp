#include "cviii_level_preload_0829.h"
#include "cviii_runtime_resources_0727.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int cartridge_identity(const uint8_t *rom,size_t n)
{
    if (!rom || n!=CVIII_RUNTIME_ROM_BYTES_0727 ||
        memcmp(rom,"NES\x1a",4)!=0 || rom[4]!=16u || rom[5]!=16u ||
        (((unsigned)rom[6]>>4u)|((unsigned)rom[7]&0xf0u))!=24u)
        return 0;
#ifndef CVIII_LEVEL_PRELOAD_TEST_SYNTHETIC
    static const uint8_t expected[32]={
        0x95,0x8a,0x4b,0x5e,0x95,0xe8,0x0a,0xcb,
        0x2c,0x71,0xa4,0x3e,0x9e,0xf2,0xe9,0x14,
        0x44,0xf3,0xd0,0x97,0xae,0x9d,0x4e,0xeb,
        0x74,0x7f,0x0d,0xac,0x8a,0xbe,0x7a,0x28
    };
    uint8_t digest[32];
    cviii_sha256_0727(rom,n,digest);
    if(memcmp(digest,expected,sizeof expected)!=0)return 0;
#endif
    return 1;
}

int cviii_level_preload_bytes_0829(const uint8_t *rom,size_t n,
                                  CviiiLevelPreload0829 *out)
{
    if(!out || !cartridge_identity(rom,n))return 0;
    const uint8_t *bank=rom+16u+10u*16384u;
    CviiiRoomCatalog0657 catalog;
    if(cviii_room_catalog_0657(bank,16384u,&catalog)!=1 ||
       catalog.stages!=CVIII_PRELOAD_STAGES_0829 ||
       catalog.leaf_count!=CVIII_PRELOAD_ROOMS_0829)return 0;
    /* Build a complete candidate off-object, so corrupt sources cannot
     * silently replace a previously usable world in the running game. */
    CviiiLevelPreload0829 *candidate=
        (CviiiLevelPreload0829 *)calloc(1,sizeof *candidate);
    if(!candidate)return 0;
    int valid=cviii_tsa_catalog_load_0730(rom,n,&candidate->tsa);
    if(valid) {
        memcpy(candidate->source_bank,bank,CVIII_PRELOAD_BANK_BYTES_0829);
        unsigned previous_stage=0;
        for(unsigned i=0;i<catalog.leaf_count;i++) {
            const CviiiRoomLeaf0657 *src=&catalog.leaves[i];
            if(src->stage>=CVIII_PRELOAD_STAGES_0829 ||
               (i && src->stage<previous_stage)) {valid=0;break;}
            previous_stage=src->stage;
            if(!candidate->count[src->stage])candidate->first[src->stage]=(uint16_t)i;
            if(candidate->count[src->stage]==255u){valid=0;break;}
            candidate->count[src->stage]++;
            if(src->root<0x8000u || src->end_exclusive>0xc000u ||
               src->end_exclusive<=src->root){valid=0;break;}
            unsigned length=(unsigned)src->end_exclusive-src->root;
            unsigned offset=src->root-0x8000u;
            if(length>16384u-offset){valid=0;break;}
            unsigned rows=0;
            if(src->width==4u) {
                if(length%4u){valid=0;break;}
                rows=length/4u;
            } else if(src->width==7u) {
                if(length<8u || (length-1u)%7u ||
                   bank[offset+length-1u]!=0xffu){valid=0;break;}
                rows=(length-1u)/7u;
                for(unsigned k=0;k<rows;k++)
                    if(bank[offset+k*7u]>3u){valid=0;break;}
                if(!valid)break;
            } else {valid=0;break;}
            candidate->room[i]=(CviiiRoomResource0829){
                src->stage,src->second,src->third,src->width,
                src->root,(uint16_t)length,(uint16_t)rows
            };
        }
        for(unsigned stage=0;stage<CVIII_PRELOAD_STAGES_0829 && valid;stage++)
            if(!candidate->count[stage])valid=0;
    }
    if(valid) {
        candidate->active_stage=0xffu;
        candidate->loaded=1u;
        memcpy(out,candidate,sizeof *out);
    }
    free(candidate);
    return valid;
}

int cviii_level_preload_open_0829(const char *path,CviiiLevelPreload0829 *out)
{
    if(!path || !*path || !out)return 0;
    FILE *f=fopen(path,"rb");
    if(!f)return 0;
    uint8_t *rom=(uint8_t *)malloc(CVIII_RUNTIME_ROM_BYTES_0727);
    if(!rom){fclose(f);return 0;}
    size_t got=fread(rom,1,CVIII_RUNTIME_ROM_BYTES_0727,f);
    int extra=fgetc(f),read_error=ferror(f),closed=fclose(f);
    int valid=!read_error && closed==0 && extra==EOF &&
        got==CVIII_RUNTIME_ROM_BYTES_0727 &&
        cviii_level_preload_bytes_0829(rom,got,out);
    free(rom);
    return valid;
}

int cviii_level_preload_stage_0829(CviiiLevelPreload0829 *cache,
                                  unsigned stage)
{
    if(!cache || !cache->loaded || stage>=CVIII_PRELOAD_STAGES_0829 ||
       !cache->count[stage])return 0;
    if(cache->active_stage!=stage) {
        cache->active_stage=(uint8_t)stage;
        if(cache->stage_changes<UINT32_MAX)cache->stage_changes++;
    }
    return 1;
}

const uint8_t *cviii_level_preload_room_0829(
    const CviiiLevelPreload0829 *cache,unsigned stage,
    unsigned subarea,unsigned room,
    size_t *length,unsigned *width,unsigned *records)
{
    if(length)*length=0;
    if(width)*width=0;
    if(records)*records=0;
    if(!cache || !cache->loaded || stage>=CVIII_PRELOAD_STAGES_0829 ||
       subarea>255u || room>255u)return NULL;
    unsigned start=cache->first[stage];
    unsigned end=start+cache->count[stage];
    if(end>CVIII_PRELOAD_ROOMS_0829)return NULL;
    for(unsigned i=start;i<end;i++) {
        const CviiiRoomResource0829 *r=&cache->room[i];
        if(r->stage==stage && r->subarea==subarea && r->room==room) {
            if(length)*length=r->length;
            if(width)*width=r->record_width;
            if(records)*records=r->record_count;
            return cache->source_bank+(unsigned)r->source_cpu-0x8000u;
        }
    }
    return NULL;
}
