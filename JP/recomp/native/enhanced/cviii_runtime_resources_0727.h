#ifndef CVIII_RUNTIME_RESOURCES_0727_H
#define CVIII_RUNTIME_RESOURCES_0727_H
#include "cviii_stage1_atlas_0724.h"
#include "cviii_chr_index_0598.h"
#include <stddef.h>
#include <stdint.h>

/* Initial, game-owned launch-time resource importer.
 * The original Japanese ROM stays on the user's computer. Runtime-produced
 * geometry is presentation-only; the native 6502 gameplay remains unchanged.
 * Resource schemas must be independently versioned as more stages are added.
 */
#define CVIII_RUNTIME_ROM_BYTES_0727 393232u
#define CVIII_RUNTIME_STAGE1_SCHEMA_0727 1u
typedef enum {
    CVIII_RESOURCE_READY_0727 = 1,
    CVIII_RESOURCE_MISSING_0727 = -1,
    CVIII_RESOURCE_IO_0727 = -2,
    CVIII_RESOURCE_IDENTITY_0727 = -3,
    CVIII_RESOURCE_DECODE_0727 = -4
} CviiiResourceStatus0727;

/* General SHA-256 bytes; usable by later resource domains/cache validators. */
void cviii_sha256_0727(const uint8_t *data, size_t length, uint8_t digest[32]);

/* Authenticate exact Japanese Mapper24 retail input and build Stage 1 tiles
 * transactionally. Returned atlas contains zero ROM buffers or file handles.
 * The caller owns the validated ROM path and may retry with a different one.
 * No serialized resource cache or non-Stage-1 assets are claimed yet.
 */
CviiiResourceStatus0727 cviii_stage1_resource_open_0727(
    const char *rom_path, CviiiStage1Atlas0724 *destination);

/* Combined one-pass importer: produces both Stage 1 tile geometry and
 * the existing authenticated 8,192-tile CHR pixel index from the same
 * owner-ROM input. Both outputs are transactional. When chr_destination is
 * NULL, no CHR index is generated. The ROM is read and SHA256-checked once.
 */
CviiiResourceStatus0727 cviii_game_resources_open_0727(
    const char *rom_path, CviiiStage1Atlas0724 *atlas_destination,
    CviiiChrIndex *chr_destination);

/* Optional canonical disk cache; only source-authenticated resources.
 * The owner ROM is SHA-256 validated on EVERY run before the cache is read.
 * Missing/corrupt/wrong-schema caches transparently rebuild in memory.
 * A null/empty cache path disables caching without breaking game launch.
 */
CviiiResourceStatus0727 cviii_game_resources_cached_open_0729(
    const char *rom_path, const char *cache_path,
    CviiiStage1Atlas0724 *atlas_destination,CviiiChrIndex *chr_destination);
#endif
