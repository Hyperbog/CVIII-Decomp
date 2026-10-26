/* CVIII Enhanced: read-only world-space 2D illumination. No guest writes.
 * Frame PPU line scroll + original room selector scopes the light coordinates.
 * Does not simulate material normals, wall shadows or unseen stage geometry.
 */
#include "cviii_lighting.h"
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
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
            s->light[idx]=(CviiiLight){.room=room,.x=px,.y=py,.radius=56,.energy=85,.red=255,.green=167,.blue=74,.used=1};
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
    float modulation[CVIII_LIGHT_MAX],cc[CVIII_LIGHT_MAX],ss[CVIII_LIGHT_MAX];
    const float radians=0.017453292519943295f;
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
        float intensity=l->flicker==1?0.f:l->flicker==2?2.7f:1.f;
        modulation[i]=1.f+warm*(slow+fast)*intensity;
        cc[i]=cosf((float)l->angle*radians);
        ss[i]=sinf((float)l->angle*radians);
    }
    if(s->enabled){
        int ambient_pct=0,amb_rgb[3]={255,255,255};
        cviii_light_scene_get(s,room,&ambient_pct,amb_rgb);
        float ar=(float)ambient_pct*amb_rgb[0]/25500.f;
        float ag=(float)ambient_pct*amb_rgb[1]/25500.f;
        float ab=(float)ambient_pct*amb_rgb[2]/25500.f;
        for(int y=CVIII_LIGHT_HUD;y<h;++y){
            int origin=unwrap(sx[y],camera,512),yy=sy[y];
            for(int x=0;x<w;++x){
                float r=ar,g=ag,b=ab;
                int world=origin+x;
                for(int i=0;i<CVIII_LIGHT_MAX;++i){
                    const CviiiLight *l=&s->light[i];
                    if(!l->used || l->muted || l->room!=room)continue;
                    float dx=(float)(world-l->x),dy=(float)(yy-l->y);
                    float rad=(float)l->radius,t;
                    if(l->shape==CVIII_SHAPE_RADIAL){
                        float d2=dx*dx+dy*dy;
                        if(d2>=rad*rad)continue;
                        t=1.f-sqrtf(d2)/rad;
                    }else{
                        float along=dx*cc[i]+dy*ss[i];
                        float across=fabsf(-dx*ss[i]+dy*cc[i]);
                        if(along<0 || along>=rad)continue;
                        float half_width;
                        if(l->shape==CVIII_SHAPE_CONE){
                            int spread=clip(l->spread?l->spread:30,5,85);
                            half_width=2.f+along*tanf((float)spread*radians);
                        }else if(l->shape==CVIII_SHAPE_SHAFT){
                            half_width=0.5f*(float)clip(l->width?l->width:32,4,160);
                        }else continue;
                        if(across>=half_width)continue;
                        t=(1.f-across/half_width)*(1.f-along/rad);
                    }
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
            for(int dx=-l->radius;dx<=l->radius && l->shape==CVIII_SHAPE_RADIAL;++dx){
                int d2=dx*dx+dy*dy;
                if(abs(d2-rad2)<=l->radius)
                    dot(p,l->x+dx-origin,y,i==s->selected?0xffffe5b0u:0xffaaaaaau);
            }
            if(dy>=-3 && dy<=3)for(int dx=-3;dx<=3;++dx)
                if(dx==0 || dy==0)dot(p,l->x+dx-origin,y,0xffffffffu);
        }
    }
}

/* Hex-encoded text never escapes a config.ini value, and allows UTF-8. */
static int hexval(char c){
    if(c>='0' && c<='9')return c-'0';
    if(c>='a' && c<='f')return c-'a'+10;
    if(c>='A' && c<='F')return c-'A'+10;
    return -1;
}
/* Validate UTF-8 before writing the destination; malformed labels never
 * partially change a previously loaded scene. */
static int valid_utf8(const unsigned char *p,size_t n){
    size_t i=0;
    while(i<n){
        unsigned c=p[i],extra=0;
        if(c>=32 && c<127){++i;continue;}
        if(c>=0xC2 && c<=0xDF)extra=1;
        else if(c>=0xE0 && c<=0xEF)extra=2;
        else if(c>=0xF0 && c<=0xF4)extra=3;
        else return 0;
        if(i+extra>=n)return 0;
        for(unsigned j=1;j<=extra;++j)
            if(p[i+j]<0x80 || p[i+j]>0xBF)return 0;
        if(c==0xE0 && p[i+1]<0xA0)return 0;
        if(c==0xED && p[i+1]>0x9F)return 0;
        if(c==0xF0 && p[i+1]<0x90)return 0;
        if(c==0xF4 && p[i+1]>0x8F)return 0;
        i+=extra+1;
    }
    return 1;
}
static int hex_label(char *dst,size_t cap,const char *v){
    size_t n=strlen(v);
    if((n&1) || n/2>=cap || cap>CVIII_LIGHT_NAME_CAP)return 0;
    unsigned char candidate[CVIII_LIGHT_NAME_CAP];
    for(size_t i=0;i<n;i+=2){
        int hi=hexval(v[i]),lo=hexval(v[i+1]);
        if(hi<0 || lo<0)return 0;
        candidate[i/2]=(unsigned char)(hi*16+lo);
    }
    if(!valid_utf8(candidate,n/2))return 0;
    memcpy(dst,candidate,n/2);
    dst[n/2]=0;
    return 1;
}
static void label_write(FILE *f,const char *key,int i,const char *v){
    if(!*v)return;
    static const char hex[]="0123456789ABCDEF";
    fprintf(f,"%s%02d = ",key,i);
    for(const unsigned char *p=(const unsigned char*)v;*p;++p){
        fputc(hex[*p>>4],f);
        fputc(hex[*p&15],f);
    }
    fputc('\n',f);
}
static int style_load(CviiiLighting *s,const char *key,const char *val){
    unsigned i;char tail;int shape,angle,spread,width,mute,flicker,n=0;
    if(sscanf(key,"LightStyle%2u%c",&i,&tail)!=1 || i>=CVIII_LIGHT_MAX)return 0;
    if(sscanf(val,"%d,%d,%d,%d,%d,%d%n",
      &shape,&angle,&spread,&width,&mute,&flicker,&n)!=6 || val[n] ||
      shape<0 || shape>2 || angle<0 || angle>359 ||
      spread<0 || spread>85 || width<0 || width>160 ||
      mute<0 || mute>1 || flicker<0 || flicker>2)return 0;
    CviiiLight *l=&s->light[i];
    l->shape=shape;l->angle=angle;l->spread=spread;
    l->width=width;l->muted=mute;l->flicker=flicker;
    return 1;
}
static int scene_load(CviiiLighting *s,const char *key,const char *value){
    unsigned i,room;char tail;int level,r,g,b,n=0;
    if(sscanf(key,"RoomAmbient%2u%c",&i,&tail)!=1 ||
       i>=CVIII_SCENE_AMBIENT_MAX)return 0;
    if(sscanf(value,"%u,%d,%d,%d,%d%n",&room,&level,&r,&g,&b,&n)!=5 ||
       value[n])return 0;
    return cviii_light_scene_set(s,room,level,r,g,b);
}
int cviii_light_load(CviiiLighting *s,const char *key,const char *value){
    if(!s || !key || !value)return 0;
    if(!strcmp(key,"Lighting")){s->enabled=!strcmp(value,"1");return 1;}
    if(!strcmp(key,"LightAmbient")){
        char extra;int n;
        if(sscanf(value,"%d %c",&n,&extra)!=1 || n<35 || n>100)return 0;
        s->ambient=n;return 1;
    }
    if(!strncmp(key,"RoomAmbient",11))return scene_load(s,key,value);
    if(!strncmp(key,"LightStyle",10))return style_load(s,key,value);
    unsigned slot;char extra;
    if(!strncmp(key,"LightName",9)){
        if(sscanf(key,"LightName%2u%c",&slot,&extra)!=1 || slot>=CVIII_LIGHT_MAX)return 0;
        return hex_label(s->light[slot].name,CVIII_LIGHT_NAME_CAP,value);
    }
    if(!strncmp(key,"LightGroup",10)){
        if(sscanf(key,"LightGroup%2u%c",&slot,&extra)!=1 || slot>=CVIII_LIGHT_MAX)return 0;
        return hex_label(s->light[slot].group,CVIII_LIGHT_GROUP_CAP,value);
    }
    if(sscanf(key,"Light%2u%c",&slot,&extra)!=1 || slot>=CVIII_LIGHT_MAX)return 0;
    unsigned room,r,g,b;int x,y,rad,energy,used,end=0;
    if(sscanf(value,"%d,%u,%d,%d,%d,%d,%u,%u,%u%n",
       &used,&room,&x,&y,&rad,&energy,&r,&g,&b,&end)!=9 || value[end] ||
       used!=1 || x<0 || x>65535 || y<0 || y>479 || rad<12 || rad>160 ||
       energy<5 || energy>160 || r>255 || g>255 || b>255)return 0;
    s->light[slot]=(CviiiLight){.room=room,.x=x,.y=y,.radius=rad,.energy=energy,.red=(uint8_t)r,.green=(uint8_t)g,.blue=(uint8_t)b,.used=1};
    return 1;
}
void cviii_light_save(const CviiiLighting *s,FILE *out){
    if(!s || !out)return;
    fprintf(out,"Lighting = %d\nLightAmbient = %d\n",s->enabled,s->ambient);
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *l=&s->light[i];
        if(l->used){
            fprintf(out,"Light%02d = 1,%u,%d,%d,%d,%d,%u,%u,%u\n",
                i,l->room,l->x,l->y,l->radius,l->energy,l->red,l->green,l->blue);
            fprintf(out,"LightStyle%02d = %d,%d,%d,%d,%d,%d\n",
                i,l->shape,l->angle,l->spread,l->width,l->muted,l->flicker);
            label_write(out,"LightName",i,l->name);
            label_write(out,"LightGroup",i,l->group);
        }
    }
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient *a=&s->scenes[i];
        if(a->used)fprintf(out,"RoomAmbient%02d = %u,%d,%d,%d,%d\n",
            i,a->room,a->level,a->red,a->green,a->blue);
    }
}
