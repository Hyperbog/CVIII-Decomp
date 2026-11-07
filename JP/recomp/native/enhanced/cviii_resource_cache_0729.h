#ifndef CVIII_RESOURCE_CACHE_0729_H
#define CVIII_RESOURCE_CACHE_0729_H
#include "cviii_runtime_resources_0727.h"

/* CVRSC029/v1: platform-independent little-endian private disk cache.
 * Only SHA-256-authenticated ROM-derived Stage 1 geometry and the
 * full 8192-tile original CHR index. No guest CPU/PPU or save-state data.
 * Return 1 on hit/write; 0 on miss, corruption, or I/O failure.
 * A failed read NEVER alters the caller's existing resource objects.
 */
#define CVIII_RESOURCE_CACHE_SCHEMA_0729 1u
int cviii_resource_cache_read_0729(const char *cache_path,
 const uint8_t original_sha256[32], CviiiStage1Atlas0724 *atlas,
 CviiiChrIndex *chr);
int cviii_resource_cache_write_0729(const char *cache_path,
 const uint8_t original_sha256[32], const CviiiStage1Atlas0724 *atlas,
 const CviiiChrIndex *chr);
#endif
