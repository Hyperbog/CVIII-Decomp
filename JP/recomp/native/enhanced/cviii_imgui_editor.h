#ifndef CVIII_IMGUI_EDITOR_H
#define CVIII_IMGUI_EDITOR_H
#include <SDL.h>
#ifdef __cplusplus
extern "C" {
#endif
/* True Dear ImGui SDL2 + SDL_Renderer bridge. C ABI for the C11 host.
 * All UI ownership is presentation-only; gameplay RAM/PPU remain untouched. */
/* SDL2's logical-size event filter scales mouse positions to the NES
 * viewport. Dear ImGui consumes WINDOW coordinates instead. */
void cviii_imgui_window_point(SDL_Renderer *renderer,int event_x,int event_y,
                             int *window_x,int *window_y);
int cviii_imgui_event(const SDL_Event *event, SDL_Window *window, SDL_Renderer *renderer);
int cviii_imgui_scene_click(int event, int native_x, int native_y);
int cviii_imgui_render(SDL_Window *window, SDL_Renderer *renderer);
void cviii_imgui_reset(void);
void cviii_imgui_shutdown(void);
#ifdef __cplusplus
}
#endif
#endif
