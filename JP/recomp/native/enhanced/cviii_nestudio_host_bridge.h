/* NEStudio IPC bridge, compiled only into owner-private Windows SDL host.
 * Strict single-producer editor / single-consumer game. No guest CPU state,
 * no ROM access, no DLL injection and no remote process memory editing.
 * Layout is intentionally fixed for .NET MemoryMappedViewAccessor.
 */
#ifndef CVIII_NESTUDIO_HOST_BRIDGE_H
#define CVIII_NESTUDIO_HOST_BRIDGE_H
#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include "cviii_lighting_host.h"
#define NEST_MAGIC 0x5453454eL /* little-endian "NEST" */
#define NEST_VERSION 1
#define NEST_MAX_LIGHTS 128
typedef struct {
    LONG used,room,x,y,radius,energy,red,green,blue,shape,muted,flicker;
    char name[32];
} NestStudioLight; /* exactly 80 bytes */
typedef struct {LONG used,slot,x,y,tile,attributes;} NestStudioSprite; /* 24 bytes */
extern int cviii_nestudio_copy_oam(uint8_t out[256]);
typedef struct {
    volatile LONG magic,version,request,response;
    volatile LONG op,a,b,c,result;
    volatile LONG revision,room,selected,editing,renderer,count,camera,frame,enabled;
    volatile LONG reserved[14]; /* 128 byte header */
    NestStudioLight lights[NEST_MAX_LIGHTS];
    NestStudioSprite sprites[64];
} NestStudioMapping;
typedef char nest_layout_1[(sizeof(NestStudioLight)==80)?1:-1];
typedef char nest_layout_2[(offsetof(NestStudioMapping,lights)==128)?1:-1];
typedef char nest_layout_3[(sizeof(NestStudioSprite)==24)?1:-1];
typedef char nest_layout_4[(offsetof(NestStudioMapping,sprites)==10368)?1:-1];
static HANDLE nest_mapping_handle;
static NestStudioMapping *nest_shared;
static int nest_checked;
static void nest_init(void){
    if(nest_checked)return;
    nest_checked=1;
    char session[72]={0},name[96]={0};
    DWORD len=GetEnvironmentVariableA("CVIII_NESTUDIO_SESSION",
                                      session,sizeof session);
    if(len<8 || len>=sizeof session)return;
    for(DWORD i=0;i<len;++i){
        char c=session[i];
        if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||
             (c>='0'&&c<='9')||c=='-'))return;
    }
    (void)snprintf(name,sizeof name,"Local\\NEStudio-%s",session);
    nest_mapping_handle=CreateFileMappingA(INVALID_HANDLE_VALUE,NULL,
         PAGE_READWRITE,0,(DWORD)sizeof(NestStudioMapping),name);
    if(!nest_mapping_handle)return;
    nest_shared=(NestStudioMapping*)MapViewOfFile(nest_mapping_handle,
        FILE_MAP_ALL_ACCESS,0,0,sizeof(NestStudioMapping));
    if(!nest_shared){
        CloseHandle(nest_mapping_handle);nest_mapping_handle=NULL;return;
    }
    nest_shared->version=NEST_VERSION;
    /* The batch/cmd launcher is not the game process. Publish the
     * owner-local native PID in unused v1 header space so the editor can
     * find the real SDL window even if cmd.exe has already exited. */
    nest_shared->reserved[0]=(LONG)GetCurrentProcessId();
    InterlockedExchange(&nest_shared->magic,NEST_MAGIC);
}
static void nest_close(void){
    if(nest_shared){
        InterlockedExchange(&nest_shared->magic,0);
        UnmapViewOfFile(nest_shared);
        nest_shared=NULL;
    }
    if(nest_mapping_handle){
        CloseHandle(nest_mapping_handle);nest_mapping_handle=NULL;
    }
}
static void nest_tick(void){
    nest_init();
    if(!nest_shared)return;
    LONG request=InterlockedCompareExchange(&nest_shared->request,0,0);
    LONG response=InterlockedCompareExchange(&nest_shared->response,0,0);
    if(request!=response){
        LONG op=nest_shared->op,a=nest_shared->a,b=nest_shared->b;
        LONG c=nest_shared->c;
        int done=0,save=0;
        switch(op){
            case 1: done=cviii_lighting_editor_external_session(1);break;
            case 2: done=cviii_lighting_editor_external_session(0);break;
            case 3: done=cviii_lighting_editor_select((int)a);break;
            case 4: done=cviii_lighting_editor_property((int)a,(int)b);
                    save=done;break;
            case 5: done=cviii_lighting_editor_add((int)a,(int)b);save=done;break;
            case 6: done=cviii_lighting_editor_duplicate();save=done;break;
            case 7: done=cviii_lighting_editor_input(5,-1,-1);save=done;break;
            case 8: done=cviii_lighting_editor_undo();save=done;break;
            case 9: done=cviii_lighting_editor_redo();save=done;break;
            case 10: done=cviii_lighting_editor_set_renderer((int)a);
                     save=done;break;
            case 11: done=cviii_lighting_editor_set_cascade_quality((int)a);
                     save=done;break;
            case 12: done=cviii_lighting_editor_particle_add((int)a,(int)b,(int)c)>=0;
                     save=done;break;
            case 13: done=cviii_lighting_editor_apply_builtin((int)a,(int)b,(int)c);
                     save=done;break;
            case 14: done=1;save=1;break;
            case 15: done=cviii_lighting_editor_checkpoint();break;
            default: done=0;break;
        }
        if(save)save_settings();
        nest_shared->result=done?1:0;
        InterlockedExchange(&nest_shared->response,request);
    }
    const CviiiLighting *model=cviii_lighting_editor_model();
    if(!model)return;
    InterlockedIncrement(&nest_shared->revision); /* odd: writer owns */
    MemoryBarrier();
    nest_shared->room=(LONG)cviii_lighting_editor_room();
    nest_shared->selected=(LONG)model->selected;
    nest_shared->editing=cviii_lighting_editor_active()?1:0;
    nest_shared->renderer=cviii_lighting_editor_renderer();
    nest_shared->frame++;
    nest_shared->enabled=model->enabled;
    LONG count=0;
    for(int i=0;i<NEST_MAX_LIGHTS && i<CVIII_LIGHT_MAX;++i){
        const CviiiLight *l=&model->light[i];
        NestStudioLight *out=&nest_shared->lights[i];
        out->used=l->used;out->room=(LONG)l->room;
        out->x=l->x;out->y=l->y;out->radius=l->radius;
        out->energy=l->energy;out->red=l->red;
        out->green=l->green;out->blue=l->blue;
        out->shape=l->shape;out->muted=l->muted;
        out->flicker=l->flicker;
        memset(out->name,0,sizeof out->name);
        memcpy(out->name,l->name,
            sizeof out->name-1<sizeof l->name?
                sizeof out->name-1:sizeof l->name);
        if(l->used && l->room==(uint32_t)nest_shared->room)++count;
    }
    nest_shared->count=count;
    uint8_t oam[256];
    if(cviii_nestudio_copy_oam(oam)){
        for(int slot=0;slot<64;++slot){
            NestStudioSprite *p=&nest_shared->sprites[slot];
            int at=slot*4;
            p->used=oam[at]<239?1:0;
            p->slot=slot;p->y=oam[at];p->tile=oam[at+1];
            p->attributes=oam[at+2];p->x=oam[at+3];
        }
    }else memset(nest_shared->sprites,0,sizeof nest_shared->sprites);
    MemoryBarrier();
    InterlockedIncrement(&nest_shared->revision); /* even: stable snapshot */
}
#endif /* _WIN32 */
#endif
