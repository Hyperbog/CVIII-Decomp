#ifndef CVIII_STAGE1_HOST_0725_H
#define CVIII_STAGE1_HOST_0725_H
#include "cviii_stage1_atlas_0724.h"
#include "cviii_chr_index_0598.h"
#include <stdint.h>
/* Game-owned read-only Enhanced presentation, no guest CPU/PPU mutations.
 * ROM identity is verified by JP_ORIGINAL_JP_ROM at CMake configuration.
 */
enum { CVIII_STAGE1_WIDE_0725=426, CVIII_STAGE1_ORIGIN_0725=85 };
typedef struct {
    CviiiStage1Atlas0724 atlas;
    CviiiChrIndex *runtime_assets; /* optional JP0728 preloaded original CHR index */
    uint32_t pixels[CVIII_STAGE1_WIDE_0725*240];
    char rom_path[1024];
    int enabled, attempted, video_wide;
} CviiiStage1Host0725;
/* Options are only applied to this presentation object, not guest memory. */
int cviii_stage1_host_rom_0725(CviiiStage1Host0725 *h, const char *path);
void cviii_stage1_host_mode_0725(CviiiStage1Host0725 *h,int enabled);
const uint32_t *cviii_stage1_host_present_0725(CviiiStage1Host0725 *h,
 const uint32_t *game_frame,int *width,int *height,int enhanced);
#endif
