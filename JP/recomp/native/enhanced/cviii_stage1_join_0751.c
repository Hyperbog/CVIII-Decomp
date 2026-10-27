#include "cviii_stage1_join_0751.h"
#include <string.h>
void cviii_stage1_join_reset_0751(CviiiStage1Join0751 *j) {
    if(j)memset(j,0,sizeof *j);
}

/* JP0782: source-verified horizontal room connections stay in memory
 * across death, checkpoint respawn and arbitrary-length transitions. */
static CviiiRoomLink0782 *find_link(CviiiStage1Join0751 *j,
                                    const uint8_t key[3],int create) {
    if(!j || !key)return NULL;
    for(unsigned i=0;i<j->link_count;i++)
        if(!memcmp(j->links[i].key,key,3))return &j->links[i];
    if(!create || j->link_count>=CVIII_STAGE1_LINK_SLOTS_0782)return NULL;
    CviiiRoomLink0782 *link=&j->links[j->link_count++];
    memset(link,0,sizeof *link);
    memcpy(link->key,key,3);
    return link;
}
void cviii_stage1_join_soft_reset_0782(CviiiStage1Join0751 *j) {
    if(!j)return;
    j->valid=0;
    j->joined=0;
    j->gap=0;
    j->has_side=0;
    j->hold_age=0;
}
void cviii_stage1_join_link_0782(CviiiStage1Join0751 *j,
    const uint8_t left[3],int lw,const uint8_t right[3],int rw) {
    if(!j || !left || !right || !memcmp(left,right,3) ||
       lw<256 || rw<256)return;
    CviiiRoomLink0782 *l=find_link(j,left,1);
    CviiiRoomLink0782 *r=find_link(j,right,1);
    if(!l || !r)return;
    memcpy(l->right,right,3);
    l->right_width=rw;
    l->has_right=1;
    memcpy(r->left,left,3);
    r->left_width=lw;
    r->has_left=1;
}
void cviii_stage1_join_restore_0782(CviiiStage1Join0751 *j,
    const uint8_t key[3],int camera,int width) {
    if(!j || !key || j->joined || width<256 ||
       camera<0 || camera>width-256)return;
    CviiiRoomLink0782 *link=find_link(j,key,0);
    if(!link)return;
    if(camera<CVIII_JOIN_SIDE && link->has_left) {
        memcpy(j->adjacent,link->left,3);
        j->prior_width=link->left_width;
        j->direction=1;
        j->joined=1;
    } else if(camera>=width-256-CVIII_JOIN_SIDE && link->has_right) {
        memcpy(j->adjacent,link->right,3);
        j->prior_width=link->right_width;
        j->direction=-1;
        j->joined=1;
    }
}
int cviii_stage1_join_neighbor_0790(const CviiiStage1Join0751 *j,
          const uint8_t key[3],int camera,int width,int side,
          uint8_t neighbor[3],int *neighbor_camera)
{
    if(!j || !key || !neighbor || !neighbor_camera ||
       width<256 || camera<0 || camera>width+CVIII_JOIN_SIDE ||
       (side!=-1 && side!=1)) return 0;
    for(unsigned i=0;i<j->link_count;i++){
        const CviiiRoomLink0782 *link=&j->links[i];
        if(memcmp(link->key,key,3))continue;
        if(side==-1 && link->has_left && link->left_width>=256) {
            memcpy(neighbor,link->left,3);
            *neighbor_camera=camera+link->left_width;
            return 1;
        }
        if(side==1 && link->has_right && link->right_width>=256) {
            memcpy(neighbor,link->right,3);
            *neighbor_camera=camera-width;
            return 1;
        }
        return 0;
    }
    return 0;
}
int cviii_stage1_neighbor_visual_0823(const uint8_t key[3],
    int camera_x,int width,int side,uint8_t neighbor[3],
    int *neighbor_camera)
{
    if(!key || !neighbor || !neighbor_camera ||
       key[0]!=0u || key[1]!=2u || key[2]>1u ||
       width!=768 || camera_x<0 || camera_x>width-256 ||
       (side!=-1 && side!=1))return 0;
    /* Only the two actual ROM-decoded horizontal BLK 1-03 halves;
     * no extrapolation into stage 1-04 or an unknown branch. */
    if((key[2]==0u && side!=1) ||
       (key[2]==1u && side!=-1))return 0;
    neighbor[0]=0u; neighbor[1]=2u;
    neighbor[2]=key[2]==0u ? 1u:0u;
    *neighbor_camera=key[2]==0u ? camera_x-width:camera_x+768;
    return 1;
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
            if(j->direction==1)
                cviii_stage1_join_link_0782(j,j->last,j->last_width,key,width);
            else
                cviii_stage1_join_link_0782(j,key,width,j->last,j->last_width);
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
