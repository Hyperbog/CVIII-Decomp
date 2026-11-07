/* JP0667: detached source-matched $8A7C-$8AA0 per-voice frame gate.
 * Not an absolute-time clock, audio renderer, or stream interpreter.
 */
#ifndef CVIII_JP_FRAME_GATE_0667_H
#define CVIII_JP_FRAME_GATE_0667_H
#include <stdbool.h>
#include <stdint.h>
typedef enum {
  CVIII_JP_FRAME_SUSPENDED = 0,
  CVIII_JP_FRAME_COUNTING = 1,
  CVIII_JP_FRAME_STREAM_DUE = 2
} CviiiJpFrameDecision;
typedef struct {
  uint8_t slot;           /* original indexed X 0..8 */
  uint8_t sound_id;       /* original $0109,X; this function starts after active check */
  uint8_t flags_011b;
  uint8_t global_01bf;
  uint8_t countdown_0100;
} CviiiJpFrameInput;
typedef struct {
  CviiiJpFrameDecision decision;
  uint8_t countdown_after;
  uint8_t parser_mode_main; /* $011B,X bit0 passed to $8DCD when due */
} CviiiJpFrameResult;
bool cviii_jp_frame_gate_0667(const CviiiJpFrameInput *in,
                               CviiiJpFrameResult *out);
#endif
