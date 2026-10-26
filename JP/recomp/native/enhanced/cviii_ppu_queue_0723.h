#ifndef CVIII_PPU_QUEUE_0723_H
#define CVIII_PPU_QUEUE_0723_H
#include <stddef.h>
#include <stdint.h>
/* Original JP PRG31:$ED46-$EF6C PPU-upload command queue.
 * Read-only decoder for CPU RAM[$0300-$03FF]. Does not advance the PPU,
 * render pixels, prove data producer provenance, or modify the game state.
 * No original game bytes are embedded. Caller validates the original ROM.
 */
#define CVIII_PPU_QUEUE_MAX_WRITES_0723 4096u
typedef struct {
    uint16_t address; /* 14-bit PPU address at the original $2007 write */
    uint8_t value;
    uint8_t command;
} CviiiPpuWrite0723;
typedef struct {
    uint16_t write_count;
    uint8_t command_count;
    uint8_t bytes_consumed; /* includes terminator; equals RAM[$1E] */
    uint8_t initial_ctrl;
    uint8_t restored_ctrl;
    CviiiPpuWrite0723 writes[CVIII_PPU_QUEUE_MAX_WRITES_0723];
} CviiiPpuQueue0723;
/* 1 for success, -1 for malformed input; failures leave *out unmodified.
 * This models the bounded queue's ordered PPU write plan, not the actual
 * PPU bus-cycle timing or natural emulator execution.
 * The source producer's $1E cursor must match the bytes consumed.
 */
int cviii_ppu_queue_0723(const uint8_t *ram, size_t ram_len,
                          CviiiPpuQueue0723 *out);
#endif
