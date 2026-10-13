/* ROM-free independent presentation/edition contract, no 6502 reconstruction. */
#include "cyc_host_extras.h"
#include "cyc_core.h"
#include "cyc_render.h"
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

static uint32_t native[256*240];
static int capture_enabled, compose_calls, bg_reads;
const uint32_t *cyc_frame_argb(void) { return native; }
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
    assert(e->option_count == 3);
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
