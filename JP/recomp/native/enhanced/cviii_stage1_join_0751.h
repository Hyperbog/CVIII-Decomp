/* JP0751: ROM-only room seam and bounded transient side-column continuity.
 * Host presentation only, no original game source bytes or PPU writes. */
#ifndef CVIII_STAGE1_JOIN_0751_H
#define CVIII_STAGE1_JOIN_0751_H
#include <stdint.h>
enum { CVIII_JOIN_W=426, CVIII_JOIN_X=85, CVIII_JOIN_H=240,
       CVIII_JOIN_Y=32, CVIII_JOIN_SIDE=85, CVIII_JOIN_ROWS=208,
       CVIII_JOIN_HOLD_MAX=30, CVIII_JOIN_GAP_MAX=90 };
typedef struct {
    uint8_t last[3], adjacent[3], valid, joined;
    int last_camera, last_width, prior_width, direction;
    unsigned gap, hold_age, has_side;
    uint32_t cached_sides[CVIII_JOIN_ROWS*CVIII_JOIN_SIDE*2u];
} CviiiStage1Join0751;
void cviii_stage1_join_reset_0751(CviiiStage1Join0751 *join);
void cviii_stage1_join_gap_0751(CviiiStage1Join0751 *join);
void cviii_stage1_join_accept_0751(CviiiStage1Join0751 *join,
                                   const uint8_t selector[3],int camera,int width_px);
int cviii_stage1_join_previous_0751(const CviiiStage1Join0751 *join,
                                    int camera,int width_px,
                                    uint8_t old_selector[3],int *old_camera);
void cviii_stage1_join_cache_0751(CviiiStage1Join0751 *join,
                                  const uint32_t frame[CVIII_JOIN_W*CVIII_JOIN_H]);
int cviii_stage1_join_hold_0751(CviiiStage1Join0751 *join,
                                uint32_t frame[CVIII_JOIN_W*CVIII_JOIN_H]);
#endif
