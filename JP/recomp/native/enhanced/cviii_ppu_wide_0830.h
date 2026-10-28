/* Game-agnostic, read-only PPU wide strip painter.
 * The native 256x240 pixels, all 6502/PPU/IRQ/AI execution and entity
 * spawning remain unchanged. This renderer uses only original PPU pages,
 * rejects mirrored/unpopulated pages and proves on-screen pixel parity
 * before extending them outside the native gameplay picture.
 * It is NOT a complete ROM-derived world map or offscreen NPC simulator.
 */
#ifndef CVIII_PPU_WIDE_0830_H
#define CVIII_PPU_WIDE_0830_H
#include <stdint.h>
typedef struct {
    uint8_t (*nametable)(uint16_t);
    uint8_t (*chr)(uint16_t);
    uint32_t (*color)(int);
    int (*scroll_x)(int), (*scroll_y)(int);
    uint16_t (*bg_table)(int);
    uint8_t (*mask)(int);
    const uint8_t *oam; /* optional 256 original bytes; used to skip sprites */
} CviiiPpuWideSource0830;
/* Returns number of background margin pixels painted, or zero on any
 * unverified/non-horizontal/no-background scene. Does not write within
 * [native_x, native_x+255], nor above the 48-line fixed HUD. A zero
 * return leaves the caller's destination bytes completely unchanged.
 */
uint32_t cviii_ppu_wide_paint_0830(
    const CviiiPpuWideSource0830 *src,
    const uint32_t *native, uint32_t *wide,
    int width,int height,int native_x);
#endif
