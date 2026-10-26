#ifndef CVIII_LIGHTING_HOST_H
#define CVIII_LIGHTING_HOST_H
/* Optional actual ReShade add-on dynamically locates these game exports. */
#if defined(_WIN32)
#define CVIII_LIGHT_EXPORT __declspec(dllexport)
#else
#define CVIII_LIGHT_EXPORT
#endif
#ifdef __cplusplus
extern "C" {
#endif
/* UI-only runtime control implemented by cviii_edition.c.
 * SDL window scaling and event ownership remain in the private host overlay.
 * No changes to guest CPU, PPU, mapper, controller state or save states. */
CVIII_LIGHT_EXPORT int cviii_lighting_editor_active(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_input(int event,int native_x,int native_y);
int cviii_lighting_editor_status(char *text,unsigned capacity);
/* SDL-validated canonical key name, persisted under [Game] in config.ini. */
CVIII_LIGHT_EXPORT const char *cviii_lighting_editor_key(void);
int cviii_lighting_editor_set_key(const char *name);
/* Live editor data / bounded property updates; never modify guest state. */
#include "cviii_lighting.h"
CVIII_LIGHT_EXPORT const CviiiLighting *cviii_lighting_editor_model(void);
CVIII_LIGHT_EXPORT unsigned cviii_lighting_editor_room(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_select(int slot);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_add(int x,int y);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_property(int property,int value);
int cviii_lighting_editor_point(int slot,int *x,int *y);
/* ReShade/ImGui-neutral authoring operations. All require editor open. */
CVIII_LIGHT_EXPORT int cviii_lighting_editor_copy(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_paste(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_duplicate(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_name(const char *name);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_group(const char *group);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_scene(int property,int value);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_external_session(int open);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_external_active(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_apply_builtin(int id,int x,int y);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_apply_kit(int slot,int x,int y);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_capture_kit(int slot,const char *name);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_sky(int property,int value);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_builtin_count(void);
CVIII_LIGHT_EXPORT const char *cviii_lighting_editor_builtin_name(int id);


#ifdef __cplusplus
}
#endif
#endif
