#include "cviii_stage1_rom_0724.h"
/* Authentic retail JP iNES file offsets: Stage 1 layout records followed
 * by the Wallachia bank08 4x4 background TSA patterns and attribute bytes.
 * The original data itself is loaded from the owner's ROM at runtime.
 */
#define TSA_BYTES 16u
#define TSA_COUNT 145u
#define TSA_PATTERN 0x20451u
#define TSA_ATTRIBUTE (TSA_PATTERN + TSA_COUNT * TSA_BYTES)
#define ROM_BYTES 393232u
#define SCREEN_HORIZONTAL 48u
#define SCREEN_VERTICAL 64u

typedef struct { uint8_t key[3]; uint32_t header; uint8_t screens; uint8_t vertical; } Room;
static const Room rooms[] = {
    {{0,0,0},0x200BAu,3,0}, /* BLK 1-01:0 */
    {{0,1,0},0x2014Bu,1,0}, /* BLK 1-02:0 */
    {{0,1,1},0x20039u,2,1}, /* BLK 1-02:1, vertical */
    {{0,1,2},0x201DDu,3,0}, /* source-proven gameplay BLK 1-02:2 */
    {{0,1,3},0x2017Cu,2,0}, /* source-proven gameplay BLK 1-02:3 */
    {{0,2,0},0x2026Eu,3,0}, /* BLK 1-03:0 */
    {{0,2,1},0x202FFu,3,0}, /* BLK 1-03:1 */
    {{0,3,0},0x20390u,4,0}  /* BLK 1-04:0 */
};
int cviii_stage1_rom_0724(const uint8_t *rom, size_t len,
    const uint8_t sel[3], CviiiStage1TileSink0724 sink,
    void *ctx, CviiiStage1Room0724 *out) {
    const Room *room = 0;
    uint32_t count, i, mx, my, wmt, hmt;
    CviiiStage1Room0724 info;
    if (!rom || !sel || !sink || !out || len != ROM_BYTES ||
        rom[0]!='N'||rom[1]!='E'||rom[2]!='S'||rom[3]!=0x1Au ||
        rom[4]!=16u || rom[5]!=16u ||
        (((unsigned)rom[6]>>4)|((unsigned)rom[7]&0xF0u))!=24u)
        return -1;
    for (i=0; i<sizeof rooms/sizeof rooms[0]; i++) {
        const Room *p = &rooms[i];
        if (p->key[0]==sel[0]&&p->key[1]==sel[1]&&p->key[2]==sel[2]) {
            room=p;break;
        }
    }
    if (!room) return 0;
    count=room->screens*(room->vertical?SCREEN_VERTICAL:SCREEN_HORIZONTAL);
    if (room->header+1u+count>TSA_PATTERN ||
        rom[room->header]!=(uint8_t)(room->screens-1u) ||
        TSA_ATTRIBUTE+TSA_COUNT>len) return -1;
    /* Transactional source validation before emitting any tile. */
    for(i=0; i<count; i++)
        if(rom[room->header+1u+i]>=TSA_COUNT) return -1;
    wmt=room->vertical?8u:room->screens*8u;
    hmt=room->vertical?room->screens*8u:6u;
    info.width_tiles=(uint16_t)(wmt*4u);
    info.height_tiles=(uint16_t)(hmt*4u);
    info.metatile_count=(uint16_t)count;
    info.vertical=room->vertical;
    info.source_layout_offset=room->header+1u;
    info.source_tsa_pattern_offset=TSA_PATTERN;
    info.source_tsa_attribute_offset=TSA_ATTRIBUTE;
    for(my=0;my<hmt;my++)for(mx=0;mx<wmt;mx++) {
        unsigned idx=room->vertical
            ? (my/8u)*SCREEN_VERTICAL + (my%8u)*8u+mx
            : (mx/8u)*SCREEN_HORIZONTAL + my*8u+(mx%8u);
        uint8_t tsa=rom[room->header+1u+idx];
        uint8_t attribute=rom[TSA_ATTRIBUTE+tsa];
        unsigned dy,dx;
        for(dy=0;dy<4u;dy++)for(dx=0;dx<4u;dx++) {
            uint8_t tile=rom[TSA_PATTERN+tsa*TSA_BYTES+dy*4u+dx];
            uint8_t palette=(uint8_t)((attribute >> (4u*(dy/2u)+2u*(dx/2u)))&3u);
            if (!sink(ctx,(uint16_t)(mx*4u+dx),(uint16_t)(my*4u+dy),tile,palette))
                return -1;
        }
    }
    *out=info;
    return 1;
}
