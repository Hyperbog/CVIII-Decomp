/* JP0725 synthetic-only verification of the real production presenter
 * on Windows/Linux. No game ROM or copyrighted output is distributed. */
#include "cviii_stage1_host_0725.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include "cyc_video.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t test_ram[2048];
static uint32_t original[256*240];
static CviiiStage1Host0725 host;
static int scroll_x,requested_mode=-1;
static uint8_t live_nt[2048];
uint8_t cyc_render_nametable(uint16_t a) {
    unsigned at=a&0xfffu;
    return live_nt[((at>>10u)&1u)*1024u+(at&1023u)];
}
static void seed_visible_room(const uint8_t key[3],unsigned page) {
    for(unsigned y=0;y<24u;y++)for(unsigned x=0;x<32u;x++) {
        uint8_t tile=0,pal=0;
        if (cviii_stage1_atlas_get_0724(&host.atlas,key,x,y,&tile,&pal))
            live_nt[page*1024u+(y+4u)*32u+x]=tile;
    }
}
/* Create the actual synthetic PPU nametable view for a later camera page. */
static void seed_visible_room_from_x(const uint8_t key[3],unsigned page,
                                     unsigned world_x) {
    for(unsigned y=0;y<24u;y++)for(unsigned x=0;x<32u;x++) {
        uint8_t tile=0,pal=0;
        if (cviii_stage1_atlas_get_0724(&host.atlas,key,world_x/8u+x,y,&tile,&pal))
            live_nt[page*1024u+(y+4u)*32u+x]=tile;
    }
}
const uint8_t *cyc_cpu_ram(void) {return test_ram;}
uint8_t cyc_render_line_mask(int line) {(void)line;return 0x1e;}
uint16_t cyc_render_line_bg_table(int line) {(void)line;return 0x1000;}
int cyc_render_line_scroll_x(int line) {(void)line;return scroll_x;}
int cyc_render_line_scroll_y(int line) {return line;}
uint8_t cyc_render_chr(uint16_t addr) {(void)addr;return 0xff;}
uint32_t cyc_render_color(int entry) {return 0xff000000u|(uint32_t)(entry&63);}
void cyc_video_set_mode(int mode) {requested_mode=mode;}
static int require(int condition,const char *what) {
    if (!condition) {fprintf(stderr,"JP0725 FAIL: %s\n",what);return 0;}
    return 1;
}
int main(void)
{
    const char *path="jp0725-synthetic-fixture-local.nes";
    uint8_t *rom=(uint8_t *)calloc(393232u,1u);
    if (!require(rom!=NULL,"ROM fixture memory"))return 1;
    memcpy(rom,"NES\x1a",4);rom[4]=16;rom[5]=16;
    rom[6]=0x80;rom[7]=0x10; /* synthetic Mapper24, never distributed */
    static const unsigned starts[]={0x200BA,0x2014B,0x20039,0x201DD,
                                    0x2017C,0x2026E,0x202FF,0x20390};
    static const unsigned screens[]={3,1,2,3,2,3,3,4};
    for(unsigned i=0;i<8;i++)rom[starts[i]]=(uint8_t)(screens[i]-1u);
    for(unsigned i=0;i<145;i++){
        for(unsigned j=0;j<16;j++)rom[0x20451u+i*16u+j]=(uint8_t)(i+j);
        rom[0x20D61u+i]=0xe4;
    }
    FILE *fp=fopen(path,"wb");
    if (!require(fp!=NULL,"fixture file")) {free(rom);return 1;}
    size_t written=fwrite(rom,1,393232u,fp);
    int closed=fclose(fp);
    if (!require(written==393232u&&closed==0,"fixture write"))return 1;
    for(unsigned i=0;i<256u*240u;i++)original[i]=0xff112233u;
    host.enabled=1;
    if (!require(cviii_stage1_host_rom_0725(&host,path)==1,"owner path option"))
        return 1;
    /* Rendered PPU nametable is independent evidence of active room.
     * A source-correct atlas alone cannot prove the game is in that room. */
    if (!require(cviii_stage1_atlas_load_0724(&host.atlas,rom,393232u)==1,
                 "synthetic room atlas"))return 1;
    const uint8_t first_room[3]={0,0,0};
    seed_visible_room(first_room,0);
    test_ram[0x18]=4;test_ram[0x5a]=0x41;test_ram[0x5b]=0x84;
    test_ram[0x5c]=0x51;test_ram[0x5d]=0x8d;
    int w=256,h=240;
    const uint32_t *pixels=cviii_stage1_host_present_0725(
        &host,original,&w,&h,1);
    if (!require(pixels!=NULL&&pixels!=original&&w==426&&h==240,
                 "wide dimensions") ||
        !require(requested_mode==NES_VIDEO_16_9,"host video mode") ||
        !require(pixels[32*426+0]==original[32*256],
                 "scene start uses genuine first-world pixel, not repeated strip") ||
        !require(pixels[200*426+255]==original[200*256+255],
                 "last native pixel at stage origin") ||
        !require(pixels[0*426+85]==original[0],
                 "HUD remains centered independently") ||
        !require(pixels[32*426+341]!=0xff000000u,
                 "preloaded margin before visit") ||
        !require(pixels[0]==0xff000000u,"no world over HUD"))
       return 1;
    for(int y=0;y<240;y++)for(int x=0;x<256;x++)
      if (!require(pixels[y*426+(y<32?85:0)+x]==original[y*256+x],
                   "all 61,440 NES pixels preserved at boundary-aware offset"))return 1;
    /* Unlike the old 30-frame fading side cache, the already-loaded
     * ROM atlas remains visible after an arbitrary long NT mismatch. */
    scroll_x=123;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if (!require(pixels[32*426+400]!=0xff000000u,
                 "already-loaded valid room retains scenery"))return 1;
    for(unsigned attempt=0;attempt<CVIII_JOIN_HOLD_MAX*4u;attempt++) {
        w=256;h=240;
        pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    }
    if (!require(pixels[32*426+400]!=0xff000000u,
                 "persistent stage atlas never expires after 30 frames"))return 1;
    /* BLK 1-02 starts at physical nametable 1 even when room-local X=0.
     * A selector alone cannot accept previous-room tile data. */
    test_ram[0x35]=1;test_ram[0x36]=3;
    scroll_x=256;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    /* Reject the new selector while NT1 still contains old tiles, but
     * KEEP painting authenticated previous scenery instead of black. */
    if (!require(pixels[32*426+400]!=0xff000000u &&
                 host.last_verified_selector[1]==0u,
                 "unverified selector retains genuine last-room backdrop"))return 1;
    const uint8_t next_room[3]={0,1,3};
    seed_visible_room(next_room,1);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if (!require(pixels[32*426+341]!=0xff000000u,
                 "NT1 room origin accepted with matching live tiles"))return 1;
    /* Live presenter seam: old source room's last 256px were actually
     * observed, then new source room's NT1 data is accepted at local X0. */
    cviii_stage1_host_reset_0751(&host);
    test_ram[0x35]=0;test_ram[0x36]=0;
    test_ram[0x53]=0;test_ram[0x54]=2;
    scroll_x=0;
    seed_visible_room_from_x(first_room,0,512u);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if (!require(host.join.last_camera==512 && host.join.valid,
                 "source-verified last-screen camera"))return 1;
    const uint8_t narrow_room[3]={0,1,0};
    test_ram[0x35]=1;test_ram[0x36]=0;
    test_ram[0x53]=0;test_ram[0x54]=0;
    scroll_x=256;
    seed_visible_room(narrow_room,1);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    /* Dynamic center is 170 in a forward seam; the old room is
     * actually rendered to the left, not fabricated by repeating. */
    if (!require(host.join.joined && host.join.direction==1 &&
                 !memcmp(host.join.adjacent,first_room,3),
                 "actual current/previous room joined") ||
        !require(pixels[60*426+40]!=0xff000000u,
                 "original preceding scenery appears in next-room margin") ||
        !require(pixels[60*426+170]==original[60*256],
                 "native gameplay pixels preserved at forward seam"))return 1;
    test_ram[0x35]=0;test_ram[0x36]=0;
    scroll_x=0;test_ram[0x65]=0x80;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if (!require(pixels[32*426+341]==0xff000000u,
                 "vertical room cannot use horizontal origin"))return 1;
    test_ram[0x65]=0;
    scroll_x=0;test_ram[0x18]=6;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if (!require(pixels[32*426+341]==0xff000000u,
                 "game over does not paint room"))return 1;
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,0);
    if (!require(pixels==original&&w==256&&h==240&&
                 requested_mode==NES_VIDEO_STOCK,"Original edition exact fallback"))
       return 1;
    free(rom);
    (void)remove(path);
    puts("PASS JP0725 native presenter 426x240 and center/fallback/transition guards");
    return 0;
}
