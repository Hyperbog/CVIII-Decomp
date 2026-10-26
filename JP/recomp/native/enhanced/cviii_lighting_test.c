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
 assert(cone[100*256+20]==0xff686868u);
 assert(cviii_light_shape(&l,0,CVIII_SHAPE_SHAFT));
 unsigned int shaft[256*240];
 for(unsigned i=0;i<256*240;++i)shaft[i]=0xff808080u;
 cviii_light_present(&l,shaft,256,240,9,500,sx,sy,0);
 assert(shaft[100*256+42]!=0xff646464u);
 assert(shaft[125*256+42]==0xff686868u);
 /* Override global ambience only for this room. */
 assert(cviii_light_scene_set(&l,9,43,220,173,90));
 int ambient_percent=-1,ambient_color[3]={0};
 cviii_light_scene_get(&l,9,&ambient_percent,ambient_color);
 assert(ambient_percent==43 && ambient_color[2]==90);
 cviii_light_scene_get(&l,10,&ambient_percent,ambient_color);
 assert(ambient_percent==81 && ambient_color[0]==255);
 assert(!cviii_light_scene_set(&l,9,140,220,173,90));
 assert(CVIII_LIGHT_MAX>=128);
 l.light[100]=(CviiiLight){.room=9,.x=950,.y=170,.radius=30,
                            .energy=60,.red=230,.green=230,.blue=180,.used=1};
 assert(cviii_light_rename(&l,100,"Far room beacon"));
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
 assert(loaded.light[100].used && loaded.light[100].x==950);
 assert(!strcmp(loaded.light[100].name,"Far room beacon"));
 cviii_light_scene_get(&loaded,9,&ambient_percent,ambient_color);
 assert(ambient_percent==43 && ambient_color[1]==173);
 assert(!cviii_light_load(&loaded,"LightName00","FF"));
 assert(!cviii_light_load(&loaded,"LightStyle00","7,0,0,0,0,0"));
 /* Global library archetypes are multi-emitter, deterministic, world-relative. */
 assert(cviii_light_builtin_count()>=7);
 assert(!strcmp(cviii_light_builtin_name(0),"Candle"));
 CviiiLighting kits;cviii_light_init(&kits);kits.edit=1;
 int start=cviii_light_apply_builtin(&kits,1,42,400,112);
 assert(start==0 && kits.light[0].used && kits.light[1].used);
 assert(kits.light[0].room==42 && kits.light[1].y==104);
 assert(!strcmp(kits.light[0].group,"Torch"));
 assert(kits.light[0].flicker==2);
 /* Group capture includes both emitters, maintaining relative positions. */
 assert(cviii_light_kit_capture(&kits,0,0,"Custom Torch Pair"));
 assert(kits.kits[0].count==2 && kits.kits[0].used);
 assert(kits.kits[0].part[0].x==0 && kits.kits[0].part[1].y==-8);
 int pasted=cviii_light_kit_apply(&kits,0,100,700,220);
 assert(pasted==2 && kits.light[3].room==100);
 assert(kits.light[2].x==700 && kits.light[3].y==212);
 assert(!strcmp(kits.light[3].name,"Torch Spill"));
 assert(cviii_light_apply_builtin(&kits,3,42,500,110)==4);
 assert(kits.light[4].shape==CVIII_SHAPE_SHAFT);
 assert(kits.light[5].shape==CVIII_SHAPE_RADIAL);
 /* Fail atomically if a multi-part rig overlaps a world boundary. */
 int old=0;for(int k=0;k<CVIII_LIGHT_MAX;++k)old+=kits.light[k].used;
 assert(cviii_light_apply_builtin(&kits,1,42,0,2)<0);
 int now=0;for(int k=0;k<CVIII_LIGHT_MAX;++k)now+=kits.light[k].used;
 assert(now==old);
 /* Named global custom rigs survive an ordinary config.ini save/load. */
 FILE *kitconfig=tmpfile();assert(kitconfig);
 cviii_light_save(&kits,kitconfig);rewind(kitconfig);
 CviiiLighting reloaded;cviii_light_init(&reloaded);
 while(fgets(buf,sizeof buf,kitconfig)){
   char *eq=strchr(buf,'=');
   if(!eq)continue;
   char *k=buf,*v=eq+1;
   while(eq>k && eq[-1]==' ')--eq;
   *eq=0;while(*v==' ')++v;
   size_t n=strlen(v);
   while(n && (v[n-1]=='\r' || v[n-1]=='\n'))v[--n]=0;
   assert(cviii_light_load(&reloaded,k,v));
 }
 fclose(kitconfig);
 assert(reloaded.kits[0].used && reloaded.kits[0].count==2);
 assert(!strcmp(reloaded.kits[0].name,"Custom Torch Pair"));
 assert(!strcmp(reloaded.kits[0].part[1].name,"Torch Spill"));
 int replay=cviii_light_kit_apply(&reloaded,0,222,800,145);
 assert(replay>=0 && reloaded.light[replay+1].y==137);
 assert(!cviii_light_kit_load(&reloaded,"LightKit00","2,XYZ"));
 /* Sky fill is additive, separate from the legacy colored ambient filter.
  * Gradient is brighter at the upper scene edge than the lower edge. */
 CviiiLighting sky;cviii_light_init(&sky);sky.enabled=1;
 assert(cviii_light_sky_set(&sky,64,45,147,190,255,-1));
 int skypct=0,skycolor[3]={0},facing=2;
 cviii_light_sky_get(&sky,64,&skypct,skycolor,&facing);
 assert(skypct==45 && skycolor[0]==147 && facing==-1);
 unsigned int skyframe[256*240];
 for(unsigned k=0;k<256*240;++k)skyframe[k]=0xff808080u;
 for(int y=0;y<240;++y){sx[y]=0;sy[y]=y;}
 cviii_light_present(&sky,skyframe,256,240,64,0,sx,sy,0);
 assert(skyframe[60*256+125]!=0xff646464u);
 assert((skyframe[60*256+125]&255u)>(skyframe[225*256+125]&255u));
 assert(skyframe[20*256+125]==0xff808080u);
 unsigned int other[256*240];
 for(unsigned k=0;k<256*240;++k)other[k]=0xff808080u;
 cviii_light_present(&sky,other,256,240,65,0,sx,sy,0);
 assert(other[60*256+125]==0xff646464u);
 assert(cviii_light_scene_set(&sky,64,68,255,255,255));
 cviii_light_sky_get(&sky,64,&skypct,skycolor,&facing);
 assert(skypct==45 && facing==-1); /* ambient edit never clears sky */
 FILE *skyconfig=tmpfile();assert(skyconfig);
 cviii_light_save(&sky,skyconfig);rewind(skyconfig);
 CviiiLighting skyrt;cviii_light_init(&skyrt);
 while(fgets(buf,sizeof buf,skyconfig)){
   char *eq=strchr(buf,'=');
   if(!eq)continue;
   char *k=buf,*v=eq+1;
   while(eq>k && eq[-1]==' ')--eq;
   *eq=0;while(*v==' ')++v;
   size_t n=strlen(v);
   while(n && (v[n-1]=='\r' || v[n-1]=='\n'))v[--n]=0;
   assert(cviii_light_load(&skyrt,k,v));
 }
 fclose(skyconfig);
 cviii_light_sky_get(&skyrt,64,&skypct,skycolor,&facing);
 assert(skypct==45 && skycolor[2]==255 && facing==-1);

 /* Light style links keep world placement local, while all group members
    read the same GLOBAL brightness/color settings in every room. */
 CviiiLighting fx;cviii_light_init(&fx);fx.enabled=1;
 int newlight=cviii_light_apply_builtin(&fx,1,7,130,108);
 assert(newlight==0);
 assert(cviii_light_style_capture(&fx,0,0,"Global Torch Style"));
 assert(cviii_light_style_link_group(&fx,0,0));
 assert(fx.light[0].style_link==1 && fx.light[1].style_link==1);
 CviiiLight effective;
 cviii_light_effective(&fx,&fx.light[1],&effective);
 assert(effective.energy==120 && effective.x==136);
 fx.styles[0].light.energy=155;
 cviii_light_effective(&fx,&fx.light[1],&effective);
 assert(effective.energy==155 && effective.x==136);
 assert(!strcmp(effective.name,"Torch Spill"));
 assert(cviii_light_style_link(&fx,1,-1));
 cviii_light_effective(&fx,&fx.light[1],&effective);
 assert(effective.energy==38);
 assert(cviii_light_style_link(&fx,1,0));
 assert(!cviii_light_style_link(&fx,1,15)); /* nonexistent global slot */
 /* Authorable rectangle casts shadow only through the intersected segment,
    with deterministic 5-sample soft penumbra and no cross-room bleed. */
 int mask=cviii_light_mask_add(&fx,7,170,100,8,18);
 assert(mask==0);
 float shadow=cviii_light_shadow(&fx,7,130,108,210,108);
 assert(shadow<0.5f && shadow>=0.f);
 assert(cviii_light_shadow(&fx,8,130,108,210,108)==1.f);
 assert(cviii_light_shadow(&fx,7,130,108,145,150)==1.f);
 assert(!cviii_light_mask_remove(&fx,-1));
 /* Scene exposure / cool white balance / saturation are independent of
    ambient color multipliers and do not touch top HUD rows. */
 assert(cviii_light_grade_set(&fx,7,55,30,125));
 int ev=0,temp=0,saturation=0;
 cviii_light_grade_get(&fx,7,&ev,&temp,&saturation);
 assert(ev==55 && temp==30 && saturation==125);
 cviii_light_grade_get(&fx,8,&ev,&temp,&saturation);
 assert(ev==0 && temp==0 && saturation==100);
 assert(!cviii_light_grade_set(&fx,7,300,0,100));
 unsigned int gradeframe[256*240];
 for(unsigned k=0;k<256*240;++k)gradeframe[k]=0xff808080u;
 for(int y=0;y<240;++y){sx[y]=0;sy[y]=y;}
 cviii_light_present(&fx,gradeframe,256,240,7,0,sx,sy,0);
 assert(gradeframe[8*256+145]==0xff808080u);
 assert(gradeframe[120*256+5]!=0xff646464u);
 /* Explicit alias maps volatile source keys to a stable saved scene ID.
    Other keys retain their original meaning; no implicit room merging. */
 assert(cviii_light_scene_resolve(&fx,0x12345678u)==0x12345678u);
 assert(cviii_light_scene_alias(&fx,0x12345678u,7));
 assert(cviii_light_scene_resolve(&fx,0x12345678u)==7);
 assert(cviii_light_scene_resolve(&fx,0x12345679u)==0x12345679u);
 assert(cviii_light_scene_alias(&fx,0x12345678u,15));
 assert(cviii_light_scene_resolve(&fx,0x12345678u)==15);
 assert(cviii_light_scene_alias(&fx,0x12345678u,7));
 /* Host-only undo/redo restores scene authoring but leaves edit state live. */
 cviii_light_history_reset();
 fx.edit=1;
 int oldenergy=fx.styles[0].light.energy;
 cviii_light_history_push(&fx);
 fx.styles[0].light.energy=76;
 assert(cviii_light_history_can_undo());
 assert(cviii_light_history_undo(&fx));
 assert(fx.styles[0].light.energy==oldenergy && fx.edit==1);
 assert(cviii_light_history_can_redo());
 assert(cviii_light_history_redo(&fx));
 assert(fx.styles[0].light.energy==76);
 cviii_light_history_reset();
 /* Version-compatible persisted styles, links, mask, grade and alias. */
 FILE *more=tmpfile();assert(more);
 cviii_light_save(&fx,more);rewind(more);
 CviiiLighting loadedfx;cviii_light_init(&loadedfx);
 while(fgets(buf,sizeof buf,more)){
     char *eq=strchr(buf,'=');if(!eq)continue;
     char *key=buf,*val=eq+1;
     while(eq>key && eq[-1]==' ')--eq;
     *eq=0;while(*val==' ')++val;
     size_t n=strlen(val);
     while(n && (val[n-1]=='\n' || val[n-1]=='\r'))val[--n]=0;
     assert(cviii_light_load(&loadedfx,key,val));
 }
 fclose(more);
 assert(loadedfx.styles[0].used && loadedfx.styles[0].light.energy==76);
 assert(loadedfx.light[0].style_link==1);
 assert(loadedfx.masks[0].used && loadedfx.masks[0].w==8);
 assert(cviii_light_scene_resolve(&loadedfx,0x12345678u)==7);
 cviii_light_grade_get(&loadedfx,7,&ev,&temp,&saturation);
 assert(ev==55 && temp==30 && saturation==125);
 return 0;
}
