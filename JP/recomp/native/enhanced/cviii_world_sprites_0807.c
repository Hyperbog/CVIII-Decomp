#include "cviii_world_sprites_0807.h"
#include <stddef.h>
#include <string.h>
/* The actual VRC6 original PRG26+27 bank is already independently hashed
 * after source-authenticated private ROM import. Do not serialize or ship it.
 * Original PRG26:$8001 exposes 28 actor slots and compressed descriptors.
 * This painter NEVER writes original game RAM, OAM, or collision registers. */
static int byte_at(const uint8_t bank[CVIII_SPRITE_BANK_BYTES_0807],
                   uint32_t cpu_addr,uint8_t *out)
{
    if(cpu_addr<0x8000u || cpu_addr>0xbfffu)return 0;
    *out=bank[cpu_addr-0x8000u];return 1;
}
static int ptr_at(const uint8_t *bank,uint32_t base,uint8_t offset,
                  uint16_t *value)
{
    uint8_t lo=0,hi=0;
    if(!byte_at(bank,base+offset,&lo) ||
       !byte_at(bank,base+(uint8_t)(offset+1u),&hi))return 0;
    *value=(uint16_t)(lo|((uint16_t)hi<<8u));
    return *value>=0x8000u && *value<=0xbfffu;
}
static int signed_byte(uint8_t v){return v<128u?(int)v:(int)v-256;}
static int shifted_y(uint8_t v){
    uint8_t shifted=(uint8_t)((v>>1u)|(v&0x80u));
    return signed_byte(shifted);
}
uint32_t cviii_world_sprites_draw_0807(const CviiiLevel1World0803 *w,
    const uint8_t key[3],int cx,int cy,int center,
    uint32_t *dest,int width,int height,
    const uint8_t bank[CVIII_SPRITE_BANK_BYTES_0807],
    const uint8_t ram[2048],uint16_t sprite_table,
    int sprite16,uint8_t (*chr)(uint16_t),uint32_t (*color)(int))
{
    if(!w || !w->ready || !key || !dest || !bank || !ram ||
       !chr || !color || width<256 || height!=240 ||
       center<0 || center+256>width ||
       (sprite_table!=0 && sprite_table!=0x1000))return 0;
    int32_t wx=0,wy=0;
    if(!cviii_world_camera_0803(w,key,cx,cy,&wx,&wy))return 0;
    uint32_t painted=0;
    uint8_t attr_cache=0;
    int cached=0;
    for(unsigned i=0;i<CVIII_WORLD_ACTORS_0803;i++){
        const CviiiWorldActor0803 *a=&w->actors[i];
        if(!a->active || a->slot!=i ||
           (a->flags&0x80u) || !a->frame)continue;
        uint16_t set=0,descriptor=0;
        if(!ptr_at(bank,0x817fu,a->selector,&set) ||
           !ptr_at(bank,set,a->frame,&descriptor))continue;
        uint8_t count=0,cursor=1;
        if(!byte_at(bank,descriptor,&count) || count>27u)continue;
        const int mirror=a->mirror==0u;
        const int sx=(int)(a->x-wx)+center;
        const int sy=(int)(a->y-wy)+1; /* NES OAM Y+1 semantics */
        for(unsigned sp=0;sp<count;sp++){
            uint8_t ycode=0,tile=0,raw=0;
            if(!byte_at(bank,descriptor+cursor++,&ycode) ||
               !byte_at(bank,descriptor+cursor++,&tile))break;
            const int reuse=(ycode&1u)!=0u;
            if(!reuse){
                uint8_t source_attr=0;
                if(!byte_at(bank,descriptor+cursor++,&source_attr))break;
                attr_cache=a->attrs
                    ?(uint8_t)((source_attr&0xfcu)|a->attrs)
                    :source_attr;
                if(mirror)attr_cache^=0x40u;
                cached=1;
            }
            if(!byte_at(bank,descriptor+cursor++,&raw))break;
            if(!cached)continue; /* no invented compression-state cache */
            if(ram[0xadu] && a->selector>=0x16u)
                tile=(uint8_t)(tile+0x80u);
            if(mirror)raw=(uint8_t)(0xf8u-raw);
            const int x=sx+signed_byte(raw),y=sy+shifted_y(ycode);
            const int pixel_rows=sprite16?16:8;
            if(x>=width || x+8<=0 || y>=height || y+pixel_rows<=48)
                continue;
            for(int row=0;row<pixel_rows;row++){
                int py=y+row;
                if(py<48 || py>=height)continue;
                int rr=(attr_cache&0x80u)?pixel_rows-1-row:row;
                uint16_t pattern=sprite16
                    ?(uint16_t)((tile&1u?0x1000u:0u)+
                        (tile&0xfeu)*16u+(rr>=8?16u:0u))
                    :(uint16_t)(sprite_table+(unsigned)tile*16u);
                uint8_t lo=chr((uint16_t)(pattern+(rr&7)));
                uint8_t hi=chr((uint16_t)(pattern+(rr&7)+8));
                for(int col=0;col<8;col++){
                    int px=x+col;
                    /* NEVER modify any native NES gameplay picture.
                     * No double-spawn, no duplication or sprite-hardware
                     * priority changes inside the original 256px. */
                    if(px<0 || px>=width ||
                       (px>=center && px<center+256))continue;
                    int bit=(attr_cache&0x40u)?col:7-col;
                    unsigned index=((lo>>bit)&1u)|(((hi>>bit)&1u)<<1u);
                    if(!index)continue;
                    dest[(size_t)py*(unsigned)width+(unsigned)px]=
                        color(16+(attr_cache&3u)*4u+(int)index);
                    painted++;
                }
            }
        }
    }
    return painted;
}
