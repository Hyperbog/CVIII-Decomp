/* JP0824: original-ROM actor slot remains game-CPU owned.
 * Fake original RAM + fake sprite descriptor; no commercial data. */
#include "cviii_level1_world_0803.h"
#include "cviii_world_sprites_0807.h"
#include "cviii_collision_route_0816.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint32_t pixels[426*240];
static uint8_t bank[CVIII_SPRITE_BANK_BYTES_0807],ram[2048];
static uint8_t chr(uint16_t p){(void)p;return 0x80u;}
static uint32_t pal(int p){return 0xff000000u+(uint32_t)p;}
static void word(unsigned at,unsigned v){
    bank[at-0x8000u]=(uint8_t)v;
    bank[at-0x8000u+1u]=(uint8_t)(v>>8);
}
static void require(int yes,const char *why){
    if(!yes){fprintf(stderr,"FAIL JP0824: %s\n",why);exit(1);}
}
int main(void){
    const uint8_t key[3]={0,2,0};
    CviiiLevel1World0803 *w=calloc(1,sizeof *w);
    CviiiStage1Atlas0724 *a=calloc(1,sizeof *a);
    require(w && a,"resources");a->loaded=1;
    const int widths[]={768,256,256,768,512,768,768,1024};
    for(unsigned i=0;i<8;i++){
        a->rooms[i].width_tiles=(uint16_t)(widths[i]/8);
        a->rooms[i].height_tiles=(uint16_t)(i==2u?64:24);
    }
    require(cviii_world_build_0803(w,a) && !w->rooms[5].placed,
            "unplaced original Stage1-03 source room");
    w->horizontal_ready=1;w->horizontal[5].valid=1;
    ram[0x401]=0x94u;ram[0x471]=0xc5u; /* original page1+source4+cull80 */
    ram[0x54f]=0x3du;ram[0x646]=3u;
    ram[0x439]=12u;ram[0x41d]=99u;ram[0x48d]=8u;ram[0x4a9]=1u;
    word(0x817fu+8u,0x8200u);
    word(0x8200u+0x94u,0x8300u);
    bank[0x300]=1u;bank[0x301]=0;bank[0x302]=3u;
    bank[0x303]=0;bank[0x304]=0;
    /* Original $B1F8 is invoked for this still-allocated CPU slot:
     * page1 correctly defers player hit handling; when original
     * CPU clears page1 on camera entry, it resumes original B339
     * proximity/collision handler without a native substitute. */
    require(cviii_b1f8_route_0816(0x3du,0xc5u,0x94u,0u,0u)==0xb1f7u &&
            cviii_b1f8_route_0816(0x3du,0x44u,0x94u,0u,0u)==0xb232u,
            "original CPU interaction gated off-page and restored in-page");
    CviiiGuestPageActor0824 gate=cviii_guest_page_actor_0824(ram,1u);
    require(gate.eligible && gate.real_original &&
            gate.viewport_x==268 && gate.side==2u,
            "original row32 source parent and high page right candidate");
    require(cviii_world_capture_live_0803(w,key,0,0,ram)==1 &&
            w->actors[1].active && w->actors[1].guest_adjacent_0824 &&
            w->actors[1].local_coords_0824 && w->actors[1].x==268 &&
            w->actors[1].original_type==0x3du,
            "the ORIGINAL CPU actor appears in unplaced room");
    for(unsigned i=0;i<426u*240u;i++)pixels[i]=0xff332211u;
    require(cviii_world_sprites_draw_0807(w,key,0,0,85,pixels,
            426,240,bank,ram,0x1000u,0,chr,pal)==8 &&
            pixels[100*426+353]==pal(19) &&
            pixels[100*426+100]==0xff332211u,
            "right extension renders actual CPU actor, never center");
    ram[0x439]=240u;
    require(cviii_world_capture_live_0803(w,key,0,0,ram)==1 &&
            w->actors[1].x==-16,
            "one-bit page resolves original left underflow");
    memset(pixels,0,sizeof pixels);
    require(cviii_world_sprites_draw_0807(w,key,0,0,85,pixels,
            426,240,bank,ram,0x1000u,0,chr,pal)==8 &&
            pixels[100*426+69]==pal(19),
            "left extension renders original CPU actor");
    ram[0x471]=0x84u;
    require(cviii_world_capture_live_0803(w,key,0,0,ram)==0 &&
            !w->actors[1].active,"no page1 source means no offscreen view");
    ram[0x471]=0xc5u;ram[0x646]=7u;
    require(!cviii_guest_page_actor_0824(ram,1).eligible &&
            cviii_world_capture_live_0803(w,key,0,0,ram)==0,
            "wrong parent index cannot fabricate an actor");
    ram[0x646]=3u;ram[0x54f]=0u;
    require(cviii_world_capture_live_0803(w,key,0,0,ram)==0,
            "original allocator type zero despawns actor immediately");
    ram[0x54f]=0x3du;w->horizontal_ready=0u;
    require(!cviii_world_capture_live_0803(w,key,0,0,ram),
            "unverified source metadata rejects local capture");
    require(!cviii_guest_page_actor_0824(ram,0).eligible &&
            !cviii_guest_page_actor_0824(ram,13).eligible,
            "no extra actor slots beyond actual original source allocator");
    free(a);free(w);
    puts("PASS JP0824 genuine original CPU adjacent-page type3D actor projection");
    return 0;
}
