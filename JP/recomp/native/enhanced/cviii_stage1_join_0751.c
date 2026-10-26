#include "cviii_stage1_join_0751.h"
#include <string.h>
void cviii_stage1_join_reset_0751(CviiiStage1Join0751 *j) {
    if(j)memset(j,0,sizeof *j);
}
void cviii_stage1_join_gap_0751(CviiiStage1Join0751 *j) {
    if(j && j->gap<CVIII_JOIN_GAP_MAX+1u)j->gap++;
}
void cviii_stage1_join_accept_0751(CviiiStage1Join0751 *j,
                                    const uint8_t key[3],int camera,int width) {
    if(!j || !key || width<256 || camera<0 || camera>width-256)return;
    if(j->valid && memcmp(j->last,key,3)) {
        /* Source-verified scene crossing near a horizontal room edge.
         * Teleports, stale selectors and long scene loads fail closed. */
        j->joined=0;
        /* Gap length does not invalidate immutable, preloaded source room.
         * The physical old/new camera edge guard still rejects warps. */
        if(j->last_width>=256) {
            if(j->last_camera>=j->last_width-256-96 &&
               camera<CVIII_JOIN_SIDE) {
                j->joined=1;
                j->direction=1;
            } else if(j->last_camera<=96 &&
                      camera>=width-256-CVIII_JOIN_SIDE) {
                j->joined=1;
                j->direction=-1;
            }
        }
        if(j->joined) {
            memcpy(j->adjacent,j->last,3);
            j->prior_width=j->last_width;
        }
    }
    if(j->joined && ((j->direction==1 && camera>=CVIII_JOIN_SIDE) ||
       (j->direction==-1 && camera<width-256-CVIII_JOIN_SIDE)))
        j->joined=0;
    memcpy(j->last,key,3);
    j->last_camera=camera;
    j->last_width=width;
    j->valid=1;
    j->gap=0;
}
int cviii_stage1_join_previous_0751(const CviiiStage1Join0751 *j,
    int camera,int width,uint8_t old_key[3],int *old_camera) {
    if(!j || !j->joined || !old_key || !old_camera ||
       camera<0 || camera>width-256)return 0;
    if(j->direction==1 && camera<CVIII_JOIN_SIDE) {
        *old_camera=j->prior_width+camera;
    } else if(j->direction==-1 &&
              camera>=width-256-CVIII_JOIN_SIDE) {
        *old_camera=camera-width;
    } else return 0;
    memcpy(old_key,j->adjacent,3);
    return 1;
}
void cviii_stage1_join_cache_0751(CviiiStage1Join0751 *j,
    const uint32_t frame[CVIII_JOIN_W*CVIII_JOIN_H]) {
    if(!j || !frame)return;
    for(unsigned y=CVIII_JOIN_Y;y<CVIII_JOIN_H;y++) {
        const unsigned n=(y-CVIII_JOIN_Y)*CVIII_JOIN_SIDE*2u;
        memcpy(j->cached_sides+n,frame+(size_t)y*CVIII_JOIN_W,
               CVIII_JOIN_SIDE*sizeof(uint32_t));
        memcpy(j->cached_sides+n+CVIII_JOIN_SIDE,
               frame+(size_t)y*CVIII_JOIN_W+CVIII_JOIN_X+256u,
               CVIII_JOIN_SIDE*sizeof(uint32_t));
    }
    j->has_side=1;
    j->hold_age=0;
}
int cviii_stage1_join_hold_0751(CviiiStage1Join0751 *j,
    uint32_t frame[CVIII_JOIN_W*CVIII_JOIN_H]) {
    if(!j || !frame || !j->has_side ||
       j->hold_age>=CVIII_JOIN_HOLD_MAX)return 0;
    for(unsigned y=CVIII_JOIN_Y;y<CVIII_JOIN_H;y++) {
        const unsigned n=(y-CVIII_JOIN_Y)*CVIII_JOIN_SIDE*2u;
        memcpy(frame+(size_t)y*CVIII_JOIN_W,j->cached_sides+n,
               CVIII_JOIN_SIDE*sizeof(uint32_t));
        memcpy(frame+(size_t)y*CVIII_JOIN_W+CVIII_JOIN_X+256u,
               j->cached_sides+n+CVIII_JOIN_SIDE,
               CVIII_JOIN_SIDE*sizeof(uint32_t));
    }
    j->hold_age++;
    return 1;
}
