/* Recomp runtime: preload every structurally indexed room resource and
 * every bounded source TSA definition from the owner's authenticated ROM.
 * This is READ-ONLY CONTENT. Game-owned spawn/AI/items remain authoritative.
 * Source rows are not inferred enemy/NPC/item identities or tile maps.
 */
#ifndef CVIII_LEVEL_PRELOAD_0829_H
#define CVIII_LEVEL_PRELOAD_0829_H
#include "cviii_room_catalog_0657.h"
#include "cviii_rom_tsa_catalog_0730.h"
#include <stddef.h>
#include <stdint.h>
enum {
    CVIII_PRELOAD_STAGES_0829=15,
    CVIII_PRELOAD_ROOMS_0829=135,
    CVIII_PRELOAD_BANK_BYTES_0829=16384
};
typedef struct {
    uint8_t stage, subarea, room, record_width;
    uint16_t source_cpu, length, record_count;
} CviiiRoomResource0829;
typedef struct {
    /* Includes every validated source record, not only visited rooms. */
    uint8_t source_bank[CVIII_PRELOAD_BANK_BYTES_0829];
    CviiiRoomResource0829 room[CVIII_PRELOAD_ROOMS_0829];
    uint16_t first[CVIII_PRELOAD_STAGES_0829];
    uint8_t count[CVIII_PRELOAD_STAGES_0829];
    CviiiTsaCatalog0730 tsa; /* 14 bounded regions; 1 unsupported */
    uint8_t loaded;
    uint8_t active_stage; /* presentation selection, 0xff until gameplay */
    uint32_t stage_changes;
} CviiiLevelPreload0829;

/* Fail-closed, transactional import; release checks entire original ROM
 * SHA-256, source-bank hierarchy, record terminators and TSA bounds.
 * The synthetic exception exists ONLY in the unit-test target.
 * Never writes to emulated CPU/PPU RAM or runs stage scripts.
 */
int cviii_level_preload_bytes_0829(const uint8_t *rom,size_t bytes,
                                  CviiiLevelPreload0829 *out);
int cviii_level_preload_open_0829(const char *original_rom,
                                 CviiiLevelPreload0829 *out);

/* Level binding is metadata-only. Selecting an unseen stage never causes
 * an entity, chest, item, NPC, AI routine, or collision to be activated.
 */
int cviii_level_preload_stage_0829(CviiiLevelPreload0829 *preload,
                                   unsigned stage);
/* Returns resident opaque original bytes only for an exact indexed room.
 * No caller may interpret them as actor IDs without a stage-specific decoder.
 * Returns NULL and clears output on any unsupported selector.
 */
const uint8_t *cviii_level_preload_room_0829(
    const CviiiLevelPreload0829 *preload,unsigned stage,
    unsigned subarea,unsigned room,
    size_t *source_length,unsigned *record_width,unsigned *record_count);
#endif
