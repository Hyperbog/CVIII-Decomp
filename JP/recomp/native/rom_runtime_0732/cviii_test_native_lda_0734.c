/* JP0734 — SYNTHETIC TEST ONLY, not the original Japanese game.
 *
 * Demonstrates the existing upstream instruction-boundary native/fallback
 * seam without distributing ROM-derived generated code or claiming original
 * PRG semantic coverage. Exactly one opcode, LDA #immediate, is dispatched
 * natively. Every other opcode falls back through cpu_interp_step().
 *
 * Opcode execution is identical to pinned NESRecomp cpu6502_interp.c A9.
 * No guest RAM/PPU shortcut: cpu_fetch + cpu_read issue real bus cycles.
 */
#include "cyc_recomp.h"
#include "cyc_core.h"
#include "hw.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

const char    *cyc_native_display_name = NULL;
const char    *cyc_native_program_name = NULL;
const uint32_t cyc_native_prg_hash = 0;
const uint32_t cyc_native_cart_hash = 0;
const uint32_t cyc_native_fds_bios_crc32 = 0;
const char    *cyc_native_fds_bios_path = NULL;
const char    *cyc_native_fds_image_path = NULL;
const char    *cyc_native_fds_hle = NULL;
const uint8_t  cyc_native_console = 0;
const CycRamView *const cyc_native_ram_views[1] = { NULL };
const uint32_t cyc_native_ram_view_count = 0;
const CycHookSite cyc_native_hook_sites[1] = { { NULL, 0, 0, 0 } };
const uint32_t cyc_native_hook_site_count = 0;

static uint64_t lda_hits;
static void print_hits(void) {
    printf("JP0734 test-native-lda hits=%" PRIu64 "\n",lda_hits);
}
bool cyc_native_has(uint16_t pc) {
    static int registered;
    if(!registered){ (void)atexit(print_hits); registered=1; }
    /* The source must be a currently mapped physical PRG ROM byte. No
     * addresses in RAM, I/O or open bus can enter native execution. */
    if (pc < 0x8000u || !hw_prg_is_rom(pc)) return false;
    uint8_t opcode;
    if (!cyc_debug_peek(pc,&opcode))return false;
    return opcode==0xA9u;
}
void cyc_native_run(void) {
    uint16_t pc=cpu.pc;
    uint8_t opcode;
    if (cpu_fetch(pc,&opcode)) {
        cpu_interrupt(false);
        return;
    }
    /* The preceding side-effect-free, current-bank opcode test holds
     * until this CPU fetch; only emulator hardware can change a mapping. */
    if (opcode!=0xA9u) {
        fprintf(stderr,"JP0734 test native opcode changed during fetch\n");
        abort(); /* fail closed rather than execute a second opcode fetch */
    }
    uint8_t value=cpu_read((uint16_t)(pc+1u),CYC_POLL|CYC_DONE);
    cpu.a=value;
    cpu_nz(value);
    cpu.pc=(uint16_t)(pc+2u);
    lda_hits++;
}
