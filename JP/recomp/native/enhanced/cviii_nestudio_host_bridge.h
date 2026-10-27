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
#define NEST_VERSION 3
#define NEST_MAX_LIGHTS 128
typedef struct {
    LONG used,room,x,y,radius,energy,red,green,blue,shape,muted,flicker;
    char name[32];
} NestStudioLight; /* exactly 80 bytes */
typedef struct {LONG used,slot,x,y,tile,attributes;} NestStudioSprite; /* 24 bytes */
/* Original 28-entry CPU object-table lifetime, never raw OAM identity. */
typedef struct {
    LONG active,slot,generation,room,x,y,frame,selector,mirror,flags,script;
} NestStudioOriginalObject; /* 44 bytes */
/* Reserved ABI for future bank+PC authenticated original dialogue events.
 * sequence == 0 until a validated original interpreter hook exists.
 * Authored viewport annotations MUST NOT feed this structure. */
typedef struct {
    volatile LONG sequence;
    LONG bank,cpu_pc,script_id,event_id,room,frame,kind;
} NestStudioOriginalDialogueEvent; /* 32 bytes */
extern int cviii_nestudio_copy_oam(uint8_t out[256]);
extern int cviii_nestudio_copy_original_objects(uint8_t out[8][28],uint8_t *phase);
extern int cviii_nestudio_copy_original_ownership(uint8_t owners[64],
    unsigned *attributed,unsigned *observed,unsigned *invalid);
extern int cviii_nestudio_ppu_source(unsigned *pc,unsigned *address,
                                   unsigned *tile,unsigned *writes);
typedef struct {
    volatile LONG magic,version,request,response;
    volatile LONG op,a,b,c,result;
    volatile LONG revision,room,selected,editing,renderer,count,camera,frame,enabled;
    volatile LONG reserved[14]; /* 128 byte header */
    NestStudioLight lights[NEST_MAX_LIGHTS];
    NestStudioSprite sprites[64];
    /* Version 2 tail; version 1 field offsets remain byte-for-byte intact. */
    volatile LONG oam_phase,original_object_count;
    NestStudioOriginalObject original_objects[28];
    NestStudioOriginalDialogueEvent original_dialogue;
    /* v3: owner assigned only by original PRG26:$8070 source reads. */
    volatile LONG owner_for_oam[64];
    volatile LONG ownership_valid,ownership_count,ownership_calls,ownership_errors;
    volatile LONG selected_original_mask;
    /* Original PPU $2007 write telemetry; NOT dialogue-printer events. */
    volatile LONG ppu_source_pc,ppu_source_addr,ppu_source_tile,ppu_write_count;
} NestStudioMapping;
typedef char nest_layout_1[(sizeof(NestStudioLight)==80)?1:-1];
typedef char nest_layout_2[(offsetof(NestStudioMapping,lights)==128)?1:-1];
typedef char nest_layout_3[(sizeof(NestStudioSprite)==24)?1:-1];
typedef char nest_layout_4[(offsetof(NestStudioMapping,sprites)==10368)?1:-1];
typedef char nest_layout_5[(sizeof(NestStudioOriginalObject)==44)?1:-1];
typedef char nest_layout_6[(offsetof(NestStudioMapping,oam_phase)==11904)?1:-1];
typedef char nest_layout_7[(offsetof(NestStudioMapping,original_objects)==11912)?1:-1];
typedef char nest_layout_8[(offsetof(NestStudioMapping,original_dialogue)==13144)?1:-1];
typedef char nest_layout_9[(offsetof(NestStudioMapping,owner_for_oam)==13176)?1:-1];
typedef char nest_layout_10[(offsetof(NestStudioMapping,selected_original_mask)==13448)?1:-1];
typedef char nest_layout_11[(sizeof(NestStudioMapping)==13468)?1:-1];
static LONG nest_object_generation[28];
static uint8_t nest_object_was_active[28];
static uint32_t nest_object_room=UINT32_MAX;
static HANDLE nest_mapping_handle;
static NestStudioMapping *nest_shared;
static int nest_checked;
/* Reserved v1 header slots 1 and 2 belong to the editor's transient
 * keyboard capture. Nothing touches emulated NES controller or CPU RAM. */
static unsigned nest_keyboard_bits(void)
{
    if(!nest_shared || !nest_shared->magic)return 0;
    if(!InterlockedCompareExchange(&nest_shared->reserved[2],0,0))return 0;
    return (unsigned)InterlockedCompareExchange(&nest_shared->reserved[1],0,0)&255u;
}
static int nest_keyboard_owned(void)
{
    return nest_shared && nest_shared->magic==NEST_MAGIC &&
        InterlockedCompareExchange(&nest_shared->reserved[2],0,0)!=0;
}
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
            /* Bring back the original full ImGui Lighting Studio. The
             * game's native SDL renderer retains every existing feature. */
            case 16:
                (void)cviii_lighting_editor_external_session(0);
                done=cviii_lighting_editor_input(1,-1,-1);
                break;
            /* Resume NEStudio's compact external inspector. */
            case 17: done=cviii_lighting_editor_external_session(1);break;
            /* Workbench input mode: 0 lighting, 1 snapshot OAM sprites,
             * 2 authored dialogue anchors. Close any native light modal. */
            case 18:
                if(a<0 || a>2){done=0;break;}
                nest_shared->reserved[3]=a;
                nest_shared->reserved[4]=0;
                nest_shared->reserved[5]=0;
                nest_shared->reserved[6]=0;
                nest_shared->reserved[7]=0;
                nest_shared->reserved[8]=0;
                nest_shared->reserved[13]=0;
                if(a!=0)(void)cviii_lighting_editor_external_session(0);
                done=1;
                break;
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
    /* Authenticated original PRG26 object-table positions and selector.
     * Generation is host-only, advancing on room change or inactive->active.
     * A slot reused without an observed inactive frame stays ambiguous. */
    uint8_t tables[8][28],phase=0;
    if(cviii_nestudio_copy_original_objects(tables,&phase)){
        const uint32_t room=(uint32_t)nest_shared->room;
        int room_changed=(room!=nest_object_room);
        if(room_changed)nest_object_room=room;
        nest_shared->oam_phase=(LONG)phase;
        LONG active_count=0;
        for(int i=0;i<28;++i){
            NestStudioOriginalObject *obj=&nest_shared->original_objects[i];
            int active=tables[0][i]!=0 && (tables[4][i]&0x80u)==0;
            if(active && (!nest_object_was_active[i] || room_changed)){
                if(++nest_object_generation[i]<=0)nest_object_generation[i]=1;
            }
            nest_object_was_active[i]=(uint8_t)active;
            obj->active=active;obj->slot=i;
            obj->generation=nest_object_generation[i];
            obj->room=(LONG)room;obj->x=tables[2][i];
            obj->y=tables[1][i];obj->frame=tables[0][i];
            obj->selector=tables[5][i];obj->mirror=tables[6][i];
            obj->flags=tables[4][i];obj->script=tables[7][i];
            active_count+=active;
        }
        nest_shared->original_object_count=active_count;
    }else{
        nest_shared->oam_phase=-1;
        nest_shared->original_object_count=0;
        memset(nest_shared->original_objects,0,
               sizeof nest_shared->original_objects);
        memset(nest_object_was_active,0,sizeof nest_object_was_active);
    }
    uint8_t owners[64];
    unsigned owned=0,calls=0,errors=0;
    int ok=cviii_nestudio_copy_original_ownership(owners,&owned,&calls,&errors);
    nest_shared->ownership_valid=ok?1:0;
    nest_shared->ownership_count=(LONG)owned;
    nest_shared->ownership_calls=(LONG)calls;
    nest_shared->ownership_errors=(LONG)errors;
    for(int i=0;i<64;++i){
        nest_shared->owner_for_oam[i]=(ok && oam[i*4]<239u &&
            owners[i]<28u)?(LONG)owners[i]:-1;
    }
    unsigned pc=0,addr=0,tile=0,writes=0;
    (void)cviii_nestudio_ppu_source(&pc,&addr,&tile,&writes);
    nest_shared->ppu_source_pc=(LONG)pc;
    nest_shared->ppu_source_addr=(LONG)addr;
    nest_shared->ppu_source_tile=(LONG)tile;
    nest_shared->ppu_write_count=(LONG)writes;
    MemoryBarrier();
    InterlockedIncrement(&nest_shared->revision); /* even: stable snapshot */
}
#endif /* _WIN32 */
#endif
