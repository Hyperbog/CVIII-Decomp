/* ROM-free independent presentation/edition contract, no 6502 reconstruction. */
#include "cyc_host_extras.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include "cviii_chr_fetch_0600.h"
#include "cviii_nt_trace_0606.h"
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
/* Read-only JP0599 debug interface mocks for isolated host extension test. */
const uint8_t *cyc_ppu_palette(void) {
    static uint8_t palette[32];
    return palette;
}
void cyc_hw_state_dump(void *target) {
    FILE *out = (FILE *)target;
    if (!out) return;
    fprintf(out, "cart.ctrl 20\n");
    for (unsigned i = 0; i < 8; ++i)
        fprintf(out, "cart.vrc_chr[%u] %03X\n", i, i);
    for (unsigned i = 0; i < 8; ++i)
        fprintf(out, "cart.chr_off[%u] %06X\n", i, i * 1024);
}

static CviiiChrFetchHook capture_hook;
void cviii_chr_fetch_set_hook(CviiiChrFetchHook hook) { capture_hook = hook; }
static CviiiNtHook nt_hook;
void cviii_nt_set_hook(CviiiNtHook hook) { nt_hook = hook; }
static uint32_t native[256*240];
static int capture_enabled, compose_calls, bg_reads;
const uint32_t *cyc_frame_argb(void) { return native; }
/* JP0601 pure read-only original PPU views for the isolated host test. */
const uint16_t *cyc_frame_index(void) {
    static uint16_t pixels[256*240];
    return pixels;
}
const CycLine *cyc_frame_lines(void) {
    static CycLine lines[240];
    return lines;
}
const uint8_t *cyc_frame_bg_opaque(void) { static uint8_t mask[256*240]; return mask; }
void cyc_render_capture_background(bool enabled) { capture_enabled=enabled; }
bool cyc_render_background(uint32_t *out) {
    bg_reads++;
    if (!capture_enabled) return false;
    for (int i=0;i<256*240;++i) out[i]=0xFF003366u;
    return true;
}
void cyc_render_sprites(uint32_t *out,int w,int h,int x,const uint8_t *bg,
                        CycSpritePlaceFn place, void *ctx) {
    (void)x;(void)place;(void)ctx;(void)bg;
    assert(w==256 && h==240);
    compose_calls++;
    out[10]=0xFF00FFFFu;
}
int main(void) {
    const CycHostExtras *e=cyc_host_extras();
    assert(e && e->options && e->option && e->present);
    assert(e->option_count == 7);
    assert(!e->option(e->ctx,"--asset-index",(const char *)0));
    int w=0,h=0;
    e->power_on(e->ctx);
    assert(capture_enabled);
    assert(e->present(e->ctx,&w,&h)==native && w==256 && h==240);
    assert(!compose_calls && !bg_reads);
    assert(e->option(e->ctx,"--unlimited-sprites","1"));
    e->power_on(e->ctx);
    assert(capture_enabled);
    assert(e->present(e->ctx,&w,&h)==native);
    assert(e->option(e->ctx,"--edition","enhanced"));
    assert(!e->option(e->ctx,"--edition","unknown"));
    e->power_on(e->ctx);
    assert(capture_enabled);
    const uint32_t *p=e->present(e->ctx,&w,&h);
    assert(p!=native && p[10]==0xFF00FFFFu);
    assert(compose_calls==1 && bg_reads==1);
    e->load_setting(e->ctx,"UnlimitedSprites","0");
    e->power_on(e->ctx);
    assert(capture_enabled && e->present(e->ctx,&w,&h)==native);
    e->load_setting(e->ctx,"Edition","Original");
    assert(e->present(e->ctx,&w,&h)==native);
    FILE *f=tmpfile();assert(f);e->save_settings(e->ctx,f);rewind(f);
    char text[128]={0};size_t n=fread(text,1,sizeof(text)-1,f);assert(n>0);fclose(f);
    assert(strstr(text,"Edition = Original") && strstr(text,"UnlimitedSprites = 0"));
    puts("PASS CVIII Original fallback / Enhanced compositor / persisted settings");
    return 0;
}
