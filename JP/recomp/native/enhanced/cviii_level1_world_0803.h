/* JP0803: one persistent Stage 1 world, reconstructed from authenticated
 * owner-original ROM atlas geometry. No ROM content is linked or published.
 * Room connections require independent original-game evidence.
 */
#ifndef CVIII_LEVEL1_WORLD_0803_H
#define CVIII_LEVEL1_WORLD_0803_H
#include "cviii_stage1_atlas_0724.h"
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
} CviiiWorldActor0803;
/* Thirty owner-ROM five-field installation records, preloaded once
 * for all five source windows. Records describe original loader inputs,
 * NOT simulated actors or invented AI/spawn positions. */
typedef struct {
    uint8_t source_group,source_index;
    uint8_t sprite_selector,frame_offset,initial_x,initial_y,mirror;
} CviiiWorldObjectTemplate0804;
typedef struct {
    uint8_t source_group,record_start,record_count,header[4];
    uint8_t active,room_index; /* last independently observed loader event */
    uint32_t activations; /* event count per distinct room */
} CviiiWorldObjectGroup0804;
typedef struct {
    CviiiWorldRoom0803 rooms[CVIII_WORLD_ROOMS_0803];
    CviiiWorldActor0803 actors[CVIII_WORLD_ACTORS_0803];
    CviiiWorldObjectTemplate0804 templates[CVIII_WORLD_TEMPLATES_0804];
    CviiiWorldObjectGroup0804 groups[CVIII_WORLD_GROUPS_0804];
    uint8_t ready,placed_count,visited_count,templates_ready;
    uint32_t actor_frame;
} CviiiLevel1World0803;

/* All eight source rooms are resident on success. One known horizontal
 * connection (1-01 to 1-02:0) is preplaced. Unknown branches stay loaded
 * but do not receive invented coordinates. Safe to call repeatedly. */
int cviii_world_build_0803(CviiiLevel1World0803 *world,
                          const CviiiStage1Atlas0724 *atlas);
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
/* Require the original CPU loader's complete RAM postcondition,
 * never spawn a template merely because it was preloaded. */
int cviii_world_detect_loader_0805(CviiiLevel1World0803 *world,
            const uint8_t selector[3],const uint8_t ram[2048]);
void cviii_world_clear_live_0805(CviiiLevel1World0803 *world);
unsigned cviii_world_capture_live_0803(CviiiLevel1World0803 *world,
        const uint8_t selector[3],int local_camera_x,int local_camera_y,
        const uint8_t ram[2048]);
#endif
