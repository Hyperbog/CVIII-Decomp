/* CVIII Enhanced: read-only world-space 2D illumination. No guest writes.
 * Frame PPU line scroll + original room selector scopes the light coordinates.
 * Does not simulate material normals, wall shadows or unseen stage geometry.
 */
#include "cviii_lighting.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
static int clip(int x,int lo,int hi){return x<lo?lo:(x>hi?hi:x);}
static int unwrap(int ppu,int reference,int cycle){
    int d=(ppu-reference%cycle+cycle*2)%cycle;
    if(d>cycle/2)d-=cycle;
    return reference+d;
}
static int wx(int x,int y,int camera,const int *sx){return unwrap(sx[y],camera,512)+x;}
void cviii_light_init(CviiiLighting *s){memset(s,0,sizeof *s);s->ambient=78;s->selected=-1;}
int cviii_light_event(CviiiLighting *s,int event,int x,int y,uint32_t room,
                      int camera,const int sx[CVIII_LIGHT_H],const int sy[CVIII_LIGHT_H]){
    if(!s)return 0;
    if(event==1){s->edit=!s->edit;s->dragging=0;return 1;}
    if(!s->edit)return 0;
    if(event==4){s->dragging=0;return 1;}
    if(event==11 || event==12){s->ambient=clip(s->ambient+(event==11?3:-3),35,100);return 1;}
    if((event==2 || event==3 || event==13) &&
       (!sx || !sy || x<0 || x>=256 || y<CVIII_LIGHT_HUD || y>=240))return 0;
    if(event==2 || event==13){
        int px=wx(x,y,camera,sx),py=sy[y],idx=-1;
        long best=400; /* 20-pixel grab handle, not a pixel-perfect crosshair */
        for(int i=0;i<CVIII_LIGHT_MAX;++i){
            CviiiLight *l=&s->light[i];
            if(!l->used || l->room!=room)continue;
            long dx=(long)px-l->x,dy=(long)py-l->y,d=dx*dx+dy*dy;
            if(d<best){best=d;idx=i;}
        }
        s->selected=idx;
        if(event==13){s->dragging=0;return 1;}
        if(idx<0){
            for(int i=0;i<CVIII_LIGHT_MAX;++i)if(!s->light[i].used){idx=i;break;}
            if(idx<0)return 0;
            s->light[idx]=(CviiiLight){room,px,py,56,85,255,167,74,1};
            s->selected=idx;
        }
        s->enabled=1;s->dragging=1;return 1;
    }
    if(event==3){
        if(s->dragging && s->selected>=0 && s->light[s->selected].used){
            s->light[s->selected].x=wx(x,y,camera,sx);
            s->light[s->selected].y=sy[y];return 1;
        }
        return 0;
    }
    if(s->selected<0 || !s->light[s->selected].used ||
       s->light[s->selected].room!=room)return 0;
    CviiiLight *l=&s->light[s->selected];
    if(event==5){l->used=0;s->selected=-1;return 1;}
    if(event==6 || event==7)l->radius=clip(l->radius+(event==6?4:-4),12,160);
    else if(event==8 || event==9)l->energy=clip(l->energy+(event==8?5:-5),5,160);
    else if(event==10){
        const unsigned colors[]={0xffa74au,0xbbd9ffu,0xff7777u,0xa5ff9cu,0xffffffu};
        unsigned old=((unsigned)l->red<<16)|((unsigned)l->green<<8)|l->blue;
        int at=0;
        for(int i=0;i<5;++i)if(colors[i]==old){at=(i+1)%5;break;}
        l->red=(uint8_t)(colors[at]>>16);l->green=(uint8_t)(colors[at]>>8);
        l->blue=(uint8_t)colors[at];
    }else return 0;
    return 1;
}
/* Reinhard-like highlight shoulder: linear darkening, smooth bounded
 * brightening. NES palette highlights keep their original color variation
 * instead of being crushed to solid white by overlapping point lights. */
static unsigned channel(unsigned input,float gain){
    float base=(float)input;
    float value;
    if(gain<=1.f)value=base*gain;
    else{
        float headroom=255.f-base;
        float raise=base*(gain-1.f);
        value=base+(headroom>0.f?headroom*raise/(headroom+raise):0.f);
    }
    return (unsigned)clip((int)(value+0.5f),0,255);
}
static uint32_t apply(uint32_t p,float r,float g,float b){
    unsigned rr=channel((p>>16)&255u,r);
    unsigned gg=channel((p>>8)&255u,g);
    unsigned bb=channel(p&255u,b);
    return (p&0xff000000u)|(rr<<16)|(gg<<8)|bb;
}
static void dot(uint32_t *p,int x,int y,unsigned color){
    if(x>=0 && x<256 && y>=CVIII_LIGHT_HUD && y<240)p[y*256+x]=color;
}
void cviii_light_present(CviiiLighting *s,uint32_t *p,int w,int h,uint32_t room,
                         int camera,const int sx[CVIII_LIGHT_H],const int sy[CVIII_LIGHT_H],uint64_t frame){
    if(!s || !p || !sx || !sy || w!=256 || h!=240)return;
    float modulation[CVIII_LIGHT_MAX];
    /* Gentle multi-band variation, not frame-by-frame white noise.
     * Isolated candles are relatively stable; larger diffusion flames
     * can show ~10 Hz oscillation in the cited combustion literature.
     * The amplitudes here are deliberate aesthetic choices, NOT fitted
     * experimental measurements. Each light has an independent phase. */
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *l=&s->light[i];
        float t=(float)((double)(frame%216000u)/60.0);
        float phase=(float)i*1.6180339f;
        float warm=(l->red>l->blue && l->red>=l->green)?1.f:0.f;
        float slow=0.018f*sinf(6.2831853f*0.73f*t+phase)
                  +0.012f*sinf(6.2831853f*1.71f*t+phase*2.3f);
        float fast=l->energy>=100?0.009f*sinf(6.2831853f*10.2f*t+phase):0.f;
        modulation[i]=1.f+warm*(slow+fast);
    }
    if(s->enabled){
        float ambient=(float)s->ambient/100.0f;
        for(int y=CVIII_LIGHT_HUD;y<h;++y){
            int origin=unwrap(sx[y],camera,512),yy=sy[y];
            for(int x=0;x<w;++x){
                float r=ambient,g=ambient,b=ambient;
                int world=origin+x;
                for(int i=0;i<CVIII_LIGHT_MAX;++i){
                    const CviiiLight *l=&s->light[i];
                    if(!l->used || l->room!=room)continue;
                    float dx=(float)(world-l->x),dy=(float)(yy-l->y);
                    float dist2=dx*dx+dy*dy,rad=(float)l->radius;
                    if(dist2>=rad*rad)continue;
                    float t=1.f-sqrtf(dist2)/rad;
                    float power=modulation[i]*(float)l->energy*0.014f*t*t*(3.f-2.f*t);
                    r+=power*(float)l->red/255.f;
                    g+=power*(float)l->green/255.f;
                    b+=power*(float)l->blue/255.f;
                }
                p[y*w+x]=apply(p[y*w+x],r,g,b);
            }
        }
    }
    if(!s->edit)return;
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *l=&s->light[i];
        if(!l->used || l->room!=room)continue;
        for(int y=CVIII_LIGHT_HUD;y<h;++y){
            int dy=sy[y]-l->y;
            if(abs(dy)>l->radius+1)continue;
            int origin=unwrap(sx[y],camera,512),rad2=l->radius*l->radius;
            for(int dx=-l->radius;dx<=l->radius;++dx){
                int d2=dx*dx+dy*dy;
                if(abs(d2-rad2)<=l->radius)
                    dot(p,l->x+dx-origin,y,i==s->selected?0xffffe5b0u:0xffaaaaaau);
            }
            if(dy>=-3 && dy<=3)for(int dx=-3;dx<=3;++dx)
                if(dx==0 || dy==0)dot(p,l->x+dx-origin,y,0xffffffffu);
        }
    }
}
int cviii_light_load(CviiiLighting *s,const char *key,const char *value){
    if(!s || !key || !value)return 0;
    if(!strcmp(key,"Lighting")){s->enabled=!strcmp(value,"1");return 1;}
    if(!strcmp(key,"LightAmbient")){
        char extra;int n;
        if(sscanf(value,"%d %c",&n,&extra)!=1 || n<35 || n>100)return 0;
        s->ambient=n;return 1;
    }
    unsigned slot;char extra;
    if(sscanf(key,"Light%2u%c",&slot,&extra)!=1 || slot>=CVIII_LIGHT_MAX)return 0;
    unsigned room,r,g,b;int x,y,rad,energy,used,end=0;
    if(sscanf(value,"%d,%u,%d,%d,%d,%d,%u,%u,%u%n",
       &used,&room,&x,&y,&rad,&energy,&r,&g,&b,&end)!=9 || value[end] ||
       used!=1 || x<0 || x>65535 || y<0 || y>479 || rad<12 || rad>160 ||
       energy<5 || energy>160 || r>255 || g>255 || b>255)return 0;
    s->light[slot]=(CviiiLight){room,x,y,rad,energy,(uint8_t)r,(uint8_t)g,(uint8_t)b,1};
    return 1;
}
void cviii_light_save(const CviiiLighting *s,FILE *out){
    if(!s || !out)return;
    fprintf(out,"Lighting = %d\nLightAmbient = %d\n",s->enabled,s->ambient);
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *l=&s->light[i];
        if(l->used)fprintf(out,"Light%02d = 1,%u,%d,%d,%d,%d,%u,%u,%u\n",
            i,l->room,l->x,l->y,l->radius,l->energy,l->red,l->green,l->blue);
    }
}
