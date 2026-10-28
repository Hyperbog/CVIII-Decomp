#include "cviii_ppu_wide_0830.h"
#include <stddef.h>

/* The PPU has two physical horizontal screens; do not infer a third one.
 * Mirrored pages cannot establish a genuine wide neighbor. */
static int ppu_coordinates(int scroll_x,int scroll_y,int dx,
                           unsigned *page,unsigned *tile_x,
                           unsigned *tile_y,unsigned *fine_x,
                           unsigned *fine_y)
{
    if(scroll_x<0 || scroll_x>=512 || scroll_y<0 || scroll_y>=480 ||
       dx< -854 || dx>854)return 0;
    int x=(scroll_x+dx+1024)%512;
    int y=scroll_y;
    *page=(unsigned)(x/256)+2u*(unsigned)(y/240);
    *tile_x=(unsigned)(x%256)/8u;
    *tile_y=(unsigned)(y%240)/8u;
    *fine_x=(unsigned)(x%8);
    *fine_y=(unsigned)(y%8);
    return 1;
}
static int tile_index(const CviiiPpuWideSource0830 *s,
                      int line,int dx,uint8_t *tile_out)
{
    unsigned p,tx,ty,fx,fy;
    if(!ppu_coordinates(s->scroll_x(line),s->scroll_y(line),dx,
                        &p,&tx,&ty,&fx,&fy))return 0;
    (void)fx;(void)fy;
    *tile_out=s->nametable((uint16_t)
        (0x2000u+p*0x400u+ty*32u+tx));
    return 1;
}
static int bgcolor(const CviiiPpuWideSource0830 *s,
                   int line,int dx,uint32_t *out)
{
    unsigned page,tx,ty,fx,fy;
    if(!ppu_coordinates(s->scroll_x(line),s->scroll_y(line),dx,
                        &page,&tx,&ty,&fx,&fy))return 0;
    uint16_t pattern_base=s->bg_table(line);
    if(pattern_base!=0u && pattern_base!=0x1000u)return 0;
    uint16_t nt=(uint16_t)(0x2000u+page*1024u+ty*32u+tx);
    uint16_t at=(uint16_t)(0x23c0u+page*1024u+(ty/4u)*8u+tx/4u);
    unsigned tile=s->nametable(nt);
    unsigned attr=s->nametable(at);
    unsigned quad=(ty%4u)/2u*2u+(tx%4u)/2u;
    unsigned palette=(attr>>(quad*2u))&3u;
    unsigned pattern=pattern_base+tile*16u+fy;
    unsigned bit=7u-fx;
    unsigned lo=s->chr((uint16_t)pattern);
    unsigned hi=s->chr((uint16_t)(pattern+8u));
    unsigned ci=((lo>>bit)&1u)|(((hi>>bit)&1u)<<1u);
    *out=s->color(ci?(int)(palette*4u+ci):0);
    return 1;
}
static int sprite_overlap(const uint8_t *oam,int x,int y)
{
    if(!oam)return 0;
    for(unsigned i=0;i<64u;i++) {
        const uint8_t *o=oam+i*4u;
        if(o[0]>=0xefu)continue;
        /* Generous 8x16 exclusion, even if this frame used 8x8.
         * Avoid treating a sprite over genuine background as a mismatch. */
        int sy=(int)o[0]+1,sx=o[3];
        if(y>=sy && y<sy+16 && x>=sx && x<sx+8)return 1;
    }
    return 0;
}
/* Check that the visible frame really uses the current PPU nametable,
 * CHR mapping and palette. Renderer reads the PPU after frame end: IRQ,
 * CHR switches, scrolling or a partially installed room can invalidate it.
 * We deliberately fall back to the original picture in those cases. */
static int visible_agrees(const CviiiPpuWideSource0830 *s,
                          const uint32_t *native)
{
    unsigned tested=0,matched=0;
    for(int y=56;y<=216;y+=16) {
        if(!(s->mask(y)&8u))return 0;
        for(int x=16;x<=240;x+=16) {
            if(sprite_overlap(s->oam,x,y))continue;
            uint32_t expected=0;
            if(!bgcolor(s,y,x,&expected))return 0;
            matched+=(native[(size_t)y*256u+(unsigned)x]==expected);
            tested++;
        }
    }
    return tested>=90u && matched*100u>=tested*96u;
}
static int independent_horizontal_pages(const CviiiPpuWideSource0830 *s)
{
    unsigned distinct=0;
    for(unsigned row=5u;row<28u;row+=5u)
        for(unsigned col=3u;col<29u;col+=6u) {
            unsigned a=0x2000u+row*32u+col;
            distinct+=(s->nametable((uint16_t)a)!=
                       s->nametable((uint16_t)(a+0x400u)));
        }
    return distinct>=4u;
}
static int margin_has_geometry(const CviiiPpuWideSource0830 *s,
                               int origin,int min_x,int max_x)
{
    uint8_t examples[32]={0};
    unsigned unique=0;
    if(max_x<=min_x)return 0;
    for(int y=64;y<=208;y+=36)
        for(int x=min_x+4;x<max_x;x+=16) {
            uint8_t tile=0;
            if(!tile_index(s,y,x-origin,&tile))return 0;
            unsigned i=0;
            for(;i<unique;i++)if(examples[i]==tile)break;
            if(i==unique && unique<32u)examples[unique++]=tile;
        }
    return unique>=4u;
}
uint32_t cviii_ppu_wide_paint_0830(
    const CviiiPpuWideSource0830 *s,
    const uint32_t *native,uint32_t *wide,
    int width,int height,int origin)
{
    if(!s || !s->nametable || !s->chr || !s->color ||
       !s->scroll_x || !s->scroll_y || !s->bg_table || !s->mask ||
       !native || !wide || width<=256 || width>864 || height!=240 ||
       origin<0 || origin+256>width)return 0;
    if(!independent_horizontal_pages(s) || !visible_agrees(s,native))
        return 0;
    int left=margin_has_geometry(s,origin,0,origin);
    int right=margin_has_geometry(s,origin,origin+256,width);
    if(!left && !right)return 0;
    /* Guard validity for every scanline BEFORE drawing any pixels;
     * a rejected renderer is strictly transactional on the canvas. */
    for(int y=48;y<240;y++) {
        if(!(s->mask(y)&8u) ||
           (s->bg_table(y)!=0u && s->bg_table(y)!=0x1000u) ||
           s->scroll_x(y)<0 || s->scroll_x(y)>=512 ||
           s->scroll_y(y)<0 || s->scroll_y(y)>=480)
            return 0;
    }
    uint32_t painted=0;
    for(int y=48;y<240;y++) {
        if(left)for(int x=0;x<origin;x++) {
            uint32_t pixel=0;
            if(!bgcolor(s,y,x-origin,&pixel))return 0;
            wide[(size_t)y*(unsigned)width+(unsigned)x]=pixel;
            painted++;
        }
        if(right)for(int x=origin+256;x<width;x++) {
            uint32_t pixel=0;
            if(!bgcolor(s,y,x-origin,&pixel))return 0;
            wide[(size_t)y*(unsigned)width+(unsigned)x]=pixel;
            painted++;
        }
    }
    return painted;
}
