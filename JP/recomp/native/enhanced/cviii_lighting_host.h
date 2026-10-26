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
CVIII_LIGHT_EXPORT unsigned cviii_lighting_editor_raw_room(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_alias(unsigned stable);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_global_capture(int slot,const char *name);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_global_link(int slot,int group);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_global_property(int slot,int property,int value);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_mask_add(int x,int y,int w,int h);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_world_point(int native_x,int native_y,int *world_x,int *world_y);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_mask_property(int slot,int property,int value);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_grade(int property,int value);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_kit_manage(int action,int source,int destination,const char *name);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_checkpoint(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_undo(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_redo(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_can_undo(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_can_redo(void);
/* 0 Standard = always supported; 1 GPU Prototype = Windows D3D11 compute.
 * The active frame falls back to Standard if the GPU backend fails. */
CVIII_LIGHT_EXPORT int cviii_lighting_editor_renderer(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_set_renderer(int mode);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_cascade_quality(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_set_cascade_quality(int quality);
CVIII_LIGHT_EXPORT const char *cviii_lighting_editor_gpu_status(void);
CVIII_LIGHT_EXPORT int cviii_lighting_editor_gpu_active(void);


#ifdef __cplusplus
}
#endif
#endif
