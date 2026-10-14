/* JP0623: pure original-font pause menu compositor, no SDL/PPU writes. */
#ifndef CVIII_START_UI_0623_H
#define CVIII_START_UI_0623_H
#include "cviii_start_menu_0623.h"
#include "cviii_chr_index_0598.h"
#include <stdint.h>
int cviii_start_ui_draw(uint32_t *pixels,unsigned w,unsigned h,
                        const CviiiChrIndex *assets,const CviiiStartMenu *menu);
#endif
