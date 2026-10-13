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
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CVIII_W 256
#define CVIII_H 240

typedef struct {
    int enhanced;
    int sprite_unlimited;
    CviiiChrIndex assets; /* read-only imported physical CHR; presentation only */
    CviiiChrAudit audit; /* opt-in read-only per-frame bank audit */
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
}

static void save_settings(void *context, FILE *file)
{
    (void)context;
    fprintf(file, "Edition = %s\nUnlimitedSprites = %d\n",
            cviii.enhanced ? "Enhanced" : "Original", cviii.sprite_unlimited);
}

static bool option(void *context, const char *name, const char *value)
{
    (void)context;
    if (!strcmp(name, "--edition")) return value && set_edition(value);
    if (!strcmp(name, "--unlimited-sprites"))
        return value && parse_boolean(value, &cviii.sprite_unlimited);
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
    (void)settings;
    cyc_render_capture_background(true);
}

static void frame_end(void *context)
{
    CviiiEdition *settings = (CviiiEdition *)context;
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
    if (!settings->enhanced || !settings->sprite_unlimited)
        return cyc_frame_argb();
    if (!cyc_render_background(settings->presentation))
        return cyc_frame_argb();
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
    {"--asset-index", true,
     "Private read-only 655368-byte JP CHR index (no renderer substitution)"},
    {"--chr-audit", true,
     "Developer CSV for sampled VRC6 CHR pages and palette (requires asset index)"},
};

static CycHostExtras cviii_extra = {
    .ctx = &cviii,
    .present = present,
    .load_setting = load_setting,
    .save_settings = save_settings,
    .power_on = power_on,
    .frame_end = frame_end,
    .options = cviii_options,
    .option_count = sizeof(cviii_options) / sizeof(cviii_options[0]),
    .option = option,
};

const CycHostExtras *cyc_host_extras(void) { return &cviii_extra; }
