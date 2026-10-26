#include "cviii_level1_world_0803.h"
#include <limits.h>
#include <stddef.h>
#include <string.h>
static const uint8_t keys[CVIII_WORLD_ROOMS_0803][3]={
    {0,0,0},{0,1,0},{0,1,1},{0,1,2},
    {0,1,3},{0,2,0},{0,2,1},{0,3,0}
};
/* JP0804: original JP raw0E physical room-installation resources.
 * Source structure, five field destination offsets and FF terminators
 * are proven by JP0659 original-6502/native execution. No inference
 * from these raw fields to later AI behavior is made here.
 */
int cviii_world_preload_templates_0804(CviiiLevel1World0803 *w,
                      const uint8_t *block,size_t len){
    static const unsigned start[CVIII_WORLD_GROUPS_0804]={
        25u,80u,120u,0u,145u
    };
    static const unsigned counts[CVIII_WORLD_GROUPS_0804]={
        10u,7u,4u,4u,5u
    };
    if(!w || !w->ready || !block ||
       len!=CVIII_WORLD_SOURCE_BYTES_0804)return 0;
    CviiiWorldObjectTemplate0804 items[CVIII_WORLD_TEMPLATES_0804]={0};
    CviiiWorldObjectGroup0804 groups[CVIII_WORLD_GROUPS_0804]={0};
    unsigned used=0;
    for(unsigned g=0;g<CVIII_WORLD_GROUPS_0804;g++){
        unsigned pos=start[g],count=counts[g];
        if(pos+4u+5u*count>=len ||
           block[pos+4u+5u*count]!=0xffu ||
           used+count>CVIII_WORLD_TEMPLATES_0804)return 0;
        groups[g].source_group=(uint8_t)g;
        groups[g].record_start=(uint8_t)used;
        groups[g].record_count=(uint8_t)count;
        memcpy(groups[g].header,block+pos,4u);
        for(unsigned j=0;j<count;j++){
            unsigned at=pos+4u+5u*j;
            if(block[at]==0xffu)return 0;
            CviiiWorldObjectTemplate0804 *item=&items[used++];
            item->source_group=(uint8_t)g;
            item->source_index=(uint8_t)j;
            item->sprite_selector=block[at];    /* CPU $048C,X */
            item->frame_offset=block[at+1u];   /* CPU $0400,X */
            item->initial_x=block[at+2u];      /* CPU $0438,X */
            item->initial_y=block[at+3u];      /* CPU $041C,X */
            item->mirror=block[at+4u];         /* CPU $04A8,X */
        }
    }
    if(used!=CVIII_WORLD_TEMPLATES_0804)return 0;
    memcpy(w->templates,items,sizeof items);
    memcpy(w->groups,groups,sizeof groups);
    w->templates_ready=1;
    return 1;
}

/* Original B7F7 loader writes five fields per record and $054E+X=1.
 * A complete postcondition is required before this resource is marked
 * observed. This code never writes RAM, emits OAM or runs actor AI.
 */
int cviii_world_detect_loader_0805(CviiiLevel1World0803 *w,
    const uint8_t key[3],const uint8_t ram[2048]){
    if(!w || !w->ready || !w->templates_ready || !ram)return -1;
    int room=cviii_world_index_0803(w,key);
    if(room<0)return -1;
    unsigned g=ram[0x7a0u];
    if(g>=CVIII_WORLD_GROUPS_0804)return -1;
    CviiiWorldObjectGroup0804 *group=&w->groups[g];
    for(unsigned i=0;i<group->record_count;i++){
        unsigned x=i+1u;
        const CviiiWorldObjectTemplate0804 *t=
            &w->templates[group->record_start+i];
        if(ram[0x48cu+x]!=t->sprite_selector ||
           ram[0x400u+x]!=t->frame_offset ||
           ram[0x438u+x]!=t->initial_x ||
           ram[0x41cu+x]!=t->initial_y ||
           ram[0x4a8u+x]!=t->mirror ||
           ram[0x54eu+x]!=1u)
            return -1;
    }
    if(!group->active || group->room_index!=(uint8_t)room){
        group->active=1;
        group->room_index=(uint8_t)room;
        group->activations++;
    }
    (void)cviii_world_visit_0803(w,key);
    return (int)g;
}
void cviii_world_clear_live_0805(CviiiLevel1World0803 *w){
    if(!w)return;
    memset(w->actors,0,sizeof w->actors);
}

int cviii_world_index_0803(const CviiiLevel1World0803 *w,
                           const uint8_t selector[3]){
    if(!w || !w->ready || !selector)return -1;
    for(int i=0;i<CVIII_WORLD_ROOMS_0803;i++)
        if(memcmp(w->rooms[i].selector,selector,3)==0)return i;
    return -1;
}
int cviii_world_build_0803(CviiiLevel1World0803 *world,
                          const CviiiStage1Atlas0724 *atlas){
    if(!world || !atlas || !atlas->loaded)return 0;
    CviiiLevel1World0803 temp={0};
    for(unsigned i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        const CviiiStage1Room0724 *src=&atlas->rooms[i];
        if(!src->width_tiles || !src->height_tiles ||
           (unsigned)src->width_tiles*src->height_tiles>
                CVIII_STAGE1_TILES_0724)return 0;
        CviiiWorldRoom0803 *room=&temp.rooms[i];
        memcpy(room->selector,keys[i],3);
        room->width=(int)src->width_tiles*8;
        room->height=(int)src->height_tiles*8;
    }
    /* Owner-traced 1-01 -> 1-02:0 true horizontal passage only.
     * Other 6 areas are all resident, but their placement is not guessed. */
    if(temp.rooms[0].width!=768 || temp.rooms[1].width!=256 ||
       temp.rooms[0].height!=192 || temp.rooms[1].height!=192)return 0;
    temp.rooms[0].placed=1;
    temp.rooms[1].placed=1;
    temp.rooms[1].x=temp.rooms[0].width;
    temp.placed_count=2;
    temp.ready=1;
    *world=temp;
    return 1;
}
int cviii_world_connect_0803(CviiiLevel1World0803 *w,
    const uint8_t first[3],const uint8_t next[3],CviiiWorldDirection0803 dir){
    int a=cviii_world_index_0803(w,first);
    int b=cviii_world_index_0803(w,next);
    if(a<0 || b<0 || a==b || dir>CVIII_WORLD_DOWN_0803 ||
       (!w->rooms[a].placed && !w->rooms[b].placed))return 0;
    const CviiiWorldRoom0803 *A=&w->rooms[a],*B=&w->rooms[b];
    int64_t dx=0,dy=0;
    switch(dir){
    case CVIII_WORLD_LEFT_0803:  dx=-(int64_t)B->width;break;
    case CVIII_WORLD_RIGHT_0803: dx=A->width;break;
    case CVIII_WORLD_UP_0803:    dy=-(int64_t)B->height;break;
    case CVIII_WORLD_DOWN_0803:  dy=A->height;break;
    default:return 0;
    }
    int64_t x=A->placed?(int64_t)A->x+dx:(int64_t)B->x-dx;
    int64_t y=A->placed?(int64_t)A->y+dy:(int64_t)B->y-dy;
    if(x<INT32_MIN || x>INT32_MAX || y<INT32_MIN || y>INT32_MAX)
        return 0;
    if(A->placed && B->placed)
        return B->x==x && B->y==y;
    /* If B is placed then candidate is A's position (computed above);
     * otherwise candidate is B's position. Reject overlapping physically
     * pre-existing rooms, with no blind guesses across unknown branches. */
    const CviiiWorldRoom0803 *moving=A->placed?B:A;
    int64_t px=x,py=y;
    for(int i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        const CviiiWorldRoom0803 *r=&w->rooms[i];
        if(!r->placed || r==A || r==B)continue;
        if(px<r->x+r->width && px+moving->width>r->x &&
           py<r->y+r->height && py+moving->height>r->y)return 0;
    }
    CviiiWorldRoom0803 *dest=&w->rooms[A->placed?b:a];
    dest->x=(int32_t)x;
    dest->y=(int32_t)y;
    dest->placed=1;
    w->placed_count++;
    return 1;
}
int cviii_world_camera_0803(const CviiiLevel1World0803 *w,
    const uint8_t selector[3],int cx,int cy,int32_t *x,int32_t *y){
    int i=cviii_world_index_0803(w,selector);
    if(i<0 || !x || !y || !w->rooms[i].placed ||
       cx<0 || cy<0 || cx>w->rooms[i].width ||
       cy>w->rooms[i].height)return 0;
    *x=w->rooms[i].x+cx;
    *y=w->rooms[i].y+cy;
    return 1;
}
int cviii_world_visit_0803(CviiiLevel1World0803 *w,
                            const uint8_t selector[3]){
    int i=cviii_world_index_0803(w,selector);
    if(i<0)return 0;
    if(!w->rooms[i].visited){
        w->rooms[i].visited=1;
        w->visited_count++;
    }
    return 1;
}
unsigned cviii_world_capture_live_0803(CviiiLevel1World0803 *w,
    const uint8_t key[3],int cx,int cy,const uint8_t ram[2048]){
    if(!w || !ram || !w->ready)return 0;
    int idx=cviii_world_index_0803(w,key);
    if(idx<0 || !w->rooms[idx].placed || cx<0 || cy<0)return 0;
    (void)cviii_world_visit_0803(w,key);
    unsigned count=0;
    for(unsigned i=0;i<CVIII_WORLD_ACTORS_0803;i++){
        CviiiWorldActor0803 *actor=&w->actors[i];
        uint8_t frame=ram[0x400u+i],flags=ram[0x470u+i];
        if(!frame || (flags&0x80u)){
            actor->active=0;
            continue;
        }
        actor->active=1;
        actor->room=(uint8_t)idx;
        actor->slot=(uint8_t)i;
        actor->selector=ram[0x48cu+i];
        actor->frame=frame;
        actor->mirror=ram[0x4a8u+i];
        actor->flags=flags;
        actor->raw_x=ram[0x438u+i];
        actor->raw_y=ram[0x41cu+i];
        actor->attrs=ram[0x454u+i];
        /* Authentic CPU array contains viewport-local sprite base XY;
         * projection is observational, not permission to simulate AI. */
        actor->x=w->rooms[idx].x+cx+actor->raw_x;
        actor->y=w->rooms[idx].y+cy+actor->raw_y;
        count++;
    }
    w->actor_frame++;
    return count;
}
