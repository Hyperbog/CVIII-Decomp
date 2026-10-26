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
 /* New candle/torch modulation: deterministic, bounded, adjustable and
    shared through global styles without moving placed emitters. */
 CviiiLighting animated;cviii_light_init(&animated);animated.enabled=1;
 animated.light[0]=(CviiiLight){.used=1,.room=88,.x=88,.y=110,
  .radius=74,.energy=128,.red=255,.green=158,.blue=65,
  .flicker=3,.anim_speed=140,.anim_strength=100};
 int sx2[240],sy2[240];
 for(int y=0;y<240;++y){sx2[y]=0;sy2[y]=y;}
 unsigned int pulseframe[256*240];
 for(unsigned j=0;j<256*240;++j)pulseframe[j]=0xff808080u;
 cviii_light_present(&animated,pulseframe,256,240,88,0,sx2,sy2,0);
 unsigned long first=pulseframe[110*256+88];
 for(unsigned j=0;j<256*240;++j)pulseframe[j]=0xff808080u;
 cviii_light_present(&animated,pulseframe,256,240,88,0,sx2,sy2,53);
 unsigned long second=pulseframe[110*256+88];
 assert(first!=second);
 int delta=(int)((second>>16)&255)-(int)((first>>16)&255);
 assert(delta>=-16 && delta<=16);
 animated.light[0].flicker=1;
 for(unsigned j=0;j<256*240;++j)pulseframe[j]=0xff808080u;
 cviii_light_present(&animated,pulseframe,256,240,88,0,sx2,sy2,0);
 first=pulseframe[110*256+88];
 for(unsigned j=0;j<256*240;++j)pulseframe[j]=0xff808080u;
 cviii_light_present(&animated,pulseframe,256,240,88,0,sx2,sy2,179);
 assert(first==pulseframe[110*256+88]); /* Steady is truly steady. */
 animated.light[0].flicker=4; /* Ember dip; safe range, no random jumps. */
 assert(cviii_light_style_capture(&animated,0,0,"Global Animated Flame"));
 assert(cviii_light_style_link(&animated,0,0));
 cviii_light_effective(&animated,&animated.light[0],&effective);
 assert(effective.flicker==4 && effective.anim_speed==140 &&
        effective.anim_strength==100);
 FILE *animated_profile=tmpfile();assert(animated_profile);
 cviii_light_save(&animated,animated_profile);rewind(animated_profile);
 CviiiLighting recovered;cviii_light_init(&recovered);
 while(fgets(buf,sizeof buf,animated_profile)){
   char *eq=strchr(buf,'=');if(!eq)continue;
   char *key=buf,*val=eq+1;
   while(eq>key && eq[-1]==' ')--eq;
   *eq=0;while(*val==' ')++val;
   size_t size=strlen(val);
   while(size && (val[size-1]=='\n' || val[size-1]=='\r'))val[--size]=0;
   assert(cviii_light_load(&recovered,key,val));
 }
 fclose(animated_profile);
 assert(recovered.light[0].flicker==4);
 assert(recovered.light[0].anim_speed==140);
 assert(recovered.light[0].anim_strength==100);
 assert(recovered.styles[0].light.anim_strength==100);
 assert(!cviii_light_load(&recovered,"LightAnim00","600,20"));
 assert(!cviii_light_load(&recovered,"GlobalAnim00","150,-2"));
 /* Penumbrae must vary smoothly in both axes, not clip at mask seam. */
 CviiiLighting soft;cviii_light_init(&soft);
 assert(cviii_light_mask_add(&soft,88,130,96,10,25)>=0);
 assert(soft.masks[0].softness>=8);
 float last=-1.f,highest_jump=0.f;
 int partial=0;
 for(int y=80;y<=165;++y){
   float visibility=cviii_light_shadow(&soft,88,88,110,180,y);
   assert(visibility>=0.f && visibility<=1.f);
   if(visibility>0.01f && visibility<0.99f)++partial;
   if(last>=0.f){
     float jump=visibility-last;
     if(jump<0.f)jump=-jump;
     if(jump>highest_jump)highest_jump=jump;
   }
   last=visibility;
 }
 assert(partial>=3 && highest_jump<0.35f);
 /* Light-kit playback preserves individual animation values after reload. */
 CviiiLighting motionkit;cviii_light_init(&motionkit);
 int torch=cviii_light_apply_builtin(&motionkit,1,88,100,130);
 assert(torch>=0);
 motionkit.light[torch].anim_speed=175;
 motionkit.light[torch].anim_strength=65;
 assert(cviii_light_kit_capture(&motionkit,0,torch,"Animated Torch"));
 FILE *kitmotion=tmpfile();assert(kitmotion);
 cviii_light_save(&motionkit,kitmotion);rewind(kitmotion);
 CviiiLighting restoredkit;cviii_light_init(&restoredkit);
 while(fgets(buf,sizeof buf,kitmotion)){
   char *eq=strchr(buf,'=');if(!eq)continue;
   char *key=buf,*val=eq+1;
   while(eq>key && eq[-1]==' ')--eq;
   *eq=0;while(*val==' ')++val;
   size_t size=strlen(val);
   while(size && (val[size-1]=='\n' || val[size-1]=='\r'))val[--size]=0;
   assert(cviii_light_load(&restoredkit,key,val));
 }
 fclose(kitmotion);
 assert(restoredkit.kits[0].used);
 assert(restoredkit.kits[0].part[0].anim_speed==175);
 assert(restoredkit.kits[0].part[0].anim_strength==65);
 /* Overlapping colored emitters mix smoothly without white clipping.
    Their combined channels stay distinguishable under highlight shoulder. */
 CviiiLighting blend;cviii_light_init(&blend);blend.enabled=1;
 blend.light[0]=(CviiiLight){.used=1,.room=77,.x=100,.y=116,
   .radius=69,.energy=95,.red=255,.green=50,.blue=25,.flicker=1};
 blend.light[1]=(CviiiLight){.used=1,.room=77,.x=100,.y=116,
   .radius=69,.energy=95,.red=36,.green=70,.blue=255,.flicker=1};
 for(unsigned j=0;j<256*240;++j)pulseframe[j]=0xff999999u;
 cviii_light_present(&blend,pulseframe,256,240,77,0,sx2,sy2,1);
 unsigned int mixed=pulseframe[116*256+100];
 assert((mixed&0xff000000u)==0xff000000u);
 assert(((mixed>>16)&255u)>((mixed>>8)&255u));
 assert((mixed&255u)>((mixed>>8)&255u));
 assert(((mixed>>16)&255u)<255u && (mixed&255u)<255u);
 blend.light[1].muted=1;
 for(unsigned j=0;j<256*240;++j)pulseframe[j]=0xff999999u;
 cviii_light_present(&blend,pulseframe,256,240,77,0,sx2,sy2,1);
 assert((mixed&255u)>(pulseframe[116*256+100]&255u));
 /* Room-scoped pixel FX: exact deterministic pixels, gameplay HUD,
    offscreen travel and full config return. All tests are ROM-free. */
 static CviiiLighting particles,fxrestored,typetest;
 cviii_light_init(&particles);
 assert(!particles.particles_enabled);
 assert(cviii_particle_add(&particles,9,CVIII_FX_DUST,540,96)==0);
 assert(particles.particles_enabled);
 assert(!strcmp(cviii_particle_kind_name(CVIII_FX_DUST),"Floating Dust"));
 assert(!strcmp(cviii_particle_kind_name(CVIII_FX_FOG),"Pixel Fog"));
 assert(cviii_particle_name(&particles,0,"Castle Hall Dust"));
 assert(cviii_particle_property(&particles,0,6,64));
 assert(cviii_particle_property(&particles,0,7,125));
 assert(cviii_particle_property(&particles,0,8,-21));
 assert(!cviii_particle_property(&particles,0,6,97));
 assert(!cviii_particle_property(&particles,0,5,500));
 assert(!cviii_particle_name(&particles,0,""));
 assert(cviii_particle_add(&particles,9,99,540,96)<0);
 assert(cviii_particle_add(&particles,9,CVIII_FX_DUST,65535,96)<0);
 static uint32_t fx0[256*240],fx1[256*240],fx2[256*240],fx3[256*240];
 for(int y=0;y<240;++y){sx[y]=500;sy[y]=y;}
 for(unsigned i=0;i<256u*240u;++i)fx0[i]=fx1[i]=fx2[i]=fx3[i]=0xff808080u;
 cviii_particle_present(&particles,fx0,9,500,sx,sy,100);
 cviii_particle_present(&particles,fx1,9,500,sx,sy,100);
 assert(memcmp(fx0,fx1,sizeof fx0)==0);
 int altered=0;
 for(int y=96;y<192;++y)
  for(int x=40;x<137;++x)
   altered+=fx0[y*256+x]!=0xff808080u;
 assert(altered>=12 && altered<=64*16);
 /* No particle may overwrite the NES HUD, even if emitter region
    extends behind rows <48. */
 for(int y=0;y<48;++y)
  for(int x=0;x<256;++x)assert(fx0[y*256+x]==0xff808080u);
 cviii_particle_present(&particles,fx2,10,500,sx,sy,100);
 assert(fx2[120*256+80]==0xff808080u);
 assert(memcmp(fx2,fx3,sizeof fx2)==0); /* another room sees no FX */
 for(int y=0;y<240;++y)sx[y]=8;
 cviii_particle_present(&particles,fx3,9,520,sx,sy,100);
 for(int y=96;y<192;++y)
  for(int x=20;x<112;++x)
   assert(fx3[y*256+x]==fx0[y*256+(x+20)]);
 for(unsigned i=0;i<256u*240u;++i)fx3[i]=0xff808080u;
 for(int y=0;y<240;++y)sx[y]=488; /* camera=1000, cloud offscreen */
 cviii_particle_present(&particles,fx3,9,1000,sx,sy,100);
 for(unsigned i=0;i<256u*240u;++i)assert(fx3[i]==0xff808080u);
 for(int y=0;y<240;++y)sx[y]=500;
 for(unsigned i=0;i<256u*240u;++i)fx3[i]=0xff808080u;
 cviii_particle_present(&particles,fx3,9,500,sx,sy,100);
 assert(memcmp(fx0,fx3,sizeof fx0)==0);
 /* Time motion changes dust while repeated frames stay deterministic. */
 for(unsigned i=0;i<256u*240u;++i)fx3[i]=0xff808080u;
 cviii_particle_present(&particles,fx3,9,500,sx,sy,750);
 assert(memcmp(fx0,fx3,sizeof fx0)!=0);
 FILE *fxprofile=tmpfile();assert(fxprofile);
 cviii_particle_save(&particles,fxprofile);rewind(fxprofile);
 cviii_light_init(&fxrestored);
 while(fgets(buf,sizeof buf,fxprofile)){
   char *eq=strchr(buf,'=');if(!eq)continue;
   char *k=buf,*v=eq+1;
   while(eq>k && eq[-1]==' ')--eq;
   *eq=0;while(*v==' ')++v;
   size_t n=strlen(v);
   while(n && (v[n-1]=='\r' || v[n-1]=='\n'))v[--n]=0;
   assert(cviii_particle_load(&fxrestored,k,v));
 }
 fclose(fxprofile);
 assert(fxrestored.particles_enabled);
 assert(fxrestored.particles[0].room==9);
 assert(fxrestored.particles[0].wind==-21);
 assert(!strcmp(fxrestored.particles[0].name,"Castle Hall Dust"));
 for(unsigned i=0;i<256u*240u;++i)fx3[i]=0xff808080u;
 cviii_particle_present(&fxrestored,fx3,9,500,sx,sy,100);
 assert(memcmp(fx0,fx3,sizeof fx0)==0);
 assert(!cviii_particle_load(&fxrestored,"Particle00","1,9,0,-1,40,40,16,16,80,0,80,2,5,6,7"));
 assert(!cviii_particle_load(&fxrestored,"ParticleName00","ZZ"));
 assert(!cviii_particle_load(&fxrestored,"Particles","false"));
 fxrestored.particles_enabled=0;
 for(unsigned i=0;i<256u*240u;++i)fx3[i]=0xff808080u;
 cviii_particle_present(&fxrestored,fx3,9,500,sx,sy,100);
 assert(memcmp(fx2,fx3,sizeof fx2)==0);
 /* Render every preset; all use real, quantized NES-grid pixels. */
 cviii_light_init(&typetest);
 for(int kind=0;kind<CVIII_FX_COUNT;++kind){
   int index=cviii_particle_add(&typetest,13,kind,50,80);
   assert(index==kind);
   assert(typetest.particles[kind].density>=1);
 }
 for(unsigned i=0;i<256u*240u;++i)fx3[i]=0xff808080u;
 cviii_particle_present(&typetest,fx3,13,0,sx2,sy2,240);
 altered=0;
 for(int y=48;y<240;++y)
  for(int x=0;x<256;++x)altered+=fx3[y*256+x]!=0xff808080u;
 assert(altered>=30);
 assert(fx3[15*256+55]==0xff808080u);
 cviii_light_history_reset();
 cviii_light_history_push(&typetest);
 assert(cviii_particle_property(&typetest,0,0,0));
 assert(!typetest.particles[0].used);
 assert(cviii_light_history_undo(&typetest));
 assert(typetest.particles[0].used);
 cviii_light_history_reset();
 return 0;
}
