/* JP0803: one persistent Stage 1 world, reconstructed from authenticated
 * owner-original ROM atlas geometry. No ROM content is linked or published.
 * Room connections require independent original-game evidence.
 */
#ifndef CVIII_LEVEL1_WORLD_0803_H
#define CVIII_LEVEL1_WORLD_0803_H
#include "cviii_stage1_atlas_0724.h"
#include "cviii_room_catalog_0657.h"
#include <stdint.h>
#include <stddef.h>
enum { CVIII_WORLD_ROOMS_0803=8, CVIII_WORLD_ACTORS_0803=28,
       CVIII_WORLD_GROUPS_0804=5, CVIII_WORLD_TEMPLATES_0804=30,
       CVIII_WORLD_SOURCE_BYTES_0804=175 };
typedef enum {
    CVIII_WORLD_LEFT_0803=0, CVIII_WORLD_RIGHT_0803=1,
    CVIII_WORLD_UP_0803=2, CVIII_WORLD_DOWN_0803=3
} CviiiWorldDirection0803;
typedef struct {
    uint8_t selector[3];
    int width,height;
    int32_t x,y;
    uint8_t placed, visited;
} CviiiWorldRoom0803;
typedef struct {
    uint8_t active, room, slot, selector, frame, mirror, flags;
    int32_t x,y;
    uint8_t raw_x,raw_y,attrs;
    uint8_t original_type; /* original $054E+X slot allocator */
    uint32_t generation; /* advances only on new slot identity */
} CviiiWorldActor0803;
/* Five owner-ROM five-field source windows decode 30 generic room
 * installation records across stages 4,1,8,2,B (hex), NOT Stage 1.
 * A stage0 room must never activate any of these by accident. */
typedef struct {
    uint8_t source_group,source_index;
    uint8_t sprite_selector,frame_offset,initial_x,initial_y,mirror;
} CviiiWorldObjectTemplate0804;
typedef struct {
    uint8_t source_group,record_start,record_count,header[4];
    uint8_t active,room_index; /* last independently observed loader event */
    uint32_t activations; /* event count per distinct room */
} CviiiWorldObjectGroup0804;
/* Authentic original bank0A typed 4-byte / 7-byte source root per
 * stage-zero room. Spans are PROVEN STRUCTURE, not NPC spawn IDs. */
typedef struct {
    uint16_t root,end_exclusive,record_count;
    uint8_t width;
    uint8_t payload_len; /* private original bank0A room-source bytes */
    uint8_t payload[128]; /* bounded per-room resident resource */
} CviiiWorldSourceRoom0811;
typedef struct {
    CviiiWorldRoom0803 rooms[CVIII_WORLD_ROOMS_0803];
    CviiiWorldSourceRoom0811 source_rooms[CVIII_WORLD_ROOMS_0803];
    CviiiWorldActor0803 actors[CVIII_WORLD_ACTORS_0803];
    CviiiWorldObjectTemplate0804 templates[CVIII_WORLD_TEMPLATES_0804];
    CviiiWorldObjectGroup0804 groups[CVIII_WORLD_GROUPS_0804];
    uint8_t ready,placed_count,visited_count,templates_ready;
    uint8_t source_rooms_ready; /* all 8 original stage0 hierarchy keys */
    uint8_t source_payload_ready; /* 8 private original room resources resident */
    uint32_t actor_frame;
} CviiiLevel1World0803;

/* All eight source rooms are resident on success. One known horizontal
 * connection (1-01 to 1-02:0) is preplaced. Unknown branches stay loaded
 * but do not receive invented coordinates. Safe to call repeatedly. */
int cviii_world_build_0803(CviiiLevel1World0803 *world,
                          const CviiiStage1Atlas0724 *atlas);
/* Attach all EIGHT original stage0 source hierarchy leaves, not only
 * seen rooms; catalog must have passed original bank0A validation.
 * Transactional: no partially loaded world on unsupported leaf.
 */
int cviii_world_attach_source_rooms_0811(CviiiLevel1World0803 *world,
                   const CviiiRoomCatalog0657 *catalog);
/* After independently hashing and structurally validating original raw0A,
 * cache all Stage1 source records in game-owned memory, not Git files. */
int cviii_world_preload_source_payload_0812(CviiiLevel1World0803 *world,
               const uint8_t *original_bank0a,size_t bank_size);
int cviii_world_index_0803(const CviiiLevel1World0803 *world,
                           const uint8_t selector[3]);
/* Source-proven physical edge: reject inconsistent positions/cycles.
 * Updates only metadata; never mutates native CPU RAM or ROM atlas tiles. */
int cviii_world_connect_0803(CviiiLevel1World0803 *world,
                 const uint8_t first[3],const uint8_t next[3],
                 CviiiWorldDirection0803 direction);
/* 1 only when the room is placed in a connected coordinate frame. */
int cviii_world_camera_0803(const CviiiLevel1World0803 *world,
                const uint8_t selector[3],int local_x,int local_y,
                int32_t *x,int32_t *y);
/* JP0806: project ALL physically placed, original-ROM-derived rooms
 * through ONE global camera. Never tile-repeat edge pixels and never
 * write over the native 256px gameplay picture or 48-line HUD.
 * Returns 0 for unknown camera topology (caller can use legacy
 * source-verified neighboring-room extension). */
uint32_t cviii_world_paint_0806(const CviiiLevel1World0803 *world,
    const CviiiStage1Atlas0724 *atlas,const uint8_t room_key[3],
    int camera_x,int camera_y,uint32_t *dest,
    int width,int height,int native_center,uint16_t bg_table,
    uint8_t (*read_chr)(uint16_t),uint32_t (*read_color)(int));
int cviii_world_visit_0803(CviiiLevel1World0803 *world,
                           const uint8_t selector[3]);
/* Read the ACTUAL original 28 PRG26 object slots. Screen coordinates are
 * transformed to placed-room coordinates; live actor state is not invented
 * when original 6502 has not yet spawned/updated that object. The registry
 * is a nonauthoritative bridge for future Enhanced renderer integration. */
/* Original raw0E:$BE8B-$BF39. Caller authenticates the original SHA256
 * physical source window first; this exact bounded parser fails atomically. */
int cviii_world_preload_templates_0804(CviiiLevel1World0803 *world,
                const uint8_t *raw0e_source,size_t source_len);
/* Require BOTH the original CPU loader's decoded $34/$35/$36 stage
 * header and complete postcondition. This imported raw0E window
 * contains NO header for current Stage 1 ($34=0). */
int cviii_world_detect_loader_0805(CviiiLevel1World0803 *world,
            const uint8_t selector[3],const uint8_t ram[2048]);
void cviii_world_clear_live_0805(CviiiLevel1World0803 *world);
unsigned cviii_world_capture_live_0803(CviiiLevel1World0803 *world,
        const uint8_t selector[3],int local_camera_x,int local_camera_y,
        const uint8_t ram[2048]);
#endif
