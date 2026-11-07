#include "cviii_ppu_queue_0723.h"
#include <string.h>
#define BUF_BASE 0x300u
#define BUF_SIZE 0x100u

typedef struct {
    const uint8_t *ram;
    unsigned cursor;
    unsigned end;
    CviiiPpuQueue0723 *result;
} Decoder0723;
static int take(Decoder0723 *d, unsigned *v) {
    if (d->cursor >= d->end) return 0;
    *v = d->ram[BUF_BASE + d->cursor++];
    return 1;
}
static int address(Decoder0723 *d, unsigned *a) {
    unsigned low, high;
    if (!take(d, &low) || !take(d, &high)) return 0;
    /* The producer stores low byte, then high byte. */
    *a = ((high << 8u) | low) & 0x3FFFu;
    return 1;
}
static int put(Decoder0723 *d, unsigned command, unsigned *a, unsigned v) {
    CviiiPpuQueue0723 *r = d->result;
    if (r->write_count >= CVIII_PPU_QUEUE_MAX_WRITES_0723) return 0;
    CviiiPpuWrite0723 *w = &r->writes[r->write_count++];
    w->address = (uint16_t)*a;
    w->value = (uint8_t)v;
    w->command = (uint8_t)command;
    /* Fixed $EC7A,X PPUCTRL OR-mask: types 2,3,8,9 step by 32. */
    *a = (*a + ((command == 2u || command == 3u ||
                  command == 8u || command == 9u) ? 32u : 1u)) & 0x3FFFu;
    return 1;
}
static int data(Decoder0723 *d, unsigned cmd, unsigned *a,
                unsigned count, int repeat) {
    unsigned v = 0, i;
    if (repeat && !take(d, &v)) return 0;
    for (i = 0; i < count; i++) {
        if (!repeat && !take(d, &v)) return 0;
        if (!put(d, cmd, a, v)) return 0;
    }
    return 1;
}
int cviii_ppu_queue_0723(const uint8_t *ram, size_t len, CviiiPpuQueue0723 *out) {
    CviiiPpuQueue0723 r;
    Decoder0723 d;
    unsigned cmd, a, n, i, v;
    if (!ram || !out || len != 2048u) return -1;
    /* Source $1E is the byte cursor after the final zero terminator.
     * It wraps to zero when that terminator resides at offset $FF. */
    memset(&r, 0, sizeof r);
    r.initial_ctrl = ram[0xFFu];
    r.restored_ctrl = r.initial_ctrl;
    d.ram = ram;
    d.cursor = 0;
    d.end = BUF_SIZE;
    d.result = &r;
    for (;;) {
        if (!take(&d, &cmd)) return -1;
        if (cmd == 0u) {
            if ((uint8_t)d.cursor != ram[0x1Eu]) return -1;
            r.bytes_consumed = (uint8_t)d.cursor;
            *out = r;
            return 1;
        }
        if (cmd > 10u || r.command_count == 255u) return -1;
        r.command_count++;
        if (cmd == 1u || cmd == 2u) {
            /* $ED94-$EDA3: literal run, FF terminator is not emitted. */
            if (!address(&d, &a)) return -1;
            for (;;) {
                if (!take(&d, &v)) return -1;
                if (v == 0xFFu) break;
                if (!put(&d, cmd, &a, v)) return -1;
            }
        } else if (cmd == 3u || cmd == 10u) {
            /* $EDA5 and $EF5C: count zero means 256 on 6502 DEX/BNE. */
            if (!address(&d, &a) || !take(&d, &n)) return -1;
            if (!data(&d, cmd, &a, n ? n : 256u, cmd == 3u)) return -1;
        } else if (cmd == 4u || cmd == 5u) {
            /* $EDC1-$EE0F: 4 or 2 groups of four, plus final single. */
            for (i = 0; i < (cmd == 4u ? 4u : 2u); i++) {
                if (!address(&d, &a) || !data(&d, cmd, &a, 4u, 0)) return -1;
            }
            if (!address(&d, &a) || !data(&d, cmd, &a, 1u, 0)) return -1;
        } else if (cmd == 6u || cmd == 7u) {
            /* $EE18-$EF59: 32 bytes, with optional next-address 8. */
            if (!address(&d, &a) || !data(&d, cmd, &a, 32u, 0)) return -1;
            if (cmd == 7u &&
                (!address(&d, &a) || !data(&d, cmd, &a, 8u, 0))) return -1;
        } else {
            /* $ED17-$ED44: 22-byte column; type 9 adds six singles. */
            if (!address(&d, &a) || !data(&d, cmd, &a, 22u, 0)) return -1;
            if (cmd == 9u) {
                for (i = 0; i < 6u; i++) {
                    if (!address(&d, &a) || !data(&d, cmd, &a, 1u, 0)) return -1;
                }
            }
        }
    }
}
