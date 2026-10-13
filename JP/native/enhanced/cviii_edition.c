/* CVIII edition presentation, JP 0589.
 * Written for the pinned external NESRecomp cyc_host_extras ABI.
 * Game execution, CPU-visible PPU flags, mapper banking and timing are untouched.
 * No ROM data or NESRecomp source is copied here.
 */
#include "cyc_host_extras.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CVIII_W 256
#define CVIII_H 240

typedef struct {
    int enhanced;
    int sprite_unlimited;
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
    return false;
}

static void power_on(void *context)
{
    CviiiEdition *settings = (CviiiEdition *)context;
    /* Capture background only in the opt-in enhanced renderer.
     * Original PPU sprite evaluation and CPU-visible $2002 remain unchanged.
     * Do not reenable capture in frame_begin: that resets capture every call.
     */
    cyc_render_capture_background(settings->enhanced && settings->sprite_unlimited);
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
};

static CycHostExtras cviii_extra = {
    .ctx = &cviii,
    .present = present,
    .load_setting = load_setting,
    .save_settings = save_settings,
    .power_on = power_on,
    .options = cviii_options,
    .option_count = sizeof(cviii_options) / sizeof(cviii_options[0]),
    .option = option,
};

const CycHostExtras *cyc_host_extras(void) { return &cviii_extra; }
