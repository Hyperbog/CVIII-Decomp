#ifdef NDEBUG
#undef NDEBUG
#endif
#include "cviii_jp_percussion_plan_0667.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void){
 uint8_t raw[16384]={0}, table[60]={0};
 const uint8_t map[12]={1,2,3,4,5,0x72,0x7b,0x6f,0x70,0x71,0x72,0x73};
 memcpy(raw+0x72,map,12);
 for(unsigned i=0;i<60;i++)table[i]=(uint8_t)(i*3u);
 unsigned noise=0,dmc=0,rest=0,accepted=0,denied=0;
 for(unsigned n=0;n<16;n++)for(unsigned p=0;p<256;p++){
  CviiiJpPercussionPlan plan={0};
  assert(cviii_jp_percussion_plan_0667(raw,sizeof(raw),n,table,sizeof(table),p,&plan));
  if(n<5){++noise;assert(plan.kind==CVIII_JP_PERC_NOISE_REQUEST&&plan.request_id==map[n]&&!plan.dmc.write_count);}
  else if(n<12){++dmc;assert(plan.kind==CVIII_JP_PERC_DMC_REQUEST&&plan.request_id==map[n]);
   if(plan.dmc.accepted){++accepted;assert(plan.dmc.write_count==6&&plan.dmc.writes[0].address==0x4015&&plan.dmc.writes[5].value==0x1f);}else{++denied;assert(!plan.dmc.write_count);}}
  else{++rest;assert(plan.kind==CVIII_JP_PERC_REST&&!plan.request_id);}
 }
 assert(noise==1280&&dmc==1792&&rest==1024&&accepted+denied==dmc);
 CviiiJpPercussionPlan bad;memset(&bad,0xa5,sizeof bad);
 CviiiJpPercussionPlan expected=bad;
 raw[0x72]=0x55;
 assert(!cviii_jp_percussion_plan_0667(raw,sizeof raw,0,table,sizeof table,0,&bad));
 assert(memcmp(&bad,&expected,sizeof bad)==0);
 assert(!cviii_jp_percussion_plan_0667(raw,sizeof raw,16,table,sizeof table,0,&bad));
 assert(!cviii_jp_percussion_plan_0667(raw,sizeof raw,7,table,59,0,&bad));
 assert(memcmp(&bad,&expected,sizeof bad)==0);
 puts("PASS JP0667 synthetic percussion 4096 request/priority cases and rejection guards");return 0;
}
