/* Read-only ownership of original PRG26:$8070 emitted sprite entries.
 * Called at actual CPU RAM operand reads inside $8070, never simulated
 * from arbitrary OAM proximity. No guest memory, CPU flags or timing writes.
 * Slots are authoritative only when the bank-qualified source signature
 * was observed and source emission count remained internally consistent.
 */
#ifndef CVIII_NESTUDIO_OWNER_H
#define CVIII_NESTUDIO_OWNER_H
#include <stdint.h>
#include <string.h>
#define CVIII_OWNER_UNKNOWN 255u
typedef struct {
    uint8_t owners[64];
    uint8_t pending_object,pending_offset,pending_remaining,pending;
    unsigned observed,attributed,invalid;
} CviiiNestOwnerTrace;
static void cviii_owner_reset(CviiiNestOwnerTrace *t)
{
    memset(t,0,sizeof(*t));
    memset(t->owners,CVIII_OWNER_UNKNOWN,sizeof(t->owners));
}
static void cviii_owner_finish(CviiiNestOwnerTrace *t,unsigned remaining)
{
    if(!t->pending)return;
    if(remaining>t->pending_remaining || remaining>64u){
        ++t->invalid;t->pending=0;return;
    }
    unsigned count=(unsigned)t->pending_remaining-remaining;
    unsigned start=t->pending_offset;
    if(count>64u){++t->invalid;t->pending=0;return;}
    for(unsigned n=0;n<count;++n){
        unsigned physical=((start+n*0xC4u)&0xFFu)>>2;
        if(t->owners[physical]!=CVIII_OWNER_UNKNOWN &&
           t->owners[physical]!=t->pending_object)
            ++t->invalid;
        else if(t->owners[physical]==CVIII_OWNER_UNKNOWN){
            t->owners[physical]=t->pending_object;
            ++t->attributed;
        }
    }
    t->pending=0;
}
static void cviii_owner_enter(CviiiNestOwnerTrace *t,unsigned owner,
                              unsigned offset,unsigned remaining)
{
    cviii_owner_finish(t,remaining);
    if(owner>=28u || (offset&3u)!=0u || remaining==0 || remaining>64u){
        ++t->invalid;return;
    }
    t->pending=1;
    t->pending_object=(uint8_t)owner;
    t->pending_offset=(uint8_t)offset;
    t->pending_remaining=(uint8_t)remaining;
    ++t->observed;
}
/* A frame with no observed source calls must never be treated as mapped. */
static int cviii_owner_ready(const CviiiNestOwnerTrace *t)
{
    return t->observed!=0 && t->invalid==0 && t->attributed!=0;
}
#endif
