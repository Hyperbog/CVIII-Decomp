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
static uint32_t isolated_room[426*240]; /* invented ROM test pixels */
static int scroll_x,scroll_y,requested_mode=-1,bg_table=0x1000;
static uint8_t live_nt[4096];
uint8_t cyc_render_nametable(uint16_t a) {
    unsigned at=a&0xfffu;
    return live_nt[((at>>10u)&3u)*1024u+(at&1023u)];
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
uint16_t cyc_render_line_bg_table(int line) {(void)line;return (uint16_t)bg_table;}
bool cyc_render_line_sprite16(int line) {(void)line;return false;}
uint16_t cyc_render_line_sprite_table(int line) {(void)line;return 0x1000u;}
int cyc_render_line_scroll_x(int line) {(void)line;return scroll_x;}
int cyc_render_line_scroll_y(int line) {return (line+scroll_y)%480;}
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
        !require(pixels[48*426+0]==original[48*256],
                 "scene start uses genuine first-world pixel below the HUD") ||
        !require(pixels[200*426+255]==original[200*256+255],
                 "last native pixel at stage origin") ||
        !require(pixels[0*426+85]==original[0] &&
                 pixels[32*426+85]==original[32*256] &&
                 pixels[40*426+85]==original[40*256] &&
                 pixels[47*426+85]==original[47*256] &&
                 pixels[47*426+340]==original[47*256+255],
                 "all NES HUD scanlines 0..47 anchored at screen X85") ||
        !require(pixels[48*426+0]==original[48*256],
                 "game-world scanline 48 uses real stage-start camera") ||
        !require(pixels[32*426+341]!=0xff000000u,
                 "preloaded margin before visit") ||
        !require(pixels[0]==0xff000000u,"no world over HUD"))
       return 1;
    for(int y=0;y<240;y++)for(int x=0;x<256;x++)
      if (!require(pixels[y*426+(y<CVIII_STAGE1_HUD_ROWS_0781?85:0)+x]==original[y*256+x],
                   "all 61,440 NES pixels preserved at boundary-aware offset"))return 1;
    /* JP0801 regression: Stage 1-03 / Stage 1-04 selection is always
     * source-backed, not tied to the first room's $5A-$5D TSA pointers.
     * Each room's natural width and each native PPU page is verified.
     * The previous buggy gate would reject every one of these cases
     * before testing any visible source tiles. */
    {
        static const uint8_t later_keys[][3]={
           {0,1,2},{0,1,3},{0,2,0},{0,2,1},{0,3,0}
        };
        static const int natural_width[]={768,512,768,768,1024};
        cviii_stage1_host_reset_0751(&host);
        for(unsigned area=0;area<5;area++) {
            const uint8_t *key=later_keys[area];
            if(!require(cviii_stage1_atlas_horizontal_width_0801(
                   &host.atlas,key)==natural_width[area],
                   "all known later Stage1 subarea geometries loaded"))
                return 1;
            /* Authentic ROM layout confirms the visible nametable even
             * when original per-room TSA producer pointers differ. */
            test_ram[0x34]=key[0];test_ram[0x35]=key[1];
            test_ram[0x36]=key[2];
            test_ram[0x5a]=0x00;test_ram[0x5b]=0x00;
            test_ram[0x5c]=0x00;test_ram[0x5d]=0x00;
            test_ram[0x53]=0;test_ram[0x54]=0;
            memset(live_nt,0,sizeof live_nt);
            seed_visible_room(key,0);
            scroll_x=0;w=256;h=240;
            pixels=cviii_stage1_host_present_0725(
                &host,original,&w,&h,1);
            if(!require(host.has_verified_scene &&
                        !memcmp(host.last_verified_selector,key,3) &&
                        host.last_verified_camera==0 &&
                        pixels[96*426+400]!=0xff000000u,
                        "later room accepted with ROM/PPU proof and wide scenery"))
                return 1;
            /* Source on next screen, respecting actual room width.
             * 2-screen rooms stop at X256; 3-/4-screen rooms can go
             * past X296. Map the following NT0 screen where visible. */
            const int next_camera=natural_width[area]>=768?296:256;
            test_ram[0x53]=(uint8_t)(next_camera&255);
            test_ram[0x54]=(uint8_t)(next_camera>>8);
            memset(live_nt,0,sizeof live_nt);
            seed_visible_room_from_x(key,1,256);
            if(natural_width[area]>=768)
                seed_visible_room_from_x(key,0,512);
            scroll_x=next_camera;w=256;h=240;
            pixels=cviii_stage1_host_present_0725(
                &host,original,&w,&h,1);
            if(!require(host.has_verified_scene &&
                        !memcmp(host.last_verified_selector,key,3) &&
                        host.last_verified_camera==next_camera,
                        "later room page1 camera verified within atlas bounds"))
                return 1;
            if(area==2u) {
                /* BLK 1-03 still renders if hardware chooses the other
                 * real NES background CHR pattern table at $0000. */
                bg_table=0;
                w=256;h=240;
                pixels=cviii_stage1_host_present_0725(
                    &host,original,&w,&h,1);
                if(!require(host.has_verified_scene &&
                            host.last_verified_camera==next_camera &&
                            !memcmp(host.last_verified_selector,key,3),
                            "BLK1-03 accepts actual PPU BG table0"))return 1;
                bg_table=0x1000;
            }
        }
        /* JP0823: reproduced user-observed BLK 1-03 right black side.
         * Both source ROM layouts are loaded, but their world rooms
         * remain unplaced. A source-backed sibling visual must fill
         * only margins without moving NES gameplay or spawning actors. */
        {
          const uint8_t blk3a[]={0,2,0},blk3b[]={0,2,1};
          cviii_stage1_host_reset_0751(&host);
          test_ram[0x34]=0;test_ram[0x35]=2;test_ram[0x36]=0;
          test_ram[0x53]=0;test_ram[0x54]=2;
          scroll_x=0;scroll_y=0;bg_table=0x1000;
          memset(live_nt,0,sizeof live_nt);
          seed_visible_room_from_x(blk3a,0,512u);
          w=256;h=240;
          pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
          memset(isolated_room,0,sizeof isolated_room);
          if(!require(cviii_stage1_atlas_paint_0724(
                 &host.atlas,blk3b,-256,0,isolated_room,
                 426,240,85,cyc_render_chr,cyc_render_color)>0 &&
              pixels[100*426+400]==isolated_room[100*426+400] &&
              pixels[100*426+400]!=0xff000000u &&
              pixels[100*426+85]==original[100*256] &&
              !host.world.rooms[5].placed &&
              !host.world.rooms[6].placed,
              "BLK 1-03 unplaced right ROM sibling fills real source margin"))
             return 1;
          /* Second subroom must keep the first original subroom in
           * its left 85 pixels, independent of room-graph placement. */
          cviii_stage1_host_reset_0751(&host);
          test_ram[0x36]=1;test_ram[0x53]=0;test_ram[0x54]=0;
          scroll_x=0;
          memset(live_nt,0,sizeof live_nt);
          seed_visible_room(blk3b,0);
          w=256;h=240;
          pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
          memset(isolated_room,0,sizeof isolated_room);
          if(!require(cviii_stage1_atlas_paint_0724(
                 &host.atlas,blk3a,768,0,isolated_room,
                 426,240,85,cyc_render_chr,cyc_render_color)>0 &&
              pixels[100*426+30]==isolated_room[100*426+30] &&
              pixels[100*426+30]!=0xff000000u &&
              pixels[100*426+85]==original[100*256],
              "BLK 1-03 left-margin projection persists across subroom"))
             return 1;
        }
        /* JP0823: even when the current BLK 1-03 room is physically
         * placed and world painter returned pixels, the following
         * BLK 1-03 sibling can still be unplaced. The old
         * if(!world_pixels) gate made that right margin black. */
        {
          const uint8_t narrow[]={0,1,0},blk3a[]={0,2,0};
          const uint8_t successor[]={0,2,1};
          cviii_stage1_host_reset_0751(&host);
          if(!require(cviii_world_build_0803(&host.world,&host.atlas) &&
               cviii_world_connect_0803(&host.world,narrow,blk3a,
                   CVIII_WORLD_RIGHT_0803),
               "synthetic physically witnessed BLK1-03 predecessor link"))
              return 1;
          test_ram[0x34]=0;test_ram[0x35]=2;test_ram[0x36]=0;
          test_ram[0x53]=0;test_ram[0x54]=2;
          scroll_x=0;
          memset(live_nt,0,sizeof live_nt);
          seed_visible_room_from_x(blk3a,0,512u);
          w=256;h=240;
          pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
          memset(isolated_room,0,sizeof isolated_room);
          if(!require(host.world.rooms[5].placed &&
              !host.world.rooms[6].placed &&
              cviii_stage1_atlas_paint_0724(&host.atlas,successor,-256,0,
                  isolated_room,426,240,85,cyc_render_chr,
                  cyc_render_color)>0 &&
              pixels[100*426+400]==isolated_room[100*426+400] &&
              pixels[100*426+400]!=0xff000000u &&
              pixels[100*426+85]==original[100*256],
              "placed current world cannot hide unplaced BLK1-03 sibling"))
              return 1;
        }
        /* Truly nonhorizontal room 1-02:1 is never painted sideways. */
        const uint8_t vertical[3]={0,1,1};
        if(!require(cviii_stage1_atlas_horizontal_width_0801(
               &host.atlas,vertical)==0,
               "vertical chapel must not receive horizontal fake map"))
            return 1;
        /* Return the fixture to an authenticated first-room state. */
        cviii_stage1_host_reset_0751(&host);
        memset(live_nt,0,sizeof live_nt);
        test_ram[0x34]=0;test_ram[0x35]=0;test_ram[0x36]=0;
        test_ram[0x53]=0;test_ram[0x54]=0;
        test_ram[0x5a]=0x41;test_ram[0x5b]=0x84;
        test_ram[0x5c]=0x51;test_ram[0x5d]=0x8d;
        seed_visible_room(first_room,0);
        scroll_x=0;w=256;h=240;
        (void)cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    }
    /* JP0808: the chapel has a real source-backed Y-axis camera.
     * Simulate matching physical PPU pattern/tile fetches across the
     * three sampled scanlines; do not guess a left/right room link. */
    cviii_stage1_host_reset_0751(&host);
    {
        const uint8_t chapel[3]={0,1,1};
        test_ram[0x35]=1;test_ram[0x36]=1;test_ram[0x65]=0x80;
        test_ram[0x53]=0;test_ram[0x54]=0;
        scroll_x=0;scroll_y=0;
        memset(live_nt,0,sizeof live_nt);
        static const int sample_lines[]={64,120,176};
        static const int sample_columns[]={24,88,152,216};
        for(unsigned row=0;row<3u;row++)
            for(unsigned col=0;col<4u;col++){
                int line=sample_lines[row],sx=sample_columns[col];
                uint8_t tile=0,pal=0;
                if(!require(cviii_stage1_atlas_get_0724(
                    &host.atlas,chapel,(unsigned)sx/8u,
                    (unsigned)(line-32)/8u,&tile,&pal),
                    "preloaded chapel source tile"))return 1;
                live_nt[(unsigned)(line/8)*32u+(unsigned)(sx/8)]=tile;
            }
        w=256;h=240;
        pixels=cviii_stage1_host_present_0725(
            &host,original,&w,&h,1);
        if(!require(host.has_verified_scene &&
                   !memcmp(host.last_verified_selector,chapel,3) &&
                   host.last_verified_camera==0 &&
                   pixels[96*426+400]==0xff000000u &&
                   pixels[96*426+85]==original[96*256],
                   "vertical chapel recognized without false horizontal art"))
            return 1;
        test_ram[0x53]=80;scroll_y=0;
        w=256;h=240;
        pixels=cviii_stage1_host_present_0725(
            &host,original,&w,&h,1);
        if(!require(host.last_verified_camera==0,
                   "invalid chapel PPU Y phase cannot invent scrolling"))
            return 1;
        cviii_stage1_host_reset_0751(&host);
        test_ram[0x65]=0;test_ram[0x35]=0;test_ram[0x36]=0;
        test_ram[0x53]=0;test_ram[0x54]=0;
        scroll_x=0;scroll_y=0;
        memset(live_nt,0,sizeof live_nt);
        seed_visible_room(first_room,0);
    }
    /* JP0800 video regression: authoritative NES PPU moves while RAM
     * $53/$54 and nametable attestation lag. Old host froze BOTH side
     * columns while 4:3 NES gameplay moved. Advance by PPU delta, not by
     * stale last-verified camera. Re-run source-exact atlas for every step. */
    cviii_stage1_host_reset_0751(&host);
    test_ram[0x35]=0;test_ram[0x36]=0;
    test_ram[0x53]=100;test_ram[0x54]=0;
    seed_visible_room(first_room,0);
    seed_visible_room_from_x(first_room,1,256u);
    scroll_x=100;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.has_verified_scene &&
                host.last_verified_camera==100 &&
                host.has_ppu_scroll_x,
                "PPU-scene baseline authenticated"))return 1;
    for(int x=104;x<=124;x+=4) {
        /* RAM stays at 100 and the PPU is still scrolling: this is
         * intentionally rejected by the strict <=2px ROM camera rule. */
        scroll_x=x;w=256;h=240;
        pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
        if(!require(host.last_verified_camera==x &&
                    host.scroll_fallback_frames==(unsigned)((x-100)/4),
                    "unverified frames follow real PPU motion, not frozen x100"))
            return 1;
        memset(isolated_room,0,sizeof isolated_room);
        if(!require(cviii_stage1_atlas_paint_0724(&host.atlas,first_room,
                    x,0,isolated_room,426,240,85,
                    cyc_render_chr,cyc_render_color)>0 &&
                    pixels[96*426+400]==isolated_room[96*426+400] &&
                    pixels[112*426+40]==isolated_room[112*426+40] &&
                    pixels[40*426+85]==original[40*256],
                    "both side margins track source atlas at moving PPU x"))
            return 1;
    }
    /* Simulate a physical PPU/nametable phase jump. A jump of 200px
     * cannot be interpreted as camera velocity in the old room. */
    scroll_x=340;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.last_verified_camera==124 &&
                host.scroll_fallback_frames==0,
                "large NT phase step does not teleport an unverified atlas"))
        return 1;
    /* Returning to normal attested conditions resynchronizes camera and
     * physical scroll phase without a permanent frozen background. */
    test_ram[0x53]=100;
    seed_visible_room(first_room,0);
    scroll_x=100;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.last_verified_camera==100 &&
                host.scroll_fallback_frames==0,
                "verified room reanchors PPU tracker"))return 1;
    /* Existing long unverified-room test begins from the origin. */
    test_ram[0x53]=0;test_ram[0x54]=0;
    scroll_x=0;w=256;h=240;
    (void)cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    /* The PPU-scroll regression populated NT1 with authentic invented
     * pixels. Restore the original fixture's empty NT1 before testing
     * rejection of a stale selector; fixtures must not bleed state. */
    memset(live_nt+1024,0,1024);
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

    /* JP0800 signed modulo-512 PPU rollover: native NES page 511->0
     * is +1 logical px, NOT a room warp or a 512px reverse jump. */
    cviii_stage1_host_reset_0751(&host);
    test_ram[0x35]=0;test_ram[0x36]=0;
    test_ram[0x53]=254;test_ram[0x54]=1;
    scroll_x=510;
    seed_visible_room_from_x(first_room,0,512u);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.last_verified_camera==510 &&
                host.has_ppu_scroll_x && host.last_ppu_scroll_x==510,
                "source-verified camera near modulo-512 PPU wrap"))return 1;
    scroll_x=2;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.last_verified_camera==514 &&
                host.scroll_fallback_frames==1u,
                "PPU 510 to 2 advances +4px across 512 wrap"))return 1;
    scroll_x=6;w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.last_verified_camera==518 &&
                host.scroll_fallback_frames==2u,
                "PPU wrap continues smooth world camera without 4:3 freeze"))
        return 1;
    /* Transition crossing: old room at physical camera 512, then narrow
     * successor at x0. Native gameplay remains wide X85 on BOTH sides;
     * original game pixels never shift to X170 during the door transfer. */
    /* Live presenter seam: old source room's last 256px were actually
     * observed, then new source room's NT1 data is accepted at local X0. */
    cviii_stage1_host_reset_0751(&host);
    test_ram[0x35]=0;test_ram[0x36]=0;
    test_ram[0x53]=0;test_ram[0x54]=2;
    scroll_x=0;
    seed_visible_room_from_x(first_room,0,512u);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if (!require(host.join.last_camera==512 && host.join.valid &&
                 host.last_verified_center==85,
                 "final first-room camera remains at fixed X85"))return 1;
    /* Room geometry after first-room x=768 is loaded already: display
     * authentic NEXT room in the rightmost side before it becomes active. */
    if (!require(pixels[60*426+400]!=0xff000000u,
                 "next area visible at right before transition"))return 1;
    /* Prevent invisible overlap: test the right-side pixel against the
     * successor's world-projected atlas in complete isolation. */
    const uint8_t next_edge_room[3]={0,1,0};
    memset(isolated_room,0,sizeof isolated_room);
    if(!require(cviii_stage1_atlas_paint_0724(&host.atlas,
                  next_edge_room,-256,0,isolated_room,426,240,85,
                  cyc_render_chr,cyc_render_color)>0 &&
                pixels[60*426+400]==isolated_room[60*426+400],
                "next room matches unique source pixel, no tile overlap"))
        return 1;
    const uint8_t narrow_room[3]={0,1,0};
    test_ram[0x35]=1;test_ram[0x36]=0;
    test_ram[0x53]=0;test_ram[0x54]=0;
    scroll_x=256;
    seed_visible_room(narrow_room,1);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    /* Room changes cannot force X170 or jump again when the cached join
     * expires; the previous room remains to the left at the same X85. */
    if (!require(host.join.joined && host.join.direction==1 &&
                 !memcmp(host.join.adjacent,first_room,3),
                 "actual current/previous room joined") ||
        !require(pixels[60*426+40]!=0xff000000u,
                 "original preceding scenery appears in next-room margin") ||
        !require(host.last_verified_center==85 &&
                 pixels[60*426+85]==original[60*256],
                 "camera offset unchanged across selector transition") ||
        !require(pixels[40*426+85]==original[40*256] &&
                 pixels[47*426+85]==original[47*256],
                 "HUD cannot slide with player across room seams"))return 1;
    memset(isolated_room,0,sizeof isolated_room);
    if(!require(cviii_stage1_atlas_paint_0724(&host.atlas,
                   first_room,768,0,isolated_room,426,240,85,
                   cyc_render_chr,cyc_render_color)>0 &&
                pixels[60*426+40]==isolated_room[60*426+40],
                "previous room matches true source tile without overlap"))
        return 1;
    /* Death/game-over and checkpoint respawn in BLK 1-02:0. Neither
     * preloaded room nor its authenticated predecessor may disappear. */
    test_ram[0x18]=6;
    w=256;h=240;
    (void)cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    test_ram[0x18]=4;
    test_ram[0x35]=1;test_ram[0x36]=0;
    test_ram[0x53]=0;test_ram[0x54]=0;
    scroll_x=256;
    seed_visible_room(narrow_room,1);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.join.joined && host.join.direction==1 &&
                host.last_verified_center==85 &&
                !memcmp(host.join.adjacent,first_room,3),
                "respawn reconstructs original preceding room") ||
       !require(pixels[60*426+40]!=0xff000000u,
                "checkpoint left side contains previous preloaded room") ||
       !require(pixels[40*426+85]==original[40*256],
                "HUD remains fixed after respawn"))return 1;

    /* A new room's active transient join ends, but the true prior room
     * remains part of the persistent atlas and camera stays at X85. */
    cviii_stage1_join_soft_reset_0782(&host.join);
    w=256;h=240;
    pixels=cviii_stage1_host_present_0725(&host,original,&w,&h,1);
    if(!require(host.last_verified_center==85 &&
                pixels[60*426+85]==original[60*256] &&
                pixels[60*426+40]!=0xff000000u,
                "no second viewport jump or disappearing prior atlas"))return 1;
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
