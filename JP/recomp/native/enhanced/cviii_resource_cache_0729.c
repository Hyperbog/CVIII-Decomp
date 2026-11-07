/* JP0729 — Private source-bound cache, deliberately not a ROM distributor.
 * Canonical little-endian file schema; no C struct/pointer serialization.
 * Rebuild from the owner-ROM on any invalid header, checksum or metadata.
 */
#include "cviii_resource_cache_0729.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif
#define CACHE_HEADER 80u
#define ROOM_META 24u
#define META_TOTAL (CVIII_STAGE1_ROOMS_0724 * ROOM_META)
#define CACHE_PAYLOAD (META_TOTAL + CVIII_STAGE1_TILES_0724 * 2u + \
                       CVIII_CHR_RAW_BYTES + CVIII_CHR_PIXEL_BYTES)
static const unsigned char magic[8]={'C','V','R','S','C','0','2','9'};
static const uint16_t expected_w[8]={96,32,32,96,64,96,96,128};
static const uint16_t expected_h[8]={24,24,64,24,24,24,24,24};
static const uint16_t expected_count[8]={144,48,128,144,96,144,144,192};
static const uint32_t expected_source[8]={
    0x200BBu,0x2014Cu,0x2003Au,0x201DEu,
    0x2017Du,0x2026Fu,0x20300u,0x20391u
};
static uint16_t get16(const uint8_t *p){
    return (uint16_t)(p[0]|((uint16_t)p[1]<<8u));
}
static uint32_t get32(const uint8_t *p){
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
           ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
static void put16(uint8_t *p,uint16_t x){
    p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8u);
}
static void put32(uint8_t *p,uint32_t x){
    for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(x>>(8u*i));
}
static int meta_valid(const CviiiStage1Atlas0724 *a)
{
    if(!a||!a->loaded||a->offsets[8]!=CVIII_STAGE1_TILES_0724)
        return 0;
    unsigned offset=0;
    for(unsigned i=0;i<8u;i++){
        const CviiiStage1Room0724 *r=&a->rooms[i];
        if(a->offsets[i]!=offset || r->width_tiles!=expected_w[i] ||
            r->height_tiles!=expected_h[i] ||
            r->metatile_count!=expected_count[i] ||
            r->vertical!=(i==2u) ||
            r->source_layout_offset!=expected_source[i] ||
            r->source_tsa_pattern_offset!=0x20451u ||
            r->source_tsa_attribute_offset!=0x20D61u) return 0;
        offset+=r->width_tiles*(unsigned)r->height_tiles;
    }
    return offset==CVIII_STAGE1_TILES_0724;
}
static void pack_room(uint8_t *p,const CviiiStage1Atlas0724 *a,unsigned i)
{
    const CviiiStage1Room0724 *r=&a->rooms[i];
    put16(p,a->offsets[i]);put16(p+2,r->width_tiles);
    put16(p+4,r->height_tiles);put16(p+6,r->metatile_count);
    p[8]=r->vertical;p[9]=p[10]=p[11]=0;
    put32(p+12,r->source_layout_offset);
    put32(p+16,r->source_tsa_pattern_offset);
    put32(p+20,r->source_tsa_attribute_offset);
}
static void unpack_room(const uint8_t *p,CviiiStage1Atlas0724 *a,unsigned i)
{
    CviiiStage1Room0724 *r=&a->rooms[i];
    a->offsets[i]=get16(p);r->width_tiles=get16(p+2);
    r->height_tiles=get16(p+4);r->metatile_count=get16(p+6);
    r->vertical=p[8];
    r->source_layout_offset=get32(p+12);
    r->source_tsa_pattern_offset=get32(p+16);
    r->source_tsa_attribute_offset=get32(p+20);
}
static int cache_buffer_pack(uint8_t *p,
  const CviiiStage1Atlas0724 *a,const CviiiChrIndex *chr)
{
    if(!meta_valid(a)||!chr||!chr->allocation||!chr->raw||!chr->pixels)
        return 0;
#ifdef CVIII_RESOURCE_TEST_SYNTHETIC_0727
    const bool original=false;
#else
    const bool original=true;
#endif
    if(!cviii_chr_index_check(chr->allocation,CVIII_CHR_INDEX_BYTES,original))
        return 0;
    for(unsigned i=0;i<CVIII_STAGE1_TILES_0724;i++)
        if(a->palette[i]>3u)return 0;
    for(unsigned i=0;i<8u;i++)pack_room(p+i*ROOM_META,a,i);
    memcpy(p+META_TOTAL,a->tile,CVIII_STAGE1_TILES_0724);
    memcpy(p+META_TOTAL+CVIII_STAGE1_TILES_0724,
           a->palette,CVIII_STAGE1_TILES_0724);
    memcpy(p+META_TOTAL+CVIII_STAGE1_TILES_0724*2u,
           chr->raw,CVIII_CHR_RAW_BYTES);
    memcpy(p+META_TOTAL+CVIII_STAGE1_TILES_0724*2u+CVIII_CHR_RAW_BYTES,
           chr->pixels,CVIII_CHR_PIXEL_BYTES);
    return 1;
}
static int cache_buffer_unpack(const uint8_t *p,
  CviiiStage1Atlas0724 *a,CviiiChrIndex *chr)
{
    for(unsigned i=0;i<8u;i++) {
        if(p[i*ROOM_META+9u]||p[i*ROOM_META+10u]||
           p[i*ROOM_META+11u])return 0;
        unpack_room(p+i*ROOM_META,a,i);
    }
    a->offsets[8]=CVIII_STAGE1_TILES_0724;
    a->loaded=1;
    if(!meta_valid(a))return 0;
    memcpy(a->tile,p+META_TOTAL,CVIII_STAGE1_TILES_0724);
    memcpy(a->palette,p+META_TOTAL+CVIII_STAGE1_TILES_0724,
           CVIII_STAGE1_TILES_0724);
    for(unsigned i=0;i<CVIII_STAGE1_TILES_0724;i++)
        if(a->palette[i]>3u)return 0;
    unsigned char *index=(unsigned char *)malloc(CVIII_CHR_INDEX_BYTES);
    if(!index)return 0;
    memcpy(index,"CVIII058",8);
    memcpy(index+8,p+META_TOTAL+CVIII_STAGE1_TILES_0724*2u,
           CVIII_CHR_RAW_BYTES+CVIII_CHR_PIXEL_BYTES);
#ifdef CVIII_RESOURCE_TEST_SYNTHETIC_0727
    const bool original=false;
#else
    const bool original=true;
#endif
    int ok=cviii_chr_index_check(index,CVIII_CHR_INDEX_BYTES,original);
    if(ok && chr) {
        cviii_chr_index_free(chr);
        chr->allocation=index;
        chr->raw=index+8;
        chr->pixels=index+8+CVIII_CHR_RAW_BYTES;
        index=NULL;
    }
    free(index);
    return ok;
}
int cviii_resource_cache_read_0729(const char *path,const uint8_t rom_sha[32],
  CviiiStage1Atlas0724 *atlas,CviiiChrIndex *chr)
{
    if(!path||!*path||!rom_sha||!atlas)return 0;
    FILE *f=fopen(path,"rb");
    if(!f)return 0;
    uint8_t head[CACHE_HEADER],*payload=NULL;
    int ok=fread(head,1,sizeof head,f)==sizeof head;
    if(ok)ok=memcmp(head,magic,8)==0 &&
        get32(head+8)==CVIII_RESOURCE_CACHE_SCHEMA_0729 &&
        get32(head+12)==CACHE_PAYLOAD &&
        memcmp(head+16,rom_sha,32)==0;
    if(ok) {
        payload=(uint8_t *)malloc(CACHE_PAYLOAD);
        ok=payload && fread(payload,1,CACHE_PAYLOAD,f)==CACHE_PAYLOAD;
    }
    if(ok)ok=fgetc(f)==EOF && !ferror(f);
    fclose(f);
    if(ok){
        uint8_t hash[32];
        cviii_sha256_0727(payload,CACHE_PAYLOAD,hash);
        ok=memcmp(head+48,hash,32)==0;
    }
    CviiiStage1Atlas0724 *tmp=NULL;
    if(ok){
        tmp=(CviiiStage1Atlas0724 *)calloc(1,sizeof *tmp);
        ok=tmp && cache_buffer_unpack(payload,tmp,chr);
    }
    if(ok)memcpy(atlas,tmp,sizeof *atlas);
    free(tmp);free(payload);
    return ok;
}
int cviii_resource_cache_write_0729(const char *path,const uint8_t rom_sha[32],
  const CviiiStage1Atlas0724 *atlas,const CviiiChrIndex *chr)
{
    if(!path||!*path||!rom_sha)return 0;
    uint8_t *payload=(uint8_t *)malloc(CACHE_PAYLOAD);
    if(!payload)return 0;
    int ok=cache_buffer_pack(payload,atlas,chr);
    uint8_t head[CACHE_HEADER]={0};
    if(ok) {
        memcpy(head,magic,8);
        put32(head+8,CVIII_RESOURCE_CACHE_SCHEMA_0729);
        put32(head+12,CACHE_PAYLOAD);
        memcpy(head+16,rom_sha,32);
        cviii_sha256_0727(payload,CACHE_PAYLOAD,head+48);
    }
    size_t pathlen=strlen(path);
    if(pathlen>2048u)ok=0;
    char *tmp=ok?(char *)malloc(pathlen+40u):NULL;
    if(ok && !tmp)ok=0;
    if(ok) {
#ifdef _WIN32
        unsigned long process=(unsigned long)GetCurrentProcessId();
#else
        unsigned long process=(unsigned long)getpid();
#endif
        (void)snprintf(tmp,pathlen+40u,"%s.tmp.%lu",path,process);
        FILE *f=fopen(tmp,"wbx"); /* C11 exclusive creation */
        if(!f)ok=0;
        else {
            ok=fwrite(head,1,sizeof head,f)==sizeof head &&
               fwrite(payload,1,CACHE_PAYLOAD,f)==CACHE_PAYLOAD &&
               fflush(f)==0;
            if(fclose(f)!=0)ok=0;
            if(ok){
#ifdef _WIN32
                ok=MoveFileExA(tmp,path,MOVEFILE_REPLACE_EXISTING|
                              MOVEFILE_WRITE_THROUGH)!=0;
#else
                ok=rename(tmp,path)==0;
#endif
            }
            if(!ok)remove(tmp);
        }
    }
    free(tmp);free(payload);
    return ok;
}
