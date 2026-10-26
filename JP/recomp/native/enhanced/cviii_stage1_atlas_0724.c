#include "cviii_stage1_atlas_0724.h"
#include <stdlib.h>
#include <string.h>
static const uint8_t keys[CVIII_STAGE1_ROOMS_0724][3]={
 {0,0,0},{0,1,0},{0,1,1},{0,1,2},{0,1,3},{0,2,0},{0,2,1},{0,3,0}
};
typedef struct {CviiiStage1Atlas0724 *atlas;unsigned room;unsigned count;} Fill;
static int store(void *context,uint16_t x,uint16_t y,uint8_t id,uint8_t pal){
    Fill *f=(Fill *)context;
    CviiiStage1Room0724 *r=&f->atlas->rooms[f->room];
    if(x>=r->width_tiles||y>=r->height_tiles)return 0;
    unsigned idx=f->atlas->offsets[f->room]+(unsigned)y*r->width_tiles+x;
    if(idx>=CVIII_STAGE1_TILES_0724)return 0;
    f->atlas->tile[idx]=id;
    f->atlas->palette[idx]=pal;
    f->count++;
    return 1;
}
static int accept(void *context,uint16_t x,uint16_t y,uint8_t id,uint8_t pal){
    (void)context;(void)x;(void)y;(void)id;(void)pal;return 1;
}
int cviii_stage1_atlas_load_0724(CviiiStage1Atlas0724 *dst,
    const uint8_t *rom,size_t len){
    if(!dst||!rom)return -1;
    CviiiStage1Atlas0724 *t=(CviiiStage1Atlas0724 *)calloc(1,sizeof *t);
    if(!t)return -1;
    unsigned i,off=0;
    for(i=0;i<CVIII_STAGE1_ROOMS_0724;i++){
        CviiiStage1Room0724 room;
        if(cviii_stage1_rom_0724(rom,len,keys[i],accept,0,&room)!=1)break;
        unsigned n=(unsigned)room.width_tiles*(unsigned)room.height_tiles;
        if(n>CVIII_STAGE1_TILES_0724-off)break;
        t->offsets[i]=(uint16_t)off;
        t->rooms[i]=room;
        off+=n;
    }
    if(i!=CVIII_STAGE1_ROOMS_0724||off!=CVIII_STAGE1_TILES_0724){free(t);return -1;}
    t->offsets[CVIII_STAGE1_ROOMS_0724]=(uint16_t)off;
    for(i=0;i<CVIII_STAGE1_ROOMS_0724;i++){
        Fill f={t,i,0};
        CviiiStage1Room0724 room;
        if(cviii_stage1_rom_0724(rom,len,keys[i],store,&f,&room)!=1||
            f.count!=(unsigned)room.width_tiles*room.height_tiles)break;
    }
    if(i!=CVIII_STAGE1_ROOMS_0724){free(t);return -1;}
    t->loaded=1;
    memcpy(dst,t,sizeof *t);
    free(t);
    return 1;
}
static int locate(const uint8_t key[3]){
    if(!key)return -1;
    for(unsigned i=0;i<CVIII_STAGE1_ROOMS_0724;i++)
        if(memcmp(key,keys[i],3)==0)return (int)i;
    return -1;
}
int cviii_stage1_atlas_get_0724(const CviiiStage1Atlas0724 *a,
    const uint8_t key[3],unsigned x,unsigned y,uint8_t *tile,uint8_t *palette){
    if(!a||!a->loaded||!tile||!palette)return 0;
    int index=locate(key);
    if(index<0)return 0;
    const CviiiStage1Room0724 *r=&a->rooms[index];
    if(x>=r->width_tiles||y>=r->height_tiles)return 0;
    unsigned at=a->offsets[index]+y*(unsigned)r->width_tiles+x;
    if(at>=CVIII_STAGE1_TILES_0724)return 0;
    *tile=a->tile[at];*palette=a->palette[at];
    return 1;
}
int cviii_stage1_atlas_width_0751(const CviiiStage1Atlas0724 *a,
    const uint8_t key[3]){
    if(!a || !a->loaded)return 0;
    int idx=locate(key);
    return idx<0 ? 0 : (int)a->rooms[idx].width_tiles*8;
}

int cviii_stage1_atlas_horizontal_width_0801(
    const CviiiStage1Atlas0724 *a,const uint8_t key[3])
{
    if(!a || !a->loaded)return 0;
    const int idx=locate(key);
    if(idx<0 || a->rooms[idx].vertical)return 0;
    return (int)a->rooms[idx].width_tiles*8;
}

uint32_t cviii_stage1_atlas_paint_bg_table_0802(
    const CviiiStage1Atlas0724 *a,const uint8_t key[3],
    int camera_x,int camera_y,uint32_t *dst,int width,int height,
    int center_x,uint16_t bg_table,
    uint8_t (*chr)(uint16_t),uint32_t (*color)(int)){
    if(bg_table!=0u && bg_table!=0x1000u)return 0;
    if(!a||!a->loaded||!key||!dst||!chr||!color||width<=256||
        width>864||height!=240||center_x<0||center_x+256>width)return 0;
    int room=locate(key);
    if(room<0)return 0;
    const CviiiStage1Room0724 *r=&a->rooms[room];
    uint32_t painted=0;
    for(int y=32;y<height;y++)for(int x=0;x<width;x++){
        /* The sprite/status HUD extends through the first 48 scanlines.
         * Preserve the stationary HUD rectangle even when game-world X=0
         * places native gameplay at the left edge of a wide frame. */
        int protected_x=y<48 ? 85 : center_x;
        if(x>=protected_x&&x<protected_x+256)continue;
        int wx=camera_x+x-center_x,wy=camera_y+y-32;
        if(wx<0||wy<0||wx>=r->width_tiles*8||wy>=r->height_tiles*8)continue;
        unsigned at=a->offsets[room]+(unsigned)(wy/8)*r->width_tiles+(unsigned)(wx/8);
        unsigned tile=a->tile[at],pal=a->palette[at];
        uint16_t pattern=(uint16_t)(bg_table+tile*16u);
        unsigned row=(unsigned)wy%8u,bit=7u-((unsigned)wx%8u);
        unsigned idx=((chr((uint16_t)(pattern+row))>>bit)&1u)|
          (((chr((uint16_t)(pattern+row+8u))>>bit)&1u)<<1u);
        dst[(size_t)y*(unsigned)width+(unsigned)x]=color(idx? (int)(pal*4u+idx):0);
        painted++;
    }
    return painted;
}

/* Retain JP0724 call ABI for archived tests/read-only tooling. */
uint32_t cviii_stage1_atlas_paint_0724(const CviiiStage1Atlas0724 *a,
    const uint8_t key[3],int camera_x,int camera_y,
    uint32_t *dst,int width,int height,int center_x,
    uint8_t (*chr)(uint16_t),uint32_t (*color)(int)){
    return cviii_stage1_atlas_paint_bg_table_0802(a,key,camera_x,camera_y,
        dst,width,height,center_x,0x1000u,chr,color);
}
