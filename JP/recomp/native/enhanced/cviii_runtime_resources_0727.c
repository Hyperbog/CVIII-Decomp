/* JP0727 — runtime owner-ROM resource extraction. No original game data
 * is in this source. SHA-256 uses FIPS-180-4 arithmetic (self-contained C11)
 * so the final binary has no Python, crypto-DLL or build-time ROM-path need.
 */
#include "cviii_runtime_resources_0727.h"
#include "cviii_resource_cache_0729.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint32_t k[64] = {
    0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,
    0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
    0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
    0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
    0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,
    0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
    0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,
    0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
    0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
    0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
    0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,
    0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
    0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,
    0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
    0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,
    0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u
};
static uint32_t rotate(uint32_t x, unsigned n) {
    return (x >> n) | (x << (32u - n));
}
static void compress(uint32_t h[8], const uint8_t block[64])
{
    uint32_t w[64],a,b,c,d,e,f,g,hh,t1,t2;
    unsigned i;
    for(i=0;i<16u;i++) {
        unsigned j=i*4u;
        w[i]=((uint32_t)block[j]<<24u)|((uint32_t)block[j+1u]<<16u)|
             ((uint32_t)block[j+2u]<<8u)|block[j+3u];
    }
    for(i=16u;i<64u;i++) {
        uint32_t x=w[i-15u],y=w[i-2u];
        uint32_t s0=rotate(x,7u)^rotate(x,18u)^(x>>3u);
        uint32_t s1=rotate(y,17u)^rotate(y,19u)^(y>>10u);
        w[i]=w[i-16u]+s0+w[i-7u]+s1;
    }
    a=h[0];b=h[1];c=h[2];d=h[3];
    e=h[4];f=h[5];g=h[6];hh=h[7];
    for(i=0;i<64u;i++) {
        uint32_t s1=rotate(e,6u)^rotate(e,11u)^rotate(e,25u);
        uint32_t ch=(e&f)^(~e&g);
        uint32_t s0=rotate(a,2u)^rotate(a,13u)^rotate(a,22u);
        uint32_t maj=(a&b)^(a&c)^(b&c);
        t1=hh+s1+ch+k[i]+w[i];
        t2=s0+maj;
        hh=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
    }
    h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;
    h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh;
}
void cviii_sha256_0727(const uint8_t *input,size_t n,uint8_t digest[32])
{
    uint32_t h[8]={
        0x6a09e667u,0xbb67ae85u,0x3c6ef372u,0xa54ff53au,
        0x510e527fu,0x9b05688cu,0x1f83d9abu,0x5be0cd19u
    };
    uint8_t tail[128]={0};
    size_t complete=n/64u,remaining=n%64u,i;
    if (!digest || (n && !input)) return;
    for(i=0;i<complete;i++)compress(h,input+i*64u);
    if(remaining)memcpy(tail,input+complete*64u,remaining);
    tail[remaining]=0x80u;
    uint64_t bits=(uint64_t)n*8u;
    size_t length_offset=remaining<56u ? 56u : 120u;
    for(i=0;i<8u;i++)tail[length_offset+i]=(uint8_t)(bits>>(56u-8u*i));
    compress(h,tail);
    if(length_offset==120u)compress(h,tail+64u);
    for(i=0;i<8u;i++) {
        digest[4u*i]=(uint8_t)(h[i]>>24u);
        digest[4u*i+1u]=(uint8_t)(h[i]>>16u);
        digest[4u*i+2u]=(uint8_t)(h[i]>>8u);
        digest[4u*i+3u]=(uint8_t)h[i];
    }
}

/* JP0728: derive the full owner-local physical CHR tile index directly
 * from the authenticated iNES image, not from a Python-generated sidecar.
 * The layout is the existing JP0598 original CHR index schema, generated
 * entirely in RAM so earlier consumers (font, HUD and editor) are reusable.
 */
static unsigned char *make_chr_index(const uint8_t *rom)
{
    unsigned char *buffer=(unsigned char *)malloc(CVIII_CHR_INDEX_BYTES);
    if(!buffer)return NULL;
    memcpy(buffer,"CVIII058",8);
    const uint8_t *chr=rom+16u+262144u;
    unsigned char *raw=buffer+8u;
    unsigned char *pixels=raw+CVIII_CHR_RAW_BYTES;
    memcpy(raw,chr,CVIII_CHR_RAW_BYTES);
    for(size_t tile=0;tile<CVIII_CHR_RAW_BYTES/16u;tile++) {
        const unsigned char *source=raw+tile*16u;
        unsigned char *target=pixels+tile*64u;
        for(unsigned y=0;y<8u;y++)for(unsigned x=0;x<8u;x++) {
            unsigned bit=7u-x;
            target[y*8u+x]=(unsigned char)(
                ((source[y]>>bit)&1u)|
                (((source[y+8u]>>bit)&1u)<<1u));
        }
    }
#ifdef CVIII_RESOURCE_TEST_SYNTHETIC_0727
    const bool require_jp=false;
#else
    const bool require_jp=true;
#endif
    if(!cviii_chr_index_check(buffer,CVIII_CHR_INDEX_BYTES,require_jp)) {
        free(buffer);
        return NULL;
    }
    return buffer;
}

CviiiResourceStatus0727 cviii_game_resources_cached_open_0729(
    const char *path,const char *cache_path,
    CviiiStage1Atlas0724 *dst,CviiiChrIndex *chr_dst)
{
    /* SHA256 of the owner's authenticated original Japanese VRC6 cartridge.
     * Hash is the identity of ROM input, NOT redistributable gameplay data. */
    static const uint8_t jp_sha256[32]={
        0x95,0x8a,0x4b,0x5e,0x95,0xe8,0x0a,0xcb,
        0x2c,0x71,0xa4,0x3e,0x9e,0xf2,0xe9,0x14,
        0x44,0xf3,0xd0,0x97,0xae,0x9d,0x4e,0xeb,
        0x74,0x7f,0x0d,0xac,0x8a,0xbe,0x7a,0x28
    };
    if(!dst||!path||!*path)return CVIII_RESOURCE_MISSING_0727;
    FILE *file=fopen(path,"rb");
    if(!file)return CVIII_RESOURCE_MISSING_0727;
    uint8_t *rom=(uint8_t *)malloc(CVIII_RUNTIME_ROM_BYTES_0727);
    if(!rom){fclose(file);return CVIII_RESOURCE_IO_0727;}
    size_t n=fread(rom,1,CVIII_RUNTIME_ROM_BYTES_0727,file);
    int extra=fgetc(file),io_error=ferror(file);
    fclose(file);
    CviiiResourceStatus0727 status=CVIII_RESOURCE_IO_0727;
    unsigned char *new_chr=NULL;
    if(!io_error && extra==EOF) {
        if(n==CVIII_RUNTIME_ROM_BYTES_0727) {
            uint8_t digest[32];
            cviii_sha256_0727(rom,n,digest);
#ifdef CVIII_RESOURCE_TEST_SYNTHETIC_0727
            /* Only synthetic test targets enable this symbol. Production
             * always checks exact SHA256 before decoding any assets. */
            (void)jp_sha256;
            int identity=rom[0]=='N'&&rom[1]=='E'&&rom[2]=='S'&&
                         rom[3]==0x1Au&&rom[4]==16u&&rom[5]==16u;
#else
            int identity=memcmp(digest,jp_sha256,sizeof digest)==0;
#endif
            if(!identity)status=CVIII_RESOURCE_IDENTITY_0727;
            else if(cache_path && *cache_path &&
                cviii_resource_cache_read_0729(cache_path,digest,dst,chr_dst)) {
                status=CVIII_RESOURCE_READY_0727;
            } else {
                /* A cache always holds both domains, even when a vetted
                 * external CHR sidecar is already active in this process. */
                const int want_chr=chr_dst || (cache_path && *cache_path);
                if(want_chr)new_chr=make_chr_index(rom);
                if(want_chr && !new_chr)status=CVIII_RESOURCE_DECODE_0727;
                else if(cviii_stage1_atlas_load_0724(dst,rom,n)!=1)
                    status=CVIII_RESOURCE_DECODE_0727;
                else {
                    status=CVIII_RESOURCE_READY_0727;
                    if(cache_path && *cache_path && new_chr) {
                        CviiiChrIndex candidate={new_chr,new_chr+8u,
                            new_chr+8u+CVIII_CHR_RAW_BYTES};
                        /* A read-only or full cache directory is optional,
                         * never a reason to prevent starting the game. */
                        (void)cviii_resource_cache_write_0729(cache_path,
                            digest,dst,&candidate);
                    }
                    if(chr_dst) {
                        cviii_chr_index_free(chr_dst);
                        chr_dst->allocation=new_chr;
                        chr_dst->raw=new_chr+8u;
                        chr_dst->pixels=new_chr+8u+CVIII_CHR_RAW_BYTES;
                        new_chr=NULL;
                    }
                }
            }
        } else status=CVIII_RESOURCE_IDENTITY_0727;
    }
    free(new_chr);
    free(rom);
    return status;
}
CviiiResourceStatus0727 cviii_game_resources_open_0727(
    const char *path,CviiiStage1Atlas0724 *dst,CviiiChrIndex *chr_dst)
{
    return cviii_game_resources_cached_open_0729(path,NULL,dst,chr_dst);
}
CviiiResourceStatus0727 cviii_stage1_resource_open_0727(
    const char *path,CviiiStage1Atlas0724 *dst)
{
    return cviii_game_resources_open_0727(path,dst,NULL);
}
