#include "cviii_world_sprites_0807.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
/* JP0845 ROM-free standalone compositor test stubs. The actual
 * production binary always links the genuine JP0803 world graph. */
#ifdef CVIII_SPRITE_STANDALONE_TEST_0845
int cviii_world_index_0803(const CviiiLevel1World0803 *w,
                           const uint8_t key[3]) {
    if(!w || !key)return -1;
    for(unsigned i=0;i<CVIII_WORLD_ROOMS_0803;i++)
        if(!memcmp(w->rooms[i].selector,key,3))return (int)i;
    return -1;
}
int cviii_world_camera_0803(const CviiiLevel1World0803 *w,
    const uint8_t key[3],int cx,int cy,int32_t *x,int32_t *y){
    int index=cviii_world_index_0803(w,key);
    if(index<0 || !w->rooms[index].placed || cx<0 || cy<0 ||
       !x || !y)return 0;
    *x=w->rooms[index].x+cx;
    *y=w->rooms[index].y+cy;
    return 1;
}
#endif
static uint32_t pic[426*240];
static uint8_t data[CVIII_SPRITE_BANK_BYTES_0807],ram[2048];
static uint8_t pixel(uint16_t addr){(void)addr;return 0x80u;}
static uint32_t palette(int x){return 0xff880000u+(uint32_t)x;}
static void set16(unsigned x,unsigned ptr){
    data[x-0x8000u]=(uint8_t)ptr;
    data[x-0x8000u+1u]=(uint8_t)(ptr>>8u);
}
int main(void){
    CviiiLevel1World0803 world={0};
    world.ready=1;
    const uint8_t first[]={0,0,0},next[]={0,1,0};
    memcpy(world.rooms[0].selector,first,3);
    memcpy(world.rooms[1].selector,next,3);
    world.rooms[0].placed=1;world.rooms[0].width=768;
    world.rooms[0].height=192;
    world.rooms[1].placed=1;world.rooms[1].x=768;
    world.rooms[1].width=256;world.rooms[1].height=192;
    CviiiWorldActor0803 *a=&world.actors[0];
    a->active=1;a->room=1;a->slot=0;
    a->selector=0;a->frame=2;a->x=1000;a->y=99;
    a->mirror=1;a->attrs=2;
    /* Invented PRG26 descriptor: pointer set selector0 -> $8200,
     * frame offset2 -> descriptor $8300, one sprite. */
    set16(0x817fu,0x8200u);
    set16(0x8202u,0x8300u);
    data[0x300]=1;
    data[0x301]=0;data[0x302]=3;
    data[0x303]=0;data[0x304]=0;
    for(unsigned i=0;i<426u*240u;i++)pic[i]=0xff112233u;
    uint32_t count=cviii_world_sprites_draw_0807(&world,first,
        700,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    /* 8 sprite rows, each with exactly one visible CHR pixel at x385.
     * This is a pixel count, not an OAM descriptor/sprite count. */
    if(count!=8 || pic[100*426+385]!=0xff88001bu ||
       pic[100*426+340]!=0xff112233u)return 1;
    /* Same exact source actor moves to normal NES viewport:
     * this painter MUST NOT duplicate the NES's OAM contribution. */
    a->x=900;
    for(unsigned i=0;i<426u*240u;i++)pic[i]=0xff112233u;
    count=cviii_world_sprites_draw_0807(&world,first,
        700,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count!=0u || pic[100*426+285]!=0xff112233u)return 2;
    /* An authentic despawn removes side sprites immediately. */
    a->active=0;a->x=1000;
    count=cviii_world_sprites_draw_0807(&world,first,
        700,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 3;
    /* JP0845: a previously genuine original type3D actor has been
     * released offscreen. Its private, source-authenticated movement
     * can present the LAST original sprite frame in the side margin,
     * without making a new guest actor or changing the NES image. */
    world.wide_sources_0825.resident=1u;
    world.wide_sources_0825.source[0].state=
        CVIII_WIDE_SOURCE_UNVERIFIED_0825;
    world.wide_sources_0825.source[0].event_cpu=0xa444u;
    world.wide_sources_0825.source[0].original_type=0x3du;
    world.wide_sources_0825.source[0].original_source_slot=3u;
    world.virtual_3d_0828.initialized=1u;
    CviiiVirtual3D0828 *v=&world.virtual_3d_0828.actor[0];
    v->state=CVIII_VIRTUAL_0828_DETACHED;
    v->source_cpu=0xa444u;
    v->original_parent=3u;
    v->original_slot=1u;
    v->original_frame=2u;
    v->original_flags=0x81u;
    v->world_x=-16;
    v->world_y=99;
    v->detached_frames=2u;
    v->cpu.ram[0x54fu]=0x3du;
    v->cpu.ram[0x646u]=3u;
    v->cpu.ram[0x48du]=0u; /* authenticated prior selector */
    v->cpu.ram[0x4a9u]=1u; /* no mirror */
    v->cpu.ram[0x455u]=2u; /* original sprite palette */
    uint8_t before_ram[2048];
    memcpy(before_ram,ram,sizeof ram);
    for(unsigned i=0;i<426u*240u;i++)pic[i]=0xff112233u;
    count=cviii_world_sprites_draw_0807(&world,next,
        0,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count!=8u || pic[100*426+69]!=0xff88001bu ||
       pic[100*426+85]!=0xff112233u ||
       memcmp(before_ram,ram,sizeof ram))return 4;
    /* No source-only spawn; no projection when merely linked. */
    v->state=CVIII_VIRTUAL_0828_LINKED;
    count=cviii_world_sprites_draw_0807(&world,next,
        0,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 5;
    v->state=CVIII_VIRTUAL_0828_DETACHED;
    v->detached_frames=0u;
    count=cviii_world_sprites_draw_0807(&world,next,
        0,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 6;
    v->detached_frames=2u;
    v->source_cpu=0xa43fu;
    count=cviii_world_sprites_draw_0807(&world,next,
        0,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 7;
    v->source_cpu=0xa444u;
    v->world_x=60; /* private position within original NES viewport */
    count=cviii_world_sprites_draw_0807(&world,next,
        0,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 8;
    v->world_x=-16;
    world.actors[1].active=1;
    world.actors[1].room=1;
    world.actors[1].original_type=0x3du;
    count=cviii_world_sprites_draw_0807(&world,next,
        0,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 9;
    world.actors[1].active=0;
    count=cviii_world_sprites_draw_0807(&world,first,
        700,0,85,pic,426,240,data,ram,0x1000,0,pixel,palette);
    if(count)return 10;
    puts("PASS JP0845 detached type3D source identity, authentic sprite snapshot, side-only projection and no guest effects");
    puts("PASS JP0807 original descriptor-driven active sprites only outside native viewport");
    return 0;
}
