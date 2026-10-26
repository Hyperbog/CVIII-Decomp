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
    if(h)cviii_stage1_join_reset_0751(&h->join);
}
int cviii_stage1_host_rom_0725(CviiiStage1Host0725 *h,const char *path)
{
    if (!h || !path || !*path || strlen(path)>=sizeof h->rom_path) return 0;
    memcpy(h->rom_path,path,strlen(path)+1u);
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
    for (int row=0;row<240;row++) {
        uint32_t *dest=h->pixels+(size_t)row*CVIII_STAGE1_WIDE_0725;
        for (int i=0;i<CVIII_STAGE1_WIDE_0725;i++)dest[i]=0xFF000000u;
        memcpy(dest+CVIII_STAGE1_ORIGIN_0725,frame+(size_t)row*256u,
               256u*sizeof(uint32_t));
    }
    uint8_t selector[3]; int camera_x,camera_y;
    if (camera(h,selector,&camera_x,&camera_y)) {
        const int room_width=cviii_stage1_atlas_width_0751(&h->atlas,selector);
        if (room_width>=256 && camera_x>=0 && camera_x<=room_width-256) {
            cviii_stage1_join_accept_0751(&h->join,selector,camera_x,room_width);
            /* The actual current-room atlas fills side columns first. */
            (void)cviii_stage1_atlas_paint_0724(&h->atlas,selector,
                camera_x,camera_y,h->pixels,CVIII_STAGE1_WIDE_0725,240,
                CVIII_STAGE1_ORIGIN_0725,cyc_render_chr,cyc_render_color);
            /* Source-verified previous room adjoins the new room where
             * current room geometry is out-of-bounds. The original center
             * and all original sprite/collision hardware remain untouched. */
            uint8_t prior[3]; int prior_camera;
            if (cviii_stage1_join_previous_0751(&h->join,camera_x,room_width,
                                                 prior,&prior_camera))
                (void)cviii_stage1_atlas_paint_0724(&h->atlas,prior,
                    prior_camera,camera_y,h->pixels,CVIII_STAGE1_WIDE_0725,240,
                    CVIII_STAGE1_ORIGIN_0725,cyc_render_chr,cyc_render_color);
            cviii_stage1_join_cache_0751(&h->join,h->pixels);
        } else cviii_stage1_join_gap_0751(&h->join);
    } else {
        const uint8_t *ram=cyc_cpu_ram();
        /* Hold only across short, horizontal Stage1 gameplay transitions.
         * Never hold over title, game-over, vertical rooms or state reset. */
        int eligible=ram && ram[0x18u]==4u && ram[0x34u]==0u &&
            !(ram[0x65u]&0x80u) && (cyc_render_line_mask(120)&0x08u);
        if (eligible) {
            cviii_stage1_join_gap_0751(&h->join);
            (void)cviii_stage1_join_hold_0751(&h->join,h->pixels);
        } else cviii_stage1_host_reset_0751(h);
    }
    *width=CVIII_STAGE1_WIDE_0725;
    return h->pixels;
}
