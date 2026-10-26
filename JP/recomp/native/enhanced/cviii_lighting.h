#ifndef CVIII_LIGHTING_H
#define CVIII_LIGHTING_H
#include <stdint.h>
#include <stdio.h>
#define CVIII_LIGHT_MAX 24
#define CVIII_LIGHT_W 256
#define CVIII_LIGHT_H 240
#define CVIII_LIGHT_HUD 48

typedef struct {
    uint32_t room;
    int x,y,radius,energy;
    uint8_t red,green,blue;
    int used;
} CviiiLight;
typedef struct {
    CviiiLight light[CVIII_LIGHT_MAX];
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
#endif
