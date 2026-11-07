/* JP0667: detached original raw05 D/E control-state effects.
 * Only individually demonstrated local state paths are accepted.
 * Owner-ROM script bytes and RAM are caller-owned; no hardware/PCM writes.
 */
#ifndef CVIII_JP_EFFECT_STATE_0667_H
#define CVIII_JP_EFFECT_STATE_0667_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define CVIII_JP0667_RAM 2048u
typedef struct {
    uint8_t mode;       /* original melodic slots 0..4 */
    uint8_t opcode;
    uint8_t arguments[3];
    uint8_t argument_count;
} CviiiJp0667Effect;
/* RAM image input/output are separate 2048-byte arrays; output unaffected
 * if validation fails. The result width includes opcode + arguments.
 * This does NOT advance the original frame loop or emit register writes.
 * ED, EF and F commands depend on external handlers and fail closed.
 */
bool cviii_jp0667_effect(const uint8_t *before, size_t before_size,
                         const CviiiJp0667Effect *effect,
                         uint8_t *after, size_t after_size,
                         uint8_t *consumed);
#endif
