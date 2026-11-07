/* JP0827: verify persistent-world host calls original 6502 VM on
 * real source-linked actors. Synthetic ROM is an intentionally tiny
 * control-flow fixture, NOT a redistributable Japanese cartridge. */
#include "cviii_level1_world_0803.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void test(int ok,const char *message){
 if(!ok){fprintf(stderr,"FAIL JP0827 world VM: %s\n",message);exit(1);}
}
int main(void){
 CviiiLevel1World0803 *w=calloc(1,sizeof *w);
 test(w!=NULL,"native world allocation");
 uint8_t ram[2048]={0},baseline[2048]={0},bank[16384]={0};
 w->ready=1u;
 w->wide_runtime_0826.initialized=1u;
 w->wide_runtime_0826.actor[0].state=CVIII_INSTANCE_LIVE_0826;
 w->wide_runtime_0826.actor[0].guest_slot=1u;
 ram[0x054fu]=0x3du;
 ram[0x0471u]=4u;
 ram[0x066au]=0x07u; /* no high nibble damage */
 ram[0x067cu]=8u;
 /* A tiny synthetic JMP/RTS circuit exercises the real VM host
  * hookup, not independently establishes B486 ROM equivalence. */
 bank[0xb486u-0x8000u]=0x4cu;
 bank[0xb487u-0x8000u]=0xd4u;
 bank[0xb488u-0x8000u]=0xb4u;
 bank[0xb4d4u-0x8000u]=0x60u;
 memcpy(baseline,ram,sizeof ram);
 test(cviii_world_probe_vm_0827(w,ram,bank)==1 &&
      w->actor_vm_probes_0827==1u &&
      w->actor_vm_matched_0827==1u &&
      w->actor_vm_mismatched_0827==0u &&
      w->actor_vm_stop_pc_0827[0]==0xb4d4u &&
      w->actor_vm_last_status_0827[0]==CVIII_VM_STOP_RTS_0827 &&
      memcmp(baseline,ram,sizeof ram)==0,
      "native world can execute isolated original-compatible opcode path");
 /* A disagreement between ROM executor and branch predictor MUST be
  * reported, not silently accepted as an offscreen damage event. */
 ram[0x066au]=0x37u;ram[0x067cu]=2u;
 test(cviii_world_probe_vm_0827(w,ram,bank)==0 &&
      w->actor_vm_probes_0827==2u &&
      w->actor_vm_matched_0827==1u &&
      w->actor_vm_mismatched_0827==1u &&
      !w->wide_runtime_0826.actor[0].has_combat_parity,
      "mismatched opcode behavior is not gameplay authority");
 w->wide_runtime_0826.actor[0].state=CVIII_INSTANCE_LOST_0826;
 test(cviii_world_probe_vm_0827(w,ram,bank)==0 &&
      w->actor_vm_probes_0827==2u,
      "deallocated original actor never runs private VM");
 cviii_world_clear_live_0805(w);
 test(w->actor_vm_probes_0827==0u &&
      !w->actor_vm_matched_0827 &&
      !w->actor_vm_mismatched_0827 &&
      !w->actor_vm_stop_pc_0827[0] &&
      !w->actor_vm_last_status_0827[0],
      "savestate/scene reset removes transient original VM evidence");
 free(w);
 puts("PASS JP0827 native world probes, mismatch rejection and reset");
 return 0;
}
