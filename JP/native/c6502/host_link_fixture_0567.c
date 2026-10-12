/* JP 0567: ROM-free generated-C fixture for Windows native C host link.
 * Values are invented; this is NOT decompiled original game code.
 * Actual local builds replace both callbacks with authenticated codegen.
 */
#include "cpu.h"
JpStep jp_bank0a_compiled_step(JpCpu *c) {
 if(!c||!c->bus||c->bus->bank!=10)return JP_STEP_UNRESOLVED;
 if(c->pc==0x8000)return jp_cpu_exec(c,0xa9,0x12,0x8002);
 return JP_STEP_UNRESOLVED;
}
JpStep jp_fixed_compiled_step(JpCpu *c) {
 if(!c || !c->bus)return JP_STEP_UNRESOLVED;
 if(c->pc==0xe000)return jp_cpu_exec(c,0xa9,0x03,0xe002);
 if(c->pc==0xe002)return jp_cpu_exec(c,0x85,0x10,0xe004);
 return JP_STEP_UNRESOLVED;
}
