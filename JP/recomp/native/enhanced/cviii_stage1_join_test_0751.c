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
    if(!check(!cviii_stage1_join_previous_0751(j,0,256,old,&offset),
       "expired source association"))return 5;
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
    free(frame);free(j);
    puts("PASS JP0751 authenticated room seams and bounded margin cache");
    return 0;
}
