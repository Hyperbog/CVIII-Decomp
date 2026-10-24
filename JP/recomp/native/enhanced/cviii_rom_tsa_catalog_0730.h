#ifndef CVIII_ROM_TSA_CATALOG_0730_H
#define CVIII_ROM_TSA_CATALOG_0730_H
#include <stdint.h>
#include <stddef.h>

/* Source-bounded Japanese original-ROM 32x32 TSA pattern catalog.
 * Stage1 palette bytes are independently verified; other stage palette
 * semantics, layout selectors and complete maps are still unverified.
 */
#define CVIII_TSA_REGIONS_0730 15u
#define CVIII_TSA_PATTERNS_0730 1478u
#define CVIII_TSA_PATTERN_BYTES_0730 (CVIII_TSA_PATTERNS_0730*16u)
typedef struct {
    const char *name;
    uint32_t source_start;
    uint32_t source_end_inclusive;
    uint16_t pattern_count; /* zero: source is unresolved, not decoded */
    uint8_t palette_verified;
} CviiiTsaRegion0730;
typedef struct {
    uint16_t offsets[CVIII_TSA_REGIONS_0730+1u];
    uint8_t tiles[CVIII_TSA_PATTERN_BYTES_0730];
    uint8_t wallachia_attributes[145u];
    uint8_t loaded;
} CviiiTsaCatalog0730;

/* Metadata includes one deliberately unresolved Clocktower span (84*16+12).
 * Source region IDs are stable for this schema.
 */
const CviiiTsaRegion0730 *cviii_tsa_regions_0730(void);
/* Copies verified-offset 4x4 patterns from an authenticated ROM; neither
 * parses full stages nor alters guest hardware. Transactional on failure.
 */
int cviii_tsa_catalog_load_0730(const uint8_t *rom,size_t n,
                                  CviiiTsaCatalog0730 *out);
/* Return 1 and all 16 8px tile IDs when structurally decoded, else 0.
 * *has_attributes is 1 only for proven original Wallachia palettes.
 */
int cviii_tsa_get_0730(const CviiiTsaCatalog0730 *catalog,
    unsigned region,unsigned pattern,uint8_t out_tiles[16],
    uint8_t *attribute,uint8_t *has_attributes);
#endif
