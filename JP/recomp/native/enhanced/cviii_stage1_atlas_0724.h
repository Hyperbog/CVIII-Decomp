#ifndef CVIII_STAGE1_ATLAS_0724_H
#define CVIII_STAGE1_ATLAS_0724_H
#include "cviii_stage1_rom_0724.h"
#include <stdint.h>
/* Static atlas: full stage data loaded from the owner ROM before any gameplay.
 * No source bytes are embedded. Dynamic PPU writes may override this
 * presentation-only backdrop in the game-owned compositor.
 */
#define CVIII_STAGE1_ROOMS_0724 8u
#define CVIII_STAGE1_TILES_0724 16640u
typedef struct {
    CviiiStage1Room0724 rooms[CVIII_STAGE1_ROOMS_0724];
    uint16_t offsets[CVIII_STAGE1_ROOMS_0724 + 1u];
    uint8_t tile[CVIII_STAGE1_TILES_0724];
    uint8_t palette[CVIII_STAGE1_TILES_0724];
    uint8_t loaded;
} CviiiStage1Atlas0724;
/* 1 for complete transactional load; failure leaves destination unchanged. */
int cviii_stage1_atlas_load_0724(CviiiStage1Atlas0724 *atlas,
    const uint8_t *rom,size_t rom_len);
/* 1 if valid static tile, 0 if unknown/outside the defined source room. */
int cviii_stage1_atlas_get_0724(const CviiiStage1Atlas0724 *atlas,
    const uint8_t selector[3],unsigned x,unsigned y,
    uint8_t *tile,uint8_t *palette);
/* Paint only the side margins using currently authentic NES CHR/palette
 * mapper views; center native pixels are NEVER modified by this function.
 * camera_x/y are caller-supplied room-local pixel offsets; never guessed.
 * Returns number of side pixels actually reconstructed.
 */
uint32_t cviii_stage1_atlas_paint_0724(const CviiiStage1Atlas0724 *atlas,
    const uint8_t selector[3], int camera_x,int camera_y,
    uint32_t *dst,int width,int height,int center_x,
    uint8_t (*read_chr)(uint16_t),uint32_t (*read_color)(int));
#endif
