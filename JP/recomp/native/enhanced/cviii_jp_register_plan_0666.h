/* JP0666: detached, original-data-backed register event plan for 2A03/VRC6.
 * Scope: raw05 $811F-$822D with specific upstream state; NOT a music player.
 * ROM/game RAM are never mutated. Caller authenticates owner source bytes. */
#ifndef CVIII_JP_REGISTER_PLAN_0666_H
#define CVIII_JP_REGISTER_PLAN_0666_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define CVIII_JP0666_BANK_SIZE 16384u
#define CVIII_JP0666_WRITES_MAX 2u
typedef struct { uint16_t address; uint8_t value; } CviiiJp0666Write;
typedef struct {
    uint8_t slot;             /* original 0,1,2,3,4 */
    uint8_t note;             /* $00-$BF, low nibble is not pitch */
    uint8_t octave;           /* $01A3,X input, bounded 0..5 */
    uint8_t transpose;        /* $01A8,X: original signed-offset index arithmetic */
    uint8_t detune;           /* $0195,X 7-bit magnitude and sign bit */
    uint8_t apu_gate;         /* $010E or $010F: nonzero suppresses APU writes */
    uint8_t high_cache;       /* $0163,X */
    uint8_t flag_011b;       /* $011B,X */
    uint8_t flag_017e;       /* $017E,X */
    uint8_t flag_018e;       /* $018E,X; bit 4 must be zero */
    uint8_t flag_06b4;       /* $06B4,X; bit 7 must be set to skip $822E */
} CviiiJp0666Input;
typedef struct {
    uint16_t period_before_detune;
    uint16_t period_after_detune;
    uint8_t high_cache_after;
    uint8_t stored_period_low; /* APU original $019C,X (x=3,4 only) */
    size_t write_count;
    CviiiJp0666Write writes[CVIII_JP0666_WRITES_MAX];
} CviiiJp0666Plan;
/* Returns false leaving *out unchanged when entering a code path outside
 * this bounded proof (transpose, envelope, unsupported slot/flag etc.). */
bool cviii_jp0666_note_plan(const uint8_t *raw05, size_t raw05_size,
                            const CviiiJp0666Input *input,
                            CviiiJp0666Plan *out);
#endif
