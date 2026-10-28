/* ROM-free artificial source catalog: no original level/object data. */
#ifdef NDEBUG
#undef NDEBUG
#endif
#include "cviii_level_preload_0829.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { ROM_N=393232, BANK_START=16+10*16384 };
static uint8_t *rom;
static void put(unsigned cpu,unsigned value) {
    rom[BANK_START+cpu-0x8000u]=(uint8_t)value;
}
static void word(unsigned cpu,unsigned value) {
    put(cpu,value);put(cpu+1u,value>>8u);
}
static void artificial_rooms(void)
{
    static const unsigned groups[15]={4,6,5,5,3,4,3,7,5,2,7,3,3,4,3};
    unsigned second[64],leaf[135],second_count=0,leaf_count=0;
    unsigned st=0x92ccu;
    for(unsigned i=0;i<15;i++) {
        if(i==9u)st=0x9af4u;
        word(0x92aeu+2u*i,st);st+=2u*groups[i];
    }
    assert(st==0x9b20u);
    st=0x9320u;
    for(unsigned i=0;i<64;i++) {
        if(i==42u)st=0x9b20u;
        second[i]=st;
        unsigned n=2u+(i<2u || (i>=42u && i<47u));
        st+=2u*n;
    }
    assert(st==0x9b82u);
    unsigned cursor=0x92ccu;
    for(unsigned i=0;i<15;i++) {
        if(i==9u)cursor=0x9af4u;
        for(unsigned j=0;j<groups[i];j++)
            word(cursor+2u*j,second[second_count++]);
        cursor+=2u*groups[i];
    }
    assert(second_count==64u);
    st=0x93ccu;
    for(unsigned i=0;i<70u;i++) {
        leaf[leaf_count++]=st;
        st+=4u*(i<38u?7u:6u);
    }
    assert(st==0x9af4u);
    st=0x9b82u;
    for(unsigned i=0;i<43u;i++) {
        leaf[leaf_count++]=st;
        st+=4u*(i<36u?6u:5u);
    }
    assert(st==0x9f6eu);
    st=0xab1fu;
    for(unsigned i=0;i<16u;i++) {
        leaf[leaf_count++]=st;
        unsigned count=i<13u?10u:11u;
        for(unsigned j=0;j<count;j++)put(st+7u*j,(i+j)&3u);
        st+=7u*count;
        put(st,0xffu);st++;
    }
    assert(st==0xafa4u);
    for(unsigned i=0;i<6u;i++)leaf[leaf_count++]=leaf[i];
    assert(leaf_count==135u);
    unsigned p=0;
    for(unsigned i=0;i<64;i++) {
        unsigned n=2u+(i<2u || (i>=42u && i<47u));
        for(unsigned j=0;j<n;j++)word(second[i]+2u*j,leaf[p++]);
    }
    assert(p==135u);
}
static void artificial_tsa(void)
{
    const CviiiTsaRegion0730 *r=cviii_tsa_regions_0730();
    for(unsigned i=0;i<CVIII_TSA_REGIONS_0730;i++) {
        if(!r[i].pattern_count)continue;
        for(unsigned row=0;row<r[i].pattern_count;row++)
            for(unsigned j=0;j<16;j++)
                rom[r[i].source_start+row*16u+j]=(uint8_t)(i+row+j);
    }
}
int main(void)
{
    rom=(uint8_t *)calloc(ROM_N,1);
    CviiiLevelPreload0829 *state=(CviiiLevelPreload0829 *)calloc(1,sizeof *state);
    CviiiLevelPreload0829 *saved=(CviiiLevelPreload0829 *)calloc(1,sizeof *saved);
    assert(rom && state && saved);
    memcpy(rom,"NES\x1a",4);rom[4]=16;rom[5]=16;
    rom[6]=0x80;rom[7]=0x10;
    artificial_rooms();artificial_tsa();
    assert(cviii_level_preload_bytes_0829(rom,ROM_N,state));
    assert(state->loaded && state->tsa.loaded &&
           state->tsa.offsets[15]==1478u &&
           state->active_stage==0xffu && state->stage_changes==0u);
    unsigned indexed=0;
    for(unsigned stage=0;stage<15;stage++) {
        assert(state->count[stage]>0);
        for(unsigned j=0;j<state->count[stage];j++) {
            const CviiiRoomResource0829 *r=
                &state->room[state->first[stage]+j];
            assert(r->stage==stage && r->record_count>0u);
            size_t n=0;unsigned width=0,count=0;
            const uint8_t *p=cviii_level_preload_room_0829(state,
                stage,r->subarea,r->room,&n,&width,&count);
            assert(p && n==r->length && width==r->record_width &&
                   count==r->record_count);
            assert(!memcmp(p,rom+BANK_START+r->source_cpu-0x8000u,n));
            indexed++;
        }
    }
    assert(indexed==135u);
    assert(cviii_level_preload_stage_0829(state,0));
    assert(state->active_stage==0u && state->stage_changes==1u);
    assert(cviii_level_preload_stage_0829(state,0));
    assert(state->stage_changes==1u);
    assert(cviii_level_preload_stage_0829(state,14));
    assert(state->active_stage==14u && state->stage_changes==2u);
    assert(!cviii_level_preload_stage_0829(state,15));
    assert(state->active_stage==14u);
    size_t n=99;unsigned width=99,count=99;
    assert(!cviii_level_preload_room_0829(state,15,0,0,
                                         &n,&width,&count));
    assert(n==0 && width==0 && count==0);
    memcpy(saved,state,sizeof *state);
    rom[BANK_START+0xafa3u-0x8000u]=0;
    assert(!cviii_level_preload_bytes_0829(rom,ROM_N,state));
    assert(!memcmp(saved,state,sizeof *state));
    rom[BANK_START+0xafa3u-0x8000u]=0xffu;
    rom[7]=0; /* wrong mapper: no partial update */
    assert(!cviii_level_preload_bytes_0829(rom,ROM_N,state));
    assert(!memcmp(saved,state,sizeof *state));
    rom[7]=0x10;
    assert(!cviii_level_preload_bytes_0829(rom,ROM_N-1u,state));
    assert(!memcmp(saved,state,sizeof *state));
    free(saved);free(state);free(rom);
    puts("PASS: all 15 stages/135 room sources, 14 TSA sets resident; no gameplay writes");
    return 0;
}
