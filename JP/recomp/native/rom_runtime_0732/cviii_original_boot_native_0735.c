/* JP0735 — original JP fixed-bank boot instruction handlers.
 *
 * Authenticated cartridge: original JP Mapper24 SHA-256 is checked by
 * cviii_runtime_entry_0733 BEFORE any guest instruction executes.
 * Each native dispatch checks the ORIGINAL fixed PRG bank 62 ($E000-$EFFF),
 * the exact entry PC, opcode, and (for LDX) the original #$FF operand.
 *
 * Physical ROM source authentication (file offsets include 16-byte header):
 * reset vector: $03E00C/$03E00D = $E00B
 *  $03E01B: $E00B D8   CLD
 *  $03E01C: $E00C 78   SEI
 *  $03E027: $E017 A2 FF LDX #$FF
 *  $03E029: $E019 9A   TXS
 *
 * Execution uses exact pinned NESRecomp cpu6502_interp.c templates, including
 * real opcode fetches, dummy/operand reads and final cycle poll. It changes
 * NO PPU/APU/mapper hardware or original 6502 memory, and other instructions
 * always use the upstream interpreter. No ROM bytes beyond opcode identity
 * and one immediate operand are embedded.
 */
#include "cyc_recomp.h"
#include "cyc_core.h"
#include "hw.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

const char *cyc_native_display_name = NULL;
const char *cyc_native_program_name = NULL;
const uint32_t cyc_native_prg_hash = 0;
const uint32_t cyc_native_cart_hash = 0;
const uint32_t cyc_native_fds_bios_crc32 = 0;
const char *cyc_native_fds_bios_path = NULL;
const char *cyc_native_fds_image_path = NULL;
const char *cyc_native_fds_hle = NULL;
const uint8_t cyc_native_console = 0;
const CycRamView *const cyc_native_ram_views[1] = { NULL };
const uint32_t cyc_native_ram_view_count = 0;
const CycHookSite cyc_native_hook_sites[1] = { { NULL, 0, 0, 0 } };
const uint32_t cyc_native_hook_site_count = 0;

typedef struct { uint16_t pc; uint8_t opcode; uint8_t operand; } BootEntry;
static const BootEntry entries[4] = {
    {0xE00Bu,0xD8u,0}, /* CLD */
    {0xE00Cu,0x78u,0}, /* SEI */
    {0xE017u,0xA2u,0xFFu}, /* LDX immediate */
    {0xE019u,0x9Au,0} /* TXS */
};
static uint64_t native_hits[4];

#ifdef CVIII_JP0735_REPORT_HITS
static void report(void)
{
    printf("JP0735 original-boot native CLD=%" PRIu64
           " SEI=%" PRIu64 " LDX=%" PRIu64
           " TXS=%" PRIu64 "\n",
           native_hits[0],native_hits[1],native_hits[2],native_hits[3]);
}
#endif

static int entry_for(uint16_t pc)
{
    for(int i=0;i<4;i++)
        if(entries[i].pc==pc) return i;
    return -1;
}
static bool matches(int entry)
{
    if(entry<0) return false;
    uint16_t pc=entries[entry].pc;
    /* VRC6 fixes the final 8 KiB ROM at E000; the physical 4 KiB bank
     * for these addresses is 62 (= $3E000 / $1000), not a logical page. */
    if(!hw_prg_is_rom(pc)||hw_prg_bank4(pc)!=62u)return false;
    uint8_t byte;
    if(!cyc_debug_peek(pc,&byte)||byte!=entries[entry].opcode)return false;
    if(entry==2 && (!cyc_debug_peek((uint16_t)(pc+1u),&byte)||
                    byte!=entries[entry].operand)) return false;
    return true;
}
bool cyc_native_has(uint16_t pc)
{
#ifdef CVIII_JP0735_REPORT_HITS
    static int registered;
    if(!registered){(void)atexit(report);registered=1;}
#endif
    return matches(entry_for(pc));
}
void cyc_native_run(void)
{
    uint16_t pc=cpu.pc;
    int entry=entry_for(pc);
    /* Always revalidate at entry. No opcode fetch occurs before validation;
     * if a mapper or cartridge invalidates the view, stop rather than
     * running a stale native instruction. */
    if(!matches(entry)) {
        fputs("JP0735: validated original boot instruction changed\n",stderr);
        abort();
    }
    uint8_t opcode;
    if(cpu_fetch(pc,&opcode)) {
        cpu_interrupt(false);
        return;
    }
    if(opcode!=entries[entry].opcode){
        fputs("JP0735: opcode changed during original boot fetch\n",stderr);
        abort();
    }
    uint8_t dummy_or_operand=cpu_read((uint16_t)(pc+1u),
                                      CYC_POLL|CYC_DONE);
    switch(entry) {
    case 0: cpu.d=0; cpu.pc=(uint16_t)(pc+1u); break;
    case 1: cpu.i=1; cpu.pc=(uint16_t)(pc+1u); break;
    case 2: cpu.x=dummy_or_operand; cpu_nz(cpu.x);
            cpu.pc=(uint16_t)(pc+2u); break;
    case 3: cpu.s=cpu.x; cpu.pc=(uint16_t)(pc+1u); break;
    default: abort();
    }
    native_hits[entry]++;
}
