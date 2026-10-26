/* CVIII host-only lighting authoring model: names, groups, clipboard, ambient.
 * C11, deterministic, no SDL, ROM or host-emulated-state dependency.
 */
#include "cviii_lighting.h"
#include <string.h>

static int bounded(int v,int lo,int hi){return v<lo?lo:v>hi?hi:v;}
static int slot_ok(const CviiiLighting *s,int i){
    return s && i>=0 && i<CVIII_LIGHT_MAX && s->light[i].used;
}
static int vacant(const CviiiLighting *s){
    for(int i=0;i<CVIII_LIGHT_MAX;++i)if(!s->light[i].used)return i;
    return -1;
}
static int safe_label(char *to,int cap,const char *from){
    if(!to || !from)return 0;
    size_t len=strlen(from);
    if(len>=(size_t)cap)return 0;
    for(size_t i=0;i<len;++i)
        if((unsigned char)from[i]<32u || (unsigned char)from[i]==127u)return 0;
    memcpy(to,from,len+1);
    return 1;
}
int cviii_light_copy(CviiiLighting *s,int i){
    if(!slot_ok(s,i))return 0;
    s->clipboard=s->light[i];
    s->clipboard_valid=1;
    return 1;
}
int cviii_light_paste(CviiiLighting *s,uint32_t room,int x,int y){
    if(!s || !s->clipboard_valid || x<0 || x>65535 || y<0 || y>479)return -1;
    int i=vacant(s);
    if(i<0)return -1;
    s->light[i]=s->clipboard;
    s->light[i].room=room;
    s->light[i].x=x;
    s->light[i].y=y;
    s->light[i].used=1;
    s->selected=i;
    return i;
}
int cviii_light_duplicate(CviiiLighting *s,int i){
    if(!slot_ok(s,i))return -1;
    CviiiLight original=s->light[i];
    int j=vacant(s);
    if(j<0)return -1;
    s->light[j]=original;
    s->light[j].x=bounded(original.x+12,0,65535);
    s->light[j].y=bounded(original.y+8,0,479);
    s->selected=j;
    return j;
}
int cviii_light_rename(CviiiLighting *s,int i,const char *name){
    return slot_ok(s,i) && safe_label(s->light[i].name,CVIII_LIGHT_NAME_CAP,name);
}
int cviii_light_group(CviiiLighting *s,int i,const char *name){
    return slot_ok(s,i) && safe_label(s->light[i].group,CVIII_LIGHT_GROUP_CAP,name);
}
int cviii_light_shape(CviiiLighting *s,int i,int shape){
    if(!slot_ok(s,i) || shape<CVIII_SHAPE_RADIAL || shape>CVIII_SHAPE_SHAFT)return 0;
    s->light[i].shape=shape;
    if(!s->light[i].spread)s->light[i].spread=30;
    if(!s->light[i].width)s->light[i].width=32;
    return 1;
}
void cviii_light_scene_get(const CviiiLighting *s,uint32_t room,int *level,int rgb[3]){
    if(!s)return;
    if(level)*level=s->ambient;
    if(rgb){rgb[0]=255;rgb[1]=255;rgb[2]=255;}
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        const CviiiSceneAmbient *a=&s->scenes[i];
        if(!a->used || a->room!=room)continue;
        if(level)*level=a->level;
        if(rgb){rgb[0]=a->red;rgb[1]=a->green;rgb[2]=a->blue;}
        return;
    }
}
int cviii_light_scene_set(CviiiLighting *s,uint32_t room,int level,int red,int green,int blue){
    if(!s)return 0;
    if(level<0 || level>100 || red<0 || red>255 || green<0 || green>255 ||
       blue<0 || blue>255)return 0;
    int index=-1;
    for(int i=0;i<CVIII_SCENE_AMBIENT_MAX;++i){
        if(s->scenes[i].used && s->scenes[i].room==room){index=i;break;}
        if(index<0 && !s->scenes[i].used)index=i;
    }
    if(index<0)return 0;
    /* Keep independent sky fill when editing neutral ambient intensity.
     * Restoring only the first fields here silently wiped sky light. */
    CviiiSceneAmbient *a=&s->scenes[index];
    a->room=room;a->level=level;a->red=red;a->green=green;
    a->blue=blue;a->used=1;
    return 1;
}
