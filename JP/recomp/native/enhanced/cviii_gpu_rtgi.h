#ifndef CVIII_GPU_RTGI_H
#define CVIII_GPU_RTGI_H
#include <stdint.h>
#include "cviii_lighting.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Optional Windows D3D11 compute prototype. Only compiled in a windowed
 * Enhanced host; failures must fall through to Standard C11 lighting.
 * Input/output is the presentation copy, NEVER the NES frame buffer. */
int cviii_gpu_rtgi_present(const CviiiLighting *settings,uint32_t *rgba,
                          uint32_t room,int camera,
                          const int scroll_x[CVIII_LIGHT_H],
                          const int scroll_y[CVIII_LIGHT_H],uint64_t frame,
                          int cascade_levels); /* 0=legacy, 2..4=RC */
const char *cviii_gpu_rtgi_status(void);
void cviii_gpu_rtgi_reset(void);
#ifdef __cplusplus
}
#endif
#endif
