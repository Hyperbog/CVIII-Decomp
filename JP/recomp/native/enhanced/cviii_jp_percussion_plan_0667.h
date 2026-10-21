/* JP0667: original mode7 -> sound request -> JP0648 DMC event plan.
 * Noise dispatch is a request, not fabricated hardware/noise writes.
 */
#ifndef CVIII_JP_PERCUSSION_PLAN_0667_H
#define CVIII_JP_PERCUSSION_PLAN_0667_H
#include "cviii_dmc_source_0648.h"
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef enum {
  CVIII_JP_PERC_REST=0,
  CVIII_JP_PERC_NOISE_REQUEST=1,
  CVIII_JP_PERC_DMC_REQUEST=2
} CviiiJpPercKind;
typedef struct {
  CviiiJpPercKind kind;
  uint8_t source_nibble,request_id;
  CviiiDmcPlan dmc;
} CviiiJpPercussionPlan;
/* raw05 16KiB must be independently authenticated; reads the original
 * source $8072-$807D dispatch table rather than a copied note list.
 * dmc_table must be the caller-verified 60-byte $A957-$A992 region.
 * No CPU writes, sample DMA, NES ownership, PCM or effects mixing.
 */
bool cviii_jp_percussion_plan_0667(const uint8_t *raw05,size_t bank_size,
                                     unsigned source_high_nibble,
                                     const uint8_t *dmc_table,size_t table_len,
                                     unsigned old_priority,
                                     CviiiJpPercussionPlan *out);
#endif
