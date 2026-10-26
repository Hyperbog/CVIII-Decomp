/* Standalone strict-C11 synthetic test; does not execute the original ROM. */
#include "cviii_lighting.h"
#include <assert.h>
#include <string.h>
int main(void){
 CviiiLighting l;cviii_light_init(&l);assert(l.ambient==78);
 int sx[240],sy[240];for(int y=0;y<240;++y){sx[y]=500;sy[y]=y;}
 assert(cviii_light_event(&l,1,0,0,9,500,sx,sy));
 assert(cviii_light_event(&l,2,32,100,9,500,sx,sy));
 assert(l.light[0].used && l.light[0].x==532 && l.light[0].y==100);
 assert(cviii_light_event(&l,4,0,0,9,500,sx,sy));
 assert(cviii_light_event(&l,6,0,0,9,500,sx,sy));
 assert(l.light[0].radius==60);
 unsigned int frame[256*240];for(unsigned i=0;i<256*240;++i)frame[i]=0xff808080u;
 l.edit=0;cviii_light_present(&l,frame,256,240,9,500,sx,sy);
 assert(frame[0]==0xff808080u);assert(frame[100*256+32]!=0xff808080u);
 /* Scroll 20 pixels right; light is native X12, not native X32. */
 for(int y=0;y<240;++y)sx[y]=8;
 unsigned int f2[256*240];for(unsigned i=0;i<256*240;++i)f2[i]=0xff808080u;
 cviii_light_present(&l,f2,256,240,9,520,sx,sy);
 assert(f2[100*256+12]==frame[100*256+32]);
 assert(f2[100*256+32]!=frame[100*256+32]);
 unsigned int f3[256*240];for(unsigned i=0;i<256*240;++i)f3[i]=0xff808080u;
 cviii_light_present(&l,f3,256,240,10,520,sx,sy);
 assert(f3[100*256+12]==0xff646464u);
 FILE *file=tmpfile();assert(file);cviii_light_save(&l,file);rewind(file);
 char buf[256];int found=0;while(fgets(buf,sizeof buf,file))if(strstr(buf,"Light00 = 1,"))found=1;
 assert(found);fclose(file);
 CviiiLighting restored;cviii_light_init(&restored);
 assert(cviii_light_load(&restored,"Light00","1,9,532,100,60,85,255,167,74"));
 assert(restored.light[0].x==532 && restored.light[0].room==9);
 return 0;
}
