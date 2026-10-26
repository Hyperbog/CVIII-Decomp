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
 l.edit=0;cviii_light_present(&l,frame,256,240,9,500,sx,sy,0);
 assert(frame[0]==0xff808080u);assert(frame[100*256+32]!=0xff808080u);
 /* Scroll 20 pixels right; light is native X12, not native X32. */
 for(int y=0;y<240;++y)sx[y]=8;
 unsigned int f2[256*240];for(unsigned i=0;i<256*240;++i)f2[i]=0xff808080u;
 cviii_light_present(&l,f2,256,240,9,520,sx,sy,0);
 assert(f2[100*256+12]==frame[100*256+32]);
 assert(f2[100*256+32]!=frame[100*256+32]);
 unsigned int f3[256*240];for(unsigned i=0;i<256*240;++i)f3[i]=0xff808080u;
 cviii_light_present(&l,f3,256,240,10,520,sx,sy,0);
 assert(f3[100*256+12]==0xff646464u);
 FILE *file=tmpfile();assert(file);cviii_light_save(&l,file);rewind(file);
 char buf[256];int found=0;while(fgets(buf,sizeof buf,file))if(strstr(buf,"Light00 = 1,"))found=1;
 assert(found);fclose(file);
 CviiiLighting restored;cviii_light_init(&restored);
 assert(cviii_light_load(&restored,"Light00","1,9,532,100,60,85,255,167,74"));
 assert(restored.light[0].x==532 && restored.light[0].room==9);
 /* The user can return to the same room after travelling out of range. */
 for(int y=0;y<240;++y)sx[y]=288; /* world camera 800 */
 unsigned int off[256*240];
 for(unsigned i=0;i<256*240;++i)off[i]=0xff808080u;
 cviii_light_present(&l,off,256,240,9,800,sx,sy,0);
 assert(off[100*256+32]==0xff646464u);
 for(int y=0;y<240;++y)sx[y]=500;
 unsigned int back[256*240];
 for(unsigned i=0;i<256*240;++i)back[i]=0xff808080u;
 cviii_light_present(&l,back,256,240,9,500,sx,sy,0);
 assert(back[100*256+32]==frame[100*256+32]);
 /* Flicker must remain subdued; no instantaneous white-light flashing. */
 unsigned int flicker[256*240];
 for(unsigned i=0;i<256*240;++i)flicker[i]=0xff808080u;
 cviii_light_present(&l,flicker,256,240,9,500,sx,sy,60);
 const int red0=(int)((back[100*256+32]>>16)&255u);
 const int red1=(int)((flicker[100*256+32]>>16)&255u);
 assert(red1-red0<6 && red0-red1<6);
 /* A bright tile must keep a real highlight gradient, not clip white. */
 unsigned int bright[256*240];
 for(unsigned i=0;i<256*240;++i)bright[i]=0xffc8c8c8u;
 cviii_light_present(&l,bright,256,240,9,500,sx,sy,0);
 const int highlight=(int)((bright[100*256+32]>>16)&255u);
 assert(highlight>200 && highlight<255);
 assert((bright[90*256+32]&0xff000000u)==0xff000000u);
 /* Ambience is bounded, and corrupt profile entries fail closed. */
 assert(cviii_light_event(&l,1,-1,-1,9,500,sx,sy)); /* reopen editor */
 assert(cviii_light_event(&l,11,-1,-1,9,500,sx,sy));
 assert(l.ambient==81);
 assert(!cviii_light_load(&restored,"Light00","1,9,532,100,0,85,255,167,74"));
 assert(restored.light[0].radius==60);
 assert(!cviii_light_load(&restored,"Light00","1,9,532,100,60,85,255,167,74junk"));
 /* Named groups and clipboard retain original properties across rooms. */
 assert(cviii_light_rename(&l,0,"Torch - West stair"));
 assert(cviii_light_group(&l,0,"Stage 1 torches"));
 assert(cviii_light_copy(&l,0));
 int copy=cviii_light_paste(&l,20,700,140);
 assert(copy==1 && l.light[copy].room==20 && l.light[copy].x==700);
 assert(!strcmp(l.light[copy].name,"Torch - West stair"));
 assert(!strcmp(l.light[copy].group,"Stage 1 torches"));
 int duplicate=cviii_light_duplicate(&l,0);
 assert(duplicate==2 && l.light[duplicate].x==544 && l.light[duplicate].y==108);
 l.light[duplicate].room=30; /* isolate cone footprint from cloned radial light */
 assert(cviii_light_shape(&l,0,CVIII_SHAPE_CONE));
 l.light[0].angle=0;l.light[0].spread=30;l.light[0].width=32;
 assert(!cviii_light_shape(&l,0,99));
 /* Cone emits rightward but not behind its emitter. */
 unsigned int cone[256*240];
 for(unsigned i=0;i<256*240;++i)cone[i]=0xff808080u;
 l.edit=0;
 cviii_light_present(&l,cone,256,240,9,500,sx,sy,0);
 assert(cone[100*256+44]!=0xff646464u);
 assert(cone[100*256+20]==0xff646464u);
 assert(cviii_light_shape(&l,0,CVIII_SHAPE_SHAFT));
 unsigned int shaft[256*240];
 for(unsigned i=0;i<256*240;++i)shaft[i]=0xff808080u;
 cviii_light_present(&l,shaft,256,240,9,500,sx,sy,0);
 assert(shaft[100*256+42]!=0xff646464u);
 assert(shaft[125*256+42]==0xff646464u);
 /* Override global ambience only for this room. */
 assert(cviii_light_scene_set(&l,9,43,220,173,90));
 int ambient_percent=-1,ambient_color[3]={0};
 cviii_light_scene_get(&l,9,&ambient_percent,ambient_color);
 assert(ambient_percent==43 && ambient_color[2]==90);
 cviii_light_scene_get(&l,10,&ambient_percent,ambient_color);
 assert(ambient_percent==81 && ambient_color[0]==255);
 assert(!cviii_light_scene_set(&l,9,140,220,173,90));
 FILE *profile=tmpfile();assert(profile);
 cviii_light_save(&l,profile);rewind(profile);
 CviiiLighting loaded;cviii_light_init(&loaded);
 int keys=0;
 while(fgets(buf,sizeof buf,profile)){
     char *eq=strchr(buf,'=');
     if(!eq)continue;
     char *k=buf,*v=eq+1;
     while(eq>k && eq[-1]==' ')--eq;
     *eq=0;
     while(*v==' ')++v;
     size_t len=strlen(v);
     while(len && (v[len-1]=='\n' || v[len-1]=='\r'))v[--len]=0;
     keys+=cviii_light_load(&loaded,k,v)!=0;
 }
 fclose(profile);
 assert(keys>=10);
 assert(loaded.light[0].used && loaded.light[0].shape==CVIII_SHAPE_SHAFT);
 assert(!strcmp(loaded.light[0].name,"Torch - West stair"));
 assert(!strcmp(loaded.light[0].group,"Stage 1 torches"));
 cviii_light_scene_get(&loaded,9,&ambient_percent,ambient_color);
 assert(ambient_percent==43 && ambient_color[1]==173);
 assert(!cviii_light_load(&loaded,"LightName00","FF"));
 assert(!cviii_light_load(&loaded,"LightStyle00","7,0,0,0,0,0"));
 return 0;
}
