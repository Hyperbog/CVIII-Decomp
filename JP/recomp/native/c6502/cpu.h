#ifndef JP_C6502_CPU_H
#define JP_C6502_CPU_H
/* JP 0562 portable C11 recompilation ABI. No ROM bytes bundled.
 * Original 2A03 CPU instruction semantics; the clocked NES hardware
 * backend remains separate and must be explicitly integrated later.
 */
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {
  JP_STEP_EXECUTED=0, JP_STEP_UNRESOLVED=1,
  JP_STEP_CANDIDATE=2, JP_STEP_UNSUPPORTED=3
} JpStep;
typedef enum { JP_OP_INVALID=0,
  JP_OP_ADC,
  JP_OP_AND,
  JP_OP_ASL,
  JP_OP_BCC,
  JP_OP_BCS,
  JP_OP_BEQ,
  JP_OP_BIT,
  JP_OP_BMI,
  JP_OP_BNE,
  JP_OP_BPL,
  JP_OP_BRK,
  JP_OP_BVC,
  JP_OP_BVS,
  JP_OP_CLC,
  JP_OP_CLD,
  JP_OP_CLI,
  JP_OP_CLV,
  JP_OP_CMP,
  JP_OP_CPX,
  JP_OP_CPY,
  JP_OP_DEC,
  JP_OP_DEX,
  JP_OP_DEY,
  JP_OP_EOR,
  JP_OP_INC,
  JP_OP_INX,
  JP_OP_INY,
  JP_OP_JMP,
  JP_OP_JSR,
  JP_OP_LDA,
  JP_OP_LDX,
  JP_OP_LDY,
  JP_OP_LSR,
  JP_OP_NOP,
  JP_OP_ORA,
  JP_OP_PHA,
  JP_OP_PHP,
  JP_OP_PLA,
  JP_OP_PLP,
  JP_OP_ROL,
  JP_OP_ROR,
  JP_OP_RTI,
  JP_OP_RTS,
  JP_OP_SBC,
  JP_OP_SEC,
  JP_OP_SED,
  JP_OP_SEI,
  JP_OP_STA,
  JP_OP_STX,
  JP_OP_STY,
  JP_OP_TAX,
  JP_OP_TAY,
  JP_OP_TSX,
  JP_OP_TXA,
  JP_OP_TXS,
  JP_OP_TYA
} JpOp;
typedef enum { JP_MODE_INVALID=0,
  JP_MODE_ABS,
  JP_MODE_ABSX,
  JP_MODE_ABSY,
  JP_MODE_ACC,
  JP_MODE_IMM,
  JP_MODE_IMP,
  JP_MODE_IND,
  JP_MODE_INDX,
  JP_MODE_INDY,
  JP_MODE_REL,
  JP_MODE_ZP,
  JP_MODE_ZPX,
  JP_MODE_ZPY
} JpMode;
typedef struct {
 JpOp op;
 JpMode mode;
 uint8_t size;
} JpDecoded;
extern const JpDecoded jp_opcodes[256];
typedef struct {
 /* VRC6a mapper24: $8000-$BFFF selects a 16KiB bank,
    $C000-$DFFF selects an independent 8KiB bank, $E000 fixed last 8KiB.
    ROM is owned/authenticated by caller and never embedded in project. */
 const uint8_t *prg;
 size_t prg_size;
 uint8_t ram[2048];
 uint8_t bank; /* VRC6 16KiB bank selector, masked to 4 bits */
 uint8_t bank8; /* Independent $C000 8KiB bank selector, 5 bits */
} JpBus;
typedef struct JpCpu {
 JpBus *bus;
 uint16_t pc;
 uint8_t a,x,y,s,p;
 uint64_t compiled_instructions,interpreted_instructions;
 int allow_candidate_static,allow_fallback;
 JpStep fault;
} JpCpu;
typedef JpStep (*JpCompiledStep)(JpCpu *);
void jp_cpu_init(JpCpu *,JpBus *);
JpStep jp_cpu_step(JpCpu *,JpCompiledStep);
JpStep jp_cpu_exec(JpCpu *,uint8_t opcode,uint16_t argument,uint16_t next);
JpStep jp_cpu_interpret_one(JpCpu *);
/* One physical-offset resolver for interpreted reads and generated C.
   Only PRG-ROM addresses are supported. Offset in 262144-byte PRG. */
JpStep jp_bus_physical_offset(const JpBus *,uint16_t address,unsigned *physical);
JpStep jp_bus_read(JpBus *,uint16_t address,uint8_t *value);
JpStep jp_bus_write(JpBus *,uint16_t address,uint8_t value);
#ifdef __cplusplus
}
#endif
#endif
