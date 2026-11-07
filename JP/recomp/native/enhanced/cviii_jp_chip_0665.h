/* JP0665: detached native 2A03/VRC6 PCM voice primitives.
 * Preview oscillator accuracy only, not a cycle accurate APU/VRC6.
 * Does not decode original sound scripts or handle DMC DMA. No active game hook.
 * Per-chip contexts may be put independently on JP0647 Music/SFX buses.
 */
#ifndef CVIII_JP_CHIP_0665_H
#define CVIII_JP_CHIP_0665_H
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
typedef enum {
    CVIII_JP_CHIP_APU_PULSE1=0,CVIII_JP_CHIP_APU_PULSE2,
    CVIII_JP_CHIP_APU_NOISE,CVIII_JP_CHIP_VRC6_PULSE1,
    CVIII_JP_CHIP_VRC6_PULSE2,CVIII_JP_CHIP_VRC6_SAW
} CviiiJpChipKind;
typedef struct {
    CviiiJpChipKind kind;
    uint32_t sample_rate;
    uint8_t r0,r1,r2,r3,apu_enable,phase;
    uint16_t lfsr;
    uint8_t saw_acc;
    uint64_t sample_count;
    double cycles_until_step;
    double dc_estimate;
} CviiiJpChipVoice;
/* Each chip gets an isolated register state. Caller supplies *authentic*
 * original register-write events when available; writes are NEVER sent to
 * the original emulated APU or mapper. Returns false for unsupported addr. */
bool cviii_jp_chip_init(CviiiJpChipVoice *s,CviiiJpChipKind kind,
                        uint32_t sample_rate);
bool cviii_jp_chip_write(CviiiJpChipVoice *s,uint16_t addr,uint8_t value);
/* JP0647 CviiiVirtualSample-compatible callback (owner may use mixer play).
 * Output: 1 while context valid; 0 if invalid. This does not produce DPCM.
 * Hardware envelope, sweep, length counter, nonlinear NES APU filtering,
 * VRC6 PCM calibration and CPU-cycle edge parity are NOT implemented. */
int cviii_jp_chip_sample(void *context,int16_t *out);
#endif
