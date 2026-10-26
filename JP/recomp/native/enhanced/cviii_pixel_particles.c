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
           e->size>=1 && e->size<=4 &&
           e->light_link>=0 && e->light_link<=CVIII_LIGHT_MAX &&
           e->link_dx>=-512 && e->link_dx<=512 &&
           e->link_dy>=-512 && e->link_dy<=512 &&
           e->layer>=0 && e->layer<=1 &&
           e->glow>=0 && e->glow<=100;
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
        case 14:copy.layer=value;break;
        case 15:copy.glow=value;break;
        default:return 0;
    }
    if(copy.light_link){
        const CviiiLight *l=&s->light[copy.light_link-1];
        if(!l->used || l->room!=copy.room)return 0;
        if(property==2)copy.link_dx=value-l->x;
        if(property==3)copy.link_dy=value-l->y;
    }
    if(!valid(&copy))return 0;
    s->particles[slot]=copy;
    return 1;
}
int cviii_particle_world_region(const CviiiLighting *s,
    const CviiiParticleEmitter *e,CviiiParticleEmitter *world){
    if(!s || !e || !world || !e->used)return 0;
    *world=*e;
    if(e->light_link){
        const CviiiLight *l=&s->light[e->light_link-1];
        if(!l->used || l->muted || l->room!=e->room)return 0;
        world->x=l->x+e->link_dx;
        world->y=l->y+e->link_dy;
    }
    return valid(world);
}
int cviii_particle_attach(CviiiLighting *s,int slot,int light_slot){
    if(!s || slot<0 || slot>=CVIII_PARTICLE_EMITTER_MAX ||
       !s->particles[slot].used || light_slot<-1 ||
       light_slot>=CVIII_LIGHT_MAX)return 0;
    CviiiParticleEmitter *e=&s->particles[slot],world;
    if(!cviii_particle_world_region(s,e,&world)){
        world=*e; /* recoverable even after linked light was deleted */
        if(e->light_link){
            const CviiiLight *old=&s->light[e->light_link-1];
            if(old->used && old->room==e->room){
                world.x=old->x+e->link_dx;
                world.y=old->y+e->link_dy;
            }
        }
    }
    if(light_slot>=0){
        const CviiiLight *l=&s->light[light_slot];
        if(!l->used || l->room!=e->room ||
           world.x-l->x < -512 || world.x-l->x>512 ||
           world.y-l->y < -512 || world.y-l->y>512)return 0;
        e->link_dx=world.x-l->x;
        e->link_dy=world.y-l->y;
        e->light_link=light_slot+1;
    }else{
        e->x=world.x;e->y=world.y;
        e->light_link=0;e->link_dx=0;e->link_dy=0;
    }
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
    if(!strncmp(key,"ParticleAttach",14)){
        int n=0,link,dx,dy,layer,glow;
        if(sscanf(key,"ParticleAttach%2u%c",&slot,&tail)!=1 ||
            slot>=CVIII_PARTICLE_EMITTER_MAX ||
            sscanf(value,"%d,%d,%d,%d,%d%n",
                 &link,&dx,&dy,&layer,&glow,&n)!=5 || value[n] ||
            link<0 || link>CVIII_LIGHT_MAX ||
            dx<-512 || dx>512 || dy<-512 || dy>512 ||
            layer<0 || layer>1 || glow<0 || glow>100)return 0;
        CviiiParticleEmitter *e=&s->particles[slot];
        e->light_link=link;e->link_dx=dx;e->link_dy=dy;
        e->layer=layer;e->glow=glow;
        return 1;
    }
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
        if(e->light_link || e->layer || e->glow)
            fprintf(file,"ParticleAttach%02d = %d,%d,%d,%d,%d\n",
                i,e->light_link,e->link_dx,e->link_dy,e->layer,e->glow);
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
                int opacity,int layer,const uint8_t *sprite_mask){
    if(x<0 || x>=256 || y<CVIII_LIGHT_HUD || y>=240)return;
    if(layer==1 && sprite_mask && sprite_mask[y*256+x])return;
    uint32_t *p=&pixels[y*256+x];
    *p=mixpixel(*p,e,opacity);
}
void cviii_particle_present_layer(const CviiiLighting *s,
    uint32_t pixels[CVIII_LIGHT_W*CVIII_LIGHT_H],uint32_t room,int camera,
    const int sx[CVIII_LIGHT_H],const int sy[CVIII_LIGHT_H],
    uint64_t frame,int layer,const uint8_t *sprite_mask){
    if(!s || !pixels || !sx || !sy || layer<0 || layer>1)return;
    if(!s->particles_enabled && !(s->edit && layer==0))return;
    int screen[480];
    for(int i=0;i<480;++i)screen[i]=-1;
    for(int y=CVIII_LIGHT_HUD;y<240;++y)
        if(sy[y]>=0 && sy[y]<480)screen[sy[y]]=y;
    float seconds=(float)((frame%216000u)/60.0);
    /* Weather is globally linked, but sampled in fixed WORLD tiles.
     * The four nearest 128px X-chunks x two vertical pages cover the
     * camera without regenerating weather at each scroll pixel. */
    CviiiParticleEmitter weather_tiles[8]={0};
    int weather_profile=cviii_weather_scene_profile(s,room);
    if(weather_profile>=0 && s->particles_enabled){
        const CviiiWeatherProfile *w=&s->weather[weather_profile];
        int activity=cviii_weather_intensity(w,room,frame);
        int cameraChunk=camera>=0?camera/128:0;
        for(int i=0;i<8;++i){
            int chunk=cameraChunk+(i%4)-1;
            int page=i/4;
            int x=chunk*128;
            if(activity<=0 || x<0 || x>65535-128)continue;
            int density=w->density/4;
            if(density<1)density=1;
            weather_tiles[i]=(CviiiParticleEmitter){
                .room=room,.used=1,.kind=w->kind,.x=x,.y=page*240,
                .w=128,.h=239,.density=density,.speed=w->speed,
                .wind=w->wind,.opacity=w->opacity*activity/100,
                .size=w->size,.red=w->red,.green=w->green,.blue=w->blue,
                .layer=w->layer
            };
        }
    }
    for(int slot=0;slot<CVIII_PARTICLE_EMITTER_MAX+8;++slot){
        CviiiParticleEmitter world;
        const CviiiParticleEmitter *src=slot<CVIII_PARTICLE_EMITTER_MAX?
            &s->particles[slot]:&weather_tiles[slot-CVIII_PARTICLE_EMITTER_MAX];
        if(!src->used || src->room!=room || !s->particles_enabled ||
           src->opacity<=0 || !valid(src) || !cviii_particle_world_region(s,src,&world))
            continue;
        const CviiiParticleEmitter *e=&world;
        if(e->layer!=layer && !(layer==0 && e->layer==1 && !sprite_mask))
            continue;
        const float time=seconds*((float)e->speed/100.f);
        for(int i=0;i<e->density;++i){
            unsigned worldTile=slot>=CVIII_PARTICLE_EMITTER_MAX?
                (unsigned)(world.x/128)*0x1278c5d7u+
                (unsigned)(world.y/240)*0x53f112a1u+
                (unsigned)s->weather[weather_profile].seed:0u;
            unsigned id=((unsigned)(slot<CVIII_PARTICLE_EMITTER_MAX?slot+1:37)
                 *0x9e3779b9u)^((unsigned)i*0x45d9f3bu)^worldTile;
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
                        if(((rx+ry+(int)(time*2.f))&3)==0)continue;
                        put(pixels,shifted+rx-ww/2,row,e,opacity/2,layer,sprite_mask);
                    }
                }
            }else if(e->kind==CVIII_FX_RAIN){
                for(int r=0;r<e->size+2;++r){
                    int worldY=wy+r;
                    if(worldY<0 || worldY>=480 || screen[worldY]<48)continue;
                    int row=screen[worldY];
                    put(pixels,xx-unwrap(sx[row],camera)-r/2,row,e,opacity,layer,sprite_mask);
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
                        put(pixels,at+dx,row,e,opacity,layer,sprite_mask);
                }
            }
        }
    }
    if(s->edit && layer==0){
        /* Sharp 1px world-space region outlines are EDITOR-ONLY.
         * Scanline PPU scroll keeps them attached to stage geometry. */
        for(int slot=0;slot<CVIII_PARTICLE_EMITTER_MAX;++slot){
            CviiiParticleEmitter local;
            if(!cviii_particle_world_region(s,&s->particles[slot],&local) ||
               local.room!=room)continue;
            const CviiiParticleEmitter *e=&local;
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

int cviii_particle_glow_samples(const CviiiLighting *s,uint32_t room,
    int camera,const int sx[CVIII_LIGHT_H],const int sy[CVIII_LIGHT_H],
    uint64_t frame,CviiiParticleGlow out[4]){
    if(!s || !out || !sx || !sy || !s->particles_enabled)return 0;
    int count=0;
    float seconds=(float)((frame%216000u)/60.0);
    for(int slot=0;slot<CVIII_PARTICLE_EMITTER_MAX && count<4;++slot){
        CviiiParticleEmitter world;
        const CviiiParticleEmitter *src=&s->particles[slot];
        if(!src->used || src->room!=room || src->glow<=0 ||
           (src->kind!=CVIII_FX_EMBERS && src->kind!=CVIII_FX_FIREFLIES) ||
           !cviii_particle_world_region(s,src,&world))continue;
        for(int i=0;i<world.density && i<3 && count<4;++i){
            unsigned id=(unsigned)(slot+1)*0x9e3779b9u ^
                         (unsigned)i*0x45d9f3bu;
            float fx=hash01(id+1u),fy=hash01(id+17u),phase=hash01(id+91u);
            float time=seconds*((float)world.speed/100.f);
            float wind=(float)world.wind/100.f*time*7.f;
            float wobble=sinf(time*(.7f+phase)+phase*6.28318f)*1.3f;
            float x,y;
            if(world.kind==CVIII_FX_EMBERS){
                x=world.x+wrapf(fx*world.w+wind+wobble,world.w);
                y=world.y+wrapf(fy*world.h-time*(11.f+phase*10.f),world.h);
            }else{
                x=world.x+wrapf(fx*world.w+wind+wobble*5.f,world.w);
                y=world.y+wrapf(fy*world.h+
                         sinf(time*.5f+phase*10.f)*5.f,world.h);
            }
            int py=(int)floorf(y);
            if(py<0 || py>=480)continue;
            int inview=0;
            for(int row=CVIII_LIGHT_HUD;row<240;++row){
                if(sy[row]!=(int)floorf(y))continue;
                int vx=(int)floorf(x)-unwrap(sx[row],camera);
                if(vx>=-32 && vx<288)inview=1;
                break;
            }
            if(!inview)continue;
            CviiiParticleGlow *g=&out[count++];
            g->x=x;g->y=y;
            g->radius=8.f+world.glow*.27f;
            g->power=8.f+world.glow*.38f;
            g->red=world.red;g->green=world.green;g->blue=world.blue;
        }
    }
    return count;
}
/* Legacy test/editor caller renders both layers without sprite depth. */
void cviii_particle_present(const CviiiLighting *s,
    uint32_t pixels[CVIII_LIGHT_W*CVIII_LIGHT_H],uint32_t room,int camera,
    const int sx[CVIII_LIGHT_H],const int sy[CVIII_LIGHT_H],uint64_t frame){
    cviii_particle_present_layer(s,pixels,room,camera,sx,sy,frame,0,NULL);
}
