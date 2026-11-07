/* All content invented. End-to-end PPU strip painter contract without ROM. */
#ifdef NDEBUG
#undef NDEBUG
#endif
#include "cviii_ppu_wide_0830.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
enum { W=426, H=240, X0=85 };
static uint8_t nt[4096],oam[256];
static uint32_t native[256*H],wide[W*H],unchanged[W*H];
static int bad_line=-1,scroll=96,wrong_bg=0;
static uint8_t read_nt(uint16_t a){return nt[a&4095u];}
static uint8_t read_chr(uint16_t a){
    return (a&15u)<8u?0xffu:0u; /* all source tiles use pixel 1 */
}
static uint32_t read_color(int p){return 0xff000000u|(unsigned)p;}
static int scroll_x(int y){(void)y;return scroll;}
static int scroll_y(int y){return y%240;}
static uint16_t table(int y){(void)y;return wrong_bg?0x0800u:0x1000u;}
static uint8_t mask(int y){return y==bad_line?0u:0x1eu;}
static CviiiPpuWideSource0830 src={
    read_nt,read_chr,read_color,scroll_x,scroll_y,table,mask,oam
};
static void fill(void){
    memset(nt,0,sizeof nt);
    memset(oam,0xff,sizeof oam);
    for(unsigned page=0;page<4u;page++) {
        for(unsigned y=0;y<30u;y++)
            for(unsigned x=0;x<32u;x++)
                nt[page*1024u+y*32u+x]=(uint8_t)(1u+page*41u+x+7u*y);
        /* Attributes are all zero: background palette zero. */
    }
    for(unsigned i=0;i<256u*H;i++)native[i]=read_color(1);
    for(unsigned y=0;y<H;y++) {
        for(unsigned x=0;x<W;x++)wide[y*W+x]=0xffaabbccu;
        memcpy(wide+y*W+X0,native+y*256u,256u*sizeof(uint32_t));
    }
    memcpy(unchanged,wide,sizeof wide);
}
int main(void){
    fill();
    uint32_t n=cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0);
    assert(n==192u*(85u+85u));
    for(unsigned y=0;y<H;y++)for(unsigned x=0;x<W;x++){
        unsigned idx=y*W+x;
        if(x>=X0 && x<X0+256u)assert(wide[idx]==unchanged[idx]);
        else if(y<48u)assert(wide[idx]==0xffaabbccu);
        else assert(wide[idx]==read_color(1));
    }
    fill();wrong_bg=1;
    assert(!cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0));
    assert(!memcmp(wide,unchanged,sizeof wide));wrong_bg=0;
    fill();bad_line=93;
    assert(!cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0));
    assert(!memcmp(wide,unchanged,sizeof wide));bad_line=-1;
    fill();native[80u*256u+64u]=0xffaabbccu;
    /* One corrupt on-screen pixel is tolerated; many aren't. */
    assert(cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0));
    fill();
    for(unsigned y=56;y<=216;y+=16)
        for(unsigned x=16;x<=240;x+=16)
            native[y*256u+x]=0xff123456u;
    assert(!cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0));
    assert(!memcmp(wide,unchanged,sizeof wide));
    fill();
    memcpy(nt+1024,nt,1024);
    memcpy(nt+3072,nt+2048,1024);
    assert(!cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0));
    assert(!memcmp(wide,unchanged,sizeof wide));
    fill();scroll=-1;
    assert(!cviii_ppu_wide_paint_0830(&src,native,wide,W,H,X0));
    assert(!memcmp(wide,unchanged,sizeof wide));scroll=96;
    fill();
    assert(!cviii_ppu_wide_paint_0830(NULL,native,wide,W,H,X0));
    assert(!cviii_ppu_wide_paint_0830(&src,native,wide,256,H,0));
    assert(!memcmp(wide,unchanged,sizeof wide));
    puts("PASS: PPU-matched side margins, native center untouched, invalid source fails closed");
    return 0;
}
