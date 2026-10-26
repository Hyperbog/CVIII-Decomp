/* JP0803 synthetic Stage 1 atlas metadata and original actor shadow. */
#include "cviii_level1_world_0803.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int check(int ok,const char *name){
    if(!ok)fprintf(stderr,"JP0803 FAIL %s\n",name);
    return ok;
}
int main(void){
    CviiiStage1Atlas0724 *atlas=calloc(1,sizeof *atlas);
    CviiiLevel1World0803 *world=calloc(1,sizeof *world);
    if(!atlas || !world)return 1;
    atlas->loaded=1;
    static const int widths[]={768,256,256,768,512,768,768,1024};
    static const int heights[]={192,192,512,192,192,192,192,192};
    for(int i=0;i<8;i++){
        atlas->rooms[i].width_tiles=(uint16_t)(widths[i]/8);
        atlas->rooms[i].height_tiles=(uint16_t)(heights[i]/8);
        atlas->rooms[i].vertical=(uint8_t)(i==2);
    }
    const uint8_t first[]={0,0,0},second[]={0,1,0},
                  third[]={0,2,0},vertical[]={0,1,1};
    if(!check(cviii_world_build_0803(world,atlas),"preload eight atlas rooms") ||
       !check(world->ready && world->placed_count==2 &&
         world->rooms[1].x==768 && !world->rooms[5].placed,
         "only physically proved stage connection placed"))return 2;
    int32_t x=0,y=0;
    if(!check(cviii_world_camera_0803(world,second,50,0,&x,&y)&&x==818,
              "physical map camera")
       || !check(!cviii_world_camera_0803(world,third,0,0,&x,&y),
              "unknown route stays unplaced"))return 3;
    if(!check(cviii_world_connect_0803(world,second,third,
                                      CVIII_WORLD_RIGHT_0803),
              "source proven future passage can attach")
       || !check(world->rooms[5].placed && world->rooms[5].x==1024 &&
                 world->placed_count==3,"world graph expanded")
       || !check(cviii_world_connect_0803(world,second,third,
                                      CVIII_WORLD_RIGHT_0803),
              "idempotent repeated edge")
       || !check(!cviii_world_connect_0803(world,second,third,
                                      CVIII_WORLD_LEFT_0803),
              "contradictory edge rejected")
       || !check(world->placed_count==3,"no duplicate room"))return 4;
    if(!check(cviii_world_connect_0803(world,second,vertical,
                                      CVIII_WORLD_DOWN_0803),
              "branching vertical room attached")
       || !check(world->rooms[2].x==768 && world->rooms[2].y==192,
              "branch coordinates")
       || !check(!cviii_world_connect_0803(world,first,vertical,
                                      CVIII_WORLD_RIGHT_0803),
              "overlap and contradictory placement rejected"))return 5;
    uint8_t ram[2048]={0};
    ram[0x400]=4;ram[0x41c]=100;ram[0x438]=60;
    ram[0x454]=3;ram[0x470]=0;ram[0x48c]=8;ram[0x4a8]=1;
    ram[0x401]=4;ram[0x471]=0x80; /* original suppressed slot */
    if(!check(cviii_world_capture_live_0803(world,second,100,0,ram)==1,
              "authentic CPU slot snapshot")
       || !check(world->actors[0].active &&
              world->actors[0].x==928 && world->actors[0].y==100 &&
              world->actors[0].selector==8 && world->actors[0].attrs==3 &&
              !world->actors[1].active,"original fields and world transform")
       || !check(world->visited_count==1 && world->actor_frame==1,
              "one room activation recorded"))return 6;
    ram[0x400]=0;
    if(!check(cviii_world_capture_live_0803(world,second,104,0,ram)==0 &&
       !world->actors[0].active,"despawn is authoritative; no ghost"))return 7;
    CviiiLevel1World0803 before=*world;
    atlas->loaded=0;
    if(!check(!cviii_world_build_0803(world,atlas) &&
                memcmp(world,&before,sizeof before)==0,
              "failed preload transactional"))return 8;
    free(atlas);free(world);
    puts("PASS JP0803 8 ROM-resident rooms, branching graph, world actor registry and guarded desawns");
    return 0;
}
