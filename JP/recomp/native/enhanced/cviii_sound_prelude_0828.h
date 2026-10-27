/* JP0828: original fixed-bank $E249 sound mapper prelude.
 * $E249 lives in the final fixed PRG bank and invokes $E2D0 to select
 * PRG bank $0C before calling external bank0C:$8850.
 *
 * This models private 6502 postconditions UP TO (but not including)
 * $E258 JSR $8850, which may write APU, queues and live game state.
 * It never mutates guest RAM, mapper or sound hardware. The original
 * Japanese ROM fixed-bank $E249-$E263 and $E2D0-$E2D5 opcodes
 * are separately SHA-verified by the owner-private auditor.
 */
#ifndef CVIII_SOUND_PRELUDE_0828_H
#define CVIII_SOUND_PRELUDE_0828_H
#include <stdint.h>
typedef struct {
 uint8_t original_bank, pending_sound, original_26;
 uint8_t proposed_25, proposed_26, proposed_prg_bank;
 uint16_t stop_pc,external_target;
 uint8_t effects_authorized;
} CviiiE249Prelude0828;
static inline int cviii_e249_prelude_0828(
 const uint8_t original_ram[2048],uint8_t sound_id,
 CviiiE249Prelude0828 *out)
{
 if(!original_ram || !out)return 0;
 CviiiE249Prelude0828 p={0};
 p.original_bank=original_ram[0x23u];
 p.original_26=original_ram[0x26u];
 p.pending_sound=sound_id;
 p.proposed_25=p.original_bank;
 p.proposed_26=0xffu;
 p.proposed_prg_bank=0x0cu;
 p.stop_pc=0xe258u;p.external_target=0x8850u;
 /* E249's fixed-bank prelude alone NEVER licenses
  * audio writes or the subsequent B525 defeat chain. */
 p.effects_authorized=0u;
 *out=p;return 1;
}
#endif
