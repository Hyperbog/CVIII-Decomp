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
enum { CVIII_SHAPE_RADIAL=0, CVIII_SHAPE_CONE=1, CVIII_SHAPE_SHAFT=2 };
typedef struct {
    uint32_t room;
    int level, red, green, blue;
    int used;
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
    int flicker;        /* 0 = subtle auto, 1 = none, 2 = torch */
} CviiiLight;
typedef struct {
    CviiiLight light[CVIII_LIGHT_MAX];
    CviiiSceneAmbient scenes[CVIII_SCENE_AMBIENT_MAX];
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
#endif
