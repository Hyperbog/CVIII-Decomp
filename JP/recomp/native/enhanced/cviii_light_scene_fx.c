/* CVIII lighting: reusable live styles, authored geometry masks, grading.
 * Strict C11. All edits live in host presentation settings, never NES RAM.
 */
#include "cviii_lighting.h"
#include <string.h>
#include <math.h>
static int cap(int x,int lo,int hi){return x<lo?lo:x>hi?hi:x;}
static int label(char *dst,size_t size,const char *name){
    if(!dst || !name)return 0;
    size_t n=strlen(name);
    if(!n || n>=size)return 0;
    for(size_t i=0;i<n;++i)if((unsigned char)name[i]<32 ||
                                (unsigned char)name[i]==127)return 0;
    memcpy(dst,name,n+1);return 1;
}
int cviii_light_style_capture(CviiiLighting *s,int slot,int light,const char *name){
    if(!s || slot<0 || slot>=CVIII_GLOBAL_STYLE_MAX ||
       light<0 || light>=CVIII_LIGHT_MAX || !s->light[light].used)return 0;
    CviiiGlobalStyle style={0};
    if(!label(style.name,sizeof style.name,name))return 0;
    style.used=1;
    cviii_light_effective(s,&s->light[light],&style.light);
    style.light.style_link=0;
    style.light.x=style.light.y=0;
    style.light.room=0;
    s->styles[slot]=style;
    return 1;
}
int cviii_light_style_link(CviiiLighting *s,int index,int slot){
    if(!s || index<0 || index>=CVIII_LIGHT_MAX || !s->light[index].used ||
       slot< -1 || slot>=CVIII_GLOBAL_STYLE_MAX)return 0;
    if(slot>=0 && !s->styles[slot].used)return 0;
    s->light[index].style_link=slot+1;
    return 1;
}
int cviii_light_style_link_group(CviiiLighting *s,int index,int slot){
    if(!s || index<0 || index>=CVIII_LIGHT_MAX || !s->light[index].used ||
       slot< -1 || slot>=CVIII_GLOBAL_STYLE_MAX)return 0;
    if(slot>=0 && !s->styles[slot].used)return 0;
    CviiiLight *selected=&s->light[index];
    if(!selected->group[0])return cviii_light_style_link(s,index,slot);
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        CviiiLight *l=&s->light[i];
        if(l->used && l->room==selected->room &&
           !strcmp(l->group,selected->group))l->style_link=slot+1;
    }
    return 1;
}
void cviii_light_effective(const CviiiLighting *s,const CviiiLight *l,CviiiLight *out){
    if(!l || !out)return;
    *out=*l;
    int slot=l->style_link-1;
    if(!s || slot<0 || slot>=CVIII_GLOBAL_STYLE_MAX ||
       !s->styles[slot].used)return;
    const CviiiLight *p=&s->styles[slot].light;
    out->radius=p->radius;out->energy=p->energy;
    out->red=p->red;out->green=p->green;out->blue=p->blue;
    out->shape=p->shape;out->angle=p->angle;
    out->spread=p->spread;out->width=p->width;out->flicker=p->flicker;
    out->anim_speed=p->anim_speed;out->anim_strength=p->anim_strength;
    /* x/y/room, name, group, and per-placement mute remain local. */
}
int cviii_light_mask_add(CviiiLighting *s,uint32_t room,int x,int y,int w,int h){
    if(!s || x<0 || y<0 || w<1 || h<1 ||
       w>65535 || h>479 || x>65535-w || y>479-h)return -1;
    for(int i=0;i<CVIII_OCCLUDER_MAX;++i)if(!s->masks[i].used){
        s->masks[i]=(CviiiOccluder){.room=room,.x=x,.y=y,.w=w,.h=h,
                                     .opacity=88,.softness=5,.used=1};
        return i;
    }
    return -1;
}
int cviii_light_mask_remove(CviiiLighting *s,int slot){
    if(!s || slot<0 || slot>=CVIII_OCCLUDER_MAX || !s->masks[slot].used)return 0;
    s->masks[slot].used=0;return 1;
}
/* Closed slab ray/rectangle intersection; the ray segment is (light,pixel).
 * No occlusion is inferred from game tiles: only deliberately drawn masks. */
static int intercept(const CviiiOccluder *m,float ax,float ay,float bx,float by){
    float dx=bx-ax,dy=by-ay,lo=0.f,hi=1.f;
    float p[4]={-dx,dx,-dy,dy};
    float q[4]={ax-m->x,(float)(m->x+m->w)-ax,
                ay-m->y,(float)(m->y+m->h)-ay};
    for(int i=0;i<4;++i){
        if(fabsf(p[i])<1e-6f){if(q[i]<0.f)return 0;}
        else{
            float t=q[i]/p[i];
            if(p[i]<0){if(t>hi)return 0;if(t>lo)lo=t;}
            else{if(t<lo)return 0;if(t<hi)hi=t;}
        }
    }
    return lo<=hi && lo<0.999f && hi>0.001f;
}
float cviii_light_shadow(const CviiiLighting *s,uint32_t room,
                        int source_x,int source_y,int x,int y){
    if(!s)return 1.f;
    float transmission=1.f;
    for(int j=0;j<CVIII_OCCLUDER_MAX;++j){
        const CviiiOccluder *m=&s->masks[j];
        if(!m->used || m->room!=room || m->opacity<=0)continue;
        if(source_x>=m->x && source_x<=m->x+m->w &&
           source_y>=m->y && source_y<=m->y+m->h)continue;
        /* Reject geometry outside the complete light->pixel segment AABB
           before tracing five penumbra samples. */
        int minx=source_x<x?source_x:x,maxx=source_x>x?source_x:x;
        int miny=source_y<y?source_y:y,maxy=source_y>y?source_y:y;
        if(m->x>maxx+16 || m->x+m->w<minx-16 ||
           m->y>maxy+16 || m->y+m->h<miny-16)continue;
        int radius=cap(m->softness,0,16);
        int covered=0;
        /* Stable 3x3 area-source PCF (binomial 1:2:1 x 1:2:1).
         * Spread across both axes, removing single-axis hard seams. */
        for(int sy=-1;sy<=1;++sy){
            int wy=sy==0?2:1;
            for(int sx=-1;sx<=1;++sx){
                int wx=sx==0?2:1;
                float lx=(float)source_x+(float)(sx*radius);
                float ly=(float)source_y+(float)(sy*radius);
                covered+=wx*wy*intercept(m,lx,ly,(float)x,(float)y);
            }
        }
        float occlusion=(float)m->opacity/100.f*(float)covered/16.f;
        transmission*=1.f-occlusion;
        if(transmission<0.005f)return 0.f;
    }
    return transmission;
}
int cviii_light_grade_set(CviiiLighting *s,uint32_t room,int ev,int temp,int sat){
    if(!s || ev< -200 || ev>200 || temp< -100 || temp>100 ||
       sat<0 || sat>200)return 0;
    int level=s->ambient,rgb[3]={255,255,255};
    cviii_light_scene_get(s,room,&level,rgb);
    if(!cviii_light_scene_set(s,room,level,rgb[0],rgb[1],rgb[2]))return 0;
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        CviiiSceneAmbient *a=&s->scenes[i];
        if(!a->used || a->room!=room)continue;
        a->exposure=ev;a->temperature=temp;a->saturation=sat;a->graded=1;
        return 1;
    }
    return 0;
}
void cviii_light_grade_get(const CviiiLighting *s,uint32_t room,
                          int *ev,int *temp,int *sat){
    if(ev)*ev=0;
    if(temp)*temp=0;
    if(sat)*sat=100;
    if(!s)return;
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient *a=&s->scenes[i];
        if(!a->used || a->room!=room || !a->graded)continue;
        if(ev)*ev=a->exposure;
        if(temp)*temp=a->temperature;
        if(sat)*sat=a->saturation;
        return;
    }
}
uint32_t cviii_light_scene_resolve(const CviiiLighting *s,uint32_t raw){
    if(!s)return raw;
    for(int i=0;i<CVIII_SCENE_ALIAS_MAX;++i)
        if(s->aliases[i].used && s->aliases[i].source==raw)
            return s->aliases[i].target;
    return raw;
}
int cviii_light_scene_alias(CviiiLighting *s,uint32_t raw,uint32_t stable){
    if(!s)return 0;
    for(int i=0;i<CVIII_SCENE_ALIAS_MAX;++i){
        CviiiSceneAlias *a=&s->aliases[i];
        if(a->used && a->source==raw){
            a->target=stable;return 1;
        }
    }
    for(int i=0;i<CVIII_SCENE_ALIAS_MAX;++i)if(!s->aliases[i].used){
        s->aliases[i]=(CviiiSceneAlias){.source=raw,.target=stable,.used=1};
        return 1;
    }
    return 0;
}
static int unhex(char c){
    if(c>='0'&&c<='9')return c-'0';
    if(c>='A'&&c<='F')return c-'A'+10;
    if(c>='a'&&c<='f')return c-'a'+10;
    return -1;
}
static void write_hex(FILE *f,const char *s){
    const char *hex="0123456789ABCDEF";
    for(const unsigned char *p=(const unsigned char*)s;*p;++p){
        fputc(hex[*p>>4],f);fputc(hex[*p&15],f);
    }
}
static int read_hex(char *dst,size_t cap,const char *text){
    size_t n=strlen(text);if((n&1)||n/2>=cap)return 0;
    char scratch[CVIII_LIGHT_NAME_CAP];
    if(cap>sizeof scratch)return 0;
    for(size_t i=0;i<n;i+=2){
        int a=unhex(text[i]),b=unhex(text[i+1]);
        if(a<0||b<0 || (a*16+b)<32 || (a*16+b)==127)return 0;
        scratch[i/2]=(char)(a*16+b);
    }
    scratch[n/2]=0;
    memcpy(dst,scratch,n/2+1);
    return 1;
}
int cviii_light_extra_load(CviiiLighting *s,const char *key,const char *val){
    if(!s || !key || !val)return 0;
    unsigned slot=0,room=0,source=0,target=0;
    char suffix;int n=0;
    if(!strncmp(key,"LightLink",9)){
        int link=0;
        if(sscanf(key,"LightLink%3u%c",&slot,&suffix)!=1 || slot>=CVIII_LIGHT_MAX ||
           sscanf(val,"%d%n",&link,&n)!=1 || val[n] ||
           link<0 || link>CVIII_GLOBAL_STYLE_MAX)return 0;
        s->light[slot].style_link=link;return 1;
    }
    if(!strncmp(key,"SceneAlias",10)){
        if(sscanf(key,"SceneAlias%2u%c",&slot,&suffix)!=1 ||
           slot>=CVIII_SCENE_ALIAS_MAX ||
           sscanf(val,"%u,%u%n",&source,&target,&n)!=2 || val[n])return 0;
        s->aliases[slot]=(CviiiSceneAlias){.source=source,.target=target,.used=1};
        return 1;
    }
    if(!strncmp(key,"SceneGrade",10)){
        int ev=0,temp=0,sat=0;
        if(sscanf(key,"SceneGrade%2u%c",&slot,&suffix)!=1 ||
           slot>=CVIII_SCENE_AMBIENT_MAX ||
           sscanf(val,"%u,%d,%d,%d%n",&room,&ev,&temp,&sat,&n)!=4 ||
           val[n])return 0;
        return cviii_light_grade_set(s,room,ev,temp,sat);
    }
    if(!strncmp(key,"Occluder",8)){
        int x,y,w,h,opacity,softness,used=0;
        if(sscanf(key,"Occluder%2u%c",&slot,&suffix)!=1 ||
           slot>=CVIII_OCCLUDER_MAX ||
           sscanf(val,"%u,%d,%d,%d,%d,%d,%d%n",
               &room,&x,&y,&w,&h,&opacity,&softness,&n)!=7 || val[n] ||
           x<0 || y<0 || w<1 || h<1 || x>65535-w || y>479-h ||
           opacity<0 || opacity>100 || softness<0 || softness>16)return 0;
        used=1;
        s->masks[slot]=(CviiiOccluder){.room=room,.x=x,.y=y,.w=w,.h=h,
                                       .opacity=opacity,.softness=softness,.used=used};
        return 1;
    }
    if(!strncmp(key,"GlobalStyle",11)){
        int radius,energy,red,green,blue,shape,angle,spread,width,flicker;
        char encoded[CVIII_LIGHT_NAME_CAP*2+1]={0};
        if(sscanf(key,"GlobalStyle%2u%c",&slot,&suffix)!=1 ||
           slot>=CVIII_GLOBAL_STYLE_MAX ||
           sscanf(val,"%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%96s%n",
             &radius,&energy,&red,&green,&blue,&shape,&angle,
             &spread,&width,&flicker,encoded,&n)!=11 || val[n] ||
           radius<12 || radius>160 || energy<5 || energy>160 ||
           red<0 || red>255 || green<0 || green>255 || blue<0 || blue>255 ||
           shape<0 || shape>2 || angle<0 || angle>359 || spread<0 || spread>85 ||
           width<0 || width>160 || flicker<0 || flicker>2)return 0;
        CviiiGlobalStyle style={0};
        if(!read_hex(style.name,sizeof style.name,encoded) || !style.name[0])return 0;
        style.used=1;
        style.light=(CviiiLight){.radius=radius,.energy=energy,
          .red=(uint8_t)red,.green=(uint8_t)green,.blue=(uint8_t)blue,
          .shape=shape,.angle=angle,.spread=spread,.width=width,.flicker=flicker};
        s->styles[slot]=style;return 1;
    }
    return 0;
}
void cviii_light_extra_save(const CviiiLighting *s,FILE *f){
    if(!s || !f)return;
    for(int i=0;i<CVIII_GLOBAL_STYLE_MAX;++i){
        const CviiiGlobalStyle *g=&s->styles[i];
        if(!g->used)continue;
        const CviiiLight *l=&g->light;
        fprintf(f,"GlobalStyle%02d = %d,%d,%u,%u,%u,%d,%d,%d,%d,%d,",
          i,l->radius,l->energy,l->red,l->green,l->blue,l->shape,
          l->angle,l->spread,l->width,l->flicker);
        write_hex(f,g->name);fputc('\n',f);
    }
    for(int i=0;i<CVIII_LIGHT_MAX;++i)
        if(s->light[i].used && s->light[i].style_link)
            fprintf(f,"LightLink%02d = %d\n",i,s->light[i].style_link);
    for(int i=0;i<CVIII_OCCLUDER_MAX;++i){
        const CviiiOccluder *m=&s->masks[i];
        if(!m->used)continue;
        fprintf(f,"Occluder%02d = %u,%d,%d,%d,%d,%d,%d\n",
          i,m->room,m->x,m->y,m->w,m->h,m->opacity,m->softness);
    }
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient *a=&s->scenes[i];
        if(a->used && a->graded)
            fprintf(f,"SceneGrade%02d = %u,%d,%d,%d\n",i,a->room,
              a->exposure,a->temperature,a->saturation);
    }
    for(int i=0;i<CVIII_SCENE_ALIAS_MAX;++i)
        if(s->aliases[i].used)
            fprintf(f,"SceneAlias%02d = %u,%u\n",i,
              s->aliases[i].source,s->aliases[i].target);
}
