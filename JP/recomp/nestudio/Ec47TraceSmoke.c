/* ROM-free authenticated $EC47 stack and deferred PPU correlation. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "../native/enhanced/cviii_nestudio_ec47_trace.h"
int main(void)
{
    uint8_t ram[2048]={0};
    uint8_t sp=0xF7u;
    ram[0x1F9]=0x4Cu;ram[0x1FA]=0xECu;
    ram[0x1FB]=0x32u;ram[0x1FC]=0x01u;ram[0x1FD]=0xB9u;
    assert(cviii_ec47_stack_matches(ram,sp,0x32u));
    assert(!cviii_ec47_stack_matches(ram,sp,0x33u));
    ram[0x1FC]=0;
    assert(!cviii_ec47_stack_matches(ram,sp,0x32u));
    CviiiNestEc47Trace t;
    cviii_ec47_reset(&t);
    assert(t.sequence==0);
    cviii_ec47_begin(&t,2u,0x32u,200u,10u,7u);
    cviii_ec47_queue_read(&t);
    cviii_ec47_queue_read(&t);
    cviii_ec47_ppu_write(&t,200u,0x2123u,0xECB0u);
    assert(t.ppu_writes==0); /* never attribute before verified return */
    cviii_ec47_finish(&t,24u);
    assert(t.queue_start==10 && t.queue_end==24);
    assert(t.queue_reads==2 && t.completed);
    cviii_ec47_ppu_write(&t,201u,0x2123u,0xECB0u);
    cviii_ec47_ppu_write(&t,202u,0x2124u,0xECB8u);
    cviii_ec47_ppu_write(&t,203u,0x2125u,0xECB8u);
    assert(t.ppu_writes==2 && t.first_ppu==0x2123u &&
           t.last_ppu==0x2124u && t.last_ppu_pc==0xECB8u);
    cviii_ec47_begin(&t,3u,0x34u,204u,24u,9u);
    assert(t.sequence==2 && !t.completed && t.ppu_writes==0);
    cviii_ec47_reset(&t);
    assert(!t.sequence && !t.completed && !t.ppu_writes);
    puts("PASS original EC47 stack, command cursor and bounded PPU correlation");
    return 0;
}
