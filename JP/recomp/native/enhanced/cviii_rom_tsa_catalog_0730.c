#include "cviii_rom_tsa_catalog_0730.h"
#include <string.h>

/* Japanese-specific original cartridge file offsets (includes 16-byte
 * iNES header). These are static candidate TSA definition spans, NOT
 * evidence of their game-owned selector/room mapping. Clocktower's
 * published $2141A-$21965 span is not divisible by 16: fail closed.
 */
static const CviiiTsaRegion0730 regions[CVIII_TSA_REGIONS_0730]={
  {"Catacombs",       0x182D0u,0x187CFu, 80u,0u},
  {"Abandoned Mines", 0x18EDBu,0x19EDAu,256u,0u},
  {"Main Hall",       0x1A2FBu,0x1A8FAu, 96u,0u},
  {"Inner Hall",      0x1AC9Au,0x1B269u, 93u,0u},
  {"Castle Keep",     0x1B592u,0x1BD51u,124u,0u},
  {"Causeway",        0x1C459u,0x1C9B8u, 86u,0u},
  {"Swamp",           0x1CD94u,0x1D143u, 59u,0u},
  {"Alucard's Cave",  0x1D78Eu,0x1DD8Du, 96u,0u},
  {"Sunken City",     0x1E3BEu,0x1E9BDu, 96u,0u},
  {"Lookout Tower",   0x1EDFAu,0x1F3C9u, 93u,0u},
  {"Wallachia",       0x20451u,0x20D60u,145u,1u},
  {"Clocktower",      0x2141Au,0x21965u,  0u,0u},
  {"Forest",          0x22120u,0x2263Fu, 82u,0u},
  {"Ghost Ship",      0x22C7Du,0x232BCu,100u,0u},
  {"Tower",           0x23737u,0x23BB6u, 72u,0u}
};
const CviiiTsaRegion0730 *cviii_tsa_regions_0730(void)
{
    return regions;
}
int cviii_tsa_catalog_load_0730(const uint8_t *rom,size_t n,
                                  CviiiTsaCatalog0730 *out)
{
    if(!rom||!out||n!=393232u||memcmp(rom,"NES\x1a",4)!=0||
       rom[4]!=16u||rom[5]!=16u||
       (((unsigned)rom[6]>>4)|((unsigned)rom[7]&0xf0u))!=24u)
        return 0;
    CviiiTsaCatalog0730 temp={0};
    unsigned offset=0;
    for(unsigned i=0;i<CVIII_TSA_REGIONS_0730;i++){
        const CviiiTsaRegion0730 *r=regions+i;
        unsigned span=r->source_end_inclusive-r->source_start+1u;
        temp.offsets[i]=(uint16_t)offset;
        if(!r->pattern_count) {
            /* Do NOT turn the malformed Clocktower boundary into tiles. */
            if(span%16u==0u)return 0;
            continue;
        }
        if(span!=(unsigned)r->pattern_count*16u ||
           (size_t)r->source_end_inclusive>=n ||
           offset+r->pattern_count>CVIII_TSA_PATTERNS_0730)
            return 0;
        memcpy(temp.tiles+(size_t)offset*16u,rom+r->source_start,span);
        offset+=r->pattern_count;
    }
    if(offset!=CVIII_TSA_PATTERNS_0730)return 0;
    temp.offsets[CVIII_TSA_REGIONS_0730]=(uint16_t)offset;
    memcpy(temp.wallachia_attributes,rom+0x20D61u,
           sizeof temp.wallachia_attributes);
    temp.loaded=1;
    memcpy(out,&temp,sizeof temp);
    return 1;
}
int cviii_tsa_get_0730(const CviiiTsaCatalog0730 *c,
    unsigned region,unsigned pattern,uint8_t out_tiles[16],
    uint8_t *attribute,uint8_t *has_attributes)
{
    if(!c||!c->loaded||!out_tiles||
       region>=CVIII_TSA_REGIONS_0730 ||
       pattern>=regions[region].pattern_count) return 0;
    unsigned offset=c->offsets[region]+pattern;
    if(offset>=CVIII_TSA_PATTERNS_0730)return 0;
    memcpy(out_tiles,c->tiles+(size_t)offset*16u,16u);
    if(has_attributes)*has_attributes=regions[region].palette_verified;
    if(attribute)*attribute=regions[region].palette_verified ?
        c->wallachia_attributes[pattern] : 0u;
    return 1;
}
