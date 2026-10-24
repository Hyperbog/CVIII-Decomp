/* ROM-free tests: invented queues only; no original assets. */
#include "cviii_ppu_queue_0723.h"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t ram[2048];
static CviiiPpuQueue0723 result;
static unsigned pos;
static void start(void) { memset(ram, 0, sizeof ram); pos = 0; ram[0xff] = 0x90; }
static void append(unsigned v) {
    assert(pos < 255u);
    ram[0x300u + pos++] = (uint8_t)v;
}
static void target(unsigned a) { append(a & 255u); append(a >> 8u); }
static void finish(unsigned n, unsigned addr, unsigned value) {
    append(0);
    ram[0x1e] = (uint8_t)pos;
    assert(cviii_ppu_queue_0723(ram, 2048, &result) == 1);
    assert(result.command_count == 1u && result.write_count == n);
    assert(result.bytes_consumed == pos);
    assert(result.initial_ctrl == 0x90 && result.restored_ctrl == 0x90);
    if (n) {
        assert(result.writes[0].address == addr);
        assert(result.writes[0].value == value);
    }
}
int main(void) {
    unsigned i, j;
    start(); append(1); target(0x2110); append(0xA0); append(0xB0); append(0xff);
    finish(2, 0x2110, 0xA0);
    assert(result.writes[1].address == 0x2111 && result.writes[1].value == 0xB0);

    start(); append(2); target(0x2021); append(4); append(5); append(0xff);
    finish(2, 0x2021, 4);
    assert(result.writes[1].address == 0x2041);

    start(); append(3); target(0x23C0); append(3); append(0x55);
    finish(3, 0x23C0, 0x55);
    assert(result.writes[2].address == 0x2400);

    start(); append(10); target(0x3FFF); append(2); append(0x10); append(0x11);
    finish(2, 0x3FFF, 0x10);
    assert(result.writes[1].address == 0);

    start(); append(4);
    for (i = 0; i < 4; i++) {
        target(0x2400u + i * 4u);
        for (j = 0; j < 4; j++) append(i * 4u + j);
    }
    target(0x2500); append(99); finish(17, 0x2400, 0);
    assert(result.writes[16].address == 0x2500 && result.writes[16].value == 99);

    start(); append(5);
    for (i = 0; i < 2; i++) {
        target(0x2300u + i * 4u);
        for (j = 0; j < 4; j++) append(i * 4u + j);
    }
    target(0x2400); append(99); finish(9, 0x2300, 0);

    start(); append(6); target(0x2000);
    for (i = 0; i < 32; i++) append(i);
    finish(32, 0x2000, 0);

    start(); append(7); target(0x2100);
    for (i = 0; i < 32; i++) append(i);
    target(0x2400);
    for (i = 0; i < 8; i++) append(i + 33);
    finish(40, 0x2100, 0);

    start(); append(8); target(0x2220);
    for (i = 0; i < 22; i++) append(i);
    finish(22, 0x2220, 0);
    assert(result.writes[21].address == 0x24C0);

    start(); append(9); target(0x2220);
    for (i = 0; i < 22; i++) append(i);
    for (i = 0; i < 6; i++) { target(0x2300 + i); append(77 + i); }
    finish(28, 0x2220, 0);
    assert(result.writes[27].address == 0x2305);

    start(); append(3); target(0x2000); append(0); append(7);
    finish(256, 0x2000, 7);

    start(); append(0); ram[0x1e] = 1;
    assert(cviii_ppu_queue_0723(ram, 2048, &result) == 1 &&
           result.write_count == 0);

    start(); append(11); append(0); ram[0x1e] = 2;
    memset(&result, 0x6d, sizeof result);
    assert(cviii_ppu_queue_0723(ram, 2048, &result) == -1);
    assert(result.writes[0].value == 0x6d);

    start(); append(1); target(0x2000); append(0x55);
    append(0); ram[0x1e] = (uint8_t)pos;
    assert(cviii_ppu_queue_0723(ram, 2048, &result) == -1);

    start(); append(1); target(0x2000); append(0x55); append(0xff);
    append(0); ram[0x1e] = 0;
    assert(cviii_ppu_queue_0723(ram, 2048, &result) == -1);
    assert(cviii_ppu_queue_0723(ram, 100, &result) == -1);

    puts("PASS JP0723 source-typed PPU queue decoder");
    return 0;
}
