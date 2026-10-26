#ifndef CVIII_LIGHTING_HOST_H
#define CVIII_LIGHTING_HOST_H
/* UI-only runtime control implemented by cviii_edition.c.
 * SDL window scaling and event ownership remain in the private host overlay.
 * No changes to guest CPU, PPU, mapper, controller state or save states. */
int cviii_lighting_editor_active(void);
int cviii_lighting_editor_input(int event,int native_x,int native_y);
int cviii_lighting_editor_status(char *text,unsigned capacity);
/* SDL-validated canonical key name, persisted under [Game] in config.ini. */
const char *cviii_lighting_editor_key(void);
int cviii_lighting_editor_set_key(const char *name);
#endif
