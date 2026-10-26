/* JP0725 - ROM-only Stage 1 background compositor for the native
 * Enhanced Edition. Original CPU, PPU, sprite pipeline and savestates
 * remain authoritative. Never include game resources in public source. */
#include "cviii_stage1_host_0725.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include "cyc_video.h"
#include "cviii_runtime_resources_0727.h"
#include <stdio.h>
#include <string.h>

/* JP0727: no build-time source path and no Python extraction. The user's
 * launch-time original Japanese ROM is authenticated with full SHA256 and
 * expanded to a game-owned read-only atlas. The selected ROM is never copied
 * into a native executable, serialized in the save, or shipped as assets.
 */
static int load(CviiiStage1Host0725 *h)
{
    if(h->atlas.loaded) return 1;
    if(h->attempted) return 0;
    h->attempted=1;
    if(!h->rom_path[0])return 0;
    /* When a validated private CHR index was already supplied, reuse it.
     * Otherwise create the original font/HUD/graphics index in the same
     * authenticated ROM read used for the Stage 1 background geometry. */
    CviiiChrIndex *assets=h->runtime_assets && !h->runtime_assets->pixels ?
        h->runtime_assets : NULL;
    CviiiResourceStatus0727 result=cviii_game_resources_cached_open_0729(
        h->rom_path,h->resource_cache_path,&h->atlas,assets);
    if(result==CVIII_RESOURCE_READY_0727) return 1;
    fprintf(stderr,"CVIII JP0727: runtime Stage 1 resource load rejected (status %d); stock presentation retained\\n",
            (int)result);
    return 0;
}

void cviii_stage1_host_reset_0751(CviiiStage1Host0725 *h)
{
    if(h) {
        cviii_stage1_join_soft_reset_0782(&h->join);
        h->has_verified_scene=0;
        h->has_ppu_scroll_x=0;
        h->scroll_fallback_frames=0;
    }
}
/* The original 1-01 exit to 1-02:0 is source-proven in JP0719. Both
 * complete rooms are loaded from the authenticated Japanese cartridge.
 * Make the connection available before any checkpoint spawn. */
static void cviii_stage1_seed_links_0782(CviiiStage1Host0725 *h)
{
    static const uint8_t first[3]={0,0,0}, next[3]={0,1,0};
    if(cviii_stage1_atlas_width_0751(&h->atlas,first)==768 &&
       cviii_stage1_atlas_width_0751(&h->atlas,next)==256)
        cviii_stage1_join_link_0782(&h->join,first,768,next,256);
}
int cviii_stage1_host_rom_0725(CviiiStage1Host0725 *h,const char *path)
{
    if (!h || !path || !*path || strlen(path)>=sizeof h->rom_path) return 0;
    memcpy(h->rom_path,path,strlen(path)+1u);
    /* Only selecting a different ROM invalidates learnt world geometry. */
    cviii_stage1_join_reset_0751(&h->join);
    cviii_stage1_host_reset_0751(h);
    h->attempted=0;
    h->atlas.loaded=0;
    return 1;
}
int cviii_stage1_host_cache_0729(CviiiStage1Host0725 *h,const char *path)
{
    if(!h||!path||!*path||strlen(path)>=sizeof h->resource_cache_path)
        return 0;
    memcpy(h->resource_cache_path,path,strlen(path)+1u);
    return 1;
}
void cviii_stage1_host_mode_0725(CviiiStage1Host0725 *h,int enabled)
{
    if (h) {
        if (!enabled)cviii_stage1_host_reset_0751(h);
        h->enabled=!!enabled;
    }
}
/* JP0726: authenticate the visible PPU nametable against the private
 * original-ROM atlas before extending the sides. This rejects old selector
 * values whose name tables still contain the previous room. The original
 * hardware may use nametable page 0 OR page 1 as the current room's first
 * screen. RAM $53/$54 remains room-local in both cases.
 */
static int room_loaded(const CviiiStage1Host0725 *h,
    const uint8_t sel[3],int world_x,int ppu_x)
{
    static const int screen_x[]={24,88,152,216};
    static const int tile_y[]={8,14,20}; /* ROM map starts at PPU row 4 */
    unsigned total=0,agree=0;
    for (unsigned y=0;y<3;y++) for (unsigned x=0;x<4;x++) {
        const int wx=world_x+screen_x[x];
        if (wx<0) continue;
        uint8_t tile,palette;
        if (!cviii_stage1_atlas_get_0724(&h->atlas,sel,
                (unsigned)wx/8u,(unsigned)tile_y[y],&tile,&palette))
            continue;
        const unsigned px=(unsigned)((ppu_x+screen_x[x])&511);
        const unsigned page=(px>>8u)&1u, col=(px>>3u)&31u;
        const uint16_t address=(uint16_t)(0x2000u+page*0x400u+
                                (unsigned)(tile_y[y]+4)*32u+col);
        total++;
        agree+=(cyc_render_nametable(address)==tile);
    }
    /* Deliberately fail closed on a partly populated/transitioning room.
     * Limited mutable tiles are allowed, wholesale wrong layout is not. */
    return total>=6u && agree*4u>=total*3u;
}
static int camera(const CviiiStage1Host0725 *h,uint8_t sel[3],
                  int *x,int *y)
{
    const uint8_t *ram=cyc_cpu_ram();
    if (!ram || ram[0x18u]!=4u ||
        ram[0x5Au]!=0x41u || ram[0x5Bu]!=0x84u ||
        ram[0x5Cu]!=0x51u || ram[0x5Du]!=0x8Du ||
        (cyc_render_line_mask(120)&0x08u)==0 ||
        cyc_render_line_bg_table(120)!=0x1000u) return 0;
    sel[0]=ram[0x34u];sel[1]=ram[0x35u];sel[2]=ram[0x36u];
    /* Original $65 bit7 identifies vertical-stage movement, not X.
     * That layout is only 256 pixels wide and cannot fill side margins. */
    if (sel[0]!=0u || (ram[0x65u]&0x80u) ||
        (sel[1]==1u && sel[2]==1u)) return 0;
    int local_x=(int)ram[0x53u]+((int)ram[0x54u]<<8);
    int ppu_x=cyc_render_line_scroll_x(120)&511;
    int ppu_y=cyc_render_line_scroll_y(120);
    if (ppu_y<118 || ppu_y>122) return 0;
    /* The original stage can begin a room at physical NT0 OR NT1,
     * including BLK 1-02 at PPU X=256 while $53/$54 is zero.
     * Accept only a proven 0/256 page phase and <=2px residual skew. */
    int phase=((ppu_x-(local_x&511)+256)&511)-256;
    int residual=phase;
    if (residual>126 || residual < -126) {
        residual=phase>0 ? phase-256 : phase+256;
    }
    if (residual < -2 || residual > 2) return 0;
    int true_x=local_x+residual;
    if (!room_loaded(h,sel,true_x,ppu_x)) return 0;
    *x=true_x;
    *y=0;
    return 1;
}

/* JP0800: the NES picture already scrolls from the real PPU on every
 * frame. When strict ROM/nametable attestation temporarily rejects the
 * room, NEVER leave the side scenery at an old frozen world position.
 * Integrate only small real scanline-X deltas into the last authenticated
 * ROM atlas camera; 0/511 modulo rollover is a normal 1-pixel change.
 * Selector changes remain untrusted until the ROM tile probes pass.
 */
enum { CVIII_PPU_SCROLL_STEP_0800=16 };
static int ppu_scroll_delta_0800(int before,int after)
{
    int delta=(after&511)-(before&511);
    if(delta>256)delta-=512;
    else if(delta<-256)delta+=512;
    return delta;
}
/* JP0790: genuine Stage 1 beginning has no scenery to its left.
 * Outside the first 85 pixels, the native NES view stays at wide X85
 * across ALL selector changes. Never jump it to X170/X0 at a door and
 * then snap back when an ephemeral room-join flag expires.
 * The persistent ROM atlas supplies real left/right adjoining scenes. */
static int viewport_center_0790(const uint8_t selector[3],int camera_x)
{
    if(selector && selector[0]==0u &&
       selector[1]==0u && selector[2]==0u &&
       camera_x>=0 && camera_x<CVIII_STAGE1_ORIGIN_0725)
        return camera_x;
    return CVIII_STAGE1_ORIGIN_0725;
}
const uint32_t *cviii_stage1_host_present_0725(CviiiStage1Host0725 *h,
    const uint32_t *frame,int *width,int *height,int enhanced)
{
    if (!h || !frame || !width || !height || *width!=256 || *height!=240)
        return frame;
    int active=enhanced && h->enabled && load(h);
    if (!active) {
        cviii_stage1_host_reset_0751(h);
        if (h->video_wide) {
            cyc_video_set_mode(NES_VIDEO_STOCK);
            h->video_wide=0;
        }
        return frame;
    }
    if (!h->video_wide) {
        cyc_video_set_mode(NES_VIDEO_16_9);
        h->video_wide=1;
    }
    cviii_stage1_seed_links_0782(h);

    /* Source attestation identifies camera/page, not the lifespan of the
     * already loaded map. Keep the LAST authenticated scene across arbitrarily
     * long horizontal room loads; never tile/copy a 16-pixel stage edge. */
    uint8_t selector[3]={0}; int camera_x=0,camera_y=0;
    int valid_camera=camera(h,selector,&camera_x,&camera_y);
    const uint8_t *ram=cyc_cpu_ram();
    const int horizontal_play=ram && ram[0x18u]==4u &&
        ram[0x34u]==0u && !(ram[0x65u]&0x80u) &&
        (cyc_render_line_mask(120)&0x08u);
    int center=CVIII_STAGE1_ORIGIN_0725;
    if(valid_camera) {
        int room_width=cviii_stage1_atlas_width_0751(&h->atlas,selector);
        if(room_width>=256 && camera_x>=0 && camera_x<=room_width-256) {
            cviii_stage1_join_accept_0751(&h->join,selector,camera_x,room_width);
            cviii_stage1_join_restore_0782(&h->join,selector,camera_x,room_width);
            center=viewport_center_0790(selector,camera_x);
            memcpy(h->last_verified_selector,selector,sizeof selector);
            h->last_verified_camera=camera_x;
            h->last_verified_center=center;
            h->has_verified_scene=1;
            h->last_ppu_scroll_x=cyc_render_line_scroll_x(120)&511;
            h->has_ppu_scroll_x=1;
            h->scroll_fallback_frames=0;
        } else valid_camera=0;
    }
    if(!valid_camera && horizontal_play && h->has_verified_scene) {
        /* Keep the authenticated ROOM, but move its atlas camera with the
         * same scanline PPU X that moves the central NES framebuffer. The
         * old implementation held last_verified_camera constant, causing
         * 4:3-only scrolling and motionless left/right side extensions.
         *
         * Do not accept a new room selector, 256px NT page jump or an
         * arbitrary warp by inference. Those still require camera() +
         * room_loaded() to authenticate their source geometry. */
        const int ppu_now=cyc_render_line_scroll_x(120)&511;
        if(h->has_ppu_scroll_x) {
            const int step=ppu_scroll_delta_0800(
                h->last_ppu_scroll_x,ppu_now);
            const int predicted=h->last_verified_camera+step;
            const int source_width=cviii_stage1_atlas_width_0751(
                &h->atlas,h->last_verified_selector);
            if(step>=-CVIII_PPU_SCROLL_STEP_0800 &&
               step<=CVIII_PPU_SCROLL_STEP_0800 &&
               source_width>=256 && predicted>=0 &&
               predicted<=source_width+CVIII_STAGE1_ORIGIN_0725) {
                h->last_verified_camera=predicted;
                h->last_verified_center=viewport_center_0790(
                    h->last_verified_selector,predicted);
                if(h->scroll_fallback_frames<UINT32_MAX)
                    h->scroll_fallback_frames++;
            } else {
                /* Large PPU jump: resync the physical phase without
                 * moving unverified world geometry. The next verified
                 * room re-anchors from the true CPU/PPU camera. */
                h->scroll_fallback_frames=0;
            }
        }
        h->last_ppu_scroll_x=ppu_now;
        h->has_ppu_scroll_x=1;
        memcpy(selector,h->last_verified_selector,sizeof selector);
        camera_x=h->last_verified_camera;
        center=h->last_verified_center;
        valid_camera=1;
    }
    if(!horizontal_play) {
        /* A death changes live game state, not the preloaded room atlas or
         * authenticated map of adjacent rooms. Keep graph and last scene;
         * the next valid checkpoint camera can recover its predecessor. */
        cviii_stage1_join_soft_reset_0782(&h->join);
        valid_camera=0;
    }
    for(int row=0;row<240;row++) {
        uint32_t *dst=h->pixels+(size_t)row*CVIII_STAGE1_WIDE_0725;
        for(int x=0;x<CVIII_STAGE1_WIDE_0725;x++)
            dst[x]=UINT32_C(0xFF000000);
        /* The entire 48-scanline NES status region is anchored to the
         * viewport, independent of the boundary-clamped world camera.
         * HUD and gameplay pixels are bit-identical to the original. */
        int native_x=row<CVIII_STAGE1_HUD_ROWS_0781 ?
            CVIII_STAGE1_ORIGIN_0725 : center;
        memcpy(dst+native_x,frame+(size_t)row*256u,
               256u*sizeof(uint32_t));
    }
    if(valid_camera) {
        const int width_px=cviii_stage1_atlas_width_0751(&h->atlas,selector);
        if(width_px>=256) {
            (void)cviii_stage1_atlas_paint_0724(&h->atlas,selector,
                camera_x,camera_y,h->pixels,CVIII_STAGE1_WIDE_0725,240,
                center,cyc_render_chr,cyc_render_color);
            /* JP0790: the predecoded Stage 1 atlas is a continuous
             * world scene, not a timed scene-copy effect. Paint each known
             * room ONLY in its true neighboring world coordinate. Current
             * room atlas rejects out-of-bounds tiles, so none overlaps.
             * This also fills the next room's right margin BEFORE the NES
             * selector changes; no speculative future-camera snap. */
            uint8_t neighbor[3];int neighbor_x=0;
            if(cviii_stage1_join_neighbor_0790(&h->join,selector,
                    camera_x,width_px,-1,neighbor,&neighbor_x))
                (void)cviii_stage1_atlas_paint_0724(&h->atlas,neighbor,
                    neighbor_x,camera_y,h->pixels,CVIII_STAGE1_WIDE_0725,240,
                    center,cyc_render_chr,cyc_render_color);
            if(cviii_stage1_join_neighbor_0790(&h->join,selector,
                    camera_x,width_px,1,neighbor,&neighbor_x))
                (void)cviii_stage1_atlas_paint_0724(&h->atlas,neighbor,
                    neighbor_x,camera_y,h->pixels,CVIII_STAGE1_WIDE_0725,240,
                    center,cyc_render_chr,cyc_render_color);
        }
    }
    *width=CVIII_STAGE1_WIDE_0725;
    return h->pixels;
}
