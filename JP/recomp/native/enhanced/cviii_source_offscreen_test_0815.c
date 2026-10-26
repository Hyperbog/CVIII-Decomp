/* JP0815: ROM-free exact point-projection and no-interaction guards. */
#include "cviii_source_offscreen_0815.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
static void ok(int cond,const char *name){
    if(!cond){fprintf(stderr,"JP0815 FAIL: %s\n",name);exit(1);}
}
int main(void){
    const int left=85,width=426;
    unsigned checks=0;
    for(int cam=0;cam<512;cam++) {
        for(int point=0;point<512;point++) {
            /* Independent integer coordinate oracle, no original ROM. */
            const int x=point-cam+left;
            const int y=55;
            const int expect=(x>=0 && x<width) ?
                ((x>=left && x<left+256) ?
                 CVIII_PROBE_NATIVE_0815:CVIII_PROBE_MARGIN_0815) :
                CVIII_PROBE_OUTSIDE_0815;
            const CviiiSourceProjection0815 p=cviii_source_project_0815(
                point,55,cam,0,left,width,240);
            ok(p.screen_x==x && p.screen_y==y &&
               p.point_region==expect,"point projection parity");
            checks++;
        }
    }
    ok(cviii_chapel_visual_world_y_0815(1024,0x180u)==1463,
       "original chapel visual +$37 world-axis offset");
    ok(cviii_source_project_0815(32,55,80,0,left,width,240)
       .point_region==CVIII_PROBE_MARGIN_0815,
       "source can enter synthetic wide-only margin");
    ok(cviii_source_project_0815(32,55,0,0,left,width,240)
       .point_region==CVIII_PROBE_NATIVE_0815,
       "authentic chapel X32 remains in original game image");
    ok(cviii_source_project_0815(32,47,0,0,left,width,240)
       .point_region==CVIII_PROBE_OUTSIDE_0815,
       "gameplay layer never paints original HUD");
    ok(cviii_source_project_0815(32,240,0,0,left,width,240)
       .point_region==CVIII_PROBE_OUTSIDE_0815,
       "bottom clipping");
    ok(cviii_source_project_0815(32,55,0,0,-1,width,240)
       .point_region==CVIII_PROBE_OUTSIDE_0815,
       "invalid native crop rejected");
    ok(cviii_source_interaction_0815(0x0d,1)==
           CVIII_INTERACTION_NOT_ACTOR_0815,
       "event row is not an interactive actor");
    ok(cviii_source_interaction_0815(0x80,0)==
           CVIII_INTERACTION_ALLOCATION_UNVERIFIED_0815,
       "unverified source never acquires interaction authority");
    ok(cviii_source_interaction_0815(0x80,1)==
           CVIII_INTERACTION_MAY_ROUTE_B162_0815,
       "active type80 defers unresolved original special collision");
    ok(cviii_source_interaction_0815(0x3d,1)==
           CVIII_INTERACTION_UNSUPPORTED_0815,
       "unknown original source tag rejected");
    /* Fabricated PRG26 layout with the original pointer-table ABI. */
    uint8_t fake_prg26[16384]={0};
    fake_prg26[0x818du-0x8000u]=0x00u;
    fake_prg26[0x818eu-0x8000u]=0x90u;
    fake_prg26[0x9001u-0x8000u]=0x00u;
    fake_prg26[0x9002u-0x8000u]=0x91u;
    fake_prg26[0x9100u-0x8000u]=4u;
    CviiiSourceVisual0815 v=cviii_source_visual_0815(fake_prg26,0x0e,1);
    ok(v.valid && v.descriptor_cpu==0x9100u && v.pieces==4u,
       "original sprite selector/frame byte offsets resolve exactly");
    ok(!cviii_source_visual_0815(NULL,0x0e,1).valid,
       "unknown cartridge means unknown visual identity");
    fake_prg26[0x9100u-0x8000u]=28u;
    ok(!cviii_source_visual_0815(fake_prg26,0x0e,1).valid,
       "overlarge original sprite piece count rejected");
    printf("PASS JP0815 %u synthetic point parity cases + 13 guards\n",checks);
    return 0;
}
