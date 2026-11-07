#include "cviii_world_sprites_0807.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
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
    puts("PASS JP0807 original descriptor-driven active sprites only outside native viewport");
    return 0;
}
