/* Host-only deterministic weather environment library, shared across rooms.
 * Weather is a linked profile, not a machine save-state, and the weather
 * timeline is a pure function of the room/seed/host frame. No RNG writes.
 */
#include "cviii_lighting.h"
#include <stdio.h>
#include <string.h>
static unsigned mix(unsigned x){
 x^=x>>16;x*=0x7feb352du;x^=x>>15;x*=0x846ca68bu;x^=x>>16;return x;
}
static int between(int n,int low,int high){return n>=low && n<=high;}
static int name_ok(const char *v){
 if(!v)return 0;
 size_t n=strlen(v);
 if(!n || n>=CVIII_LIGHT_NAME_CAP)return 0;
 for(size_t i=0;i<n;++i)if((unsigned char)v[i]<32 || (unsigned char)v[i]>126)return 0;
 return 1;
}
static int hexval(int x){
 if(x>='0' && x<='9')return x-'0';
 if(x>='A' && x<='F')return x-'A'+10;
 if(x>='a' && x<='f')return x-'a'+10;
 return -1;
}
static const struct {
 const char *name;int kind,count,speed,wind,opacity,size,chance,period;
 int red,green,blue;
} builtin[]={
 {"Rain Showers",CVIII_FX_RAIN,54,100,12,49,1,65,12,119,162,227},
 {"Thunderstorm",CVIII_FX_RAIN,96,155,-36,68,2,85,8,136,168,221},
 {"Winter Snow",CVIII_FX_SNOW,52,85,15,57,1,72,22,228,241,255},
 {"Drifting Mist",CVIII_FX_FOG,72,50,25,27,2,78,25,177,198,215},
 {"Volcanic Ash",CVIII_FX_ASH,44,105,-25,62,1,60,15,188,170,157},
 {"Night Fireflies",CVIII_FX_FIREFLIES,17,62,14,88,1,58,18,210,246,123}
};
static int valid(const CviiiWeatherProfile *p){
 return p && p->kind>=0 && p->kind<CVIII_FX_COUNT &&
 between(p->density,1,96)&&between(p->speed,0,300)&&
 between(p->wind,-100,100)&&between(p->opacity,0,100)&&
 between(p->size,1,4)&&between(p->chance,0,100)&&
 between(p->period,1,120)&&between(p->seed,0,65535)&&
 between(p->layer,0,1);
}
int cviii_weather_template(CviiiLighting *s,int profile,int type){
 if(!s || profile<0 || profile>=CVIII_WEATHER_PROFILE_MAX ||
    type<0 || type>=(int)(sizeof builtin/sizeof builtin[0]))return 0;
 CviiiWeatherProfile *p=&s->weather[profile];
 const int base=profile*739+type*53+612;
 *p=(CviiiWeatherProfile){.used=1,.kind=builtin[type].kind,
   .density=builtin[type].count,.speed=builtin[type].speed,
   .wind=builtin[type].wind,.opacity=builtin[type].opacity,
   .size=builtin[type].size,.chance=builtin[type].chance,
   .period=builtin[type].period,.seed=base,
   .layer=(type==3?1:0),
   .red=(uint8_t)builtin[type].red,.green=(uint8_t)builtin[type].green,
   .blue=(uint8_t)builtin[type].blue};
 (void)snprintf(p->name,sizeof p->name,"%s",builtin[type].name);
 return 1;
}
int cviii_weather_name(CviiiLighting *s,int slot,const char *name){
 if(!s || slot<0 || slot>=CVIII_WEATHER_PROFILE_MAX ||
    !s->weather[slot].used || !name_ok(name))return 0;
 strcpy(s->weather[slot].name,name);return 1;
}
int cviii_weather_property(CviiiLighting *s,int slot,int property,int value){
 if(!s || slot<0 || slot>=CVIII_WEATHER_PROFILE_MAX ||
    !s->weather[slot].used)return 0;
 CviiiWeatherProfile p=s->weather[slot];
 switch(property){
  case 0:s->weather[slot].used=0;
    for(int i=0;i<CVIII_WEATHER_SCENE_MAX;++i)
      if(s->weather_scenes[i].used && s->weather_scenes[i].profile==slot)
         s->weather_scenes[i].used=0;
    return 1;
  case 1:p.kind=value;break;
  case 2:p.density=value;break;
  case 3:p.speed=value;break;
  case 4:p.wind=value;break;
  case 5:p.opacity=value;break;
  case 6:p.size=value;break;
  case 7:p.chance=value;break;
  case 8:p.period=value;break;
  case 9:p.seed=value;break;
  case 10:p.layer=value;break;
  case 11:if(!between(value,0,255))return 0;p.red=(uint8_t)value;break;
  case 12:if(!between(value,0,255))return 0;p.green=(uint8_t)value;break;
  case 13:if(!between(value,0,255))return 0;p.blue=(uint8_t)value;break;
  default:return 0;
 }
 if(!valid(&p))return 0;
 s->weather[slot]=p;return 1;
}
int cviii_weather_scene_profile(const CviiiLighting *s,uint32_t room){
 if(!s)return -1;
 for(int i=0;i<CVIII_WEATHER_SCENE_MAX;++i)
  if(s->weather_scenes[i].used && s->weather_scenes[i].room==room &&
     s->weather_scenes[i].profile>=0 &&
     s->weather_scenes[i].profile<CVIII_WEATHER_PROFILE_MAX &&
     s->weather[s->weather_scenes[i].profile].used)
      return s->weather_scenes[i].profile;
 return -1;
}
int cviii_weather_link(CviiiLighting *s,uint32_t room,int profile){
 if(!s || profile<-1 || profile>=CVIII_WEATHER_PROFILE_MAX ||
    (profile>=0 && !s->weather[profile].used))return 0;
 for(int i=0;i<CVIII_WEATHER_SCENE_MAX;++i){
   CviiiWeatherScene *link=&s->weather_scenes[i];
   if(link->used && link->room==room){
     if(profile<0)link->used=0;
     else link->profile=profile;
     return 1;
   }
 }
 if(profile<0)return 1;
 for(int i=0;i<CVIII_WEATHER_SCENE_MAX;++i)
   if(!s->weather_scenes[i].used){
     s->weather_scenes[i]=(CviiiWeatherScene){.used=1,.room=room,.profile=profile};
     return 1;
   }
 return 0;
}
int cviii_weather_intensity(const CviiiWeatherProfile *p,uint32_t room,uint64_t frame){
 if(!valid(p) || !p->used || p->chance==0)return 0;
 unsigned segment=(unsigned)(frame/((uint64_t)p->period*60u));
 unsigned t=(unsigned)(frame%((uint64_t)p->period*60u));
 unsigned base=mix((unsigned)p->seed ^ mix(room));
 unsigned r0=mix(base^mix(segment));
 unsigned r1=mix(base^mix(segment+1));
 float a=(r0%100u)<(unsigned)p->chance?
    (.45f+(r0%56u)*.01f):0.f;
 float b=(r1%100u)<(unsigned)p->chance?
    (.45f+(r1%56u)*.01f):0.f;
 /* Bounded smooth transitions: no hard climate jump at epoch rollover. */
 float f=(float)t/(float)(p->period*60);
 f=f*f*(3.f-2.f*f);
 float value=a+(b-a)*f;
 int pct=(int)(value*100.f+.5f);
 return pct<0?0:pct>100?100:pct;
}
int cviii_weather_load(CviiiLighting *s,const char *key,const char *v){
 if(!s || !key || !v)return 0;
 unsigned slot;char extra;
 if(!strncmp(key,"WeatherName",11)){
   if(sscanf(key,"WeatherName%2u%c",&slot,&extra)!=1 ||
      slot>=CVIII_WEATHER_PROFILE_MAX)return 0;
   size_t n=strlen(v);char name[CVIII_LIGHT_NAME_CAP];
   if(!n || (n&1) || n/2>=sizeof name)return 0;
   for(size_t i=0;i<n;i+=2){
      int a=hexval(v[i]),b=hexval(v[i+1]);
      if(a<0 || b<0)return 0;
      name[i/2]=(char)((a<<4)|b);
   }
   name[n/2]=0;
   if(!name_ok(name))return 0;
   strcpy(s->weather[slot].name,name);
   return 1;
 }
 if(!strncmp(key,"WeatherRoom",11)){
   unsigned room=0;int profile=-1,n=0;
   if(sscanf(key,"WeatherRoom%2u%c",&slot,&extra)!=1 ||
      slot>=CVIII_WEATHER_SCENE_MAX ||
      sscanf(v,"%u,%d%n",&room,&profile,&n)!=2 || v[n] ||
      profile<0 || profile>=CVIII_WEATHER_PROFILE_MAX)return 0;
   s->weather_scenes[slot]=(CviiiWeatherScene){.used=1,.room=room,.profile=profile};
   return 1;
 }
 if(sscanf(key,"Weather%2u%c",&slot,&extra)!=1 ||
    slot>=CVIII_WEATHER_PROFILE_MAX)return 0;
 CviiiWeatherProfile p={0};unsigned r,g,b;int used,n=0;
 if(sscanf(v,"%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%u,%u,%u%n",
   &used,&p.kind,&p.density,&p.speed,&p.wind,&p.opacity,&p.size,
   &p.chance,&p.period,&p.seed,&p.layer,&r,&g,&b,&n)!=14 ||
   v[n] || used!=1 || r>255||g>255||b>255)return 0;
 p.used=1;p.red=(uint8_t)r;p.green=(uint8_t)g;p.blue=(uint8_t)b;
 if(!valid(&p))return 0;
 s->weather[slot]=p;return 1;
}
void cviii_weather_save(const CviiiLighting *s,FILE *file){
 if(!s || !file)return;
 for(int i=0;i<CVIII_WEATHER_PROFILE_MAX;++i){
  const CviiiWeatherProfile *p=&s->weather[i];
  if(!p->used)continue;
  fprintf(file,"Weather%02d = 1,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%u,%u,%u\n",
    i,p->kind,p->density,p->speed,p->wind,p->opacity,p->size,p->chance,
    p->period,p->seed,p->layer,p->red,p->green,p->blue);
  if(p->name[0]){
   fprintf(file,"WeatherName%02d = ",i);
   for(const unsigned char *q=(const unsigned char*)p->name;*q;++q)
     fprintf(file,"%02X",(unsigned)*q);
   fputc('\n',file);
  }
 }
 for(int i=0;i<CVIII_WEATHER_SCENE_MAX;++i)
  if(s->weather_scenes[i].used)
   fprintf(file,"WeatherRoom%02d = %u,%d\n",i,
     s->weather_scenes[i].room,s->weather_scenes[i].profile);
}
