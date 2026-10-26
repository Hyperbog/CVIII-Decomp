/* JP0740 optional private original-JP CYC source-writer instrumentation.
 * Included only when JP0740_TRACE_CPU_WRITES=ON (OFF by default). */
#ifndef CVIII_JP0740_NATIVE_TRACE_H
#define CVIII_JP0740_NATIVE_TRACE_H
#include <stdint.h>
void cviii_jp0740_instruction(uint16_t pc, uint32_t physical_prg_offset);
void cviii_jp0740_write(uint16_t bus_addr, uint8_t old, uint8_t value, uint64_t cycles);
void cviii_jp0740_read(uint16_t bus_addr, uint8_t value, uint64_t cycles);
#endif
