/* CVIII Enhanced: deterministic, world-anchored native-pixel particles.
 * Pure C11 presentation pass. No game state, PPU writes, RNG state,
 * GPU dependency, frame allocations, framebuffer upscaling, or real blur.
 * Always call AFTER the selected Standard/GPU lighting pass and BEFORE UI.
 */
#include "cviii_lighting.h"
#include <string.h>
#include <stdio.h>
#include <math.h>

static int clampi(int n,int lo,int hi){return n<lo?lo:n>hi?hi:n;}
static unsigned mix(unsigned x){
    x^=x>>16;x*=0x7feb352du;x^=x>>15;x*=0x846ca68bu;x^=x>>16;
    return x;
}
static float hash01(unsigned x){return (float)(mix(x)&0xffffu)/65536.f;}
static float wrapf(float x,float span){
    if(span<=0.f)return 0.f;
    x=fmodf(x,span);
    return x<0.f?x+span:x;
}
static int unwrap(int ppu,int camera){
    int base=camera%512;
    int d=(ppu-base+1024)%512;
    if(d>256)d-=512;
    return camera+d;
}
const char *cviii_particle_kind_name(int kind){
    static const char *const names[CVIII_FX_COUNT]={
        "Floating Dust","Rising Embers","Pixel Fog","Falling Ash",
        "Snow","Rain","Fireflies"
    };
    return kind>=0 && kind<CVIII_FX_COUNT?names[kind]:"Unknown";
}
static void defaults(CviiiParticleEmitter *e,uint32_t room,int kind,int x,int y){
    static const unsigned rgb[][3]={
        {204,192,157},{255,128,37},{157,180,197},
        {170,162,151},{228,238,255},{116,163,223},{198,245,115}
    };
    const int fog=kind==CVIII_FX_FOG;
    *e=(CviiiParticleEmitter){
        .room=room,.used=1,.kind=kind,.x=x,.y=y,
        .w=fog?160:96,.h=fog?60:96,
        .density=fog?64:kind==CVIII_FX_RAIN?72:kind==CVIII_FX_FIREFLIES?14:32,
        .speed=fog?36:100,.wind=fog?18:0,
        .opacity=fog?22:kind==CVIII_FX_EMBERS?90:kind==CVIII_FX_RAIN?44:58,
        .size=fog?2:1,
        .red=(uint8_t)rgb[kind][0],.green=(uint8_t)rgb[kind][1],
        .blue=(uint8_t)rgb[kind][2]
    };
    (void)snprintf(e->name,sizeof e->name,"%s",cviii_particle_kind_name(kind));
    if(x+e->w>65535)e->w=65535-x;
    if(y+e->h>479)e->h=479-y;
}
int cviii_particle_add(CviiiLighting *s,uint32_t room,int kind,int x,int y){
    if(!s || kind<0 || kind>=CVIII_FX_COUNT || x<0 || x>=65535 ||
       y<0 || y>=479)return -1;
    for(int i=0;i<CVIII_PARTICLE_EMITTER_MAX;++i)if(!s->particles[i].used){
        defaults(&s->particles[i],room,kind,x,y);
        s->particles_enabled=1;
        return i;
    }
    return -1;
}
static int valid(const CviiiParticleEmitter *e){
    return e->kind>=0 && e->kind<CVIII_FX_COUNT &&
           e->x>=0 && e->x<65535 && e->y>=0 && e->y<479 &&
           e->w>=1 && e->h>=1 && e->x<=65535-e->w && e->y<=479-e->h &&
           e->density>=1 && e->density<=CVIII_PARTICLE_INSTANCE_MAX &&
           e->speed>=0 && e->speed<=300 &&
           e->wind>=-100 && e->wind<=100 &&
           e->opacity>=0 && e->opacity<=100 &&
           e->size>=1 && e->size<=4;
}
int cviii_particle_property(CviiiLighting *s,int slot,int property,int value){
    if(!s || slot<0 || slot>=CVIII_PARTICLE_EMITTER_MAX ||
       !s->particles[slot].used)return 0;
    CviiiParticleEmitter copy=s->particles[slot];
    switch(property){
        case 0:s->particles[slot].used=0;return 1;
        case 1:copy.kind=value;break;
        case 2:copy.x=value;break;
        case 3:copy.y=value;break;
        case 4:copy.w=value;break;
        case 5:copy.h=value;break;
        case 6:copy.density=value;break;
        case 7:copy.speed=value;break;
        case 8:copy.wind=value;break;
        case 9:copy.opacity=value;break;
        case 10:copy.size=value;break;
        case 11:if(value<0||value>255)return 0;copy.red=(uint8_t)value;break;
        case 12:if(value<0||value>255)return 0;copy.green=(uint8_t)value;break;
        case 13:if(value<0||value>255)return 0;copy.blue=(uint8_t)value;break;
        default:return 0;
    }
    if(!valid(&copy))return 0;
    s->particles[slot]=copy;
    return 1;
}
int cviii_particle_name(CviiiLighting *s,int slot,const char *name){
    if(!s || slot<0 || slot>=CVIII_PARTICLE_EMITTER_MAX ||
       !s->particles[slot].used || !name)return 0;
    size_t n=strlen(name);
    if(!n || n>=CVIII_LIGHT_NAME_CAP)return 0;
    for(size_t i=0;i<n;++i)
        if((unsigned char)name[i]<32 || (unsigned char)name[i]>126)return 0;
    memcpy(s->particles[slot].name,name,n+1);
    return 1;
}
static int hval(char c){
    if(c>='0'&&c<='9')return c-'0';
    if(c>='A'&&c<='F')return c-'A'+10;
    if(c>='a'&&c<='f')return c-'a'+10;
    return -1;
}
int cviii_particle_load(CviiiLighting *s,const char *key,const char *value){
    if(!s||!key||!value)return 0;
    if(!strcmp(key,"Particles")){
        if(strcmp(value,"0") && strcmp(value,"1"))return 0;
        s->particles_enabled=value[0]=='1';return 1;
    }
    unsigned slot=0;char tail=0;
    if(!strncmp(key,"ParticleName",12)){
        if(sscanf(key,"ParticleName%2u%c",&slot,&tail)!=1 ||
           slot>=CVIII_PARTICLE_EMITTER_MAX)return 0;
        size_t n=strlen(value);
        if(!n || (n&1) || n/2>=CVIII_LIGHT_NAME_CAP)return 0;
        char name[CVIII_LIGHT_NAME_CAP];
        for(size_t i=0;i<n;i+=2){
            int a=hval(value[i]),b=hval(value[i+1]);
            if(a<0 || b<0 || a*16+b<32 || a*16+b>126)return 0;
            name[i/2]=(char)(a*16+b);
        }
        name[n/2]=0;
        memcpy(s->particles[slot].name,name,n/2+1);return 1;
    }
    if(sscanf(key,"Particle%2u%c",&slot,&tail)!=1 ||
       slot>=CVIII_PARTICLE_EMITTER_MAX)return 0;
    unsigned room=0,r=0,g=0,b=0;int used=0,n=0;
    CviiiParticleEmitter p={0};
    if(sscanf(value,"%d,%u,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%u,%u,%u%n",
        &used,&room,&p.kind,&p.x,&p.y,&p.w,&p.h,&p.density,
        &p.speed,&p.wind,&p.opacity,&p.size,&r,&g,&b,&n)!=15 ||
        value[n] || used!=1 || r>255 || g>255 || b>255)return 0;
    p.used=1;p.room=room;p.red=(uint8_t)r;p.green=(uint8_t)g;p.blue=(uint8_t)b;
    if(!valid(&p))return 0;
    s->particles[slot]=p;return 1;
}
void cviii_particle_save(const CviiiLighting *s,FILE *file){
    if(!s||!file)return;
    fprintf(file,"Particles = %d\n",s->particles_enabled?1:0);
    for(int i=0;i<CVIII_PARTICLE_EMITTER_MAX;++i){
        const CviiiParticleEmitter *e=&s->particles[i];
        if(!e->used)continue;
        fprintf(file,"Particle%02d = 1,%u,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%u,%u,%u\n",
            i,e->room,e->kind,e->x,e->y,e->w,e->h,e->density,
            e->speed,e->wind,e->opacity,e->size,e->red,e->green,e->blue);
        if(e->name[0]){
            fprintf(file,"ParticleName%02d = ",i);
            for(const unsigned char *p=(const unsigned char*)e->name;*p;++p)
                fprintf(file,"%02X",(unsigned)*p);
            fputc('\n',file);
        }
    }
}
static uint32_t mixpixel(uint32_t existing,const CviiiParticleEmitter *e,int opacity){
    // Alpha is quantized to sixteenths to keep a palette/pixel-art character.
    int q=clampi((opacity*16+50)/100,0,16);
    if(q<=0)return existing;
    unsigned r=(existing>>16)&255u,g=(existing>>8)&255u,b=existing&255u;
    r=(r*(unsigned)(16-q)+e->red*(unsigned)q+8u)/16u;
    g=(g*(unsigned)(16-q)+e->green*(unsigned)q+8u)/16u;
    b=(b*(unsigned)(16-q)+e->blue*(unsigned)q+8u)/16u;
    return (existing&0xff000000u)|(r<<16)|(g<<8)|b;
}
static void put(uint32_t *pixels,int x,int y,const CviiiParticleEmitter *e,
                int opacity){
    if(x<0 || x>=256 || y<CVIII_LIGHT_HUD || y>=240)return;
    uint32_t *p=&pixels[y*256+x];
    *p=mixpixel(*p,e,opacity);
}
void cviii_particle_present(const CviiiLighting *s,uint32_t pixels[CVIII_LIGHT_W*CVIII_LIGHT_H],
                            uint32_t room,int camera,
                            const int sx[CVIII_LIGHT_H],const int sy[CVIII_LIGHT_H],
                            uint64_t frame){
    if(!s || !pixels || !sx || !sy ||
       (!s->particles_enabled && !s->edit))return;
    /* Rebuild reverse scanline mapping from the ACTUAL rendered PPU
     * scroll: both stage scroll and visible room IDs remain authoritative. */
    int screen[480];
    for(int i=0;i<480;++i)screen[i]=-1;
    for(int y=CVIII_LIGHT_HUD;y<240;++y)
        if(sy[y]>=0 && sy[y]<480)screen[sy[y]]=y;
    float seconds=(float)((frame%216000u)/60.0);
    for(int slot=0;slot<CVIII_PARTICLE_EMITTER_MAX;++slot){
        const CviiiParticleEmitter *e=&s->particles[slot];
        if(!e->used || e->room!=room || !valid(e) ||
           !s->particles_enabled || e->opacity<=0)continue;
        const float time=seconds*((float)e->speed/100.f);
        for(int i=0;i<e->density;++i){
            unsigned id=(unsigned)(slot+1)*0x9e3779b9u ^ (unsigned)i*0x45d9f3bu;
            float fx=hash01(id+1u),fy=hash01(id+17u),phase=hash01(id+91u);
            float x=(float)e->x+fx*e->w,y=(float)e->y+fy*e->h;
            float wind=((float)e->wind/100.f)*time*7.f;
            float wobble=sinf(time*(.7f+phase)+phase*6.28318f)*1.3f;
            switch(e->kind){
                case CVIII_FX_DUST:
                    x=e->x+wrapf(fx*e->w+wind+time*(.6f+phase*1.6f),e->w);
                    y=e->y+wrapf(fy*e->h+time*(.4f+phase),e->h);break;
                case CVIII_FX_EMBERS:
                    x=e->x+wrapf(fx*e->w+wind+wobble,e->w);
                    y=e->y+wrapf(fy*e->h-time*(11.f+phase*10.f),e->h);break;
                case CVIII_FX_FOG:
                    x=e->x+wrapf(fx*e->w+wind+time*2.5f,e->w);
                    y=e->y+wrapf(fy*e->h+sinf(time*.3f+phase*6.f)*2.f,e->h);break;
                case CVIII_FX_ASH:
                    x=e->x+wrapf(fx*e->w+wind+time*1.7f+wobble,e->w);
                    y=e->y+wrapf(fy*e->h+time*(3.f+phase*6.f),e->h);break;
                case CVIII_FX_SNOW:
                    x=e->x+wrapf(fx*e->w+wind+wobble*2.f,e->w);
                    y=e->y+wrapf(fy*e->h+time*(7.f+phase*5.f),e->h);break;
                case CVIII_FX_RAIN:
                    x=e->x+wrapf(fx*e->w+wind-time*(4.f+phase*4.f),e->w);
                    y=e->y+wrapf(fy*e->h+time*(44.f+phase*25.f),e->h);break;
                case CVIII_FX_FIREFLIES:
                    x=e->x+wrapf(fx*e->w+wind+wobble*5.f,e->w);
                    y=e->y+wrapf(fy*e->h+sinf(time*.5f+phase*10.f)*5.f,e->h);break;
                default:continue;
            }
            int xx=(int)floorf(x),wy=(int)floorf(y);
            if(wy<0 || wy>=480 || screen[wy]<CVIII_LIGHT_HUD)continue;
            int yy=screen[wy];
            int opacity=e->opacity;
            if(e->kind==CVIII_FX_FIREFLIES){
                float pulse=.3f+.7f*(.5f+.5f*sinf(time*(2.f+phase*3.f)+phase*12.f));
                opacity=(int)(opacity*pulse);
            }
            if(e->kind==CVIII_FX_FOG){
                /* No blurred rectangle. Stippled native-pixel cloudlets,
                 * sparse at the edges and phase-shifted by deterministic ID. */
                int ww=e->size*4+4,hh=e->size+2;
                for(int ry=0;ry<hh;++ry){
                    int worldY=wy+ry-hh/2;
                    if(worldY<0 || worldY>=480 || screen[worldY]<48)continue;
                    int row=screen[worldY];
                    int shifted=xx-unwrap(sx[row],camera);
                    for(int rx=0;rx<ww;++rx){
                        int edge=rx<ww/2?rx:ww-rx-1;
                        if((mix(id^(unsigned)(rx+ry*17))&7u)>=(unsigned)(edge+1))
                            continue;
                        if(((rx+ry+(int)(frame/24))&3)==0)continue;
                        put(pixels,shifted+rx-ww/2,row,e,opacity/2);
                    }
                }
            }else if(e->kind==CVIII_FX_RAIN){
                for(int r=0;r<e->size+2;++r){
                    int worldY=wy+r;
                    if(worldY<0 || worldY>=480 || screen[worldY]<48)continue;
                    int row=screen[worldY];
                    put(pixels,xx-unwrap(sx[row],camera)-r/2,row,e,opacity);
                }
            }else{
                int side=e->size;
                if(e->kind==CVIII_FX_EMBERS || e->kind==CVIII_FX_FIREFLIES)
                    side=clampi(e->size,1,2);
                for(int dy=0;dy<side;++dy){
                    int worldY=wy+dy;
                    if(worldY<0 || worldY>=480 || screen[worldY]<48)continue;
                    int row=screen[worldY];
                    int at=xx-unwrap(sx[row],camera);
                    for(int dx=0;dx<side;++dx)
                        put(pixels,at+dx,row,e,opacity);
                }
            }
        }
    }
    if(s->edit){
        /* Sharp 1px world-space region outlines are EDITOR-ONLY.
         * Scanline PPU scroll keeps them attached to stage geometry. */
        for(int slot=0;slot<CVIII_PARTICLE_EMITTER_MAX;++slot){
            const CviiiParticleEmitter *e=&s->particles[slot];
            if(!e->used || e->room!=room || !valid(e))continue;
            for(int y=CVIII_LIGHT_HUD;y<240;++y){
                int wy=sy[y];
                if(wy<e->y || wy>e->y+e->h)continue;
                int left=e->x-unwrap(sx[y],camera);
                if(wy==e->y || wy==e->y+e->h){
                    for(int x=left;x<=left+e->w;++x)
                        if(x>=0 && x<256)
                            pixels[y*256+x]=0xff4dd2e6u;
                }else{
                    if(left>=0 && left<256)
                        pixels[y*256+left]=0xff4dd2e6u;
                    if(left+e->w>=0 && left+e->w<256)
                        pixels[y*256+left+e->w]=0xff4dd2e6u;
                }
            }
        }
    }
}
