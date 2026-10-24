/* JP0725 - ROM-only Stage 1 background compositor for the native
 * Enhanced Edition. Original CPU, PPU, sprite pipeline and savestates
 * remain authoritative. Never include game resources in public source. */
#include "cviii_stage1_host_0725.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include "cyc_video.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef CVIII_STAGE1_ROM_PATH
#define CVIII_STAGE1_ROM_PATH ""
#endif

/* The production importer accepts only the source-validated Japanese
 * Mapper24 retail cartridge. Public tests must explicitly opt into invented
 * synthetic fixtures and cannot accidentally loosen the shipping gate.
 * FNV is an identity cross-check; the private CMake build separately
 * authenticates the original image's full SHA256.
 */
static int source_identity(const uint8_t *rom,size_t n)
{
#ifdef CVIII_STAGE1_TEST_SYNTHETIC_ROM
    (void)rom;
    return n==393232u;
#else
    if (n!=393232u) return 0;
    uint64_t h=UINT64_C(0xcbf29ce484222325);
    for (size_t i=0;i<n;i++) {
        h^=rom[i];
        h*=UINT64_C(0x100000001b3);
    }
    return h==UINT64_C(0x76615b120049ad3f);
#endif
}
static int load(CviiiStage1Host0725 *h)
{
    if (h->atlas.loaded) return 1;
    if (h->attempted) return 0;
    h->attempted=1;
    const char *path=h->rom_path[0] ? h->rom_path : CVIII_STAGE1_ROM_PATH;
    if (!path[0]) return 0; /* no owner ROM supplied: fail closed */
    FILE *f=fopen(path,"rb");
    if (!f) {
        fprintf(stderr,"CVIII JP0725: private Stage 1 ROM not found; stock video retained\n");
        return 0;
    }
    uint8_t *rom=(uint8_t *)malloc(393232u);
    if (!rom) { fclose(f); return 0; }
    size_t n=fread(rom,1,393232u,f);
    int extra=fgetc(f),error=ferror(f);
    fclose(f);
    int ok=extra==EOF && !error && source_identity(rom,n) &&
           cviii_stage1_atlas_load_0724(&h->atlas,rom,n)==1;
    free(rom);
    if (!ok) fprintf(stderr,"CVIII JP0725: rejected Stage 1 ROM source; stock video retained\n");
    return ok;
}

int cviii_stage1_host_rom_0725(CviiiStage1Host0725 *h,const char *path)
{
    if (!h || !path || !*path || strlen(path)>=sizeof h->rom_path) return 0;
    memcpy(h->rom_path,path,strlen(path)+1u);
    h->attempted=0;
    h->atlas.loaded=0;
    return 1;
}
void cviii_stage1_host_mode_0725(CviiiStage1Host0725 *h,int enabled)
{
    if (h) h->enabled=!!enabled;
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
    /* Original $65 bit7 marks vertical room orientation. There $53/$54\n     * tracks Y instead of X, and the static room is only 256px wide.\n     * Side scenery is therefore deliberately suppressed. */
    if (sel[0]!=0 || (ram[0x65u]&0x80u) ||
        (sel[1]==1u && sel[2]==1u)) return 0;
    uint8_t tile,palette;
    if (!cviii_stage1_atlas_get_0724(&h->atlas,sel,0,0,&tile,&palette))
        return 0;
    const int room_x=ram[0x53u]+(ram[0x54u]<<8);
    const int actual_ppu_x=cyc_render_line_scroll_x(120)&511;
    const int dx=((room_x-actual_ppu_x+256)&511)-256;
    /* Transition/loading frames can carry old nametable/selector state. */
    if (dx < -2 || dx > 2) return 0;
    const int actual_ppu_y=cyc_render_line_scroll_y(120);
    if (actual_ppu_y<118 || actual_ppu_y>122) return 0;
    int aligned=(room_x&~511)+actual_ppu_x;
    if (aligned-room_x>256) aligned-=512;
    if (room_x-aligned>256) aligned+=512;
    *x=aligned;
    *y=0; /* four reserved HUD tile rows; no Stage 1 horizontal Y camera */
    return 1;
}
const uint32_t *cviii_stage1_host_present_0725(CviiiStage1Host0725 *h,
    const uint32_t *frame,int *width,int *height,int enhanced)
{
    if (!h || !frame || !width || !height || *width!=256 || *height!=240)
        return frame;
    int active=enhanced && h->enabled && load(h);
    if (!active) {
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
        (void)cviii_stage1_atlas_paint_0724(&h->atlas,selector,
            camera_x,camera_y,h->pixels,CVIII_STAGE1_WIDE_0725,240,
            CVIII_STAGE1_ORIGIN_0725,cyc_render_chr,cyc_render_color);
    }
    *width=CVIII_STAGE1_WIDE_0725;
    return h->pixels;
}
