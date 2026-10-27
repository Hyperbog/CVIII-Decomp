/* JP0803: one persistent Stage 1 world, reconstructed from authenticated
 * owner-original ROM atlas geometry. No ROM content is linked or published.
 * Room connections require independent original-game evidence.
 */
#ifndef CVIII_LEVEL1_WORLD_0803_H
#define CVIII_LEVEL1_WORLD_0803_H
#include "cviii_stage1_atlas_0724.h"
#include "cviii_room_catalog_0657.h"
#include "cviii_stage1_source_link_0814.h"
#include "cviii_source_offscreen_0815.h"
#include "cviii_horizontal_sources_0816.h"
#include "cviii_horizontal_activation_0817.h"
#include "cviii_horizontal_child_0818.h"
#include "cviii_horizontal_lineage_0819.h"
#include "cviii_contact_effects_0821.h"
#include "cviii_extended_actor_0824.h"
#include "cviii_wide_source_admission_0825.h"
#include "cviii_wide_instance_0826.h"
#include "cviii_actor_vm_0827.h"
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
    uint8_t guest_adjacent_0824,local_coords_0824; /* original CPU state */
    uint32_t generation; /* advances only on new slot identity */
    /* Optional JP0814 original-ROM provenance. Never grants interaction. */
    uint16_t source_cpu_0814; /* exact matched original seven-byte record */
    uint32_t source_generation_0814; /* must equal active generation */
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
/* JP0813: original stage0/1/1 ($AB1F) resident 7-byte world sources.
 * "eligible" is the original $8205 admission, not an active game actor.
 * Object type remains raw; no guessed candles/AI. Epoch counts advance
 * only on independently attested chapel camera samples. */
typedef struct {
    uint16_t source_cpu, axis_world;
    uint8_t raw_type, local_x, eligible, local_axis, world_placed;
    int32_t world_x, world_y; /* only when source-verified room is placed */
    uint32_t entries, exits;
} CviiiStage1SourceLife0813;
enum { CVIII_STAGE1_CHAPEL_SOURCES_0813=9 };
/* JP0815: inert source-only candidate or genuine actor (never a hitbox).
 * Visual selector/frame are valid ONLY with 'actor_confirmed' and must
 * still be decoded by the existing original PRG26 sprite renderer. */
typedef struct {
    uint16_t source_cpu;
    uint8_t source_type, linked_slot, actor_confirmed;
    uint8_t guest_installed, guest_slot; /* original $054E slot, not OAM */
    uint8_t sprite_selector, sprite_frame, sprite_mirror, sprite_attrs;
    uint8_t point_region, interaction_policy;
    uint8_t visual_valid, sprite_pieces;
    uint16_t sprite_descriptor_cpu; /* original PRG26 compressed source */
    int32_t screen_x,screen_y;
    uint32_t actor_generation;
} CviiiSourceOffscreen0815;
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
    /* Persistent source identity is independent from 28-slot actor shadows. */
    CviiiStage1SourceLife0813 chapel[CVIII_STAGE1_CHAPEL_SOURCES_0813];
    uint32_t chapel_epochs;
    /* JP0814: instantaneous authenticated-original installation witnesses.
     * Do not interpret link presence as gameplay collision eligibility. */
    CviiiSourceLink0814 chapel_links[CVIII_STAGE1_CHAPEL_SOURCES_0813];
    uint32_t chapel_link_epochs;
    CviiiSourceOffscreen0815 chapel_projection[CVIII_STAGE1_CHAPEL_SOURCES_0813];
    uint32_t chapel_projection_epochs;
    uint8_t chapel_margin_actor_count;
    /* JP0816: resident original room-cell tables; not spawned actors. */
    CviiiHorizontalRoom0816 horizontal[CVIII_HORIZONTAL_ROOMS_0816];
    CviiiHorizontalSelection0816 horizontal_last;
    uint32_t horizontal_observations;
    uint8_t horizontal_ready;
    /* JP0817: source-slot states, NOT actor slots or inferred spawns. */
    CviiiHorizontalLive0817 horizontal_live[CVIII_SOURCE_SLOTS_0817];
    CviiiHorizontalMotion0817 horizontal_predicted[CVIII_SOURCE_SLOTS_0817];
    uint32_t horizontal_scheduler_samples;
    uint32_t horizontal_row_activations, horizontal_row_deactivations;
    uint32_t horizontal_event_transitions;
    /* Source-to-child witnesses from original $8B50, independent of OAM
     * visibility and actor simulation. Transition counts are observed
     * snapshot changes, never proven natural spawn/despawn cycles. */
    CviiiHorizontalChild0818 horizontal_children[13];
    uint32_t horizontal_child_samples;
    uint32_t horizontal_child_allocations, horizontal_child_removals;
    uint8_t horizontal_child_room;
    /* JP0819: six CURRENT original parent source census snapshots.
     * Counts are observation transitions, not verified spawn/despawn
     * or simulated offscreen updates. */
    CviiiParentCensus0819 parent_census[CVIII_SOURCE_PARENTS_0819];
    uint32_t parent_census_epochs;
    uint32_t parent_new_witnesses, parent_lost_witnesses;
    uint32_t parent_released_while_child_allocated;
    /* JP0820: this child outlived its row32 source; an identical
     * source slot later reappearing is NOT proof of source identity.
     * Room changes and reset make provenance unknown, never dead. */
    uint16_t horizontal_unresolved_lineage_mask;
    uint32_t horizontal_source_reuse_warnings;
    /* JP0821: frame-level original $B5DF special slot23 signature.
     * Entry counts mean observed signatures, NOT proven B5DF calls.
     * The original OAM and guest CPU remain authoritative. */
    CviiiEffect23Witness0821 effect23;
    uint32_t effect23_observations, effect23_entries;
    uint8_t effect23_room;
    /* JP0825: persistent native source definitions; CPU-ownership
     * is separately witnessed. Never use READY sources as hitboxes. */
    CviiiWideSources0825 wide_sources_0825;
    CviiiWideRuntime0826 wide_runtime_0826;
    /* JP0827: bounded physical-ROM opcode execution for the genuine
     * actor slots. Counterfactual replay on isolated private RAM,
     * NEVER original CPU gameplay authority. */
    uint32_t actor_vm_probes_0827,actor_vm_matched_0827;
    uint32_t actor_vm_mismatched_0827,actor_vm_deferred_0827;
    uint16_t actor_vm_stop_pc_0827[CVIII_WIDE_SOURCE_COUNT_0825];
    uint8_t actor_vm_last_status_0827[CVIII_WIDE_SOURCE_COUNT_0825];
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
/* Read-only source eligibility for vertical Stage1 chapel, valid camera
 * only. No active actors are created, changed, or prolonged in guest RAM.
 * Returns number eligible, or -1 for an unsupported/inconsistent state. */
/* Called ONCE with already authenticated owner raw0A before its temporary
 * source bank is released. Transactional; never stores original code bank.
 * All seven horizontal leaves are source-indexed; no spawn simulation. */
int cviii_world_preload_horizontal_0816(CviiiLevel1World0803 *world,
                      const uint8_t raw0a[16384],size_t bank_len);
/* Observe original CPU $53/$54/$62/$07F6 and source phase; returns
 * selected source cell, 0 for no bounded source, -1 for unsupported.
 * Read-only original source identities, no hitboxes or guest RAM writes. */
int cviii_world_observe_horizontal_0816(CviiiLevel1World0803 *world,
                    const uint8_t selector[3],const uint8_t ram[2048]);
/* Sample actual $07C2/$07C8/$07E0 source slots after the authentic
 * CPU frame. $83D1 math is a *next-step prediction*, not injected
 * into the original game. Counters count observations, NOT spawn events. */
int cviii_world_observe_scheduler_0817(CviiiLevel1World0803 *world,
                    const uint8_t selector[3],const uint8_t ram[2048]);
/* Correlate only already-allocated original $3D children to the
 * row32 source index recorded by original $8B50 in $0645,X.
 * No extra guest actor, sprite, timer or collision side effects. */
int cviii_world_observe_children_0818(CviiiLevel1World0803 *world,
                    const uint8_t selector[3],const uint8_t ram[2048]);
int cviii_world_track_chapel_0813(CviiiLevel1World0803 *world,
                  const uint8_t selector[3],int camera_y);
/* Correlate source bytes with exact original $82xx RAM postconditions.
 * Called ONLY after camera-attested JP0813 source refresh.
 * Returns unambiguous original-slot associations, or -1 if unsupported.
 * Never constructs guest actors, sprites, hitboxes, or damage events. */
int cviii_world_link_chapel_0814(CviiiLevel1World0803 *world,
                   const uint8_t selector[3],const uint8_t ram[2048]);
/* Read-only prediction: all 9 original source points, associated sprite
 * descriptors only where a guest actor actually exists. No hitboxes or
 * wider gameplay collision/pickup rules are enabled by this observer. */
int cviii_world_probe_chapel_0815(CviiiLevel1World0803 *world,
   const uint8_t selector[3],int camera_x,int camera_y,
   int native_left,int wide_width,
   const uint8_t authenticated_prg26[16384]);
/* Bounded original bank0B opcode replay for currently authenticated
 * source-linked CPU actors; bank must be SHA-authenticated by host.
 * This models a would-call-B486 snapshot; does not claim CPU actually
 * invoked B486, and never changes machine RAM or approves native combat. */
int cviii_world_probe_vm_0827(CviiiLevel1World0803 *world,
        const uint8_t ram[2048],const uint8_t bank0b[16384]);
void cviii_world_clear_live_0805(CviiiLevel1World0803 *world);
unsigned cviii_world_capture_live_0803(CviiiLevel1World0803 *world,
        const uint8_t selector[3],int local_camera_x,int local_camera_y,
        const uint8_t ram[2048]);
#endif
