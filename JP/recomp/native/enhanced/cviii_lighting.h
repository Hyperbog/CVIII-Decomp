#ifndef CVIII_LIGHTING_H
#define CVIII_LIGHTING_H
#include <stdint.h>
#include <stdio.h>
#define CVIII_LIGHT_MAX 128
#define CVIII_LIGHT_W 256
#define CVIII_LIGHT_H 240
#define CVIII_LIGHT_HUD 48
#define CVIII_LIGHT_NAME_CAP 48
#define CVIII_LIGHT_GROUP_CAP 32
#define CVIII_SCENE_AMBIENT_MAX 32
#define CVIII_KIT_MAX 12
#define CVIII_KIT_PARTS 8
#define CVIII_GLOBAL_STYLE_MAX 16
#define CVIII_OCCLUDER_MAX 64
#define CVIII_SCENE_ALIAS_MAX 32
enum { CVIII_SHAPE_RADIAL=0, CVIII_SHAPE_CONE=1, CVIII_SHAPE_SHAFT=2 };
typedef struct {
    uint32_t room;
    int level, red, green, blue;
    int used;
    /* Sky is an independent additive fill, never an RGB multiply filter.
       strength 0..100, facing -1 top, 0 uniform, +1 bottom. */
    int sky, sky_red, sky_green, sky_blue, sky_facing;
    int exposure; /* signed centi-stops: -200..200 */
    int temperature; /* -100 warm, 0 neutral, +100 cool */
    int saturation; /* percent, 0..200, default 100 when unused */
    int graded;
} CviiiSceneAmbient;

typedef struct {
    uint32_t room;
    int x,y,radius,energy;
    uint8_t red,green,blue;
    int used;
    char name[CVIII_LIGHT_NAME_CAP];
    char group[CVIII_LIGHT_GROUP_CAP];
    int shape;          /* 0 radial, 1 spot cone, 2 parallel shaft */
    int angle;          /* degrees clockwise, 0 right, 90 down */
    int spread;         /* half-angle for cone, 5..85 degrees */
    int width;          /* shaft full width, 4..160 game pixels */
    int muted;          /* 1 = excluded from rendering */
    int flicker;        /* 0 subtle flame, 1 steady, 2 torch, 3 pulse, 4 ember */
    int anim_speed;     /* 0 legacy default, otherwise 1..400 percent */
    int anim_strength;  /* 0 legacy default, otherwise 1..100 percent */
    int style_link;     /* 0 local, 1..16 global photometric style */
} CviiiLight;
typedef struct {
    int used, count;
    char name[CVIII_LIGHT_NAME_CAP];
    CviiiLight part[CVIII_KIT_PARTS]; /* relative to selected anchor */
} CviiiLightKit;
typedef struct {
    int used;
    char name[CVIII_LIGHT_NAME_CAP];
    CviiiLight light;   /* values only; no world/room position sharing */
} CviiiGlobalStyle;
typedef struct {
    uint32_t room;
    int x,y,w,h;       /* author-drawn 2D world-space rectangle */
    int opacity;       /* shadow strength 0..100 */
    int softness;      /* penumbra offset 0..16 pixels */
    int used;
} CviiiOccluder;
typedef struct {
    uint32_t source, target;
    int used;
} CviiiSceneAlias;
typedef struct {
    CviiiLight light[CVIII_LIGHT_MAX];
    CviiiSceneAmbient scenes[CVIII_SCENE_AMBIENT_MAX];
    CviiiLightKit kits[CVIII_KIT_MAX];
    CviiiGlobalStyle styles[CVIII_GLOBAL_STYLE_MAX];
    CviiiOccluder masks[CVIII_OCCLUDER_MAX];
    CviiiSceneAlias aliases[CVIII_SCENE_ALIAS_MAX];
    CviiiLight clipboard;
    int clipboard_valid;
    int enabled,ambient,edit,selected,dragging;
} CviiiLighting;
void cviii_light_init(CviiiLighting *s);
void cviii_light_present(CviiiLighting *s,uint32_t *pixels,int width,int height,
                         uint32_t room,int camera_x,const int scroll_x[CVIII_LIGHT_H],
                         const int scroll_y[CVIII_LIGHT_H],uint64_t frame);
/* event: 1 toggle, 2 left down, 3 drag, 4 up, 5 delete,
 * 6/7 radius +/-, 8/9 intensity +/-, 10 color,
 * 11/12 ambient +/-, 13 select (right click) */
int cviii_light_event(CviiiLighting *s,int event,int x,int y,
                      uint32_t room,int camera_x,const int scroll_x[CVIII_LIGHT_H],
                      const int scroll_y[CVIII_LIGHT_H]);
int cviii_light_load(CviiiLighting *s,const char *key,const char *value);
void cviii_light_save(const CviiiLighting *s,FILE *file);
/* Pure C11 editor model; no SDL, external overlay, or ROM dependency. */
int cviii_light_copy(CviiiLighting *s,int slot);
int cviii_light_paste(CviiiLighting *s,uint32_t room,int x,int y);
int cviii_light_duplicate(CviiiLighting *s,int slot);
int cviii_light_rename(CviiiLighting *s,int slot,const char *name);
int cviii_light_group(CviiiLighting *s,int slot,const char *group);
int cviii_light_shape(CviiiLighting *s,int slot,int shape);
int cviii_light_scene_set(CviiiLighting *s,uint32_t room,int level,int red,int green,int blue);
void cviii_light_scene_get(const CviiiLighting *s,uint32_t room,int *level,int rgb[3]);
/* Global emitter rigs; IDs 0..builtins-1 are immutable default archetypes.
 * Captured kit slots are 0..CVIII_KIT_MAX-1; all placements are atomic. */
int cviii_light_builtin_count(void);
const char *cviii_light_builtin_name(int id);
int cviii_light_apply_builtin(CviiiLighting *s,int id,uint32_t room,int x,int y);
int cviii_light_kit_capture(CviiiLighting *s,int slot,int selected,const char *name);
int cviii_light_kit_apply(CviiiLighting *s,int slot,uint32_t room,int x,int y);
int cviii_light_kit_rename(CviiiLighting *s,int slot,const char *name);
int cviii_light_kit_clone(CviiiLighting *s,int from,int to);
int cviii_light_kit_delete(CviiiLighting *s,int slot);
int cviii_light_kit_load(CviiiLighting *s,const char *key,const char *value);
void cviii_light_kit_save(const CviiiLighting *s,FILE *file);
int cviii_light_sky_set(CviiiLighting *s,uint32_t room,int strength,int red,int green,int blue,int facing);
void cviii_light_sky_get(const CviiiLighting *s,uint32_t room,int *strength,int rgb[3],int *facing);
/* Global style: place locally, tune collectively; no geometry linking. */
int cviii_light_style_capture(CviiiLighting *s,int slot,int light,const char *name);
int cviii_light_style_link(CviiiLighting *s,int light,int slot);
int cviii_light_style_link_group(CviiiLighting *s,int light,int slot);
void cviii_light_effective(const CviiiLighting *s,const CviiiLight *source,CviiiLight *result);
int cviii_light_mask_add(CviiiLighting *s,uint32_t room,int x,int y,int w,int h);
int cviii_light_mask_remove(CviiiLighting *s,int slot);
float cviii_light_shadow(const CviiiLighting *s,uint32_t room,
                         int source_x,int source_y,int world_x,int world_y);
int cviii_light_grade_set(CviiiLighting *s,uint32_t room,int exposure,int temperature,int saturation);
void cviii_light_grade_get(const CviiiLighting *s,uint32_t room,
                           int *exposure,int *temperature,int *saturation);
uint32_t cviii_light_scene_resolve(const CviiiLighting *s,uint32_t source);
int cviii_light_scene_alias(CviiiLighting *s,uint32_t source,uint32_t target);
int cviii_light_extra_load(CviiiLighting *s,const char *key,const char *value);
void cviii_light_extra_save(const CviiiLighting *s,FILE *file);
/* Fixed-depth host authoring history, independent of emulated save slots. */
void cviii_light_history_reset(void);
void cviii_light_history_push(const CviiiLighting *s);
int cviii_light_history_undo(CviiiLighting *s);
int cviii_light_history_redo(CviiiLighting *s);
int cviii_light_history_can_undo(void);
int cviii_light_history_can_redo(void);

#endif
