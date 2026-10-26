#include "cviii_stage1_atlas_0724.h"
/* Windows/CI Release adds NDEBUG; tests must never silently skip checks
 * or suppress setup side effects written inside assert expressions. */
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t pixel(uint16_t v){(void)v;return 255;}
static uint32_t color(int c){return 0xff000000u|((unsigned)c<<8u);}
int main(void){
 uint8_t *rom=calloc(393232,1);assert(rom);memcpy(rom,"NES\x1a",4);
 rom[4]=16;rom[5]=16;rom[6]=0x80;rom[7]=0x10;
 const unsigned heads[]={0x200BA,0x2014B,0x20039,0x201DD,
                        0x2017C,0x2026E,0x202FF,0x20390};
 const unsigned sizes[]={3,1,2,3,2,3,3,4};
 for(unsigned i=0;i<8;i++)rom[heads[i]]=sizes[i]-1;
 for(unsigned i=0;i<145;i++){
  for(unsigned j=0;j<16;j++)rom[0x20451+i*16+j]=(uint8_t)(i+j);
  rom[0x20d61+i]=0xe4;
 }
 CviiiStage1Atlas0724 *a=calloc(1,sizeof *a);assert(a);
 assert(cviii_stage1_atlas_load_0724(a,rom,393232)==1);
 uint8_t key[]={0,0,0},tile=255,pal=255;
 assert(cviii_stage1_atlas_get_0724(a,key,0,0,&tile,&pal)&&tile==0&&pal==0);
 assert(cviii_stage1_atlas_get_0724(a,key,3,3,&tile,&pal)&&tile==15&&pal==3);
 uint32_t *p=malloc(426*240*4);assert(p);
 for(int i=0;i<426*240;i++)p[i]=0xff123456;
 uint32_t count=cviii_stage1_atlas_paint_0724(a,key,85,0,p,426,240,85,pixel,color);
 assert(count==170u*192u && p[32*426+0] != 0xff123456 &&
        p[32*426+85]==0xff123456 && p[32*426+85+255]==0xff123456);
    /* JP0781: world view at X=0 must not overpaint the fixed NES HUD's
     * lower PLAYER/ENEMY/heart rows 32..47. Actual room pixels outside
     * the HUD may still be painted using the world camera. */
    for(int y=0;y<426*240;y++)p[y]=0xff123456u;
    count=cviii_stage1_atlas_paint_0724(a,key,0,0,p,426,240,0,pixel,color);
    assert(count>0u &&
           p[40*426+85]==0xff123456u &&
           p[47*426+340]==0xff123456u &&
           p[48*426+85]==0xff123456u &&
           p[48*426+341]!=0xff123456u &&
           p[40*426+400]!=0xff123456u);
 rom[0x2014c]=200;
 assert(cviii_stage1_atlas_load_0724(a,rom,393232)==-1);
 assert(cviii_stage1_atlas_get_0724(a,key,3,3,&tile,&pal)&&tile==15&&pal==3);
 free(p);free(a);free(rom);
 puts("PASS JP0724 previsited Stage1 atlas and native-center preservation");
 return 0;
}
