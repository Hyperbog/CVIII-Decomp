#ifndef CVIII_LIGHTING_HOST_H
#define CVIII_LIGHTING_HOST_H
#ifdef __cplusplus
extern "C" {
#endif
/* UI-only runtime control implemented by cviii_edition.c.
 * SDL window scaling and event ownership remain in the private host overlay.
 * No changes to guest CPU, PPU, mapper, controller state or save states. */
int cviii_lighting_editor_active(void);
int cviii_lighting_editor_input(int event,int native_x,int native_y);
int cviii_lighting_editor_status(char *text,unsigned capacity);
/* SDL-validated canonical key name, persisted under [Game] in config.ini. */
const char *cviii_lighting_editor_key(void);
int cviii_lighting_editor_set_key(const char *name);
/* Live editor data / bounded property updates; never modify guest state. */
#include "cviii_lighting.h"
const CviiiLighting *cviii_lighting_editor_model(void);
unsigned cviii_lighting_editor_room(void);
int cviii_lighting_editor_select(int slot);
int cviii_lighting_editor_add(int x,int y);
int cviii_lighting_editor_property(int property,int value);
int cviii_lighting_editor_point(int slot,int *x,int *y);
/* ReShade/ImGui-neutral authoring operations. All require editor open. */
int cviii_lighting_editor_copy(void);
int cviii_lighting_editor_paste(void);
int cviii_lighting_editor_duplicate(void);
int cviii_lighting_editor_name(const char *name);
int cviii_lighting_editor_group(const char *group);
int cviii_lighting_editor_scene(int property,int value);

#ifdef __cplusplus
}
#endif
#endif
