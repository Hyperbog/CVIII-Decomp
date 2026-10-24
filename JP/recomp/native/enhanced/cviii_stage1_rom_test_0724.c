/* ROM-free synthetic JP0724 room map/palette decoder regression. */
#include "cviii_stage1_rom_0724.h"
/* Windows/CI Release adds NDEBUG; tests must never silently skip checks
 * or suppress setup side effects written inside assert expressions. */
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
static unsigned n, seen[128*64];
static int put(void *ctx,uint16_t x,uint16_t y,uint8_t tile,uint8_t pal){
    (void)ctx;
    assert(x<128&&y<64&&pal<4);
    n++;
    seen[y*128+x]=((unsigned)tile<<8)|pal;
    return 1;
}
int main(void){
    uint8_t *rom=calloc(393232,1);
    assert(rom);
    memcpy(rom,"NES\x1a",4);
    rom[4]=16;rom[5]=16;rom[6]=0x80;rom[7]=0x10;
    const unsigned headers[]={0x200BA,0x2014B,0x20039,0x201DD,
                              0x2017C,0x2026E,0x202FF,0x20390};
    const unsigned screens[]={3,1,2,3,2,3,3,4};
    for(unsigned i=0;i<8;i++)rom[headers[i]]=(uint8_t)(screens[i]-1);
    for(unsigned i=0;i<145;i++){
        for(unsigned j=0;j<16;j++)rom[0x20451+i*16+j]=(uint8_t)(i+j);
        rom[0x20D61+i]=(uint8_t)(i&3?0xE4:0x1B);
    }
    for(unsigned i=0;i<8;i++){
        uint8_t sel[3]={0};
        if(i==0){sel[1]=0;sel[2]=0;}
        else if(i<=4){sel[1]=1;sel[2]=(uint8_t)(i-1);}
        else if(i<=6){sel[1]=2;sel[2]=(uint8_t)(i-5);}
        else{sel[1]=3;}
        n=0;memset(seen,0,sizeof seen);
        CviiiStage1Room0724 h={0};
        assert(cviii_stage1_rom_0724(rom,393232,sel,put,0,&h)==1);
        assert(h.metatile_count==screens[i]*(i==2?64:48));
        assert(n==h.width_tiles*h.height_tiles);
        assert(h.vertical==(i==2));
    }
    uint8_t sel[]={0,0,0};
    CviiiStage1Room0724 h={0};
    rom[0x200BB]=145;
    n=0;
    assert(cviii_stage1_rom_0724(rom,393232,sel,put,0,&h)==-1&&n==0);
    rom[0x200BB]=0;
    assert(cviii_stage1_rom_0724(rom,393232,sel,put,0,&h)==1);
    assert(seen[0]==3u);
    sel[0]=15;
    assert(cviii_stage1_rom_0724(rom,393232,sel,put,0,&h)==0);
    assert(cviii_stage1_rom_0724(rom,393230,sel,put,0,&h)==-1);
    free(rom);
    puts("PASS JP0724 eight Stage 1 ROM layouts and attribute quadrants");
    return 0;
}
