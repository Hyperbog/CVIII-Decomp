#include "cviii_jp_percussion_plan_0667.h"
#include <string.h>
bool cviii_jp_percussion_plan_0667(const uint8_t *raw05,size_t size,
                                     unsigned nibble,const uint8_t *table,
                                     size_t len,unsigned priority,
                                     CviiiJpPercussionPlan *out)
{
    if(!raw05 || !out || size!=16384u || nibble>15u || priority>255u ||
       !table || len!=CVIII_DMC_TABLE_BYTES)return false;
    CviiiJpPercussionPlan plan;
    memset(&plan,0,sizeof plan);
    plan.source_nibble=(uint8_t)nibble;
    if(nibble>=12u){plan.kind=CVIII_JP_PERC_REST;}
    else {
        const unsigned id=raw05[0x8072u-0x8000u+nibble];
        if(id>=0x6fu && id<=0x7du){
            plan.kind=CVIII_JP_PERC_DMC_REQUEST;
            plan.request_id=(uint8_t)id;
            if(!cviii_dmc_plan_0648(table,len,id,priority,&plan.dmc))return false;
        }else if(id>=1u && id<=5u){
            plan.kind=CVIII_JP_PERC_NOISE_REQUEST;
            plan.request_id=(uint8_t)id;
        }else return false; /* unsupported original command */
    }
    *out=plan;
    return true;
}
