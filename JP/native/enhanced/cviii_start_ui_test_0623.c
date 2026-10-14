/* ROM-free numeric layout and original CHR-slot bounds of pause UI. */
#include "cviii_start_ui_0623.h"
#include <assert.h>
#include <stdio.h>
#define W 256u
#define H 240u
static unsigned char chr[CVIII_CHR_PIXEL_BYTES];
static uint32_t canvas[W*H+2u];
int main(void)
{
    CviiiChrIndex index={0};
    CviiiStartMenu menu={0};
    assert(cviii_start_defaults(&menu));
    assert(cviii_start_toggle(&menu,1,1));
    for(unsigned t=0x1041u;t<=0x1069u;t++)
        for(unsigned i=0;i<64u;i++)chr[t*64u+i]=3u;
    for(unsigned i=0;i<W*H;i++)canvas[1+i]=0xFF224466u;
    canvas[0]=0x00FEDCBAu;canvas[W*H+1u]=0x00ABCDEFu;
    assert(!cviii_start_ui_draw(canvas+1,W,H,&index,&menu));
    assert(!cviii_start_ui_draw(canvas+1,W+1,H,&index,&menu));
    index.pixels=chr;
    assert(cviii_start_ui_draw(canvas+1,W,H,&index,&menu));
    assert(canvas[1+52u*W+76u]==0xFFF1EEEAu);
    assert(canvas[1+79u*W+32u]==0xFFFF882Cu);
    assert(canvas[1+96u*W+32u]==0xFFF1EEEAu);
    assert(canvas[1]==0xFF224466u && canvas[W*H]==0xFF224466u);
    for(unsigned i=0;i<3u;i++)assert(cviii_start_move(&menu,1));
    assert(cviii_start_accept(&menu)==CVIII_START_NONE);
    assert(cviii_start_ui_draw(canvas+1,W,H,&index,&menu));
    assert(canvas[1+183u*W+40u]==0xFFFF882Cu);
    cviii_start_close(&menu);
    assert(!cviii_start_ui_draw(canvas+1,W,H,&index,&menu));
    assert(canvas[0]==0x00FEDCBAu && canvas[W*H+1u]==0x00ABCDEFu);
    puts("PASS JP0623 original-CHR pause UI, selected rows and safe bounds");
    return 0;
}
