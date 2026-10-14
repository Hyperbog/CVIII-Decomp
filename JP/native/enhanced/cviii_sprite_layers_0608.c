/* JP0608: one-frame PC-only sprite continuity; no machine-state changes.
 * This is an experimental visual improvement, not actor identity recovery.
 * Per-sprite pixels are captured during the host's frame_end callback.
 */
#include "cviii_sprite_layers_0608.h"
#include <stdlib.h>
#include <string.h>
static bool near(int a, int b, int radius) { return abs(a - b) <= radius; }
static bool matches(const CviiiLayerSprite *a, const CviiiLayerSprite *b,
                    unsigned old_slot, unsigned new_slot)
{
    if (!b->valid || !near(a->x,b->x,4) || !near(a->y,b->y,4) ||
        (a->attr & 0xC3) != (b->attr & 0xC3) || a->height != b->height)
        return false;
    return a->tile == b->tile ||
           (old_slot == new_slot && near(a->x,b->x,1) && near(a->y,b->y,1));
}
void cviii_layers_reset(CviiiSpriteLayers *layers)
{
    if (layers) memset(layers,0,sizeof(*layers));
}
static void sample(CviiiLayerSprite *s, const uint8_t *oam,
                   const uint8_t mask[CVIII_LAYER_H],
                   const uint8_t tall[CVIII_LAYER_H],
                   const uint16_t tables[CVIII_LAYER_H], const CviiiLayerFns *f)
{
    if (oam[0] >= 0xEF) return;
    unsigned y = (unsigned)oam[0]+1;
    if (y >= CVIII_LAYER_H || !(mask[y]&0x10)) return;
    s->valid=1; s->x=oam[3]; s->y=(uint8_t)y;
    s->tile=oam[1]; s->attr=oam[2]; s->height=tall[y]?16:8;
    for (unsigned row=0; row<s->height; ++row) {
        unsigned rr=(s->attr&0x80)?s->height-1-row:row;
        uint16_t base=s->height==16
          ? (uint16_t)(((s->tile&1u)?0x1000u:0u)+(s->tile&0xFEu)*16u+
                       (rr>=8u?16u:0u))
          : (uint16_t)(tables[y]+(unsigned)s->tile*16u);
        uint8_t lo=f->read_chr(f->user,(uint16_t)(base+(rr&7u)));
        uint8_t hi=f->read_chr(f->user,(uint16_t)(base+(rr&7u)+8u));
        for (unsigned x=0; x<8; ++x) {
            unsigned bit=(s->attr&0x40)?x:7u-x;
            s->pixels[row*8+x]=(uint8_t)(((lo>>bit)&1u) |
                                     (((hi>>bit)&1u)<<1u));
        }
    }
}
void cviii_layers_capture(CviiiSpriteLayers *s, const uint8_t oam[256],
                          const uint8_t mask[CVIII_LAYER_H],
                          const uint8_t tall[CVIII_LAYER_H],
                          const uint16_t tables[CVIII_LAYER_H],
                          const CviiiLayerFns *f)
{
    if (!s || !oam || !mask || !tall || !tables || !f || !f->read_chr) return;
    CviiiLayerSprite previous[CVIII_LAYER_SLOTS];
    memcpy(previous,s->current,sizeof(previous));
    memset(s->current,0,sizeof(s->current));
    memset(s->held,0,sizeof(s->held));
    s->held_now=0;
    unsigned present=0,old_present=0;
    for(unsigned i=0;i<CVIII_LAYER_SLOTS;++i) {
        sample(&s->current[i],oam+i*4,mask,tall,tables,f);
        present+=s->current[i].valid?1u:0u;
        old_present+=previous[i].valid?1u:0u;
    }
    /* Major scene transitions, menus and game-over must not leave ghosts. */
    bool scene_change=old_present>=8u && present*2u<old_present;
    if(s->primed && !scene_change) {
        for(unsigned i=0;i<CVIII_LAYER_SLOTS;++i) {
            if(!previous[i].valid)continue;
            bool found=false;
            for(unsigned j=0;j<CVIII_LAYER_SLOTS;++j)
                if(matches(&previous[i],&s->current[j],i,j)){found=true;break;}
            if(!found){s->held[i]=previous[i];++s->held_now;}
        }
    }
    s->primed=true; ++s->frames; s->total_held+=s->held_now;
}
static void paint(const CviiiLayerSprite *s,uint32_t *frame,const uint8_t *bg,
                  const uint8_t mask[CVIII_LAYER_H],const CviiiLayerFns *f)
{
    if(!s->valid)return;
    for(unsigned row=0;row<s->height;++row){
        unsigned y=(unsigned)s->y+row;
        if(y>=CVIII_LAYER_H || !(mask[y]&0x10))continue;
        for(unsigned col=0;col<8;++col){
            unsigned x=(unsigned)s->x+col;
            if(x>=CVIII_LAYER_W || (x<8 && !(mask[y]&0x04)))continue;
            unsigned color=s->pixels[row*8+col];
            if(!color)continue;
            size_t at=(size_t)y*CVIII_LAYER_W+x;
            if((s->attr&0x20) && bg && bg[at])continue;
            frame[at]=f->color(f->user,16u+(s->attr&3u)*4u+color);
        }
    }
}
void cviii_layers_draw(const CviiiSpriteLayers *s,uint32_t *frame,
                       const uint8_t *bg,const uint8_t mask[CVIII_LAYER_H],
                       const CviiiLayerFns *f)
{
    if(!s || !frame || !mask || !f || !f->color)return;
    /* NES lower-numbered OAM slots appear above higher slots. */
    for(int i=CVIII_LAYER_SLOTS-1;i>=0;--i) {
        paint(&s->held[i],frame,bg,mask,f);
        paint(&s->current[i],frame,bg,mask,f);
    }
}
