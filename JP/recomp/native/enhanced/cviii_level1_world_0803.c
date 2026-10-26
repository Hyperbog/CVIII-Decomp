#include "cviii_level1_world_0803.h"
#include "cviii_stage1_source_window_0813.h"
#include <limits.h>
#include <stddef.h>
#include <string.h>
static const uint8_t keys[CVIII_WORLD_ROOMS_0803][3]={
    {0,0,0},{0,1,0},{0,1,1},{0,1,2},
    {0,1,3},{0,2,0},{0,2,1},{0,3,0}
};
/* JP0804: original JP raw0E physical room-installation resources.
 * Source structure, five field destination offsets and FF terminators
 * are proven by JP0659 original-6502/native execution. No inference
 * from these raw fields to later AI behavior is made here.
 */
int cviii_world_preload_templates_0804(CviiiLevel1World0803 *w,
                      const uint8_t *block,size_t len){
    static const unsigned start[CVIII_WORLD_GROUPS_0804]={
        25u,80u,120u,0u,145u
    };
    static const unsigned counts[CVIII_WORLD_GROUPS_0804]={
        10u,7u,4u,4u,5u
    };
    if(!w || !w->ready || !block ||
       len!=CVIII_WORLD_SOURCE_BYTES_0804)return 0;
    CviiiWorldObjectTemplate0804 items[CVIII_WORLD_TEMPLATES_0804]={0};
    CviiiWorldObjectGroup0804 groups[CVIII_WORLD_GROUPS_0804]={0};
    unsigned used=0;
    for(unsigned g=0;g<CVIII_WORLD_GROUPS_0804;g++){
        unsigned pos=start[g],count=counts[g];
        if(pos+4u+5u*count>=len ||
           block[pos+4u+5u*count]!=0xffu ||
           used+count>CVIII_WORLD_TEMPLATES_0804)return 0;
        groups[g].source_group=(uint8_t)g;
        groups[g].record_start=(uint8_t)used;
        groups[g].record_count=(uint8_t)count;
        memcpy(groups[g].header,block+pos,4u);
        for(unsigned j=0;j<count;j++){
            unsigned at=pos+4u+5u*j;
            if(block[at]==0xffu)return 0;
            CviiiWorldObjectTemplate0804 *item=&items[used++];
            item->source_group=(uint8_t)g;
            item->source_index=(uint8_t)j;
            item->sprite_selector=block[at];    /* CPU $048C,X */
            item->frame_offset=block[at+1u];   /* CPU $0400,X */
            item->initial_x=block[at+2u];      /* CPU $0438,X */
            item->initial_y=block[at+3u];      /* CPU $041C,X */
            item->mirror=block[at+4u];         /* CPU $04A8,X */
        }
    }
    if(used!=CVIII_WORLD_TEMPLATES_0804)return 0;
    memcpy(w->templates,items,sizeof items);
    memcpy(w->groups,groups,sizeof groups);
    w->templates_ready=1;
    return 1;
}

/* Original B7F7 loader writes five fields per record and $054E+X=1.
 * A complete postcondition is required before this resource is marked
 * observed. This code never writes RAM, emits OAM or runs actor AI.
 */
int cviii_world_detect_loader_0805(CviiiLevel1World0803 *w,
    const uint8_t key[3],const uint8_t ram[2048]){
    if(!w || !w->ready || !w->templates_ready || !ram)return -1;
    int room=cviii_world_index_0803(w,key);
    if(room<0)return -1;
    unsigned g=ram[0x7a0u];
    if(g>=CVIII_WORLD_GROUPS_0804)return -1;
    CviiiWorldObjectGroup0804 *group=&w->groups[g];
    /* JP0810: original cross-bank $B808–$B82C decodes the FIRST
     * header byte into $34(high nibble)/$35(low nibble) and the SECOND
     * header high nibble into $36. The five records in raw0E are
     * generic stage examples (4,1,8,2,11), NOT Stage 1 ($34=0).
     * A byte-equal installed stream in another room does not prove an
     * original loader event or grant permission to spawn NPCs. */
    if((group->header[0]>>4u)!=key[0] ||
       (group->header[0]&15u)!=key[1] ||
       (group->header[1]>>4u)!=key[2])
        return -1;
    for(unsigned i=0;i<group->record_count;i++){
        unsigned x=i+1u;
        const CviiiWorldObjectTemplate0804 *t=
            &w->templates[group->record_start+i];
        if(ram[0x48cu+x]!=t->sprite_selector ||
           ram[0x400u+x]!=t->frame_offset ||
           ram[0x438u+x]!=t->initial_x ||
           ram[0x41cu+x]!=t->initial_y ||
           ram[0x4a8u+x]!=t->mirror ||
           ram[0x54eu+x]!=1u)
            return -1;
    }
    if(!group->active || group->room_index!=(uint8_t)room){
        group->active=1;
        group->room_index=(uint8_t)room;
        group->activations++;
    }
    (void)cviii_world_visit_0803(w,key);
    return (int)g;
}
/* JP0816: build typed horizontal room-cell source metadata from the
 * original physical raw0A while it is privately loaded. The 7 horizontal
 * rooms have 4-byte packed cells (two source/aux pairs each). No original
 * source byte tables are compiled or serialized into this game binary. */
int cviii_world_preload_horizontal_0816(CviiiLevel1World0803 *w,
                     const uint8_t bank[16384],size_t bank_len)
{
    if(!w || !w->ready || !w->source_rooms_ready ||
       !w->source_payload_ready || !bank || bank_len!=16384u)return 0;
    CviiiHorizontalRoom0816 tmp[CVIII_HORIZONTAL_ROOMS_0816]={0};
    for(unsigned i=0;i<CVIII_HORIZONTAL_ROOMS_0816;i++){
        if(i==2u)continue; /* seven-byte vertical chapel */
        const CviiiWorldSourceRoom0811 *src=&w->source_rooms[i];
        if(src->width!=4u ||
           !cviii_horizontal_build_room_0816(
                &tmp[i],i,src->root,src->payload,src->payload_len,
                bank,bank_len))return 0;
    }
    memcpy(w->horizontal,tmp,sizeof tmp);
    w->horizontal_ready=1u;
    memset(&w->horizontal_last,0,sizeof w->horizontal_last);
    w->horizontal_observations=0u;
    return 1;
}
int cviii_world_observe_horizontal_0816(CviiiLevel1World0803 *w,
                const uint8_t key[3],const uint8_t ram[2048])
{
    if(!w || !w->ready || !w->horizontal_ready ||
       !key || !ram || key[0]!=0u)return -1;
    const int room=cviii_world_index_0803(w,key);
    if(room<0 || room==2 || !w->horizontal[room].valid)return -1;
    const uint16_t camera=(uint16_t)((uint16_t)ram[0x53u] |
                                    ((uint16_t)ram[0x54u]<<8u));
    const CviiiHorizontalSelection0816 next=cviii_horizontal_select_0816(
         &w->horizontal[room],(unsigned)room,camera,ram[0x62u],
         ram[0x7f6u]!=0u);
    w->horizontal_last=next;
    if(w->horizontal_observations!=UINT32_MAX)
        w->horizontal_observations++;
    return next.valid ? 1:0;
}
/* JP0813: retain the original Stage 1 chapel's resident source identities
 * while independently observing the original 6502 $8213-$8254 admission
 * window. A source is NOT an active actor. Authentic game actor allocation,
 * culling, hitboxes, and CPU/PPU state remain wholly owned by NESRecomp.
 * This is invoked only with source-verified, vertical 00/01/01 camera Y. */
int cviii_world_track_chapel_0813(CviiiLevel1World0803 *w,
    const uint8_t key[3],int camera_y)
{
    if(!w || !w->ready || !w->source_payload_ready || !key ||
       camera_y<0 || camera_y>=512 ||
       key[0]!=0u || key[1]!=1u || key[2]!=1u)return -1;
    const CviiiWorldSourceRoom0811 *s=&w->source_rooms[2];
    if(s->root!=0xab1fu || s->end_exclusive!=0xab5fu ||
       s->width!=7u || s->record_count!=CVIII_STAGE1_CHAPEL_SOURCES_0813 ||
       s->payload_len!=64u || s->payload[63]!=0xffu)return -1;
    CviiiStage1SourceLife0813 incoming[CVIII_STAGE1_CHAPEL_SOURCES_0813];
    unsigned count=0;
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++){
        const uint8_t *record=s->payload+7u*i;
        /* $8321: first two bytes -> ZP $09 (high), $0A (low).
         * $827D: type selects source row vs object allocator; byte 3
         * is the independent horizontal coordinate in either branch. */
        const uint16_t axis=(uint16_t)(((uint16_t)record[0]<<8)|record[1]);
        const CviiiStage1Admission0813 admitted=
            cviii_stage1_admit_0813(axis,(uint16_t)camera_y);
        const CviiiStage1SourceLife0813 *old=&w->chapel[i];
        CviiiStage1SourceLife0813 *item=&incoming[i];
        *item=*old;
        item->source_cpu=(uint16_t)(s->root+7u*i);
        item->axis_world=axis;
        item->raw_type=record[2];
        item->local_x=record[3];
        item->local_axis=admitted.local_axis;
        item->eligible=admitted.admitted;
        /* Never put an unplaced branch into the global world. The
         * persistent room graph is authoritative for world offsets. */
        item->world_placed=w->rooms[2].placed;
        item->world_x=0;
        item->world_y=0;
        if(item->world_placed){
            const int64_t gx=(int64_t)w->rooms[2].x+record[3];
            const int64_t gy=(int64_t)w->rooms[2].y+axis;
            if(gx<INT32_MIN || gx>INT32_MAX ||
               gy<INT32_MIN || gy>INT32_MAX)return -1;
            item->world_x=(int32_t)gx;
            item->world_y=(int32_t)gy;
        }
        if(item->eligible && !old->eligible && item->entries!=UINT32_MAX)
            item->entries++;
        else if(!item->eligible && old->eligible && item->exits!=UINT32_MAX)
            item->exits++;
        count+=item->eligible;
    }
    memcpy(w->chapel,incoming,sizeof incoming);
    if(w->chapel_epochs!=UINT32_MAX)w->chapel_epochs++;
    return (int)count;
}
/* JP0814: correlate original $AB1F seven-byte source records with
 * actual original CPU RAM postconditions. The *emulated* $53/$54 is
 * authoritative for the scan; a presentation PPU camera may lag by a
 * frame and must not be substituted in actor identity checks.
 * Source IDs are not actor IDs. Failed and non-unique matches do
 * not produce synthetic actors, damage, hitboxes or OAM. */
int cviii_world_link_chapel_0814(CviiiLevel1World0803 *w,
    const uint8_t key[3],const uint8_t ram[2048])
{
    if(!w || !w->ready || !w->source_payload_ready || !key || !ram ||
       key[0]!=0u || key[1]!=1u || key[2]!=1u ||
       w->source_rooms[2].root!=0xab1fu ||
       w->source_rooms[2].end_exclusive!=0xab5fu ||
       w->source_rooms[2].width!=7u ||
       w->source_rooms[2].record_count!=CVIII_STAGE1_CHAPEL_SOURCES_0813 ||
       w->source_rooms[2].payload_len!=64u ||
       w->source_rooms[2].payload[63]!=0xffu)return -1;
    const uint16_t source_camera=(uint16_t)(
        (uint16_t)ram[0x53u] | ((uint16_t)ram[0x54u]<<8));
    CviiiSourceLink0814 found[CVIII_STAGE1_CHAPEL_SOURCES_0813]={0};
    int matches=0;
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++){
        const uint8_t *record=w->source_rooms[2].payload+7u*i;
        const uint16_t axis=(uint16_t)(
             ((uint16_t)record[0]<<8)|(uint16_t)record[1]);
        const CviiiStage1Admission0813 admission=
            cviii_stage1_admit_0813(axis,source_camera);
        if(!admission.admitted)continue;
        found[i]=cviii_source_link_0814(record,admission.local_axis,ram);
    }
    /* Check duplicates against the immutable candidate set. A three-way
     * collision must invalidate ALL three sources, not just the first two. */
    CviiiSourceLink0814 unique[CVIII_STAGE1_CHAPEL_SOURCES_0813];
    memcpy(unique,found,sizeof unique);
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++){
        if(found[i].kind==CVIII_LINK_NONE_0814 ||
           found[i].kind==CVIII_LINK_AMBIGUOUS_0814)continue;
        for(unsigned j=0;j<CVIII_STAGE1_CHAPEL_SOURCES_0813;j++){
            if(i==j)continue;
            if(found[i].kind==found[j].kind &&
               found[i].slot==found[j].slot){
                unique[i].kind=CVIII_LINK_AMBIGUOUS_0814;
                unique[i].slot=0;
                break;
            }
        }
    }
    memcpy(found,unique,sizeof found);
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++)
        if(found[i].kind==CVIII_LINK_EVENT_0814 ||
           found[i].kind==CVIII_LINK_DIRECT_0814)matches++;
    memcpy(w->chapel_links,found,sizeof found);
    /* A verified direct installation may label an ALREADY live original
     * world actor of the same room/slot/type. It does not activate an
     * unspawned actor or change the rendering/collision implementation.
     * The generation tag is invalidated by the existing slot-reuse logic. */
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++){
        if(found[i].kind!=CVIII_LINK_DIRECT_0814)continue;
        const unsigned x=found[i].slot;
        CviiiWorldActor0803 *actor=&w->actors[x];
        const uint8_t *record=w->source_rooms[2].payload+7u*i;
        if(actor->active && actor->room==2u &&
           actor->slot==x && actor->original_type==record[2]){
            actor->source_cpu_0814=(uint16_t)(
                w->source_rooms[2].root+7u*i);
            actor->source_generation_0814=actor->generation;
        }
    }
    if(w->chapel_link_epochs!=UINT32_MAX)w->chapel_link_epochs++;
    return matches;
}
/* JP0815 dry-run of original source presence, visual identity and
 * unsimulated collision responsibilities. Keeps all nine source records
 * resident even when the NES world has not yet allocated their actors.
 * No new game actors, OAM pieces or collision/pickup side effects. */
int cviii_world_probe_chapel_0815(CviiiLevel1World0803 *w,
    const uint8_t key[3],int camera_x,int camera_y,
    int native_left,int wide_width,
    const uint8_t authenticated_prg26[16384])
{
    if(!w || !w->ready || !w->source_payload_ready ||
       !key || key[0]!=0u || key[1]!=1u || key[2]!=1u ||
       camera_x<0 || camera_y<0 || camera_y>=512 ||
       native_left<0 || wide_width<256 ||
       native_left>wide_width-256 || !w->rooms[2].placed ||
       w->source_rooms[2].root!=0xab1fu ||
       w->source_rooms[2].end_exclusive!=0xab5fu ||
       w->source_rooms[2].width!=7u ||
       w->source_rooms[2].record_count!=CVIII_STAGE1_CHAPEL_SOURCES_0813 ||
       w->source_rooms[2].payload_len!=64u ||
       w->source_rooms[2].payload[63]!=0xffu)return -1;
    CviiiSourceOffscreen0815 output[CVIII_STAGE1_CHAPEL_SOURCES_0813]={0};
    const int64_t wx=(int64_t)w->rooms[2].x+camera_x;
    const int64_t wy=(int64_t)w->rooms[2].y+camera_y;
    unsigned margin_actors=0u;
    for(unsigned i=0;i<CVIII_STAGE1_CHAPEL_SOURCES_0813;i++){
        const uint8_t *record=w->source_rooms[2].payload+7u*i;
        const uint16_t cpu=(uint16_t)(0xab1fu+7u*i);
        const uint16_t axis=(uint16_t)(
            ((uint16_t)record[0]<<8)|record[1]);
        CviiiSourceOffscreen0815 *p=&output[i];
        p->source_cpu=cpu;
        p->source_type=record[2];
        p->linked_slot=0xffu;
        p->guest_slot=0xffu;
        /* A bounded postcondition proves $054E slot installation,
         * even if the original $0470 bit7 hides its sprite from OAM.
         * Distinct from an actually visible original PRG26 actor. */
        if(w->chapel_links[i].kind==CVIII_LINK_DIRECT_0814){
            const unsigned slot=w->chapel_links[i].slot;
            if(slot>=13u && slot<=18u){
                p->guest_installed=1u;
                p->guest_slot=(uint8_t)slot;
            }
        }
        /* Event-source X=0..5 links do not directly identify the
         * eventual spawned actor. Only a direct original $80 actor
         * can carry a source-tagged visual descriptor. */
        for(unsigned x=13u;x<=18u;x++){
            const CviiiWorldActor0803 *actor=&w->actors[x];
            if(!actor->active || actor->room!=2u ||
               actor->slot!=x || actor->original_type!=record[2] ||
               actor->source_cpu_0814!=cpu ||
               actor->source_generation_0814!=actor->generation)
                continue;
            p->actor_confirmed=1u;
            p->linked_slot=(uint8_t)x;
            p->sprite_selector=actor->selector;
            p->sprite_frame=actor->frame;
            p->sprite_mirror=actor->mirror;
            p->sprite_attrs=actor->attrs;
            p->actor_generation=actor->generation;
            const CviiiSourceVisual0815 visual=cviii_source_visual_0815(
                 authenticated_prg26,actor->selector,actor->frame);
            p->visual_valid=visual.valid;
            p->sprite_descriptor_cpu=visual.descriptor_cpu;
            p->sprite_pieces=visual.pieces;
            break;
        }
        const int64_t gx=p->actor_confirmed ?
            w->actors[p->linked_slot].x :
            (int64_t)w->rooms[2].x+record[3];
        /* When original $8205 admits a source, use its exact 6502
         * projected local Y, including page borrow/$10 correction.
         * Only for a source outside admission is axis+$37 retained as
         * a non-rendered world-space planning coordinate. */
        const CviiiStage1Admission0813 admission=
            cviii_stage1_admit_0813(axis,(uint16_t)camera_y);
        const int64_t gy=p->actor_confirmed ?
            w->actors[p->linked_slot].y :
            admission.admitted ?
                wy+admission.local_axis :
                cviii_chapel_visual_world_y_0815(w->rooms[2].y,axis);
        const CviiiSourceProjection0815 point=cviii_source_project_0815(
            gx,gy,wx,wy,native_left,wide_width,240);
        p->screen_x=point.screen_x;
        p->screen_y=point.screen_y;
        p->point_region=point.point_region;
        p->interaction_policy=(uint8_t)cviii_source_interaction_0815(
            record[2],p->actor_confirmed || p->guest_installed);
        if(p->actor_confirmed &&
           p->point_region==CVIII_PROBE_MARGIN_0815)margin_actors++;
    }
    memcpy(w->chapel_projection,output,sizeof output);
    w->chapel_margin_actor_count=(uint8_t)margin_actors;
    if(w->chapel_projection_epochs!=UINT32_MAX)
        w->chapel_projection_epochs++;
    return (int)margin_actors;
}
void cviii_world_clear_live_0805(CviiiLevel1World0803 *w){
    if(!w)return;
    memset(w->actors,0,sizeof w->actors);
    /* Save-state/reset invalidates transient observer continuity, not
     * authenticated preloaded source payloads or world room positions. */
    memset(w->chapel,0,sizeof w->chapel);
    w->chapel_epochs=0u;
    memset(w->chapel_links,0,sizeof w->chapel_links);
    w->chapel_link_epochs=0u;
    memset(w->chapel_projection,0,sizeof w->chapel_projection);
    w->chapel_projection_epochs=0u;
    w->chapel_margin_actor_count=0u;
}

/* JP0811: independent original PRG0A room hierarchy, stage selector0.
 * This is not an actor list: width4/width7 are room resources whose
 * source producer semantics must be proved before enabling NPC spawn.
 * All eight known stage0 selectors are matched exactly and atomically. */
int cviii_world_attach_source_rooms_0811(CviiiLevel1World0803 *w,
                        const CviiiRoomCatalog0657 *cat)
{
    if(!w || !w->ready || !cat || cat->leaf_count!=135u)return 0;
    CviiiWorldSourceRoom0811 metadata[CVIII_WORLD_ROOMS_0803]={0};
    for(unsigned room=0;room<CVIII_WORLD_ROOMS_0803;room++){
        const uint8_t *key=w->rooms[room].selector;
        int match=-1;
        for(unsigned j=0;j<cat->leaf_count;j++){
            const CviiiRoomLeaf0657 *leaf=&cat->leaves[j];
            if(leaf->stage!=key[0] ||
               leaf->second!=key[1] || leaf->third!=key[2])continue;
            if(match>=0)return 0;
            match=(int)j;
        }
        if(match<0)return 0;
        const CviiiRoomLeaf0657 *leaf=&cat->leaves[match];
        if(leaf->root<0x93ccu || leaf->end_exclusive<=leaf->root ||
           leaf->end_exclusive>0xafa4u ||
           (leaf->width!=4u && leaf->width!=7u))return 0;
        unsigned size=(unsigned)leaf->end_exclusive-leaf->root;
        if(leaf->width==7u){
            if(size<8u || (size-1u)%7u)return 0;
            metadata[room].record_count=(uint16_t)((size-1u)/7u);
        }else{
            if(size%4u)return 0;
            metadata[room].record_count=(uint16_t)(size/4u);
        }
        metadata[room].root=leaf->root;
        metadata[room].end_exclusive=leaf->end_exclusive;
        metadata[room].width=leaf->width;
    }
    memcpy(w->source_rooms,metadata,sizeof metadata);
    w->source_rooms_ready=1u;
    return 1;
}

/* Each authenticated source span belongs to the original stage0
 * hierarchy (not generic raw0E object samples). Preloading makes both
 * 4-byte and 7-byte room resources persistent at stage initialization.
 * The source format is intentionally left uninterpreted until each
 * original 6502 data consumer is reconstructed, preventing fake NPCs.
 */
int cviii_world_preload_source_payload_0812(CviiiLevel1World0803 *w,
                      const uint8_t *bank,size_t len)
{
    if(!w || !w->ready || !w->source_rooms_ready ||
       !bank || len!=16384u)return 0;
    uint8_t data[CVIII_WORLD_ROOMS_0803][128]={0};
    uint8_t lengths[CVIII_WORLD_ROOMS_0803]={0};
    for(unsigned i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        const CviiiWorldSourceRoom0811 *src=&w->source_rooms[i];
        if(src->root<0x8000u || src->end_exclusive>0xc000u ||
           src->root>=src->end_exclusive)return 0;
        unsigned size=(unsigned)src->end_exclusive-src->root;
        if(size>128u)return 0;
        const uint8_t *body=bank+(unsigned)src->root-0x8000u;
        if(src->width==7u){
            if(size<8u || (size-1u)%7u ||
               body[size-1u]!=0xffu)return 0;
            for(unsigned j=0;j<src->record_count;j++)
                if(body[j*7u]>3u)return 0;
        }else if(src->width!=4u || size%4u)return 0;
        memcpy(data[i],body,size);
        lengths[i]=(uint8_t)size;
    }
    for(unsigned i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        memcpy(w->source_rooms[i].payload,data[i],lengths[i]);
        w->source_rooms[i].payload_len=lengths[i];
    }
    w->source_payload_ready=1;
    return 1;
}

int cviii_world_index_0803(const CviiiLevel1World0803 *w,
                           const uint8_t selector[3]){
    if(!w || !w->ready || !selector)return -1;
    for(int i=0;i<CVIII_WORLD_ROOMS_0803;i++)
        if(memcmp(w->rooms[i].selector,selector,3)==0)return i;
    return -1;
}
int cviii_world_build_0803(CviiiLevel1World0803 *world,
                          const CviiiStage1Atlas0724 *atlas){
    if(!world || !atlas || !atlas->loaded)return 0;
    CviiiLevel1World0803 temp={0};
    for(unsigned i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        const CviiiStage1Room0724 *src=&atlas->rooms[i];
        if(!src->width_tiles || !src->height_tiles ||
           (unsigned)src->width_tiles*src->height_tiles>
                CVIII_STAGE1_TILES_0724)return 0;
        CviiiWorldRoom0803 *room=&temp.rooms[i];
        memcpy(room->selector,keys[i],3);
        room->width=(int)src->width_tiles*8;
        room->height=(int)src->height_tiles*8;
    }
    /* Owner-traced 1-01 -> 1-02:0 true horizontal passage only.
     * Other 6 areas are all resident, but their placement is not guessed. */
    if(temp.rooms[0].width!=768 || temp.rooms[1].width!=256 ||
       temp.rooms[0].height!=192 || temp.rooms[1].height!=192)return 0;
    temp.rooms[0].placed=1;
    temp.rooms[1].placed=1;
    temp.rooms[1].x=temp.rooms[0].width;
    temp.placed_count=2;
    temp.ready=1;
    *world=temp;
    return 1;
}
int cviii_world_connect_0803(CviiiLevel1World0803 *w,
    const uint8_t first[3],const uint8_t next[3],CviiiWorldDirection0803 dir){
    int a=cviii_world_index_0803(w,first);
    int b=cviii_world_index_0803(w,next);
    if(a<0 || b<0 || a==b || dir>CVIII_WORLD_DOWN_0803 ||
       (!w->rooms[a].placed && !w->rooms[b].placed))return 0;
    const CviiiWorldRoom0803 *A=&w->rooms[a],*B=&w->rooms[b];
    int64_t dx=0,dy=0;
    switch(dir){
    case CVIII_WORLD_LEFT_0803:  dx=-(int64_t)B->width;break;
    case CVIII_WORLD_RIGHT_0803: dx=A->width;break;
    case CVIII_WORLD_UP_0803:    dy=-(int64_t)B->height;break;
    case CVIII_WORLD_DOWN_0803:  dy=A->height;break;
    default:return 0;
    }
    int64_t x=A->placed?(int64_t)A->x+dx:(int64_t)B->x-dx;
    int64_t y=A->placed?(int64_t)A->y+dy:(int64_t)B->y-dy;
    if(x<INT32_MIN || x>INT32_MAX || y<INT32_MIN || y>INT32_MAX)
        return 0;
    if(A->placed && B->placed)
        return B->x==x && B->y==y;
    /* If B is placed then candidate is A's position (computed above);
     * otherwise candidate is B's position. Reject overlapping physically
     * pre-existing rooms, with no blind guesses across unknown branches. */
    const CviiiWorldRoom0803 *moving=A->placed?B:A;
    int64_t px=x,py=y;
    for(int i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        const CviiiWorldRoom0803 *r=&w->rooms[i];
        if(!r->placed || r==A || r==B)continue;
        if(px<r->x+r->width && px+moving->width>r->x &&
           py<r->y+r->height && py+moving->height>r->y)return 0;
    }
    CviiiWorldRoom0803 *dest=&w->rooms[A->placed?b:a];
    dest->x=(int32_t)x;
    dest->y=(int32_t)y;
    dest->placed=1;
    w->placed_count++;
    return 1;
}
/* JP0806 world compositor: every loaded/positioned room uses the same
 * global camera and independently verified source coordinates.
 * A room's atlas painter bounds itself to that room's original layout,
 * so physically adjacent rooms cannot duplicate or freeze side tiles.
 * Unknown branches are never invented to fill black pixels.
 */
uint32_t cviii_world_paint_0806(const CviiiLevel1World0803 *w,
    const CviiiStage1Atlas0724 *atlas,const uint8_t key[3],
    int camera_x,int camera_y,uint32_t *dest,
    int width,int height,int center,uint16_t bg_table,
    uint8_t (*chr)(uint16_t),uint32_t (*color)(int))
{
    if(!w || !w->ready || !atlas || !atlas->loaded ||
       !key || !dest || !chr || !color || width<=256 ||
       height!=240 || center<0 || center+256>width)return 0;
    const int selected=cviii_world_index_0803(w,key);
    if(selected<0 || !w->rooms[selected].placed)return 0;
    const int64_t world_x=(int64_t)w->rooms[selected].x+camera_x;
    const int64_t world_y=(int64_t)w->rooms[selected].y+camera_y;
    uint32_t pixels=0;
    for(int i=0;i<CVIII_WORLD_ROOMS_0803;i++){
        const CviiiWorldRoom0803 *room=&w->rooms[i];
        if(!room->placed)continue;
        const int64_t rx=world_x-room->x,ry=world_y-room->y;
        /* No source geometry for this room can reach viewport margins. */
        /* World source at wx = rx + screen_x - center, with
         * screen_x in [0,width-1]. A NEXT room 256px ahead is
         * already visible in the 85px right margin. Do NOT clip
         * against the room's own width or the 256px NES viewport! */
        if(rx<=center-width || rx>=room->width+center ||
           ry<=-(height-32) || ry>=room->height)continue;
        if(rx<INT_MIN || rx>INT_MAX || ry<INT_MIN || ry>INT_MAX)
            continue;
        pixels+=cviii_stage1_atlas_paint_bg_table_0802(
           atlas,room->selector,(int)rx,(int)ry,dest,
           width,height,center,bg_table,chr,color);
    }
    return pixels;
}

int cviii_world_camera_0803(const CviiiLevel1World0803 *w,
    const uint8_t selector[3],int cx,int cy,int32_t *x,int32_t *y){
    int i=cviii_world_index_0803(w,selector);
    if(i<0 || !x || !y || !w->rooms[i].placed ||
       cx<0 || cy<0 || cx>w->rooms[i].width ||
       cy>w->rooms[i].height)return 0;
    *x=w->rooms[i].x+cx;
    *y=w->rooms[i].y+cy;
    return 1;
}
int cviii_world_visit_0803(CviiiLevel1World0803 *w,
                            const uint8_t selector[3]){
    int i=cviii_world_index_0803(w,selector);
    if(i<0)return 0;
    if(!w->rooms[i].visited){
        w->rooms[i].visited=1;
        w->visited_count++;
    }
    return 1;
}
unsigned cviii_world_capture_live_0803(CviiiLevel1World0803 *w,
    const uint8_t key[3],int cx,int cy,const uint8_t ram[2048]){
    if(!w || !ram || !w->ready)return 0;
    int idx=cviii_world_index_0803(w,key);
    if(idx<0 || !w->rooms[idx].placed || cx<0 || cy<0)return 0;
    (void)cviii_world_visit_0803(w,key);
    unsigned count=0;
    for(unsigned i=0;i<CVIII_WORLD_ACTORS_0803;i++){
        CviiiWorldActor0803 *actor=&w->actors[i];
        uint8_t frame=ram[0x400u+i],flags=ram[0x470u+i];
        if(!frame || (flags&0x80u)){
            actor->active=0;
            actor->source_cpu_0814=0;
            actor->source_generation_0814=0;
            continue;
        }
        const uint8_t selector=ram[0x48cu+i];
        const uint8_t type=ram[0x54eu+i];
        const int same_identity=actor->active &&
             actor->room==(uint8_t)idx &&
             actor->slot==(uint8_t)i &&
             actor->selector==selector && actor->original_type==type;
        /* Original PRG26 sprite base coordinates are 8-bit local X.
         * When an original actor crosses native X0, the source byte
         * wraps to $FF but its physical WORLD position remains near its
         * preceding world position. Only unwrap if the already-live
         * slot/descriptor retains its original identity and displacement
         * is within genuine per-frame motion bounds; never fabricate a
         * spawn or synthesize an absent actor. */
        int32_t world_x=w->rooms[idx].x+cx+ram[0x438u+i];
        if(same_identity) {
            int64_t predicted=(int64_t)actor->x;
            int64_t candidate=world_x;
            if(candidate-predicted>=224 &&
               candidate-256-predicted>=-32 &&
               candidate-256-predicted<=32)
                world_x-=256;
            else if(predicted-candidate>=224 &&
               candidate+256-predicted>=-32 &&
               candidate+256-predicted<=32)
                world_x+=256;
        }
        if(!same_identity) {
            actor->generation++;
            actor->source_cpu_0814=0;
            actor->source_generation_0814=0;
        }
        actor->original_type=type;
        actor->active=1;
        actor->room=(uint8_t)idx;
        actor->slot=(uint8_t)i;
        actor->selector=selector;
        actor->frame=frame;
        actor->mirror=ram[0x4a8u+i];
        actor->flags=flags;
        actor->raw_x=ram[0x438u+i];
        actor->raw_y=ram[0x41cu+i];
        actor->attrs=ram[0x454u+i];
        /* Authentic CPU array contains viewport-local sprite base XY;
         * projection is observational, not permission to simulate AI. */
        actor->x=world_x;
        actor->y=w->rooms[idx].y+cy+actor->raw_y;
        count++;
    }
    w->actor_frame++;
    return count;
}
