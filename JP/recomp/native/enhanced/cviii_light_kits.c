/* Host-only reusable light kits (C11).
 * A kit is a set of relative-position emitters, not a screen-fixed overlay.
 * All placement is atomic and assigns the target room to every new light.
 */
#include "cviii_lighting.h"
#include <string.h>
#include <stdlib.h>

static int safe_name(char *dst,int cap,const char *src){
    if(!src)return 0;
    size_t len=strlen(src);
    if(!len || len>=(size_t)cap)return 0;
    for(size_t i=0;i<len;++i)
        if((unsigned char)src[i]<32 || (unsigned char)src[i]==127)return 0;
    memcpy(dst,src,len+1);
    return 1;
}
typedef struct {const char *title;int count;CviiiLight light[3];} Builtin;
/* Window: warm-edged upper shaft + cool reflected wide fill, a useful
 * art-directed 2D combination without pretending there are occluders. */
static const Builtin builtins[]={
    {"Candle",1,{{.x=0,.y=0,.radius=45,.energy=68,.red=255,.green=178,.blue=91,.used=1,.flicker=0,.name="Candle Flame",.group="Candle"}}},
    {"Torch",2,{
        {.x=0,.y=0,.radius=76,.energy=120,.red=255,.green=142,.blue=57,.used=1,.flicker=2,.name="Torch Core",.group="Torch"},
        {.x=6,.y=-8,.radius=112,.energy=38,.red=255,.green=111,.blue=44,.used=1,.flicker=0,.name="Torch Spill",.group="Torch"}}},
    {"Lantern",2,{
        {.x=0,.y=0,.radius=66,.energy=78,.red=255,.green=198,.blue=121,.used=1,.flicker=1,.name="Lantern Glass",.group="Lantern"},
        {.x=0,.y=10,.radius=28,.energy=25,.red=255,.green=226,.blue=166,.used=1,.flicker=1,.name="Lantern Bounce",.group="Lantern"}}},
    {"Window",2,{
        {.x=0,.y=0,.radius=154,.energy=116,.red=198,.green=218,.blue=255,.used=1,.shape=CVIII_SHAPE_SHAFT,.angle=115,.width=62,.flicker=1,.name="Window Shaft",.group="Window"},
        {.x=6,.y=15,.radius=80,.energy=36,.red=175,.green=199,.blue=249,.used=1,.flicker=1,.name="Window Bounce",.group="Window"}}},
    {"Moonlight",2,{
        {.x=0,.y=0,.radius=160,.energy=82,.red=132,.green=172,.blue=255,.used=1,.shape=CVIII_SHAPE_SHAFT,.angle=105,.width=54,.flicker=1,.name="Moonbeam",.group="Moonlight"},
        {.x=8,.y=24,.radius=102,.energy=24,.red=142,.green=181,.blue=255,.used=1,.flicker=1,.name="Moon Bounce",.group="Moonlight"}}},
    {"Sunbeam",2,{
        {.x=0,.y=0,.radius=160,.energy=113,.red=255,.green=229,.blue=174,.used=1,.shape=CVIII_SHAPE_CONE,.angle=74,.spread=19,.flicker=1,.name="Sun Shaft",.group="Sunbeam"},
        {.x=10,.y=35,.radius=110,.energy=43,.red=255,.green=215,.blue=152,.used=1,.flicker=1,.name="Sun Bounce",.group="Sunbeam"}}},
    {"Magic",2,{
        {.x=0,.y=0,.radius=64,.energy=106,.red=147,.green=103,.blue=255,.used=1,.flicker=1,.name="Arcane Core",.group="Magic"},
        {.x=0,.y=0,.radius=108,.energy=31,.red=113,.green=78,.blue=240,.used=1,.flicker=0,.name="Arcane Halo",.group="Magic"}}}
};
int cviii_light_builtin_count(void){return (int)(sizeof builtins/sizeof builtins[0]);}
const char *cviii_light_builtin_name(int id){
    return id>=0 && id<cviii_light_builtin_count()?builtins[id].title:NULL;
}
static int place_parts(CviiiLighting *s,const CviiiLight *parts,int count,
                       uint32_t room,int x,int y){
    if(!s || !parts || count<1 || count>CVIII_KIT_PARTS)return -1;
    int free_slots[CVIII_KIT_PARTS],found=0;
    for(int i=0;i<CVIII_LIGHT_MAX && found<count;++i)
        if(!s->light[i].used)free_slots[found++]=i;
    if(found!=count)return -1;
    for(int i=0;i<count;++i){
        long nx=(long)x+parts[i].x,ny=(long)y+parts[i].y;
        if(nx<0 || nx>65535 || ny<0 || ny>479)return -1;
        if(parts[i].radius<12 || parts[i].radius>160 ||
           parts[i].energy<5 || parts[i].energy>160 ||
           parts[i].shape<0 || parts[i].shape>2)return -1;
    }
    for(int i=0;i<count;++i){
        int slot=free_slots[i];
        s->light[slot]=parts[i];
        s->light[slot].x=x+parts[i].x;
        s->light[slot].y=y+parts[i].y;
        s->light[slot].room=room;
        s->light[slot].used=1;
    }
    s->selected=free_slots[0];
    s->enabled=1;
    s->dragging=0;
    return free_slots[0];
}
int cviii_light_apply_builtin(CviiiLighting *s,int id,uint32_t room,int x,int y){
    if(id<0 || id>=cviii_light_builtin_count())return -1;
    return place_parts(s,builtins[id].light,builtins[id].count,room,x,y);
}
int cviii_light_kit_capture(CviiiLighting *s,int slot,int selected,const char *name){
    if(!s || slot<0 || slot>=CVIII_KIT_MAX ||
       selected<0 || selected>=CVIII_LIGHT_MAX ||
       !s->light[selected].used)return 0;
    CviiiLightKit kit={0};
    if(!safe_name(kit.name,CVIII_LIGHT_NAME_CAP,name))return 0;
    const CviiiLight *anchor=&s->light[selected];
    for(int i=0;i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *l=&s->light[i];
        if(!l->used || l->room!=anchor->room)continue;
        if(anchor->group[0]){
            if(strcmp(l->group,anchor->group))continue;
        }else if(i!=selected)continue;
        if(kit.count==CVIII_KIT_PARTS)return 0;
        CviiiLight *part=&kit.part[kit.count++];
        *part=*l;
        part->x=l->x-anchor->x;
        part->y=l->y-anchor->y;
        part->room=0;
    }
    if(!kit.count)return 0;
    kit.used=1;
    s->kits[slot]=kit;
    return 1;
}
int cviii_light_kit_apply(CviiiLighting *s,int slot,uint32_t room,int x,int y){
    if(!s || slot<0 || slot>=CVIII_KIT_MAX || !s->kits[slot].used)return -1;
    return place_parts(s,s->kits[slot].part,s->kits[slot].count,room,x,y);
}
int cviii_light_kit_rename(CviiiLighting *s,int slot,const char *name){
    if(!s || slot<0 || slot>=CVIII_KIT_MAX || !s->kits[slot].used)return 0;
    return safe_name(s->kits[slot].name,CVIII_LIGHT_NAME_CAP,name);
}
int cviii_light_kit_clone(CviiiLighting *s,int from,int to){
    if(!s || from<0 || from>=CVIII_KIT_MAX ||
       to<0 || to>=CVIII_KIT_MAX || from==to ||
       !s->kits[from].used)return 0;
    s->kits[to]=s->kits[from];
    return 1;
}
int cviii_light_kit_delete(CviiiLighting *s,int slot){
    if(!s || slot<0 || slot>=CVIII_KIT_MAX || !s->kits[slot].used)return 0;
    memset(&s->kits[slot],0,sizeof s->kits[slot]);
    return 1;
}

/* Scene sky is a separate, additive high/low gradient. Old scene ambient
 * presets continue to work without a Sky record. */
void cviii_light_sky_get(const CviiiLighting *s,uint32_t room,
                         int *strength,int rgb[3],int *facing){
    if(strength)*strength=0;
    if(facing)*facing=-1;
    if(rgb){rgb[0]=186;rgb[1]=209;rgb[2]=255;}
    if(!s)return;
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient *a=&s->scenes[i];
        if(!a->used || a->room!=room)continue;
        if(strength)*strength=a->sky;
        if(rgb){rgb[0]=a->sky_red;rgb[1]=a->sky_green;rgb[2]=a->sky_blue;}
        if(facing)*facing=a->sky_facing;
        return;
    }
}
int cviii_light_sky_set(CviiiLighting *s,uint32_t room,int strength,
                         int red,int green,int blue,int facing){
    if(!s || strength<0 || strength>100 || red<0 || red>255 ||
       green<0 || green>255 || blue<0 || blue>255 ||
       facing< -1 || facing>1)return 0;
    int level=s->ambient,rgb[3];
    cviii_light_scene_get(s,room,&level,rgb);
    if(!cviii_light_scene_set(s,room,level,rgb[0],rgb[1],rgb[2]))return 0;
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        CviiiSceneAmbient *a=&s->scenes[i];
        if(!a->used || a->room!=room)continue;
        a->sky=strength;a->sky_red=red;a->sky_green=green;
        a->sky_blue=blue;a->sky_facing=facing;
        return 1;
    }
    return 0;
}
/* Config entries: KitXX = count,hex(name), PartXX_0 = pack + 2 hex labels.
 * Labels use hex for comma/newline safety and are validated on import. */
static const char hexdigits[]="0123456789ABCDEF";
static void hex_write(FILE *f,const char *text){
    for(const unsigned char *p=(const unsigned char*)text;*p;++p){
        fputc(hexdigits[*p>>4],f);
        fputc(hexdigits[*p&15],f);
    }
}
static int nibble(char c){
    if(c>='0' && c<='9')return c-'0';
    if(c>='a' && c<='f')return c-'a'+10;
    if(c>='A' && c<='F')return c-'A'+10;
    return -1;
}
static int hex_read(char *dst,size_t cap,const char *hex){
    size_t size=strlen(hex);
    if(size&1 || size/2>=cap)return 0;
    char tmp[CVIII_LIGHT_NAME_CAP];
    if(cap>sizeof tmp)return 0;
    for(size_t i=0;i<size;i+=2){
        int a=nibble(hex[i]),b=nibble(hex[i+1]);
        if(a<0 || b<0)return 0;
        unsigned byte=(unsigned)(a*16+b);
        if(byte<32 || byte==127)return 0;
        tmp[i/2]=(char)byte;
    }
    tmp[size/2]=0;
    memcpy(dst,tmp,size/2+1);
    return 1;
}
void cviii_light_kit_save(const CviiiLighting *s,FILE *f){
    if(!s || !f)return;
    for(int k=0;k<CVIII_KIT_MAX;++k){
        const CviiiLightKit *kit=&s->kits[k];
        if(!kit->used)continue;
        fprintf(f,"LightKit%02d = %d,",k,kit->count);
        hex_write(f,kit->name);fputc('\n',f);
        for(int i=0;i<kit->count;++i){
            const CviiiLight *l=&kit->part[i];
            fprintf(f,"LightKitPart%02d_%d = %d,%d,%d,%d,%u,%u,%u,%d,%d,%d,%d,%d,%d,",
                k,i,l->x,l->y,l->radius,l->energy,l->red,l->green,l->blue,
                l->shape,l->angle,l->spread,l->width,l->muted,l->flicker);
            if(!l->name[0])fputc('-',f);else hex_write(f,l->name);
            fputc(',',f);
            if(!l->group[0])fputc('-',f);else hex_write(f,l->group);
            fputc('\n',f);
        }
    }
}
int cviii_light_kit_load(CviiiLighting *s,const char *key,const char *value){
    if(!s || !key || !value)return 0;
    unsigned kit=0,part=0;int n=0;char tail;
    if(sscanf(key,"LightKitPart%2u_%1u%c",&kit,&part,&tail)==2 &&
       kit<CVIII_KIT_MAX && part<CVIII_KIT_PARTS){
        CviiiLight v={0};
        unsigned r,g,b;
        char label[CVIII_LIGHT_NAME_CAP*2+2]={0};
        char group[CVIII_LIGHT_GROUP_CAP*2+2]={0};
        int fields=sscanf(value,"%d,%d,%d,%d,%u,%u,%u,%d,%d,%d,%d,%d,%d,%95[^,],%65s%n",
          &v.x,&v.y,&v.radius,&v.energy,&r,&g,&b,
          &v.shape,&v.angle,&v.spread,&v.width,&v.muted,&v.flicker,
          label,group,&n);
        if(fields!=15 || value[n] || r>255 || g>255 || b>255 ||
           v.radius<12 || v.radius>160 || v.energy<5 || v.energy>160 ||
           v.shape<0 || v.shape>2 || v.angle<0 || v.angle>359 ||
           v.spread<0 || v.spread>85 || v.width<0 || v.width>160 ||
           v.muted<0 || v.muted>1 || v.flicker<0 || v.flicker>2 ||
           v.x< -65535 || v.x>65535 || v.y< -479 || v.y>479 ||
           (strcmp(label,"-") && !hex_read(v.name,sizeof v.name,label)) ||
           (strcmp(group,"-") && !hex_read(v.group,sizeof v.group,group)))return 0;
        v.red=(uint8_t)r;v.green=(uint8_t)g;v.blue=(uint8_t)b;v.used=1;
        s->kits[kit].part[part]=v;
        return 1;
    }
    if(sscanf(key,"LightKit%2u%c",&kit,&tail)!=1 || kit>=CVIII_KIT_MAX)return 0;
    int count=0; char label[CVIII_LIGHT_NAME_CAP*2+2]={0};
    if(sscanf(value,"%d,%95s%n",&count,label,&n)!=2 || value[n] ||
       count<1 || count>CVIII_KIT_PARTS)return 0;
    char name[CVIII_LIGHT_NAME_CAP];
    if(!hex_read(name,sizeof name,label) || !name[0])return 0;
    s->kits[kit].used=1;s->kits[kit].count=count;
    memcpy(s->kits[kit].name,name,strlen(name)+1);
    return 1;
}
