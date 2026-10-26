#include "cviii_level1_world_0803.h"
#include <limits.h>
#include <stddef.h>
#include <string.h>
static const uint8_t keys[CVIII_WORLD_ROOMS_0803][3]={
    {0,0,0},{0,1,0},{0,1,1},{0,1,2},
    {0,1,3},{0,2,0},{0,2,1},{0,3,0}
};
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
