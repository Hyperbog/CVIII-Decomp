#ifndef CVIII_STAGE1_ROM_0724_H
#define CVIII_STAGE1_ROM_0724_H
#include <stddef.h>
#include <stdint.h>
/* Read-only owner-ROM-backed Stage 1 background extraction.
 * Requires the exact Japanese Mapper24 retail cartridge, SHA-verified by
 * the caller. No proprietary graphics/level bytes are embedded.
 * This decodes static TILE IDS + ATTRIBUTE PALETTE SELECTORS only;
 * the runtime must resolve the game's authentic room CHR pages/palettes.
 */
typedef struct {
    uint16_t width_tiles, height_tiles;
    uint16_t metatile_count;
    uint8_t vertical;
    uint32_t source_layout_offset;
    uint32_t source_tsa_pattern_offset;
    uint32_t source_tsa_attribute_offset;
} CviiiStage1Room0724;
/* callback returns nonzero to continue, zero to abort; x/y in 8px tiles. */
typedef int (*CviiiStage1TileSink0724)(void *ctx, uint16_t x, uint16_t y,
    uint8_t tile_id, uint8_t palette_id);
/* 1 success, 0 unrecognized selector, -1 input/source/sink failure.
 * All source structures are validated before invoking the tile sink.
 */
int cviii_stage1_rom_0724(const uint8_t *rom, size_t len,
    const uint8_t selector[3], CviiiStage1TileSink0724 sink,
    void *ctx, CviiiStage1Room0724 *out);
#endif
