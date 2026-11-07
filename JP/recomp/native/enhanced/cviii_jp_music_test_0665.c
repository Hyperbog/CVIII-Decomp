/* ROM-free invented source. No proprietary notes, DPCM payload or timbre. */
#include "cviii_jp_music_0665.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int testno; static void expect(int ok){++testno;if(!ok){fprintf(stderr,"JP0665 test failed at assertion %d\n",testno);exit(1);}}
int main(void){
    uint8_t b[CVIII_JP0665_RAW05_SIZE]={0};
    uint8_t d[CVIII_JP0665_RAW0C_SIZE]={0};
    const unsigned ptr=0x905au-0x8000u,idx=0x8f60u-0x8000u+0x50u*2u;
    d[idx]=0x5a;d[idx+1]=0x90;d[ptr]=5;d[ptr+1]=5;
    for(unsigned i=0;i<6;++i){
        unsigned root=0x87aeu+0x10u*i;unsigned mode=(i==5?7:i);
        d[ptr+2u+3u*i]=(uint8_t)mode;
        d[ptr+3u+3u*i]=(uint8_t)root;d[ptr+4u+3u*i]=(uint8_t)(root>>8);
        unsigned o=root-0x8000u;
        if(i!=5){
            b[o]=0xd1;b[o+1]=1;b[o+2]=0;b[o+3]=0;
            b[o+4]=0xc1;b[o+5]=0x22;b[o+6]=0xfb;
            b[o+7]=0x31;b[o+8]=0xfe;b[o+9]=2;
            b[o+10]=0xfe;b[o+11]=0xff;b[o+12]=(uint8_t)root;
            b[o+13]=(uint8_t)(root>>8);
        }else{
            b[o]=0xd1;b[o+1]=0x90;b[o+2]=0x21;b[o+3]=0x90;
            b[o+4]=0xfe;b[o+5]=0xff;b[o+6]=(uint8_t)root;
            b[o+7]=(uint8_t)(root>>8);
        }
    }
    CviiiJp0665Voice v[CVIII_JP0665_VOICES];
    expect(cviii_jp0665_init(b,sizeof(b),d,sizeof(d),v));
    CviiiJp0665Event ev={0};
    expect(cviii_jp0665_next(&v[0],&ev)==1 && ev.kind==CVIII_JP0665_REST &&
           ev.duration_ticks==2 && ev.tick==0);
    expect(cviii_jp0665_next(&v[0],&ev)==1 && ev.kind==CVIII_JP0665_NOTE &&
           ev.tick==2 && ev.duration_ticks==3 && ev.destination_period_low==0x9001u);
    expect(cviii_jp0665_next(&v[0],&ev)==1 && ev.tick==5);
    expect(cviii_jp0665_next(&v[0],&ev)==1 && ev.tick==7);
    expect(cviii_jp0665_next(&v[0],&ev)==1 && ev.tick==9);
    expect(cviii_jp0665_next(&v[5],&ev)==1 && ev.tick==0 &&
           ev.kind==CVIII_JP0665_DPCM_REQUEST && ev.sound_request_id==0x71);
    expect(cviii_jp0665_next(&v[5],&ev)==1 && ev.tick==1 &&
           ev.kind==CVIII_JP0665_NOISE_REQUEST && ev.sound_request_id==3);
    expect(cviii_jp0665_next(&v[5],&ev)==1 && ev.tick==3 &&
           ev.kind==CVIII_JP0665_DPCM_REQUEST);
    uint8_t tampered[CVIII_JP0665_RAW0C_SIZE];memcpy(tampered,d,sizeof d);
    tampered[ptr+1]=6;
    expect(!cviii_jp0665_init(b,sizeof(b),tampered,sizeof(tampered),v));
    expect(!cviii_jp0665_init(b,sizeof(b)-1,d,sizeof(d),v));
    puts("PASS JP0665 C11 source-driven note/rest/percussion events (invented fixture)");
    return 0;
}
