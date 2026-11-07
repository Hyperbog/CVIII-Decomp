/* JP0807 original PRG26 descriptor rendering of already-active world
 * object slots outside the NES viewport. Gameplay/OAM stay authoritative. */
#ifndef CVIII_WORLD_SPRITES_0807_H
#define CVIII_WORLD_SPRITES_0807_H
#include "cviii_level1_world_0803.h"
#include <stdint.h>
enum { CVIII_SPRITE_BANK_BYTES_0807=16384 };
uint32_t cviii_world_sprites_draw_0807(const CviiiLevel1World0803 *world,
    const uint8_t current_room[3],int camera_x,int camera_y,
    int native_center,uint32_t *dst,int width,int height,
    const uint8_t bank[CVIII_SPRITE_BANK_BYTES_0807],
    const uint8_t ram[2048],uint16_t ppu_sprite_table,
    int ppu_sprite16,uint8_t (*chr)(uint16_t),
    uint32_t (*color)(int));
#endif
