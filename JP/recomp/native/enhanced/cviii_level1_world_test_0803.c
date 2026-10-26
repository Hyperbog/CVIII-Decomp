/* JP0803 synthetic Stage 1 atlas metadata and original actor shadow. */
#include "cviii_level1_world_0803.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t chroma(uint16_t addr){(void)addr;return 255u;}
static uint32_t palette(int index){return 0xff400000u+(uint32_t)index;}
static uint32_t panorama[426*240];
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
    /* JP0806: one world camera paints genuine scenery on both margins
     * across first, second and third connected rooms; never overpaint
     * the native 256px image or the complete HUD. */
    memset(panorama,0,sizeof panorama);
    for(int row=0;row<240;row++)
        for(int col=85;col<341;col++)
            panorama[row*426+col]=0xff112233u;
    uint32_t n=cviii_world_paint_0806(world,atlas,first,700,0,
                        panorama,426,240,85,0x1000u,chroma,palette);
    if(!check(n>0 && panorama[100*426+0]!=0u &&
               panorama[100*426+370]!=0u,
               "placed consecutive rooms share the same pan camera") ||
       !check(panorama[100*426+85]==0xff112233u &&
               panorama[100*426+340]==0xff112233u &&
               panorama[25*426+0]==0u,
               "unmodified native 4:3 pixels and fixed HUD"))return 16;
    memset(panorama,0,sizeof panorama);
    n=cviii_world_paint_0806(world,atlas,second,0,0,
                        panorama,426,240,85,0x1000u,chroma,palette);
    if(!check(n>0 && panorama[100*426+0]!=0u &&
               panorama[100*426+370]!=0u,
               "world camera same source pixels after authoritative selector switch"))
        return 17;
    /* Regression for the exact first room->256px successor onset:
     * at camera X512 the next original room begins at viewport X341;
     * it must be visible at x400 before the NES switches selectors. */
    memset(panorama,0,sizeof panorama);
    n=cviii_world_paint_0806(world,atlas,first,512,0,
                        panorama,426,240,85,0x1000u,chroma,palette);
    if(!check(n>0 && panorama[100*426+400]!=0u &&
               panorama[100*426+341]!=0u,
               "preloaded narrow successor enters right widescreen margin"))
        return 19;
    /* No projection into an unknown branch, no repeated fake geometry. */
    memset(panorama,0,sizeof panorama);
    if(!check(cviii_world_paint_0806(world,atlas,(uint8_t[]){0,1,3},
                        0,0,panorama,426,240,85,0x1000u,
                        chroma,palette)==0u,
              "unproven graph edge never fabricated"))return 18;
    /* JP0811 the independent authenticated bank0A hierarchy has
     * EIGHT stage0 leaves, one for every original stage1 atlas room.
     * The typed hierarchy remains source metadata, not fake enemies. */
    CviiiRoomCatalog0657 catalog={0};
    catalog.leaf_count=135;
    /* All unrelated catalog stage keys must be distinct; zeroed
     * trailing leaves are not duplicate source key 00/00/00. */
    for(unsigned i=8u;i<135u;i++)catalog.leaves[i].stage=0xffu;
    for(unsigned i=0;i<8u;i++){
        CviiiRoomLeaf0657 *leaf=&catalog.leaves[i];
        leaf->stage=world->rooms[i].selector[0];
        leaf->second=world->rooms[i].selector[1];
        leaf->third=world->rooms[i].selector[2];
        leaf->width=(uint8_t)(i==2?7u:4u);
        leaf->root=(uint16_t)(i==2?0xab1fu:0x9400u+4u*i);
        leaf->end_exclusive=(uint16_t)(leaf->root+
                                     (leaf->width==7u?15u:8u));
    }
    if(!check(cviii_world_attach_source_rooms_0811(world,&catalog) &&
               world->source_rooms_ready &&
               world->source_rooms[2].width==7u &&
               world->source_rooms[2].record_count==2u &&
               world->source_rooms[7].record_count==2u,
               "all eight stage0 original room source leaves resident"))
        return 25;
    CviiiWorldSourceRoom0811 existing[8];
    memcpy(existing,world->source_rooms,sizeof existing);
    catalog.leaves[5].stage=1; /* absent 0/2/0 source */
    if(!check(!cviii_world_attach_source_rooms_0811(world,&catalog) &&
               memcmp(existing,world->source_rooms,sizeof existing)==0,
               "missing real stage0 leaf rejected atomically"))return 26;
    /* JP0812 stage0 sources are all truly resident, not just a
     * source-root index into a file that must load on camera movement.
     * Entirely synthetic source bytes; no original ROM is distributed. */
    catalog.leaves[5].stage=0;
    if(!check(cviii_world_attach_source_rooms_0811(world,&catalog),
              "restore complete stage0 source fixture"))return 27;
    static uint8_t bank0a[16384];
    for(unsigned i=0;i<8u;i++){
        const CviiiWorldSourceRoom0811 *leaf=&world->source_rooms[i];
        unsigned off=(unsigned)leaf->root-0x8000u;
        bank0a[off]=i==2?1u:(uint8_t)(i+4u);
        if(leaf->width==7u)
            bank0a[(unsigned)leaf->end_exclusive-0x8000u-1u]=0xffu;
    }
    if(!check(cviii_world_preload_source_payload_0812(world,
                    bank0a,sizeof bank0a) &&
              world->source_payload_ready &&
              world->source_rooms[0].payload_len==8u &&
              world->source_rooms[2].payload_len==15u &&
              world->source_rooms[2].payload[0]==1u &&
              world->source_rooms[7].payload[0]==11u,
              "all eight authentic-source windows held in world memory"))
        return 28;
    bank0a[(unsigned)world->source_rooms[2].end_exclusive-0x8000u-1u]=0;
    CviiiWorldSourceRoom0811 preserved=world->source_rooms[2];
    if(!check(!cviii_world_preload_source_payload_0812(world,
                 bank0a,sizeof bank0a) &&
               memcmp(&world->source_rooms[2],&preserved,
                      sizeof preserved)==0,
               "invalid chapel source FF cannot partially replace world"))
        return 29;
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
    /* Original 8-bit sprite X wraps from +2 to $FE as the camera
     * advances 6px. A real previously-live actor continues just LEFT of
     * the native viewport, available to the wider source sprite pass. */
    world->actors[0].x=970;
    ram[0x438]=254;
    if(!check(cviii_world_capture_live_0803(world,second,206,0,ram)==1 &&
              world->actors[0].x==972 && world->actors[0].active &&
              world->actors[0].raw_x==254,
              "live source object unwraps offscreen into world X-2"))
        return 20;
    ram[0x400]=0;
    if(!check(cviii_world_capture_live_0803(world,second,104,0,ram)==0 &&
       !world->actors[0].active,"despawn is authoritative; no ghost"))return 7;
    /* JP0809: one original game-owned object slot may be recycled for
     * another enemy while its sprite selector remains unchanged.
     * Original $054E+X type identifies a new slot producer and rejects
     * stale 8-bit X unwrapping across an unrelated spawn. */
    ram[0x400]=4;ram[0x054e]=0x13;
    if(!check(cviii_world_capture_live_0803(world,second,104,0,ram)==1 &&
              world->actors[0].generation>=2u &&
              world->actors[0].original_type==0x13u,
              "original allocator type creates distinct actor generation"))
        return 21;
    uint32_t generation=world->actors[0].generation;
    if(!check(cviii_world_capture_live_0803(world,second,104,0,ram)==1 &&
              world->actors[0].generation==generation,
              "same slot/type does not recreate or duplicate original actor"))
        return 22;
    ram[0x054e]=0x14;
    if(!check(cviii_world_capture_live_0803(world,second,104,0,ram)==1 &&
              world->actors[0].generation==generation+1u,
              "reused slot with different source type is new identity"))
        return 23;
    CviiiLevel1World0803 before=*world;
    atlas->loaded=0;
    if(!check(!cviii_world_build_0803(world,atlas) &&
                memcmp(world,&before,sizeof before)==0,
              "failed preload transactional"))return 8;
    /* No cartridge bytes in this test: invented raw0E five-field streams
     * with original control structure, including 30 record instances. */
    uint8_t block[CVIII_WORLD_SOURCE_BYTES_0804]={0};
    static const unsigned starts[]={25,80,120,0,145};
    static const unsigned counts[]={10,7,4,4,5};
    for(unsigned g=0;g<5;g++){
        for(unsigned i=0;i<4;i++)
            block[starts[g]+i]=(uint8_t)(g+i);
        for(unsigned i=0;i<counts[g];i++){
            unsigned at=starts[g]+4u+5u*i;
            block[at]=(uint8_t)(2+2*g);
            block[at+1u]=4;
            block[at+2u]=(uint8_t)(20+i);
            block[at+3u]=(uint8_t)(40+i);
            block[at+4u]=1;
        }
        block[starts[g]+4+5*counts[g]]=0xffu;
    }
    if(!check(cviii_world_preload_templates_0804(world,block,sizeof block) &&
              world->templates_ready &&
              world->groups[0].record_count==10 &&
              world->groups[4].record_count==5 &&
              world->templates[0].initial_x==20 &&
              world->templates[29].source_group==4,
              "all five source streams and thirty original loader records"))
        return 9;
    CviiiLevel1World0803 unchanged=*world;
    block[starts[2]+4]=0xffu;
    if(!check(!cviii_world_preload_templates_0804(world,block,sizeof block) &&
              memcmp(world,&unchanged,sizeof unchanged)==0,
              "early source terminator leaves world intact"))return 10;
    block[starts[2]+4]=6;
    block[starts[0]+4+5*counts[0]]=0;
    if(!check(!cviii_world_preload_templates_0804(world,block,sizeof block) &&
              memcmp(world,&unchanged,sizeof unchanged)==0,
              "missing FF terminator leaves world intact"))return 11;
    /* Original CPU loader postcondition: the five-field records must
     * actually be installed into game RAM before a resource is active. */
    ram[0x7a0]=4;
    /* Invented synthetic stream for Stage1 key 00/01/00. Original
     * JP raw0E group4 instead begins $B1, which is Stage B, not 0. */
    block[starts[4]]=0x01u;
    block[starts[4]+1u]=0u;
    world->groups[4].header[0]=0x01u;
    world->groups[4].header[1]=0u;
    for(unsigned i=0;i<world->groups[4].record_count;i++){
        const CviiiWorldObjectTemplate0804 *row=&world->templates[
            world->groups[4].record_start+i];
        unsigned slot=i+1u;
        ram[0x48cu+slot]=row->sprite_selector;
        ram[0x400u+slot]=row->frame_offset;
        ram[0x438u+slot]=row->initial_x;
        ram[0x41cu+slot]=row->initial_y;
        ram[0x4a8u+slot]=row->mirror;
        ram[0x54eu+slot]=1u;
    }
    if(!check(cviii_world_detect_loader_0805(world,second,ram)==4 &&
              world->groups[4].active &&
              world->groups[4].room_index==1 &&
              world->groups[4].activations==1,
              "original CPU postcondition observed"))return 12;
    if(!check(cviii_world_detect_loader_0805(world,second,ram)==4 &&
              world->groups[4].activations==1,
              "successive matching frames do not duplicate actors"))return 13;
    world->groups[4].header[0]=0xB1u;
    if(!check(cviii_world_detect_loader_0805(world,second,ram)==-1 &&
              world->groups[4].activations==1,
              "genuine other-stage header cannot become Stage1 actor spawn"))
        return 24;
    world->groups[4].header[0]=0x01u;
    ram[0x54f]=0;
    if(!check(cviii_world_detect_loader_0805(world,second,ram)==-1 &&
              world->groups[4].activations==1,
              "partial original loader rejected"))return 14;
    /* JP0813: invented seven-byte chapel source data, no game content. */
    CviiiWorldSourceRoom0811 *chapel=&world->source_rooms[2];
    memset(chapel,0,sizeof *chapel);
    chapel->root=0xab1fu;chapel->end_exclusive=0xab5fu;
    chapel->record_count=CVIII_STAGE1_CHAPEL_SOURCES_0813;
    chapel->width=7u;chapel->payload_len=64u;
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++){
        chapel->payload[7u*i]=0x03u;
        chapel->payload[7u*i+1u]=0xf0u;
        chapel->payload[7u*i+2u]=0x80u;
        chapel->payload[7u*i+3u]=(uint8_t)(0x20u+i);
    }
    chapel->payload[0]=0x01u;chapel->payload[1]=0x80u;
    chapel->payload[63]=0xffu;
    world->source_payload_ready=1u;
    if(!check(cviii_world_track_chapel_0813(world,vertical,0x180)==1 &&
              world->chapel[0].axis_world==0x0180u &&
              world->chapel[0].local_axis==0x37u &&
              world->chapel[0].world_placed &&
              world->chapel[0].world_x==world->rooms[2].x+0x20 &&
              world->chapel[0].world_y==world->rooms[2].y+0x180 &&
              world->chapel[0].entries==1u && world->chapel_epochs==1u,
              "original world-axis admission") ||
       !check(cviii_world_track_chapel_0813(world,vertical,0x200)==0 &&
              world->chapel[0].exits==1u && !world->chapel[0].eligible &&
              world->chapel[0].axis_world==0x0180u,
              "source persists after leaving original admission window") ||
       !check(cviii_world_track_chapel_0813(world,vertical,0x180)==1 &&
              world->chapel[0].entries==2u && world->chapel_epochs==3u,
              "re-enter original window without spawning game actors") ||
       !check(cviii_world_track_chapel_0813(world,second,0x180)==-1 &&
              world->chapel[0].entries==2u,
              "wrong selector rejected without mutation"))
        return 25;
    /* JP0814 original-ROM installation signatures, fabricated RAM only.
     * The observation MUST NOT create or prolong a game actor. */
    ram[0x53u]=0x80u;ram[0x54u]=0x01u; /* original CPU camera $0180 */
    /* The guest already allocated actor 13; tagging cannot create it. */
    world->actors[13].active=1u;
    world->actors[13].frame=1u;
    ram[0x0400u+13u]=1u;
    world->actors[13].room=2u;
    world->actors[13].slot=13u;
    world->actors[13].original_type=0x80u;
    world->actors[13].generation=7u;
    ram[0x054eu+13u]=0x80u;
    ram[0x0438u+13u]=chapel->payload[3];
    ram[0x05d8u+13u]=chapel->payload[4];
    ram[0x041cu+13u]=0x37u;
    ram[0x05efu+13u]=0x30u;
    if(!check(cviii_world_link_chapel_0814(world,vertical,ram)==1 &&
              world->chapel_links[0].kind==CVIII_LINK_DIRECT_0814 &&
              world->chapel_links[0].slot==13u &&
              world->chapel_link_epochs==1u &&
              world->actors[13].source_cpu_0814==0xab1fu &&
              world->actors[13].source_generation_0814==7u,
              "type80 direct original installer exact match"))return 26;
    /* JP0815: real source is installed, but the proposed X movement
     * here is a synthetic projection-only test, not a natural Mesen
     * camera or a new original CPU movement rule. */
    world->actors[13].x=world->rooms[2].x+0x20;
    world->actors[13].y=world->rooms[2].y+0x180+0x37;
    world->actors[13].selector=0x0eu;
    world->actors[13].mirror=1u;
    /* Invented authenticated-bank SHAPE, not copyrighted sprite art.
     * JP0807 selector/frame bytes are pointer-table offsets. */
    uint8_t fake_sprites[16384]={0};
    fake_sprites[0x818du-0x8000u]=0x00u;
    fake_sprites[0x818eu-0x8000u]=0x90u;
    fake_sprites[0x9001u-0x8000u]=0x00u;
    fake_sprites[0x9002u-0x8000u]=0x91u;
    fake_sprites[0x9100u-0x8000u]=4u;
    if(!check(cviii_world_probe_chapel_0815(
                  world,vertical,80,0x180,85,426,fake_sprites)==1 &&
              world->chapel_projection[0].actor_confirmed &&
              world->chapel_projection[0].linked_slot==13u &&
              world->chapel_projection[0].sprite_selector==0x0eu &&
              world->chapel_projection[0].sprite_frame==1u &&
              world->chapel_projection[0].visual_valid &&
              world->chapel_projection[0].sprite_descriptor_cpu==0x9100u &&
              world->chapel_projection[0].sprite_pieces==4u &&
              world->chapel_projection[0].screen_x==37 &&
              world->chapel_projection[0].screen_y==55 &&
              world->chapel_projection[0].point_region==
                  CVIII_PROBE_MARGIN_0815 &&
              world->chapel_projection[0].interaction_policy==
                  CVIII_INTERACTION_MAY_ROUTE_B162_0815,
              "only original installed actor projects into synthetic margin"))
        return 31;
    if(!check(cviii_world_probe_chapel_0815(
                  world,vertical,0,0x180,85,426,fake_sprites)==0 &&
              world->chapel_projection[0].point_region==
                  CVIII_PROBE_NATIVE_0815 &&
              world->chapel_projection[0].screen_x==117,
              "authentic chapel X stays inside NES game window"))
        return 32;
    uint32_t projected_epochs=world->chapel_projection_epochs;
    if(!check(cviii_world_probe_chapel_0815(
                  world,second,0,0x180,85,426,fake_sprites)==-1 &&
              projected_epochs==world->chapel_projection_epochs,
              "wrong source selector cannot mutate projection"))
        return 33;
    /* Two records claiming one original slot are both ambiguous. */
    memcpy(chapel->payload+7u,chapel->payload,7u);
    if(!check(cviii_world_link_chapel_0814(world,vertical,ram)==0 &&
              world->chapel_links[0].kind==CVIII_LINK_AMBIGUOUS_0814 &&
              world->chapel_links[1].kind==CVIII_LINK_AMBIGUOUS_0814,
              "reject multiple sources to one direct allocator slot"))
        return 27;
    /* Original nonnegative $0D source follows $8287-$82A8,
     * not the direct-object branch at $82B2. */
    chapel->payload[7u+2u]=0x0du;
    chapel->payload[7u+3u]=0xd8u;
    chapel->payload[7u+5u]=0x7au;
    chapel->payload[7u+6u]=0x4cu;
    ram[0x07c2u+3u]=0x0du;
    ram[0x07dau+3u]=0xd8u;
    ram[0x07e6u+3u]=0x7au;
    ram[0x07ceu+3u]=0x4cu;
    ram[0x07d4u+3u]=0x37u;
    ram[0x07c8u+3u]=0u;ram[0x07e0u+3u]=0u;
    if(!check(cviii_world_link_chapel_0814(world,vertical,ram)==2 &&
              world->chapel_links[1].kind==CVIII_LINK_EVENT_0814 &&
              world->chapel_links[1].slot==3u &&
              world->chapel_links[0].kind==CVIII_LINK_DIRECT_0814,
              "source-event and direct actor paths stay separate"))
        return 28;
    /* Destroyed or recycled game actors cannot inherit stale provenance. */
    ram[0x0400u+13u]=0u;
    (void)cviii_world_capture_live_0803(world,vertical,0,0,ram);
    if(!check(!world->actors[13].source_cpu_0814 &&
              !world->actors[13].source_generation_0814,
              "actor deactivation invalidates source tag"))return 30;
    if(!check(cviii_world_probe_chapel_0815(
                  world,vertical,80,0x180,85,426,fake_sprites)==0 &&
              !world->chapel_projection[0].actor_confirmed &&
              world->chapel_projection[0].source_cpu==0xab1fu &&
              world->chapel_projection[0].interaction_policy==
                  CVIII_INTERACTION_NOT_SPAWNED_0815,
              "source remains resident but never fabricates a ghost actor"))
        return 34;
    uint32_t previous_links=world->chapel_link_epochs;
    if(!check(cviii_world_link_chapel_0814(world,second,ram)==-1 &&
              world->chapel_link_epochs==previous_links,
              "wrong room must not change source identities"))
        return 29;
    cviii_world_clear_live_0805(world);
    if(!check(!world->actors[0].active &&
              world->groups[4].active && world->templates_ready &&
              world->rooms[1].placed,
              "savestate clears shadows but retains world/resources"))return 15;
    free(atlas);free(world);
    puts("PASS JP0803/0804/0805 persistent world, source templates and original loader activation");
    return 0;
}
