/* JP0751 synthetic-only previous-room join and bounded side frame test. */
#include "cviii_stage1_join_0751.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int check(int ok,const char *msg) {
    if(!ok)fprintf(stderr,"JP0751 FAIL: %s\n",msg);
    return ok;
}
int main(void) {
    CviiiStage1Join0751 *j=calloc(1,sizeof *j);
    uint32_t *frame=calloc(CVIII_JOIN_W*CVIII_JOIN_H,sizeof(uint32_t));
    if(!check(j && frame,"fixture allocations"))return 1;
    const uint8_t a[3]={0,0,0}, b[3]={0,1,0},c[3]={0,1,2};
    uint8_t old[3];int offset=0;
    cviii_stage1_join_accept_0751(j,a,512,768);
    cviii_stage1_join_gap_0751(j);
    cviii_stage1_join_accept_0751(j,b,0,256);
    if(!check(cviii_stage1_join_previous_0751(j,0,256,old,&offset) &&
       !memcmp(old,a,3) && offset==768,"forward true preceding room"))return 2;
    cviii_stage1_join_reset_0751(j);
    cviii_stage1_join_accept_0751(j,a,100,768);
    cviii_stage1_join_accept_0751(j,c,0,768);
    if(!check(!cviii_stage1_join_previous_0751(j,0,768,old,&offset),
       "false teleport not joined"))return 3;
    cviii_stage1_join_reset_0751(j);
    cviii_stage1_join_accept_0751(j,b,0,256);
    cviii_stage1_join_accept_0751(j,c,512,768);
    if(!check(cviii_stage1_join_previous_0751(j,512,768,old,&offset) &&
       !memcmp(old,b,3) && offset==-256,"reverse authentic transition"))return 4;
    cviii_stage1_join_reset_0751(j);
    cviii_stage1_join_accept_0751(j,a,512,768);
    for(int i=0;i<CVIII_JOIN_GAP_MAX+1;i++)cviii_stage1_join_gap_0751(j);
    cviii_stage1_join_accept_0751(j,b,0,256);
    if(!check(cviii_stage1_join_previous_0751(j,0,256,old,&offset) &&
       !memcmp(old,a,3) && offset==768,
       "persistent preloaded room survives any transition duration"))return 5;
    /* A checkpoint may spawn in the next room without re-crossing the
     * transition. The decoded first-room atlas must remain visible. */
    cviii_stage1_join_soft_reset_0782(j);
    cviii_stage1_join_link_0782(j,a,768,b,256);
    cviii_stage1_join_accept_0751(j,b,0,256);
    cviii_stage1_join_restore_0782(j,b,0,256);
    if(!check(cviii_stage1_join_previous_0751(j,0,256,old,&offset) &&
       !memcmp(old,a,3) && offset==768,
       "checkpoint restored the real preceding room"))return 9;
    cviii_stage1_join_soft_reset_0782(j);
    cviii_stage1_join_accept_0751(j,c,100,768);
    cviii_stage1_join_restore_0782(j,c,100,768);
    if(!check(!cviii_stage1_join_previous_0751(j,100,768,old,&offset),
       "unknown connection must never be fabricated"))return 10;
    for(int y=0;y<CVIII_JOIN_H;y++)for(int x=0;x<CVIII_JOIN_W;x++)
        frame[y*CVIII_JOIN_W+x]=x<85 ? 0xff101010u:
           (x>=341 ? 0xff202020u:0xffabcdefu);
    cviii_stage1_join_cache_0751(j,frame);
    memset(frame,0,CVIII_JOIN_W*CVIII_JOIN_H*sizeof(uint32_t));
    for(int y=0;y<CVIII_JOIN_H;y++)for(int x=85;x<341;x++)
        frame[y*CVIII_JOIN_W+x]=0xffabcdefu;
    for(int i=0;i<CVIII_JOIN_HOLD_MAX;i++)
        if(!check(cviii_stage1_join_hold_0751(j,frame),"short hold"))return 6;
    if(!check(!cviii_stage1_join_hold_0751(j,frame),"bounded hold expiry") ||
       !check(frame[32*CVIII_JOIN_W]==0xff101010u &&
              frame[32*CVIII_JOIN_W+341]==0xff202020u &&
              frame[120*CVIII_JOIN_W+85]==0xffabcdefu &&
              frame[0]==0u && frame[0*CVIII_JOIN_W+341]==0u,
              "center and HUD never touched"))return 7;
    cviii_stage1_join_reset_0751(j);
    if(!check(!cviii_stage1_join_hold_0751(j,frame),"state reset clears history"))
       return 8;

    /* JP0790: known next/previous scenes are available without waiting
     * for a selector switch. The camera never moves a SECOND TIME when
     * the room join expires, even for a 256px checkpoint room. */
    cviii_stage1_join_soft_reset_0782(j);
    cviii_stage1_join_link_0782(j,a,768,b,256);
    uint8_t known[3];int projected=0;
    if(!check(cviii_stage1_join_neighbor_0790(j,a,512,768,1,known,&projected) &&
       !memcmp(known,b,3) && projected==-256,
       "next room right side projects into first room tail"))return 12;
    if(!check(cviii_stage1_join_neighbor_0790(j,b,0,256,-1,known,&projected) &&
       !memcmp(known,a,3) && projected==768,
       "previous room left side remains at true world offset"))return 13;
    cviii_stage1_join_soft_reset_0782(j);
    if(!check(cviii_stage1_join_neighbor_0790(j,a,526,768,1,known,&projected) &&
       !memcmp(known,b,3) && projected==-242,
       "current-ROM camera can move beyond viewport end before next room verifies"))
        return 16;
    if(!check(cviii_stage1_join_neighbor_0790(j,b,0,256,-1,known,&projected) &&
       projected==768,"neighbor survives respawn and scene reload"))return 14;
    if(!check(!cviii_stage1_join_neighbor_0790(j,c,0,768,-1,known,&projected),
       "unknown neighbors never fabricate scenery"))return 15;
    free(frame);free(j);
    puts("PASS JP0751 authenticated room seams and bounded margin cache");
    return 0;
}
