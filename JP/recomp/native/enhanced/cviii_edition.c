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
#include "cviii_lighting.h"
#include "cviii_lighting_host.h"
#include "cviii_object_oam_trace_0609.h"
#include "cviii_audio_bus_0610.h"
#include "cviii_sound_requests_0612.h"
#include "cviii_sound_decisions_0646.h"
#include "cviii_dmc_dma_trace_0650.h"
#include "cviii_audio_session_0614.h"
#include "cviii_audio_levels_0618.h"
#include "cviii_virtual_audio_0647.h"
#include "cviii_audio_ui_0619.h"
#include "cviii_menu_registry_0620.h"
#include "cviii_audio_menu_0620.h"
#include "cviii_audio_menu_state_0622.h"
#include "cviii_start_menu_0623.h"
#include "cviii_start_host_0623.h"
#include "cviii_start_ui_0623.h"
#include "cviii_slot_picker_0625.h"
#include "cviii_menu_stack_0626.h"
#ifdef CYC_WITH_RECOMP_UI
#include "recomp_runtime_ui.h"
#endif
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
    CviiiLighting lighting; /* separate host-only level lighting */
    char lighting_editor_key[32]; /* persisted SDL2 scancode name */
    uint64_t lighting_frame; /* host animation, never serialized to guest */
    CviiiObjectOamTrace object_trace; /* read-only JP PRG26 object/OAM correlation */
    CviiiAudioBus audio_bus; /* opt-in nonmutating 2A03/VRC6 sound writes */
    CviiiSoundRequests sound_requests; /* original fixed $E249 ingress only */
    CviiiSoundDecisions sound_decisions; /* opt-in $0C sound terminal observations */
    CviiiDmcDmaTrace dmc_dma_trace; /* opt-in actual DMC fetch physical-bank evidence */
    CviiiAudioSession audio_session; /* extra-CPU row-count epoch markers */
    CviiiAudioLevels volume; /* enhanced host gains, never emulated RAM */
    CviiiVirtualAudio virtual_audio; /* dormant until original program decoder is verified */
    int audio_ui_preview; /* opt-in independent visual QA */
    CviiiAudioMenuState audio_ui; /* F6 modal selection, no guest RAM */
    CviiiStartMenu start_menu; /* F4 menu actions, no guest RAM */
    CviiiSlotPicker slot_menu; /* JP0625, host-selected save file number */
    char audio_session_id[33]; /* launcher-supplied private session GUID */
    uint8_t layer_masks[CVIII_LAYER_H];
    CviiiChrIndex assets; /* read-only imported physical CHR; presentation only */
    CviiiChrAudit audit; /* opt-in read-only per-frame bank audit */
    CviiiChrFetchAudit fetch; /* opt-in actual PPU pattern-read observation */
    CviiiFrameEvidence frame_evidence; /* opt-in correlated PPU evidence */
    CviiiNtTrace nt_trace; /* opt-in real nametable and attribute reads */
    uint32_t presentation[CVIII_W * CVIII_H];
} CviiiEdition;

static CviiiEdition cviii = { .volume = CVIII_AUDIO_LEVELS_DEFAULT };
static int cviii_start_ready;
static int cviii_lighting_ready;
static int cviii_external_light_editor;

/* JP0620: optional built-in paused runtime menu rows for recomp-ui builds.
 * The separate F6 modal now uses the original CHR overlay on all supported
 * private windowed builds, including those built without recomp-ui.
 * Native pause/input routing remains in the separately pinned SDL overlay. */
#ifdef CYC_WITH_RECOMP_UI
typedef struct {
    CviiiAudioLevels *levels;
    CviiiVolumeChannel channel;
} CviiiVolumeMenuBinding;
static CviiiMenuRegistry cviii_menu;
static CviiiVolumeMenuBinding cviii_menu_bindings[3] = {
    {&cviii.volume,CVIII_VOLUME_MASTER},
    {&cviii.volume,CVIII_VOLUME_MUSIC},
    {&cviii.volume,CVIII_VOLUME_SFX}
};
static RecompRuntimeUiItem cviii_ui_rows[CVIII_MENU_MAX_ITEMS];
static RecompRuntimeUiCallbacks cviii_ui_callbacks;
static int cviii_menu_ready;

static int cviii_menu_get_volume(void *user,int *value)
{
    CviiiVolumeMenuBinding *b=(CviiiVolumeMenuBinding *)user;
    *value=cviii_audio_levels_get(b->levels,b->channel);
    return *value>=0;
}
static int cviii_menu_set_volume(void *user,int value)
{
    CviiiVolumeMenuBinding *b=(CviiiVolumeMenuBinding *)user;
    return cviii_audio_levels_set(b->levels,b->channel,value);
}
static int cviii_host_menu_get(void *ctx,const RecompRuntimeUiItem *it,int *out)
{
    return cviii_menu_get((const CviiiMenuRegistry *)ctx,it->key,out);
}
static int cviii_host_menu_set(void *ctx,const RecompRuntimeUiItem *it,int v)
{
    return cviii_menu_set((const CviiiMenuRegistry *)ctx,it->key,v);
}
static void cviii_init_audio_menu(CycHostExtras *extras)
{
    if(cviii_menu_ready)return;
    static const char *const keys[3]={
        "cviii.audio.master","cviii.audio.music","cviii.audio.sfx"
    };
    static const char *const labels[3]={
        "Master Volume","Music Volume (pending mixer)",
        "Sound Effects Volume (pending mixer)"
    };
    static const char *const descriptions[3]={
        "Enhanced output PCM master level, 0 to 100 in one-percent steps.",
        "Saved preference only until independent music voice mixing exists.",
        "Saved preference only until independent sound-effect mixing exists."
    };
    for(unsigned i=0;i<3u;++i) {
        CviiiMenuSetting setting={
            keys[i],"Audio",labels[i],descriptions[i],
            0,100,1,&cviii_menu_bindings[i],
            cviii_menu_get_volume,cviii_menu_set_volume
        };
        if(!cviii_menu_register(&cviii_menu,&setting)){
            fprintf(stderr,"CVIII JP0620: audio menu registration failed\n");
            return;
        }
    }
    /* Additional game-owned settings can be registered above without any
     * change to the host's navigation, save or pause behavior. */
    for(size_t i=0;i<cviii_menu.count;++i) {
        const CviiiMenuSetting *item=&cviii_menu.items[i];
        cviii_ui_rows[i]=(RecompRuntimeUiItem){
            .key=item->key, .section=item->section,
            .label=item->label, .description=item->description,
            .type=RECOMP_RUNTIME_UI_INT, .minimum=item->minimum,
            .maximum=item->maximum, .step=item->step
        };
    }
    cviii_menu_seal(&cviii_menu);
    cviii_ui_callbacks=(RecompRuntimeUiCallbacks){
        .context=&cviii_menu,
        .get_value=cviii_host_menu_get,
        .set_value=cviii_host_menu_set
    };
    extras->menu_items=cviii_ui_rows;
    extras->menu_item_count=cviii_menu.count;
    extras->menu_callbacks=&cviii_ui_callbacks;
    cviii_menu_ready=1;
}
#endif

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
        cviii_audio_menu_state_close(&cviii.audio_ui);
        cviii_start_close(&cviii.start_menu);
        cviii_slot_cancel(&cviii.slot_menu);
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
    else if (!strcmp(key,"LightingEditorKey"))
        (void)cviii_lighting_editor_set_key(value);
    else if (!strncmp(key,"Light",5) || !strncmp(key,"RoomAmbient",11) ||
             !strncmp(key,"RoomSky",7) || !strncmp(key,"GlobalStyle",11) ||
             !strncmp(key,"Occluder",8) || !strncmp(key,"SceneGrade",10) ||
             !strncmp(key,"SceneAlias",10))
        (void)cviii_light_load(&cviii.lighting,key,value);
    else (void)cviii_audio_levels_load(&cviii.volume,key,value);
}

static void save_settings(void *context, FILE *file)
{
    (void)context;
    fprintf(file, "Edition = %s\nUnlimitedSprites = %d\nStableSprites = %d\n",
            cviii.enhanced ? "Enhanced" : "Original",
            cviii.sprite_unlimited, cviii.stable_sprites);
    cviii_audio_levels_save(&cviii.volume,file);
    cviii_light_save(&cviii.lighting,file);
    fprintf(file,"LightingEditorKey = %s\n",cviii.lighting_editor_key);
}

static bool option(void *context, const char *name, const char *value)
{
    (void)context;
    if (!strcmp(name, "--edition")) return value && set_edition(value);
    if (!strcmp(name, "--unlimited-sprites"))
        return value && parse_boolean(value, &cviii.sprite_unlimited);
    if (!strcmp(name, "--stable-sprites"))
        return value && parse_boolean(value, &cviii.stable_sprites);
    /* Developer overrides only; final interface will use HUD-art sliders.
     * Music/SFX levels persist but do not yet affect the unsplit PCM bus. */
    if (!strcmp(name,"--audio-ui-preview"))
        return value && parse_boolean(value,&cviii.audio_ui_preview);
    if (!strcmp(name,"--master-volume") ||
        !strcmp(name,"--music-volume") ||
        !strcmp(name,"--sfx-volume")) {
        uint8_t percent;
        if (!cviii_audio_levels_parse(value,&percent)) return false;
        CviiiVolumeChannel channel =
            !strcmp(name,"--master-volume") ? CVIII_VOLUME_MASTER :
            !strcmp(name,"--music-volume") ? CVIII_VOLUME_MUSIC : CVIII_VOLUME_SFX;
        return cviii_audio_levels_set(&cviii.volume,channel,(int)percent)!=0;
    }
    if (!strcmp(name, "--audio-reg-trace")) {
        if (!value || !cviii_audio_bus_open(&cviii.audio_bus, value)) {
            fprintf(stderr, "CVIII: cannot open private 2A03/VRC6 audio register log\n");
            return false;
        }
        printf("CVIII: tracing sound chip writes; no changes to music or effects\n");
        return true;
    }
    if (!strcmp(name, "--sound-request-trace")) {
        if (!value || !cviii_sound_requests_open(&cviii.sound_requests, value)) {
            fprintf(stderr, "CVIII: cannot open private original JP sound-request CSV\n");
            return false;
        }
        printf("CVIII: read-only original $E249 request entries; no sound changes\n");
        return true;
    }
    if (!strcmp(name, "--sound-decision-trace")) {
        if (!value || !cviii_sound_decisions_open(&cviii.sound_decisions, value)) {
            fprintf(stderr, "CVIII: cannot open private original sound-decision CSV\n");
            return false;
        }
        printf("CVIII: original sound branch observation; no audio changes\n");
        return true;
    }
    if (!strcmp(name, "--dmc-dma-trace")) {
        if (!value || !cviii_dmc_dma_trace_open(&cviii.dmc_dma_trace,value)) {
            fprintf(stderr,"CVIII: cannot open private DMC DMA physical-bank CSV\n");
            return false;
        }
        printf("CVIII: actual DMC sample fetch and mapper write intent; original audio unchanged\n");
        return true;
    }
    if (!strcmp(name, "--audio-session-id")) {
        if (!value || strlen(value)!=32 || strspn(value,"0123456789abcdef")!=32)
            return false;
        memcpy(cviii.audio_session_id,value,33);
        return true;
    }
    if (!strcmp(name, "--audio-epoch-trace")) {
        if (!value || !cviii_audio_session_open(&cviii.audio_session,
                                               value,cviii.audio_session_id)) {
            fprintf(stderr,"CVIII: private audio epoch manifest open failed\n");
            return false;
        }
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
    settings->lighting.edit=0;
    settings->lighting.dragging=0;
    cviii_external_light_editor=0;
    settings->lighting_frame=0;
    cviii_audio_menu_state_close(&settings->audio_ui); /* reset cannot leave a stale modal */
    cviii_start_close(&settings->start_menu);
    cviii_slot_cancel(&settings->slot_menu);
    cviii_virtual_audio_clear(&settings->virtual_audio); /* no host voice survives power */
    cyc_render_capture_background(true);
    cviii_sound_decisions_boundary("power_on",cyc_cycle_count());
    cviii_dmc_dma_trace_boundary("power_on",cyc_cycle_count());
    cviii_audio_session_mark(&settings->audio_session,"power_on",
        cyc_cycle_count(),settings->sound_requests.requests,settings->audio_bus.writes,
        settings->sound_requests.output,settings->audio_bus.output);
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
    settings->lighting.edit=0;
    settings->lighting.dragging=0;
    cviii_external_light_editor=0;
    settings->lighting_frame=0;
    cviii_audio_menu_state_close(&settings->audio_ui); /* loaded gameplay never owns a stale modal */
    cviii_start_close(&settings->start_menu);
    cviii_slot_cancel(&settings->slot_menu);
    cviii_virtual_audio_clear(&settings->virtual_audio); /* clear on host load epoch */
    cviii_sound_decisions_boundary("state_loaded",cyc_cycle_count());
    cviii_dmc_dma_trace_boundary("state_loaded",cyc_cycle_count());
    cviii_audio_session_mark(&settings->audio_session,"state_loaded",
        cyc_cycle_count(),settings->sound_requests.requests,settings->audio_bus.writes,
        settings->sound_requests.output,settings->audio_bus.output);
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
    ++settings->lighting_frame;
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

static const uint32_t *present_game(void *context, int *width, int *height)
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

/* Present-frame, read-only camera. These original RAM selector meanings need
 * real-route QA before any stage geometry is considered certified. */
static uint32_t cviii_lighting_raw_room(void)
{
    const uint8_t *ram=cyc_cpu_ram();
    if(!ram)return UINT32_MAX;
    return ((uint32_t)ram[0x34u]<<24)|((uint32_t)ram[0x35u]<<16)|
           ((uint32_t)ram[0x36u]<<8)|(uint32_t)ram[0x07a0u];
}
static uint32_t cviii_lighting_room(void)
{
    return cviii_light_scene_resolve(&cviii.lighting,cviii_lighting_raw_room());
}
static int cviii_lighting_camera(void)
{
    const uint8_t *ram=cyc_cpu_ram();
    return ram ? ((int)ram[0x53u]|((int)ram[0x54u]<<8)) : 0;
}
static void cviii_lighting_scroll(int sx[CVIII_LIGHT_H],int sy[CVIII_LIGHT_H])
{
    for(int y=0;y<CVIII_LIGHT_H;++y){
        sx[y]=cyc_render_line_scroll_x(y);
        sy[y]=cyc_render_line_scroll_y(y);
    }
}
int cviii_lighting_editor_external_active(void)
{
    return cviii_external_light_editor;
}
int cviii_lighting_editor_external_session(int open)
{
    if(open && !cviii.enhanced)return 0;
    cviii_external_light_editor=open!=0;
    cviii.lighting.edit=open!=0;
    cviii.lighting.dragging=0;
    return 1;
}
int cviii_lighting_editor_active(void)
{
    return cviii.enhanced && cviii.lighting.edit;
}
int cviii_lighting_editor_input(int event,int x,int y)
{
    if(!cviii.enhanced)return 0;
    if(event==2 || event==5 || (event>=6 && event<=12))
        cviii_light_history_push(&cviii.lighting);
    int sx[CVIII_LIGHT_H],sy[CVIII_LIGHT_H];
    /* No private SDL pointer or guest state is ever handed to the editor. */
    if(event==2 || event==3 || event==13)
        cviii_lighting_scroll(sx,sy);
    return cviii_light_event(&cviii.lighting,event,x,y,
        cviii_lighting_room(),cviii_lighting_camera(),
        event==2 || event==3 || event==13 ? sx : NULL,
        event==2 || event==3 || event==13 ? sy : NULL);
}

/* Bounded game-owned edit operations. SDL only chooses user-visible values;
 * ownership, stage keys and original-frame PPU scroll stay here. */
const CviiiLighting *cviii_lighting_editor_model(void)
{
    return &cviii.lighting;
}
unsigned cviii_lighting_editor_room(void)
{
    return cviii_lighting_room();
}
int cviii_lighting_editor_select(int slot)
{
    CviiiLighting *v=&cviii.lighting;
    if(!cviii_lighting_editor_active() || slot<0 || slot>=CVIII_LIGHT_MAX ||
       !v->light[slot].used || v->light[slot].room!=cviii_lighting_room())
        return 0;
    v->selected=slot;
    v->dragging=0;
    return 1;
}
int cviii_lighting_editor_add(int x,int y)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    CviiiLighting *v=&cviii.lighting;
    if(!cviii_lighting_editor_active() || x<0 || x>=CVIII_W ||
       y<CVIII_LIGHT_HUD || y>=CVIII_H)return 0;
    int slot=-1;
    for(int i=0;i<CVIII_LIGHT_MAX;++i)
        if(!v->light[i].used){slot=i;break;}
    if(slot<0)return 0;
    int camera=cviii_lighting_camera();
    int origin=cyc_render_line_scroll_x(y);
    int delta=(origin-camera%512+1024)%512;
    if(delta>256)delta-=512;
    int wx=camera+delta+x;
    int wy=cyc_render_line_scroll_y(y);
    if(wx<0 || wx>65535 || wy<0 || wy>479)return 0;
    v->light[slot]=(CviiiLight){.room=cviii_lighting_room(),.x=wx,.y=wy,.radius=56,.energy=85,.red=255,.green=167,.blue=74,.used=1};
    v->selected=slot;
    v->enabled=1;
    v->dragging=0;
    return 1;
}
int cviii_lighting_editor_property(int property,int value)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    CviiiLighting *v=&cviii.lighting;
    if(!cviii_lighting_editor_active())return 0;
    if(property==0){v->enabled=value!=0;return 1;}
    if(property==1){v->ambient=value<35?35:(value>100?100:value);return 1;}
    if(v->selected<0 || v->selected>=CVIII_LIGHT_MAX)return 0;
    CviiiLight *l=&v->light[v->selected];
    if(!l->used || l->room!=cviii_lighting_room())return 0;
    if(property==2)l->radius=value<12?12:(value>160?160:value);
    else if(property==3)l->energy=value<5?5:(value>160?160:value);
    else if(property==4)l->red=(uint8_t)(value<0?0:(value>255?255:value));
    else if(property==5)l->green=(uint8_t)(value<0?0:(value>255?255:value));
    else if(property==6)l->blue=(uint8_t)(value<0?0:(value>255?255:value));
    else if(property==7)return cviii_light_shape(v,v->selected,value);
    else if(property==8)l->angle=value<0?0:(value>359?359:value);
    else if(property==9)l->spread=value<5?5:(value>85?85:value);
    else if(property==10)l->width=value<4?4:(value>160?160:value);
    else if(property==11)l->muted=value!=0;
    else if(property==12)l->flicker=value<0?0:(value>4?4:value);
    else if(property==15)l->anim_speed=value<0?0:(value>400?400:value);
    else if(property==16)l->anim_strength=value<0?0:(value>100?100:value);
    else if(property==13)l->x=value<0?0:(value>65535?65535:value);
    else if(property==14)l->y=value<0?0:(value>479?479:value);
    else return 0;
    return 1;
}
int cviii_lighting_editor_copy(void)
{
    CviiiLighting *v=&cviii.lighting;
    return cviii_lighting_editor_active() && cviii_light_copy(v,v->selected);
}
int cviii_lighting_editor_paste(void)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    CviiiLighting *v=&cviii.lighting;
    if(!cviii_lighting_editor_active() || !v->clipboard_valid)return 0;
    /* Paste into current scene's center, not original stage/viewport.
     * Per-scanline PPU coordinates are authoritative for visible rows. */
    int cam=cviii_lighting_camera(),y=120;
    int scan=cyc_render_line_scroll_x(y);
    int d=(scan-cam%512+1024)%512;
    if(d>256)d-=512;
    int world=cam+d+128;
    return cviii_light_paste(v,cviii_lighting_room(),world,
                             cyc_render_line_scroll_y(y))>=0;
}
int cviii_lighting_editor_duplicate(void)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    CviiiLighting *v=&cviii.lighting;
    return cviii_lighting_editor_active() &&
        cviii_light_duplicate(v,v->selected)>=0;
}
int cviii_lighting_editor_name(const char *text)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    CviiiLighting *v=&cviii.lighting;
    return cviii_lighting_editor_active() &&
        cviii_light_rename(v,v->selected,text);
}
int cviii_lighting_editor_group(const char *text)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    CviiiLighting *v=&cviii.lighting;
    return cviii_lighting_editor_active() &&
        cviii_light_group(v,v->selected,text);
}
int cviii_lighting_editor_scene(int property,int value)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return 0;
    int pct=0,rgb[3];
    const uint32_t room=cviii_lighting_room();
    cviii_light_scene_get(&cviii.lighting,room,&pct,rgb);
    if(property==0)pct=value;
    else if(property>=1 && property<=3)rgb[property-1]=value;
    else return 0;
    return cviii_light_scene_set(&cviii.lighting,room,pct,rgb[0],rgb[1],rgb[2]);
}

static int cviii_lighting_placement(int native_x,int native_y,int *wx,int *wy)
{
    if(!wx || !wy || !cviii_lighting_editor_active())return 0;
    if(native_x<0)native_x=128;
    if(native_y<0)native_y=120;
    if(native_x>=CVIII_W || native_y<CVIII_LIGHT_HUD ||
       native_y>=CVIII_H)return 0;
    int cam=cviii_lighting_camera();
    int sc=cyc_render_line_scroll_x(native_y);
    int d=(sc-cam%512+1024)%512;
    if(d>256)d-=512;
    int x=cam+d+native_x,y=cyc_render_line_scroll_y(native_y);
    if(x<0 || x>65535 || y<0 || y>479)return 0;
    *wx=x;*wy=y;return 1;
}
int cviii_lighting_editor_world_point(int native_x,int native_y,
                                       int *wx,int *wy)
{
    return cviii_lighting_placement(native_x,native_y,wx,wy);
}
int cviii_lighting_editor_builtin_count(void)
{
    return cviii_light_builtin_count();
}
const char *cviii_lighting_editor_builtin_name(int id)
{
    return cviii_light_builtin_name(id);
}
int cviii_lighting_editor_apply_builtin(int id,int native_x,int native_y)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    int wx=0,wy=0;
    if(!cviii_lighting_placement(native_x,native_y,&wx,&wy))return 0;
    return cviii_light_apply_builtin(&cviii.lighting,id,
        cviii_lighting_room(),wx,wy)>=0;
}
int cviii_lighting_editor_apply_kit(int slot,int native_x,int native_y)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    int wx=0,wy=0;
    if(!cviii_lighting_placement(native_x,native_y,&wx,&wy))return 0;
    return cviii_light_kit_apply(&cviii.lighting,slot,
        cviii_lighting_room(),wx,wy)>=0;
}
int cviii_lighting_editor_capture_kit(int slot,const char *name)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return 0;
    CviiiLighting *v=&cviii.lighting;
    if(v->selected<0 || v->selected>=CVIII_LIGHT_MAX ||
       !v->light[v->selected].used ||
       v->light[v->selected].room!=cviii_lighting_room())return 0;
    return cviii_light_kit_capture(v,slot,v->selected,name);
}
int cviii_lighting_editor_sky(int property,int value)
{
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return 0;
    int level=0,rgb[3],face=-1;
    uint32_t room=cviii_lighting_room();
    cviii_light_sky_get(&cviii.lighting,room,&level,rgb,&face);
    if(property==0)level=value;
    else if(property>=1 && property<=3)rgb[property-1]=value;
    else if(property==4)face=value;
    else return 0;
    return cviii_light_sky_set(&cviii.lighting,room,level,
                               rgb[0],rgb[1],rgb[2],face);
}

/* Manual scene aliases bridge transient gameplay selectors safely.
 * Existing room IDs are unmodified until the user explicitly maps one. */
unsigned cviii_lighting_editor_raw_room(void){return cviii_lighting_raw_room();}
int cviii_lighting_editor_alias(unsigned stable){
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    return cviii_lighting_editor_active() &&
        cviii_light_scene_alias(&cviii.lighting,cviii_lighting_raw_room(),stable);
}
int cviii_lighting_editor_global_capture(int slot,const char *name){
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return 0;
    int selected=cviii.lighting.selected;
    if(selected<0 || selected>=CVIII_LIGHT_MAX ||
       !cviii.lighting.light[selected].used ||
       cviii.lighting.light[selected].room!=cviii_lighting_room())return 0;
    return cviii_light_style_capture(&cviii.lighting,slot,selected,name);
}
int cviii_lighting_editor_global_link(int slot,int group){
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return 0;
    int selected=cviii.lighting.selected;
    if(selected<0 || selected>=CVIII_LIGHT_MAX ||
       !cviii.lighting.light[selected].used ||
       cviii.lighting.light[selected].room!=cviii_lighting_room())return 0;
    return group?
        cviii_light_style_link_group(&cviii.lighting,selected,slot):
        cviii_light_style_link(&cviii.lighting,selected,slot);
}
int cviii_lighting_editor_kit_manage(int action,int source,
                                       int destination,const char *name)
{
    if(!cviii_lighting_editor_active())return 0;
    cviii_light_history_push(&cviii.lighting);
    if(action==1)return cviii_light_kit_rename(&cviii.lighting,source,name);
    if(action==2)return cviii_light_kit_clone(&cviii.lighting,source,destination);
    if(action==3)return cviii_light_kit_delete(&cviii.lighting,source);
    return 0;
}
int cviii_lighting_editor_global_property(int slot,int property,int value)
{
    if(!cviii_lighting_editor_active() || slot<0 || slot>=CVIII_GLOBAL_STYLE_MAX ||
       !cviii.lighting.styles[slot].used)return 0;
    cviii_light_history_push(&cviii.lighting);
    CviiiLight *p=&cviii.lighting.styles[slot].light;
    if(property==2)p->radius=value<12?12:value>160?160:value;
    else if(property==3)p->energy=value<5?5:value>160?160:value;
    else if(property==4)p->red=(uint8_t)(value<0?0:value>255?255:value);
    else if(property==5)p->green=(uint8_t)(value<0?0:value>255?255:value);
    else if(property==6)p->blue=(uint8_t)(value<0?0:value>255?255:value);
    else if(property==7)p->shape=value<0?0:value>2?2:value;
    else if(property==8)p->angle=value<0?0:value>359?359:value;
    else if(property==9)p->spread=value<5?5:value>85?85:value;
    else if(property==10)p->width=value<4?4:value>160?160:value;
    else if(property==12)p->flicker=value<0?0:value>4?4:value;
    else if(property==15)p->anim_speed=value<0?0:value>400?400:value;
    else if(property==16)p->anim_strength=value<0?0:value>100?100:value;
    else return 0;
    return 1;
}
int cviii_lighting_editor_mask_add(int x,int y,int w,int h){
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return -1;
    return cviii_light_mask_add(&cviii.lighting,cviii_lighting_room(),x,y,w,h);
}
int cviii_lighting_editor_mask_property(int slot,int property,int value){
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active() || slot<0 || slot>=CVIII_OCCLUDER_MAX)
        return 0;
    CviiiOccluder *m=&cviii.lighting.masks[slot];
    if(!m->used || m->room!=cviii_lighting_room())return 0;
    if(property==0){
        return cviii_light_mask_remove(&cviii.lighting,slot);
    }
    CviiiOccluder t=*m;
    if(property==1)t.x=value;
    else if(property==2)t.y=value;
    else if(property==3)t.w=value;
    else if(property==4)t.h=value;
    else if(property==5)t.opacity=value;
    else if(property==6)t.softness=value;
    else return 0;
    if(t.x<0 || t.y<0 || t.w<1 || t.h<1 || t.x>65535-t.w ||
       t.y>479-t.h || t.opacity<0 || t.opacity>100 ||
       t.softness<0 || t.softness>16)return 0;
    *m=t;return 1;
}
int cviii_lighting_editor_grade(int property,int value){
    if(cviii_lighting_editor_active())cviii_light_history_push(&cviii.lighting);
    if(!cviii_lighting_editor_active())return 0;
    int ev=0,temp=0,sat=100;
    unsigned room=cviii_lighting_room();
    cviii_light_grade_get(&cviii.lighting,room,&ev,&temp,&sat);
    if(property==0)ev=value;
    else if(property==1)temp=value;
    else if(property==2)sat=value;
    else return 0;
    return cviii_light_grade_set(&cviii.lighting,room,ev,temp,sat);
}

int cviii_lighting_editor_checkpoint(void){
    if(!cviii_lighting_editor_active())return 0;
    cviii_light_history_push(&cviii.lighting);
    return 1;
}
int cviii_lighting_editor_undo(void){
    return cviii_lighting_editor_active() &&
        cviii_light_history_undo(&cviii.lighting);
}
int cviii_lighting_editor_redo(void){
    return cviii_lighting_editor_active() &&
        cviii_light_history_redo(&cviii.lighting);
}
int cviii_lighting_editor_can_undo(void){return cviii_light_history_can_undo();}
int cviii_lighting_editor_can_redo(void){return cviii_light_history_can_redo();}

int cviii_lighting_editor_point(int slot,int *x,int *y)
{
    if(!x || !y || slot<0 || slot>=CVIII_LIGHT_MAX)return 0;
    const CviiiLight *l=&cviii.lighting.light[slot];
    if(!l->used || l->room!=cviii_lighting_room())return 0;
    int camera=cviii_lighting_camera();
    int best=999,screen_y=-1,screen_x=-1;
    for(int row=CVIII_LIGHT_HUD;row<CVIII_H;++row){
        int dy=cyc_render_line_scroll_y(row)-l->y;
        if(dy<0)dy=-dy;
        if(dy>=best || dy>1)continue;
        int sc=cyc_render_line_scroll_x(row);
        int dx=(sc-camera%512+1024)%512;
        if(dx>256)dx-=512;
        int xp=l->x-(camera+dx);
        if(xp<0 || xp>=CVIII_W)continue;
        best=dy;screen_y=row;screen_x=xp;
    }
    if(screen_y<0)return 0;
    *x=screen_x;*y=screen_y;
    return 1;
}

/* Editor preview feedback: host-only, no SDL dependency and no RAM writes. */
int cviii_lighting_editor_status(char *out,unsigned cap)
{
    if(!out || !cap)return 0;
    const CviiiLighting *v=&cviii.lighting;
    int i=v->selected;
    if(i<0 || i>=CVIII_LIGHT_MAX || !v->light[i].used){
        return snprintf(out,cap,"AMBIENT %d%% | no light selected",v->ambient)>=0;
    }
    const CviiiLight *l=&v->light[i];
    return snprintf(out,cap,"LIGHT %d: R=%d POWER=%d RGB=%u,%u,%u AMB=%d%%",
                    i+1,l->radius,l->energy,l->red,l->green,l->blue,v->ambient)>=0;
}

/* Expose only the canonical, bounded SDL key name; no SDL types needed
 * in this C11 Enhanced module (headless and Windows builds share it). */
const char *cviii_lighting_editor_key(void)
{
    return cviii.lighting_editor_key[0]?cviii.lighting_editor_key:"Home";
}
int cviii_lighting_editor_set_key(const char *name)
{
    if(!name)return 0;
    size_t count=strlen(name);
    if(count==0 || count>=sizeof(cviii.lighting_editor_key))return 0;
    for(size_t i=0;i<count;++i){
        char c=name[i];
        if(!((c>='A' && c<='Z') || (c>='a' && c<='z') ||
             (c>='0' && c<='9') || c==' ' || c=='-'))return 0;
    }
    memcpy(cviii.lighting_editor_key,name,count+1);
    return 1;
}

/* JP0623 game-owned Start/Pause state and stable action identities. */
int cviii_pause_active(void)
{
    return cviii_menu_stack_parent_active(&cviii.start_menu,&cviii.audio_ui);
}
int cviii_pause_toggle(void)
{
    if(!cviii_start_ready) {
        if(!cviii_start_defaults(&cviii.start_menu))return 0;
        cviii_start_seal(&cviii.start_menu);
        cviii_start_ready=1;
    }
    if(cviii.audio_ui.open)return 0; /* audio owns input until Back */
    if(cviii.start_menu.open)cviii_slot_cancel(&cviii.slot_menu);
    return cviii_start_toggle(&cviii.start_menu,cviii.enhanced,
                               cviii.assets.pixels!=NULL);
}
void cviii_pause_close(void)
{
    cviii_start_close(&cviii.start_menu);
    cviii_slot_cancel(&cviii.slot_menu);
}
/* JP0625: game-only slot edits; host owns authenticated state serialization. */
int cviii_pause_slot_active(void)
{
    return cviii_pause_active() && cviii_slot_active(&cviii.slot_menu);
}
int cviii_pause_slot_begin(int action,unsigned current_slot)
{
    if(!cviii_pause_active() || !cviii.enhanced)return 0;
    return cviii_slot_begin(&cviii.slot_menu,(CviiiStartAction)action,current_slot);
}
void cviii_pause_slot_cancel(void)
{
    cviii_slot_cancel(&cviii.slot_menu);
}
int cviii_pause_slot_step(int direction)
{
    return cviii_pause_active() &&
           cviii_slot_step(&cviii.slot_menu,direction);
}
int cviii_pause_slot_accept(unsigned *slot)
{
    if(!cviii_pause_active())return (int)CVIII_START_NONE;
    return (int)cviii_slot_accept(&cviii.slot_menu,slot);
}
void cviii_pause_move(int direction)
{
    if(cviii_pause_active())
        (void)cviii_start_move(&cviii.start_menu,direction);
}
int cviii_pause_accept(void)
{
    return cviii_pause_active() ?
        (int)cviii_start_accept(&cviii.start_menu) : (int)CVIII_START_NONE;
}
/* JP0626: child Audio holds parent selection, returns there after Back. */
int cviii_pause_audio_enter(void)
{
    return cviii_menu_stack_enter_audio(&cviii.start_menu,&cviii.audio_ui,
                                        cviii.enhanced,cviii.assets.pixels!=NULL);
}

/* JP0620 game-owned UI control exported to the private window host overlay.
 * No SDL dependency here; the host handles pause, input and saving config. */
int cviii_audio_menu_active(void)
{
    return cviii.audio_ui.open;
}
int cviii_audio_menu_toggle(void)
{
    return cviii_audio_menu_state_toggle(&cviii.audio_ui,
        cviii.enhanced,cviii.assets.pixels!=NULL);
}
void cviii_audio_menu_close(void)
{
    cviii_audio_menu_state_close(&cviii.audio_ui);
}
int cviii_audio_menu_move(int direction)
{
    return cviii_audio_menu_state_move(&cviii.audio_ui,&cviii.volume,direction);
}

/* Audio hook only changes presentation PCM, not APU registers or CPU state.
 * Legacy original debug mode is kept unscaled for behavioral A/B checks. */
/* JP0619: developer preview composes owner-verified CHR pixels at the
 * presentation boundary only, after the unaltered gameplay picture. */
static const uint32_t *present(void *context,int *width,int *height)
{
    CviiiEdition *settings=(CviiiEdition *)context;
    const uint32_t *frame=present_game(context,width,height);
    if(settings->enhanced && (settings->lighting.enabled || settings->lighting.edit) &&
       *width==CVIII_W && *height==CVIII_H){
        int sx[CVIII_LIGHT_H],sy[CVIII_LIGHT_H];
        cviii_lighting_scroll(sx,sy);
        if(frame!=settings->presentation)
            memcpy(settings->presentation,frame,sizeof settings->presentation);
        cviii_light_present(&settings->lighting,settings->presentation,
            CVIII_W,CVIII_H,cviii_lighting_room(),cviii_lighting_camera(),
            sx,sy,settings->lighting_frame);
        frame=settings->presentation;
    }
    if (settings->enhanced && !settings->audio_ui.open &&
        settings->start_menu.open && settings->assets.pixels && *width==CVIII_W && *height==CVIII_H) {
        if(frame!=settings->presentation)
            memcpy(settings->presentation,frame,sizeof settings->presentation);
        if(cviii_pause_slot_active() &&
           cviii_start_slot_ui_draw(settings->presentation,CVIII_W,CVIII_H,
                                    &settings->assets,&settings->slot_menu))
            return settings->presentation;
        if(cviii_start_ui_draw(settings->presentation,CVIII_W,CVIII_H,
                               &settings->assets,&settings->start_menu))
            return settings->presentation;
    }
    if (!settings->enhanced ||
        (!settings->audio_ui_preview && !settings->audio_ui.open) ||
        !settings->assets.pixels || *width!=CVIII_W || *height!=CVIII_H)
        return frame;
    if (frame!=settings->presentation)
        memcpy(settings->presentation,frame,sizeof settings->presentation);
    if (!cviii_audio_ui_render_mode(settings->presentation,CVIII_W,CVIII_H,
                                    &settings->assets,&settings->volume,
                                    settings->audio_ui.open ? settings->audio_ui.selected : 0u,
                                    settings->audio_ui.open!=0))
        return frame;
    return settings->presentation;
}
static void audio_mix(void *context,int16_t *samples,size_t count)
{
    const CviiiEdition *settings=(const CviiiEdition *)context;
    if (settings->enhanced)
        cviii_audio_levels_master_pcm(&settings->volume,samples,count);
}

static const CycHostOption cviii_options[] = {
    {"--edition", true, "Original or Enhanced PC edition (Original default)"},
    {"--unlimited-sprites", true,
     "Enhanced experimental 64-OAM sprite compositor (0/1, default 0)"},
    {"--stable-sprites", true,
     "EXPERIMENTAL logical sprite-object layer order with 1-frame history (0/1, default 0)"},
    {"--sprite-object-trace", true,
     "Developer owner-local per-frame 28 object fields and 64 hardware OAM entries"},
    {"--audio-ui-preview", true, "Developer only: draw noninteractive authentic health-bar UI"},
    {"--master-volume", true, "Enhanced master PCM gain, 0..100 (1% increments)"},
    {"--music-volume", true, "Reserved persistent music gain, requires separate bus"},
    {"--sfx-volume", true, "Reserved persistent SFX gain, requires separate bus"},
    {"--audio-reg-trace", true,
     "Read-only 2A03/VRC6 audio register traffic for source separation research"},
    {"--sound-request-trace", true,
     "Original JP fixed $E249 sound request entry register/stack snapshots"},
    {"--sound-decision-trace", true,
     "Owner-only original PRG0C sound request/terminal decision CSV (no audio change)"},
    {"--dmc-dma-trace", true,
     "Private actual DMC DMA ROM-byte/PRG-bank fetch and VRC6 bank-write-intent CSV"},
    {"--audio-session-id", true, "Owner-local GUID binding both audio traces"},
    {"--audio-epoch-trace", true, "Owner-local power-on/load epoch row boundaries"},
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
    .audio_mix = audio_mix,
    .options = cviii_options,
    .option_count = sizeof(cviii_options) / sizeof(cviii_options[0]),
    .option = option,
};

const CycHostExtras *cyc_host_extras(void)
{
    if(!cviii_lighting_ready){
        cviii_light_init(&cviii.lighting);
        cviii_light_history_reset();
        (void)cviii_lighting_editor_set_key("Home");
        cviii_lighting_ready=1;
    }
#ifdef CYC_WITH_RECOMP_UI
    cviii_init_audio_menu(&cviii_extra);
#endif
    return &cviii_extra;
}
