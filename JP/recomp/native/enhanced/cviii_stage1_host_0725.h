#ifndef CVIII_STAGE1_HOST_0725_H
#define CVIII_STAGE1_HOST_0725_H
#include "cviii_stage1_atlas_0724.h"
#include "cviii_chr_index_0598.h"
#include "cviii_stage1_join_0751.h"
#include "cviii_level1_world_0803.h"
#include <stdint.h>
/* Game-owned read-only Enhanced presentation, no guest CPU/PPU mutations.
 * ROM identity is verified by JP_ORIGINAL_JP_ROM at CMake configuration.
 */
/* Original NES HUD occupies scanlines 0..47. It is a fixed screen layer
 * independent of the game world's boundary-clamped camera offset. */
enum { CVIII_STAGE1_WIDE_0725=426, CVIII_STAGE1_ORIGIN_0725=85,
       CVIII_STAGE1_HUD_ROWS_0781=48 };
typedef struct {
    CviiiStage1Atlas0724 atlas;
    CviiiChrIndex *runtime_assets; /* optional JP0728 preloaded original CHR index */
    uint32_t pixels[CVIII_STAGE1_WIDE_0725*240];
    char rom_path[1024];
    char resource_cache_path[1024]; /* optional user-private JP0729 cache */
    CviiiStage1Join0751 join; /* original previous-room presentation */
    CviiiLevel1World0803 world; /* persistent coordinate graph and actor registry */
    uint8_t last_verified_selector[3];
    int last_verified_camera, last_verified_center;
    int has_verified_scene; /* retains authenticated room between transitions */
    int last_ppu_scroll_x; /* authoritative visible scanline modulo-512 X */
    int has_ppu_scroll_x; /* reset with scene, never serialized to saves */
    unsigned scroll_fallback_frames; /* diagnostic consecutive step tracking */
    int enabled, attempted, video_wide;
} CviiiStage1Host0725;
/* Options are only applied to this presentation object, not guest memory. */
void cviii_stage1_host_reset_0751(CviiiStage1Host0725 *host);
int cviii_stage1_host_rom_0725(CviiiStage1Host0725 *h, const char *path);
int cviii_stage1_host_cache_0729(CviiiStage1Host0725 *h, const char *path);
void cviii_stage1_host_mode_0725(CviiiStage1Host0725 *h,int enabled);
const uint32_t *cviii_stage1_host_present_0725(CviiiStage1Host0725 *h,
 const uint32_t *game_frame,int *width,int *height,int enhanced);
#endif
