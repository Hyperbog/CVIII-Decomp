/* CVIII edition presentation, JP 0589.
 * Written for the pinned external NESRecomp cyc_host_extras ABI.
 * Game execution, CPU-visible PPU flags, mapper banking and timing are untouched.
 * No ROM data or NESRecomp source is copied here.
 */
#include "cyc_host_extras.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include "cviii_chr_index_0598.h"
#include "cviii_chr_audit_0599.h"
#include "cviii_chr_fetch_0600.h"
#include "cviii_frame_evidence_0601.h"
#include "cviii_nt_trace_0606.h"
#include "cviii_sprite_layers_0608.h"
#include "cviii_object_oam_trace_0609.h"
#include "cviii_audio_bus_0610.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CVIII_W 256
#define CVIII_H 240

typedef struct {
    int enhanced;
    int sprite_unlimited;
    int stable_sprites; /* optional host-only temporal presentation; off by default */
    CviiiSpriteLayers sprite_layers;
    CviiiObjectOamTrace object_trace; /* read-only JP PRG26 object/OAM correlation */
    CviiiAudioBus audio_bus; /* opt-in nonmutating 2A03/VRC6 sound writes */
    uint8_t layer_masks[CVIII_LAYER_H];
    CviiiChrIndex assets; /* read-only imported physical CHR; presentation only */
    CviiiChrAudit audit; /* opt-in read-only per-frame bank audit */
    CviiiChrFetchAudit fetch; /* opt-in actual PPU pattern-read observation */
    CviiiFrameEvidence frame_evidence; /* opt-in correlated PPU evidence */
    CviiiNtTrace nt_trace; /* opt-in real nametable and attribute reads */
    uint32_t presentation[CVIII_W * CVIII_H];
} CviiiEdition;

static CviiiEdition cviii;

static int parse_boolean(const char *text, int *value)
{
    if (!strcmp(text, "1") || !strcmp(text, "on") || !strcmp(text, "true")) {
        *value = 1;
        return 1;
    }
    if (!strcmp(text, "0") || !strcmp(text, "off") || !strcmp(text, "false")) {
        *value = 0;
        return 1;
    }
    return 0;
}

static int set_edition(const char *name)
{
    if (!strcmp(name, "original") || !strcmp(name, "Original")) {
        cviii.enhanced = 0;
        return 1;
    }
    if (!strcmp(name, "enhanced") || !strcmp(name, "Enhanced")) {
        cviii.enhanced = 1;
        return 1;
    }
    return 0;
}

static void load_setting(void *context, const char *key, const char *value)
{
    (void)context;
    if (!strcmp(key, "Edition")) (void)set_edition(value);
    else if (!strcmp(key, "UnlimitedSprites"))
        (void)parse_boolean(value, &cviii.sprite_unlimited);
    else if (!strcmp(key, "StableSprites"))
        (void)parse_boolean(value, &cviii.stable_sprites);
}

static void save_settings(void *context, FILE *file)
{
    (void)context;
    fprintf(file, "Edition = %s\nUnlimitedSprites = %d\nStableSprites = %d\n",
            cviii.enhanced ? "Enhanced" : "Original",
            cviii.sprite_unlimited, cviii.stable_sprites);
}

static bool option(void *context, const char *name, const char *value)
{
    (void)context;
    if (!strcmp(name, "--edition")) return value && set_edition(value);
    if (!strcmp(name, "--unlimited-sprites"))
        return value && parse_boolean(value, &cviii.sprite_unlimited);
    if (!strcmp(name, "--stable-sprites"))
        return value && parse_boolean(value, &cviii.stable_sprites);
    if (!strcmp(name, "--audio-reg-trace")) {
        if (!value || !cviii_audio_bus_open(&cviii.audio_bus, value)) {
            fprintf(stderr, "CVIII: cannot open private 2A03/VRC6 audio register log\n");
            return false;
        }
        printf("CVIII: tracing sound chip writes; no changes to music or effects\n");
        return true;
    }
    if (!strcmp(name, "--sprite-object-trace")) {
        if (!value || !cviii_object_oam_trace_open(&cviii.object_trace, value)) {
            fprintf(stderr, "CVIII: cannot open owner-local object/OAM trace output\n");
            return false;
        }
        printf("CVIII: recording actual game-object and hardware OAM per frame\n");
        return true;
    }
    if (!strcmp(name, "--asset-index")) {
        if (!value || !cviii_chr_index_load(&cviii.assets, value)) {
            fprintf(stderr, "CVIII: rejected missing, mismatched or damaged JP asset index\n");
            return false;
        }
        printf("CVIII: loaded authenticated read-only JP CHR index (8192 tiles); PPU remains authoritative\n");
        return true;
    }
    if (!strcmp(name, "--chr-audit")) {
        if (!value || !cviii_chr_audit_open(&cviii.audit, value)) {
            fprintf(stderr, "CVIII: cannot open requested CHR audit output\n");
            return false;
        }
        printf("CVIII: recording 1-in-60-frame read-only VRC6 bank/palette samples\n");
        return true;
    }
    if (!strcmp(name, "--chr-fetch-audit")) {
        if (!value || !cviii_chr_fetch_open(&cviii.fetch, value)) {
            fprintf(stderr, "CVIII: cannot open requested CHR fetch audit output\n");
            return false;
        }
        printf("CVIII: recording sampled actual VRC6 PPU CHR reads (no substitution)\n");
        return true;
    }
    if (!strcmp(name, "--frame-evidence")) {
        if (!value || !cviii_frame_evidence_open(&cviii.frame_evidence, value)) {
            fprintf(stderr, "CVIII: cannot open read-only PPU frame evidence output\n");
            return false;
        }
        printf("CVIII: recording sampled original PPU frame fingerprints\n");
        return true;
    }
    if (!strcmp(name, "--nt-fetch-audit")) {
        if (!value || !cviii_nt_open(&cviii.nt_trace, value)) {
            fprintf(stderr, "CVIII: cannot open PPU background tile and attribute audit\n");
            return false;
        }
        printf("CVIII: sampling true PPU nametable/attribute reads, no rendering changes\n");
        return true;
    }
    return false;
}

static void power_on(void *context)
{
    CviiiEdition *settings = (CviiiEdition *)context;
    /* Both editions must serialize the SAME optional presentation-state
     * schema. NESRecomp registers the 'cyc.background' savestate hook ONLY
     * while capture is enabled. Disabling it in Original makes Original
     * snapshots incompatible with Enhanced snapshots, even though CPU/PPU
     * machine state is otherwise identical.
     *
     * Always capture the presentation-only background history so load-state
     * validation sees a stable auxiliary schema. Original still returns
     * untouched hardware pixels in present(), without sprite recomposition.
     * The capture does NOT affect sprite-0, overflow, IRQ, DMA or CPU state.
     * Do not recapture in frame_begin: that clears the saved history.
     */
    cviii_layers_reset(&settings->sprite_layers);
    cyc_render_capture_background(true);
}

static uint8_t layer_read_chr(void *user, uint16_t address)
{
    (void)user;
    return cyc_render_chr(address);
}
static uint32_t layer_color(void *user, unsigned palette_index)
{
    (void)user;
    return cyc_render_color((int)palette_index);
}
static const CviiiLayerFns layer_functions = {layer_read_chr, layer_color, NULL};

static void state_loaded(void *context)
{
    CviiiEdition *settings = (CviiiEdition *)context;
    cviii_layers_reset(&settings->sprite_layers);
}

static void frame_begin(void *context)
{
    CviiiEdition *settings = (CviiiEdition *)context;
    if (settings->enhanced) {
        cviii_chr_fetch_frame_begin(&settings->fetch, &settings->assets);
        cviii_nt_begin(&settings->nt_trace, settings->fetch.active != 0,
                       settings->fetch.frames);
    }
}

static void frame_end(void *context)
{
    CviiiEdition *settings = (CviiiEdition *)context;
    if (settings->object_trace.out)
        cviii_object_oam_trace_frame(&settings->object_trace,
                                    cyc_cpu_ram(), cyc_ppu_oam());
    if (settings->enhanced && settings->stable_sprites) {
        uint8_t tall[CVIII_LAYER_H];
        uint16_t tables[CVIII_LAYER_H];
        for (unsigned y=0;y<CVIII_LAYER_H;++y) {
            settings->layer_masks[y] = cyc_render_line_mask((int)y);
            tall[y] = (uint8_t)cyc_render_line_sprite16((int)y);
            tables[y] = cyc_render_line_sprite_table((int)y);
        }
        const uint8_t *oam = cyc_render_oam();
        /* $22 is the ORIGINAL game OAM emission phase. Unlike raw OAM
         * slot priority it is stable when converted back into logical
         * object emission order (stride $C4, frame shift $44). */
        const uint8_t *ram = cyc_cpu_ram();
        if (oam && ram) cviii_layers_capture(&settings->sprite_layers,
            oam, ram[0x22], settings->layer_masks, tall, tables,
            &layer_functions);
    }
    if (settings->frame_evidence.output && settings->fetch.active) {
        const CycLine *source_lines = cyc_frame_lines();
        if (source_lines) {
            uint8_t serialized_lines[CVIII_FRAME_LINES_BYTES];
            for (unsigned y = 0; y < CVIII_FRAME_HEIGHT; ++y) {
                const CycLine *line = &source_lines[y];
                serialized_lines[y * 5u] = (uint8_t)line->v;
                serialized_lines[y * 5u + 1u] = (uint8_t)(line->v >> 8);
                serialized_lines[y * 5u + 2u] = line->fine_x;
                serialized_lines[y * 5u + 3u] = line->ctrl;
                serialized_lines[y * 5u + 4u] = line->mask;
            }
            (void)cviii_frame_evidence_sample(&settings->frame_evidence,
                &settings->fetch, cyc_frame_index(),
                cyc_frame_bg_opaque(), serialized_lines);
        } else {
            ++settings->frame_evidence.input_failures;
        }
    }
    cviii_nt_end(&settings->nt_trace);
    cviii_chr_fetch_frame_end(&settings->fetch);
    if (!settings->audit.out || !settings->assets.raw || !settings->assets.pixels)
        return;
    ++settings->audit.frames;
    if ((settings->audit.frames - 1) % settings->audit.interval != 0) return;
    /* This is a read-only snapshot of the mapper and palette AFTER frame
     * execution. Mid-scanline changes are not observable at this cadence.
     * NESRecomp's existing public state-dump API avoids including any
     * internal mapper structures in our game-owned host source. */
    FILE *snapshot = tmpfile();
    if (!snapshot) {
        fprintf(stderr, "CVIII CHR audit: temporary mapper snapshot unavailable\n");
        ++settings->audit.mismatch;
        return;
    }
    cyc_hw_state_dump(snapshot);
    cviii_chr_audit_frame(&settings->audit, &settings->assets,
                          snapshot, cyc_ppu_palette());
    fclose(snapshot);
}

static const uint32_t *present(void *context, int *width, int *height)
{
    CviiiEdition *settings = (CviiiEdition *)context;
    *width = CVIII_W;
    *height = CVIII_H;
    if (!settings->enhanced ||
        (!settings->sprite_unlimited && !settings->stable_sprites))
        return cyc_frame_argb();
    if (!cyc_render_background(settings->presentation))
        return cyc_frame_argb();
    if (settings->stable_sprites && settings->sprite_layers.primed) {
        cviii_layers_draw(&settings->sprite_layers, settings->presentation,
                          cyc_frame_bg_opaque(), settings->layer_masks,
                          &layer_functions);
        return settings->presentation;
    }
    /* Composite up to 64 *OAM-present* sprites over the PPU background.
     * This cannot restore sprites the game never put in OAM.
     * Actual mid-frame CHR switching remains a limitation: experimental.
     * No emulated sprite overflow, sprite-0 hit, IRQ or DMA is altered.
     */
    cyc_render_sprites(settings->presentation, CVIII_W, CVIII_H, 0,
                       cyc_frame_bg_opaque(), NULL, NULL);
    return settings->presentation;
}

static const CycHostOption cviii_options[] = {
    {"--edition", true, "Original or Enhanced PC edition (Original default)"},
    {"--unlimited-sprites", true,
     "Enhanced experimental 64-OAM sprite compositor (0/1, default 0)"},
    {"--stable-sprites", true,
     "EXPERIMENTAL logical sprite-object layer order with 1-frame history (0/1, default 0)"},
    {"--sprite-object-trace", true,
     "Developer owner-local per-frame 28 object fields and 64 hardware OAM entries"},
    {"--audio-reg-trace", true,
     "Read-only 2A03/VRC6 audio register traffic for source separation research"},
    {"--asset-index", true,
     "Private read-only 655368-byte JP CHR index (no renderer substitution)"},
    {"--chr-audit", true,
     "Developer CSV for sampled VRC6 CHR pages and palette (requires asset index)"},
    {"--chr-fetch-audit", true,
     "Read-only actual PPU CHR fetch vs cached ROM scanline CSV (requires asset index)"},
    {"--frame-evidence", true,
     "Original PPU 9-bit frame fingerprint CSV for same sampled fetch frames"},
    {"--nt-fetch-audit", true,
     "Read-only PPU nametable and attribute bus values for sampled frames"},
};

static CycHostExtras cviii_extra = {
    .ctx = &cviii,
    .present = present,
    .load_setting = load_setting,
    .save_settings = save_settings,
    .power_on = power_on,
    .frame_begin = frame_begin,
    .frame_end = frame_end,
    .state_loaded = state_loaded,
    .options = cviii_options,
    .option_count = sizeof(cviii_options) / sizeof(cviii_options[0]),
    .option = option,
};

const CycHostExtras *cyc_host_extras(void) { return &cviii_extra; }
