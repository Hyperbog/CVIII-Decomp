/* JP0740: opt-in read-only CPU bus and physically mapped opcode provenance.
 * Production CMake default omits these hooks entirely. No game assets,
 * controller schedule, ROM content or CPU/PPU changes are emitted here.
 */
#include "cviii_jp0740_native_trace.h"
#include <stdint.h>
extern uint32_t cyc_ring_frame;
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

static FILE *trace;
static unsigned status;
static uint64_t events;
static uint16_t instruction_pc;
static uint32_t instruction_phys;
static int passed_window_end;
static uint32_t first_frame=9370u, last_frame=9600u;
static int window_set;
static void configure_window(void)
{
    const char *a,*b;
    char *end_a,*end_b;
    unsigned long lo,hi;
    if(window_set)return;
    window_set=1;
    a=getenv("JP0745_TRACE_FIRST_FRAME");
    b=getenv("JP0745_TRACE_LAST_FRAME");
    if(!a && !b)return; /* Preserve original JP0740 defaults. */
    if(!a || !b || !a[0] || !b[0]){
        fputs("JP0745 needs BOTH trace window bounds\\n",stderr);abort();
    }
    lo=strtoul(a,&end_a,10);
    hi=strtoul(b,&end_b,10);
    if(*end_a || *end_b || hi<lo || hi-lo>500u || hi>1000000u){
        fputs("JP0745 invalid / unbounded trace window\\n",stderr);abort();
    }
    first_frame=(uint32_t)lo;
    last_frame=(uint32_t)hi;
}
static const uint64_t maximum_events=150000u;

static void finish(void)
{
    if(trace){
        fprintf(trace,"END\t%s\t%" PRIu64 "\n",
                events>maximum_events?"OVERFLOW":
                passed_window_end?"COMPLETE":"INCOMPLETE",events);
        if(fclose(trace)) fputs("JP0740 native output close error\n",stderr);
        trace=NULL;
    }
}
static int enabled(void)
{
    const char *path;
    if(status)return status==1;
    path=getenv("JP0740_NATIVE_TRACE_TSV");
    if(!path || !path[0]){status=2;return 0;}
    trace=fopen(path,"wb");
    if(!trace){
        fputs("JP0740 cannot open native tracing output\n",stderr);
        abort();
    }
    fputs("JP0740_NATIVE\t1\n",trace);
    if(atexit(finish)){
        fputs("JP0740 cannot register trace finalizer\n",stderr);
        abort();
    }
    status=1;
    return 1;
}
static int in_window(void)
{
    configure_window();
    return cyc_ring_frame>=first_frame && cyc_ring_frame<=last_frame;
}
void cviii_jp0740_instruction(uint16_t pc,uint32_t phys)
{
    if(!in_window() || !enabled())return;
    if(cyc_ring_frame>=last_frame)passed_window_end=1;
    instruction_pc=pc;
    instruction_phys=phys;
}
static void emit(char kind,uint16_t addr,uint8_t old,uint8_t value,uint64_t cycles)
{
    if(!in_window() || !enabled())return;
    if(++events>maximum_events){
        fputs("JP0740 native trace event overflow\n",stderr);
        abort();
    }
    if(kind=='W'){
        fprintf(trace,"W\t%" PRIu64 "\t%" PRIu32 "\t%" PRIu64
                      "\t%04X\t%02X\t%02X\t%04X\t%04X\t%05" PRIX32 "\n",
                events,cyc_ring_frame,cycles,addr,old,value,addr,
                instruction_pc,instruction_phys);
    }else{
        fprintf(trace,"R\t%" PRIu64 "\t%" PRIu32 "\t%" PRIu64
                      "\t%04X\t%02X\t%04X\t%05" PRIX32 "\n",
                events,cyc_ring_frame,cycles,addr,value,
                instruction_pc,instruction_phys);
    }
}
void cviii_jp0740_write(uint16_t addr,uint8_t old,uint8_t value,uint64_t cycles)
{
    uint16_t a=(uint16_t)(addr&0x07FFu);
    if(addr==0x4016u || a==0x0028u || a==0x002Au ||
       a==0x0062u || a==0x0053u ||
       a==0x0054u || a==0x0055u || a==0x0063u || a==0x006Bu ||
       a==0x041Cu || a==0x0438u || a==0x04C4u || a==0x04F2u ||
       a==0x0509u || a==0x0520u || a==0x0565u || a==0x05C1u)
        emit('W',addr==0x4016u?addr:a,old,value,cycles);
}
void cviii_jp0740_read(uint16_t addr,uint8_t value,uint64_t cycles)
{
    if(addr==0x4016u || addr==0x4017u)
        emit('R',addr,0,value,cycles);
}
