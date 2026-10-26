/* JP0730 invented ROM metadata regression; no original game data. */
#include "cviii_rom_tsa_catalog_0730.h"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void)
{
    uint8_t *rom=(uint8_t *)calloc(393232u,1);
    CviiiTsaCatalog0730 *catalog=(CviiiTsaCatalog0730 *)calloc(1,sizeof *catalog);
    assert(rom && catalog);
    memcpy(rom,"NES\x1a",4);rom[4]=16;rom[5]=16;
    rom[6]=0x80;rom[7]=0x10;
    const CviiiTsaRegion0730 *regions=cviii_tsa_regions_0730();
    unsigned expected_count=0,valid=0;
    for(unsigned i=0;i<CVIII_TSA_REGIONS_0730;i++){
        const CviiiTsaRegion0730 *r=regions+i;
        if(!r->pattern_count) {
            assert(i==11u && ((r->source_end_inclusive-
                   r->source_start+1u)%16u)!=0u);
            continue;
        }
        assert(r->source_end_inclusive-r->source_start+1u==
               (unsigned)r->pattern_count*16u);
        assert(r->source_end_inclusive<393232u);
        valid++;
        expected_count+=r->pattern_count;
        for(unsigned j=0;j<r->pattern_count;j++)
          for(unsigned k=0;k<16u;k++)
            rom[r->source_start+(size_t)j*16u+k]=
                (uint8_t)(i+j+k);
    }
    assert(valid==14u && expected_count==CVIII_TSA_PATTERNS_0730);
    for(unsigned i=0;i<145u;i++)rom[0x20D61u+i]=(uint8_t)(i^0x55u);
    assert(cviii_tsa_catalog_load_0730(rom,393232u,catalog)==1);
    assert(catalog->loaded && catalog->offsets[15]==1478u);
    for(unsigned i=0;i<15u;i++){
        const CviiiTsaRegion0730 *r=regions+i;
        uint8_t tile[16]={0},attr=0xEFu,has=3u;
        if(!r->pattern_count){
            assert(!cviii_tsa_get_0730(catalog,i,0,tile,&attr,&has));
            continue;
        }
        for(unsigned j=0;j<r->pattern_count;j++){
            assert(cviii_tsa_get_0730(catalog,i,j,tile,&attr,&has));
            for(unsigned k=0;k<16;k++)
                assert(tile[k]==(uint8_t)(i+j+k));
            assert(has==(i==10u));
            if(i==10u)assert(attr==(uint8_t)(j^0x55u));
            else assert(attr==0u);
        }
    }
    rom[6]=0;  /* failed validation must not reset previous catalog */
    assert(!cviii_tsa_catalog_load_0730(rom,393232u,catalog));
    assert(catalog->loaded && catalog->offsets[15]==1478u);
    free(catalog);free(rom);
    puts("PASS JP0730 fourteen bounded TSA regions; Clocktower blocked");
    return 0;
}
