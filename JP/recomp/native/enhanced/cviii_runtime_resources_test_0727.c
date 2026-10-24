/* JP0727: both production fail-closed and synthetic import tests.
 * Only invented ROM bytes appear in this test; never publish retail assets.
 */
#include "cviii_runtime_resources_0727.h"
#include "cviii_resource_cache_0729.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void sha_test(const char *input,const char *expected)
{
    uint8_t hash[32];
    size_t n=strlen(input);
    cviii_sha256_0727((const uint8_t *)input,n,hash);
    for(unsigned i=0;i<32u;i++) {
        unsigned expected_byte=0;
        assert(sscanf(expected+2u*i,"%2x",&expected_byte)==1);
        assert(hash[i]==expected_byte);
    }
}
static void emit(const char *path,const uint8_t *rom,size_t n)
{
    FILE *f=fopen(path,"wb");
    assert(f);
    assert(fwrite(rom,1,n,f)==n);
    assert(fclose(f)==0);
}
int main(void)
{
    sha_test("","e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    sha_test("abc","ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    sha_test("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
             "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
    char repeated[65];
    memset(repeated,'a',64);
    repeated[64]=0;
    sha_test(repeated,"ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb");

    const char *path="jp0727-invented-runtime-media.nes";
    CviiiStage1Atlas0724 *atlas=(CviiiStage1Atlas0724 *)calloc(1,sizeof *atlas);
    uint8_t *rom=(uint8_t *)calloc(CVIII_RUNTIME_ROM_BYTES_0727,1);
    assert(rom && atlas);
    atlas->loaded=77;
    assert(cviii_stage1_resource_open_0727("nonexistent-jp0727-source.nes",atlas)
           ==CVIII_RESOURCE_MISSING_0727);
    assert(atlas->loaded==77);
    memcpy(rom,"NES\x1a",4);rom[4]=16;rom[5]=16;
    rom[6]=0x80;rom[7]=0x10;
    static const unsigned headers[]={0x200BA,0x2014B,0x20039,0x201DD,
                                      0x2017C,0x2026E,0x202FF,0x20390};
    static const unsigned pages[]={3,1,2,3,2,3,3,4};
    for(unsigned i=0;i<8;i++)rom[headers[i]]=(uint8_t)(pages[i]-1u);
    for(unsigned i=0;i<145;i++) {
        for(unsigned j=0;j<16;j++)rom[0x20451+i*16+j]=(uint8_t)(i+j);
        rom[0x20d61+i]=0xe4;
    }
    /* Synthetic CHR source: first pixel uses both bitplanes. The rest
     * remain zero. All 8,192 graphics tiles are reconstructed in memory. */
    rom[16u+262144u]=0x80;
    rom[16u+262144u+8u]=0x80;
    CviiiChrIndex chr={0};
    emit(path,rom,CVIII_RUNTIME_ROM_BYTES_0727-1);
    assert(cviii_stage1_resource_open_0727(path,atlas)
           !=CVIII_RESOURCE_READY_0727 && atlas->loaded==77);

    emit(path,rom,CVIII_RUNTIME_ROM_BYTES_0727);
#ifdef CVIII_RESOURCE_TEST_SYNTHETIC_0727
    assert(cviii_game_resources_open_0727(path,atlas,&chr)
           ==CVIII_RESOURCE_READY_0727);
    assert(chr.allocation && chr.raw && chr.pixels);
    assert(chr.raw[0]==0x80 && chr.raw[8]==0x80);
    assert(chr.pixels[0]==3u && chr.pixels[1]==0u);
    assert(chr.pixels[64u]==0u);
    assert(cviii_chr_index_check(chr.allocation,CVIII_CHR_INDEX_BYTES,false));
    uint8_t tile=0,palette=0,sel[3]={0,0,0};
    assert(atlas->loaded && cviii_stage1_atlas_get_0724(
        atlas,sel,3,3,&tile,&palette));
    assert(tile==15 && palette==3);
    /* The disk format must round-trip without pointer/struct padding
     * dependencies. The ROM is authenticated before every cache lookup. */
    const char *cache="jp0729-only-private-synthetic-cache.dat";
    (void)remove(cache);
    uint8_t digest[32],wrong_digest[32];
    cviii_sha256_0727(rom,CVIII_RUNTIME_ROM_BYTES_0727,digest);
    memcpy(wrong_digest,digest,32);
    wrong_digest[1]^=0x55;
    assert(cviii_game_resources_cached_open_0729(
        path,cache,atlas,&chr)==CVIII_RESOURCE_READY_0727);
    FILE *probe=fopen(cache,"rb");
    assert(probe);
    assert(fclose(probe)==0);
    CviiiStage1Atlas0724 *from_cache=calloc(1,sizeof *from_cache);
    CviiiChrIndex cache_chr={0};
    assert(from_cache);
    assert(cviii_resource_cache_read_0729(cache,digest,from_cache,&cache_chr));
    assert(memcmp(from_cache->tile,atlas->tile,CVIII_STAGE1_TILES_0724)==0);
    assert(memcmp(from_cache->palette,atlas->palette,CVIII_STAGE1_TILES_0724)==0);
    assert(memcmp(cache_chr.raw,chr.raw,CVIII_CHR_RAW_BYTES)==0);
    assert(memcmp(cache_chr.pixels,chr.pixels,CVIII_CHR_PIXEL_BYTES)==0);
    assert(!cviii_resource_cache_read_0729(cache,wrong_digest,
                                           from_cache,&cache_chr));
    /* Tampering with the payload checksum must reject the entire cache,
     * leaving both previously loaded resources unchanged. */
    unsigned char *saved_index=cache_chr.allocation;
    probe=fopen(cache,"r+b");
    assert(probe && fseek(probe,48L,SEEK_SET)==0);
    int oldbyte=fgetc(probe);
    assert(oldbyte!=EOF && fseek(probe,48L,SEEK_SET)==0);
    assert(fputc(oldbyte^0xff,probe)!=EOF && fclose(probe)==0);
    assert(!cviii_resource_cache_read_0729(cache,digest,
                                           from_cache,&cache_chr));
    assert(cache_chr.allocation==saved_index &&
           from_cache->loaded==1);
    assert(cviii_game_resources_cached_open_0729(
        path,cache,atlas,&chr)==CVIII_RESOURCE_READY_0727);
    assert(cviii_resource_cache_read_0729(cache,digest,
                                          from_cache,NULL));
    /* Newer unknown cache schema must regenerate from the original ROM. */
    probe=fopen(cache,"r+b");
    assert(probe && fseek(probe,8L,SEEK_SET)==0);
    assert(fputc(0xff,probe)!=EOF && fclose(probe)==0);
    assert(cviii_game_resources_cached_open_0729(
        path,cache,atlas,&chr)==CVIII_RESOURCE_READY_0727);
    assert(cviii_resource_cache_read_0729(cache,digest,
                                          from_cache,NULL));
    cviii_chr_index_free(&cache_chr);
    free(from_cache);
    unsigned char *prior=chr.allocation;
    /* A malformed new ROM must not destroy the previous atlas or CHR. */
    rom[headers[0]]=7u;
    emit(path,rom,CVIII_RUNTIME_ROM_BYTES_0727);
    /* The prior valid cache may not mask an invalid/different ROM. */
    assert(cviii_game_resources_cached_open_0729(path,cache,atlas,&chr)
           ==CVIII_RESOURCE_DECODE_0727);
    assert(chr.allocation==prior && atlas->loaded);
    assert(cviii_stage1_atlas_get_0724(atlas,sel,3,3,&tile,&palette));
    cviii_chr_index_free(&chr);
    (void)remove(cache);
#else
    /* This synthetic media MUST fail production full-file SHA256.
     * Test still passes if a corrupt or unrelated retail image is rejected.
     */
    assert(cviii_game_resources_open_0727(path,atlas,&chr)
           ==CVIII_RESOURCE_IDENTITY_0727);
    assert(chr.allocation==NULL);
    assert(atlas->loaded==77);
#endif
    (void)remove(path);
    free(rom);
    free(atlas);
    puts("PASS JP0727 SHA256, runtime resource loading and fail-closed isolation");
    return 0;
}
