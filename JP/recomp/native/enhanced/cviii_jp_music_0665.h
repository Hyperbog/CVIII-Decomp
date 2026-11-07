/* JP0665: read-only original bank05 note/rest/percussion event traversal.
 * Owner-ROM source must be authenticated by caller. No audio hardware mutation.
 * E-channel envelopes, exact register writes and subframe timing not yet decoded.
 */
#ifndef CVIII_JP_MUSIC_0665_H
#define CVIII_JP_MUSIC_0665_H
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#define CVIII_JP0665_VOICES 6u
#define CVIII_JP0665_RAW05_SIZE 16384u
#define CVIII_JP0665_RAW0C_SIZE 16384u
typedef enum {
    CVIII_JP0665_VRC6_PULSE1=0, CVIII_JP0665_VRC6_PULSE2=1,
    CVIII_JP0665_VRC6_SAW=2, CVIII_JP0665_APU_PULSE1=3,
    CVIII_JP0665_APU_PULSE2=4, CVIII_JP0665_PERCUSSION=7
} CviiiJp0665Route;
typedef enum {
    CVIII_JP0665_NOTE=1, CVIII_JP0665_REST=2,
    CVIII_JP0665_NOISE_REQUEST=3, CVIII_JP0665_DPCM_REQUEST=4
} CviiiJp0665EventKind;
typedef struct {
    uint64_t tick;
    uint16_t source_pc; /* owner-private provenance; never commit event dumps */
    uint16_t pitch_table_base_period; /* not octave/transpose-adjusted */
    uint16_t destination_period_low, destination_period_high; /* original chip registers */
    uint8_t route, kind, note_index, note_byte, duration_units;
    uint8_t sound_request_id; /* 0 for melodic notes/rest */
    uint16_t duration_ticks; /* original 8-bit timer after multiplication */
    bool exact_register_values_verified; /* always false until full E semantics */
} CviiiJp0665Event;
typedef struct {
    const uint8_t *bank05;
    uint16_t pc, fd_return, fb_anchor, repeat_site;
    uint8_t route, unit, repeat_counter, octave;
    uint64_t ticks, events;
    bool has_return, has_anchor, has_repeat, ended, unknown_effects;
} CviiiJp0665Voice;
/* raw0C sound ID $51 selects six bank05 mode slots 0,1,2,3,4,7.
 * FAIL CLOSED on malformed pointers, bank sizes or missing authentic source.
 * The caller must verify original-ROM SHA before calling this function. */
bool cviii_jp0665_init(const uint8_t *raw05, size_t n05,
                       const uint8_t *raw0c, size_t n0c,
                       CviiiJp0665Voice voices[CVIII_JP0665_VOICES]);
/* Returns 1 for next event, 0 when stopped, -1 on source error; bounded.
 * Event tick is relative and abstract, not sample/cycle timestamp.
 * It decodes actual note-length math and source control-flow, but cannot
 * validate all effects nor prove PCM parity. */
int cviii_jp0665_next(CviiiJp0665Voice *v, CviiiJp0665Event *out);
#endif
