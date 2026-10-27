/* JP0751: ROM-only room seam and bounded transient side-column continuity.
 * Host presentation only, no original game source bytes or PPU writes. */
#ifndef CVIII_STAGE1_JOIN_0751_H
#define CVIII_STAGE1_JOIN_0751_H
#include <stdint.h>
enum { CVIII_JOIN_W=426, CVIII_JOIN_X=85, CVIII_JOIN_H=240,
       CVIII_JOIN_Y=32, CVIII_JOIN_SIDE=85, CVIII_JOIN_ROWS=208,
       CVIII_JOIN_HOLD_MAX=30, CVIII_JOIN_GAP_MAX=90 };
/* Persistent atlas-room adjacency: only source-proven connections. */
enum { CVIII_STAGE1_LINK_SLOTS_0782=8 };
typedef struct {
    uint8_t key[3],left[3],right[3];
    int left_width,right_width;
    unsigned has_left,has_right;
} CviiiRoomLink0782;
typedef struct {
    CviiiRoomLink0782 links[CVIII_STAGE1_LINK_SLOTS_0782];
    unsigned link_count;
    uint8_t last[3], adjacent[3], valid, joined;
    int last_camera, last_width, prior_width, direction;
    unsigned gap, hold_age, has_side;
    uint32_t cached_sides[CVIII_JOIN_ROWS*CVIII_JOIN_SIDE*2u];
} CviiiStage1Join0751;
void cviii_stage1_join_reset_0751(CviiiStage1Join0751 *join);
void cviii_stage1_join_gap_0751(CviiiStage1Join0751 *join);
/* Death, respawn or temporary PPU invalidity clears camera, not world. */
void cviii_stage1_join_soft_reset_0782(CviiiStage1Join0751 *join);
void cviii_stage1_join_link_0782(CviiiStage1Join0751 *join,
                                const uint8_t left[3],int left_width,
                                const uint8_t right[3],int right_width);
void cviii_stage1_join_restore_0782(CviiiStage1Join0751 *join,
                                   const uint8_t key[3],int camera,int width);
/* JP0790: independently paint known neighboring rooms on BOTH sides of
 * the current room, not only during a just-observed scene transition.
 * side=-1 for previous-left, +1 for next-right. The returned camera is
 * projected into the authentic neighboring room's atlas coordinates. */
int cviii_stage1_join_neighbor_0790(const CviiiStage1Join0751 *join,
          const uint8_t key[3],int camera,int width,int side,
          uint8_t neighbor[3],int *neighbor_camera);
void cviii_stage1_join_accept_0751(CviiiStage1Join0751 *join,
                                   const uint8_t selector[3],int camera,int width_px);
int cviii_stage1_join_previous_0751(const CviiiStage1Join0751 *join,
                                    int camera,int width_px,
                                    uint8_t old_selector[3],int *old_camera);
/* JP0823 visual-only subroom continuity: both BLK 1-03 halves are
 * decoded from the authenticated original ROM. This paints side margins
 * only; it does NOT certify a physical transition, connect world rooms,
 * install actors, extend AI or grant collision. A real visited-room link
 * always takes precedence when available. */
int cviii_stage1_neighbor_visual_0823(const uint8_t key[3],
    int camera_x,int width,int side,uint8_t neighbor[3],
    int *neighbor_camera);
void cviii_stage1_join_cache_0751(CviiiStage1Join0751 *join,
                                  const uint32_t frame[CVIII_JOIN_W*CVIII_JOIN_H]);
int cviii_stage1_join_hold_0751(CviiiStage1Join0751 *join,
                                uint32_t frame[CVIII_JOIN_W*CVIII_JOIN_H]);
#endif
