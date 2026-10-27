/* Original Japanese PRG31:$EC47 source-call authentication.
 * No guest writes. All offsets are CPU 6502 stack semantics.
 * At E2CB: E2CA's PHA is on stack; JSR return EC4C at S+2/+3,
 * EC47 original-A at S+4, caller B8FF JSR return B901 at S+5/+6.
 * Direct B8F4 source bytes are separately checked by the runtime.
 */
#ifndef CVIII_NESTUDIO_EC47_TRACE_H
#define CVIII_NESTUDIO_EC47_TRACE_H
#include <stdint.h>
#include <string.h>
typedef struct {
    uint32_t sequence,stage,token,source_frame,queue_start,queue_end;
    uint32_t queue_reads,completed,ppu_writes,first_ppu,last_ppu,last_ppu_pc;
    uint32_t source_message_sequence;
} CviiiNestEc47Trace;
static int cviii_ec47_stack_matches(const uint8_t ram[2048],
                                    uint8_t sp,uint8_t token)
{
    unsigned a=0x100u | ((unsigned)(sp+2u)&0xFFu);
    unsigned b=0x100u | ((unsigned)(sp+3u)&0xFFu);
    unsigned c=0x100u | ((unsigned)(sp+4u)&0xFFu);
    unsigned d=0x100u | ((unsigned)(sp+5u)&0xFFu);
    unsigned e=0x100u | ((unsigned)(sp+6u)&0xFFu);
    return ram[a]==0x4Cu && ram[b]==0xECu &&
           ram[c]==token && ram[d]==0x01u && ram[e]==0xB9u;
}
static void cviii_ec47_reset(CviiiNestEc47Trace *trace)
{
    memset(trace,0,sizeof(*trace));
}
static void cviii_ec47_begin(CviiiNestEc47Trace *trace,
    unsigned stage,unsigned token,unsigned frame,unsigned cursor,
    unsigned source_sequence)
{
    ++trace->sequence;
    if(!trace->sequence)trace->sequence=1;
    trace->stage=stage;trace->token=token;
    trace->source_frame=frame;trace->queue_start=cursor;
    trace->queue_end=cursor;trace->queue_reads=0;
    trace->ppu_writes=0;trace->first_ppu=0;
    trace->last_ppu=0;trace->last_ppu_pc=0;
    trace->completed=0;trace->source_message_sequence=source_sequence;
}
static void cviii_ec47_queue_read(CviiiNestEc47Trace *trace)
{
    if(trace->sequence && !trace->completed)++trace->queue_reads;
}
static void cviii_ec47_finish(CviiiNestEc47Trace *trace,unsigned cursor)
{
    if(!trace->sequence)return;
    trace->queue_end=cursor&255u;trace->completed=1;
}
/* Temporal observation: NOT proof that a given PPU tile belongs to
 * this command stream. Two-frame window avoids unrelated late writes. */
static void cviii_ec47_ppu_write(CviiiNestEc47Trace *trace,
    unsigned frame,unsigned addr,unsigned pc)
{
    if(!trace->sequence || !trace->completed ||
       frame<trace->source_frame || frame-trace->source_frame>2u)
        return;
    if(!trace->ppu_writes)trace->first_ppu=addr;
    ++trace->ppu_writes;
    trace->last_ppu=addr;trace->last_ppu_pc=pc;
}
#endif
