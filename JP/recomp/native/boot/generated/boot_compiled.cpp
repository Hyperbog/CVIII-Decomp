// GENERATED from original fixed bank31 ASM + scripted reset/NMI trace.
// All physical instruction sites compile as native C++, no ROM bytes embedded.
// Unknown offsets fail closed; scripted trace does not prove natural game liveness.
#include "static_6502.hpp"
namespace jpstatic {
StepResult compiled_boot_step(Cpu& cpu) {
 unsigned offset;
 if(cpu.pc>=0xE000)offset=31u*8192u+unsigned(cpu.pc-0xE000);
 else if(cpu.pc>=0xC000)offset=30u*8192u+unsigned(cpu.pc-0xC000);
 else if(cpu.pc>=0x8000 && cpu.pc<0xC000 && cpu.bus.bank<=15)
   offset=unsigned(cpu.bus.bank)*16384u+unsigned(cpu.pc-0x8000);
 else return StepResult::unresolved;
 switch(offset) {
  case 0x307AE: // $87AE opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0x87B0);return StepResult::executed;
  case 0x307B0: // $87B0 opcode $86, TRACE_EXECUTED
   cpu.exec<Op::STX,Mode::zp>(0x00E2,0x87B2);return StepResult::executed;
  case 0x307B2: // $87B2 opcode $AA, TRACE_EXECUTED
   cpu.exec<Op::TAX,Mode::imp>(0x0000,0x87B3);return StepResult::executed;
  case 0x307B3: // $87B3 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0109,0x87B6);return StepResult::executed;
  case 0x307B6: // $87B6 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x06D3,0x87B9);return StepResult::executed;
  case 0x307B9: // $87B9 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0x87BA);return StepResult::executed;
  case 0x307BA: // $87BA opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x0009,0x87BC);return StepResult::executed;
  case 0x307BC: // $87BC opcode $90, TRACE_EXECUTED
   cpu.exec<Op::BCC,Mode::rel>(0x87B3,0x87BE);return StepResult::executed;
  case 0x307BE: // $87BE opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x0173,0x87C1);return StepResult::executed;
  case 0x307C1: // $87C1 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x017C,0x87C4);return StepResult::executed;
  case 0x307C4: // $87C4 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x016A,0x87C7);return StepResult::executed;
  case 0x307C7: // $87C7 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x00EB,0x87C9);return StepResult::executed;
  case 0x307C9: // $87C9 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x06DC,0x87CC);return StepResult::executed;
  case 0x307CC: // $87CC opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x01BF,0x87CF);return StepResult::executed;
  case 0x307CF: // $87CF opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x01BE,0x87D2);return StepResult::executed;
  case 0x307D2: // $87D2 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x01BD,0x87D5);return StepResult::executed;
  case 0x307D5: // $87D5 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x06DD,0x87D8);return StepResult::executed;
  case 0x307D8: // $87D8 opcode $A6, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::zp>(0x00E2,0x87DA);return StepResult::executed;
  case 0x307DA: // $87DA opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0030,0x87DC);return StepResult::executed;
  case 0x307DC: // $87DC opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4000,0x87DF);return StepResult::executed;
  case 0x307DF: // $87DF opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x87E2);return StepResult::executed;
  case 0x307E2: // $87E2 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4004,0x87E5);return StepResult::executed;
  case 0x307E5: // $87E5 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x87E8);return StepResult::executed;
  case 0x307E8: // $87E8 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x400C,0x87EB);return StepResult::executed;
  case 0x307EB: // $87EB opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x87EE);return StepResult::executed;
  case 0x307EE: // $87EE opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x007F,0x87F0);return StepResult::executed;
  case 0x307F0: // $87F0 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4001,0x87F3);return StepResult::executed;
  case 0x307F3: // $87F3 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x87F6);return StepResult::executed;
  case 0x307F6: // $87F6 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4005,0x87F9);return StepResult::executed;
  case 0x307F9: // $87F9 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x87FC);return StepResult::executed;
  case 0x307FC: // $87FC opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0x87FE);return StepResult::executed;
  case 0x307FE: // $87FE opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x9000,0x8801);return StepResult::executed;
  case 0x30801: // $8801 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x8804);return StepResult::executed;
  case 0x30804: // $8804 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xA000,0x8807);return StepResult::executed;
  case 0x30807: // $8807 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x880A);return StepResult::executed;
  case 0x3080A: // $880A opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xB000,0x880D);return StepResult::executed;
  case 0x3080D: // $880D opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x8810);return StepResult::executed;
  case 0x30810: // $8810 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x000F,0x8812);return StepResult::executed;
  case 0x30812: // $8812 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4015,0x8815);return StepResult::executed;
  case 0x30815: // $8815 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8F55,0x8818);return StepResult::executed;
  case 0x30818: // $8818 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0x8819);return StepResult::executed;
  case 0x309E2: // $89E2 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x01BE,0x89E5);return StepResult::executed;
  case 0x309E5: // $89E5 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x89FE,0x89E7);return StepResult::executed;
  case 0x309FE: // $89FE opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0x8A00);return StepResult::executed;
  case 0x30A00: // $8A00 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x01BF,0x8A03);return StepResult::executed;
  case 0x30A03: // $8A03 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x06DD,0x8A06);return StepResult::executed;
  case 0x30A06: // $8A06 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x8A1F,0x8A08);return StepResult::executed;
  case 0x30A1F: // $8A1F opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x002D,0x8A21);return StepResult::executed;
  case 0x30A21: // $8A21 opcode $CD, TRACE_EXECUTED
   cpu.exec<Op::CMP,Mode::abs>(0x0185,0x8A24);return StepResult::executed;
  case 0x30A24: // $8A24 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x8A29,0x8A26);return StepResult::executed;
  case 0x30A29: // $8A29 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x017C,0x8A2C);return StepResult::executed;
  case 0x30A2C: // $8A2C opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x8A31,0x8A2E);return StepResult::executed;
  case 0x30A31: // $8A31 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x4015,0x8A34);return StepResult::executed;
  case 0x30A34: // $8A34 opcode $29, TRACE_EXECUTED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0x8A36);return StepResult::executed;
  case 0x30A36: // $8A36 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0x8A3D,0x8A38);return StepResult::executed;
  case 0x30A38: // $8A38 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0x8A3A);return StepResult::executed;
  case 0x30A3A: // $8A3A opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x019E,0x8A3D);return StepResult::executed;
  case 0x30A3D: // $8A3D opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0x8A3F);return StepResult::executed;
  case 0x30A3F: // $8A3F opcode $A0, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0x8A41);return StepResult::executed;
  case 0x30A41: // $8A41 opcode $86, TRACE_EXECUTED
   cpu.exec<Op::STX,Mode::zp>(0x00EE,0x8A43);return StepResult::executed;
  case 0x30A43: // $8A43 opcode $8C, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::abs>(0x01BC,0x8A46);return StepResult::executed;
  case 0x30A46: // $8A46 opcode $BD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::absx>(0x0109,0x8A49);return StepResult::executed;
  case 0x30A49: // $8A49 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x8A4E,0x8A4B);return StepResult::executed;
  case 0x30A4E: // $8A4E opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0x8A4F);return StepResult::executed;
  case 0x30A4F: // $8A4F opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x0009,0x8A51);return StepResult::executed;
  case 0x30A51: // $8A51 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x8A5A,0x8A53);return StepResult::executed;
  case 0x30A53: // $8A53 opcode $BD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::absx>(0x8A5B,0x8A56);return StepResult::executed;
  case 0x30A56: // $8A56 opcode $A8, TRACE_EXECUTED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0x8A57);return StepResult::executed;
  case 0x30A57: // $8A57 opcode $4C, TRACE_EXECUTED
   cpu.exec<Op::JMP,Mode::abs>(0x8A41,0x8A5A);return StepResult::executed;
  case 0x30A5A: // $8A5A opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0x8A5B);return StepResult::executed;
  case 0x30F55: // $8F55 opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F56);return StepResult::executed;
  case 0x30F56: // $8F56 opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F57);return StepResult::executed;
  case 0x30F57: // $8F57 opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F58);return StepResult::executed;
  case 0x30F58: // $8F58 opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F59);return StepResult::executed;
  case 0x30F59: // $8F59 opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F5A);return StepResult::executed;
  case 0x30F5A: // $8F5A opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F5B);return StepResult::executed;
  case 0x30F5B: // $8F5B opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F5C);return StepResult::executed;
  case 0x30F5C: // $8F5C opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F5D);return StepResult::executed;
  case 0x30F5D: // $8F5D opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F5E);return StepResult::executed;
  case 0x30F5E: // $8F5E opcode $EA, TRACE_EXECUTED
   cpu.exec<Op::NOP,Mode::imp>(0x0000,0x8F5F);return StepResult::executed;
  case 0x30F5F: // $8F5F opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0x8F60);return StepResult::executed;
  case 0x34001: // $8001 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0x8003);return StepResult::executed;
  case 0x34003: // $8003 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0005,0x8005);return StepResult::executed;
  case 0x34005: // $8005 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0040,0x8007);return StepResult::executed;
  case 0x34007: // $8007 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0007,0x8009);return StepResult::executed;
  case 0x34009: // $8009 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0022,0x800B);return StepResult::executed;
  case 0x3400B: // $800B opcode $18, TRACE_EXECUTED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0x800C);return StepResult::executed;
  case 0x3400C: // $800C opcode $69, TRACE_EXECUTED
   cpu.exec<Op::ADC,Mode::imm>(0x0044,0x800E);return StepResult::executed;
  case 0x3400E: // $800E opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0022,0x8010);return StepResult::executed;
  case 0x34010: // $8010 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0004,0x8012);return StepResult::executed;
  case 0x34012: // $8012 opcode $A6, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::zp>(0x0005,0x8014);return StepResult::executed;
  case 0x34014: // $8014 opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x001C,0x8016);return StepResult::executed;
  case 0x34016: // $8016 opcode $B0, TRACE_EXECUTED
   cpu.exec<Op::BCS,Mode::rel>(0x8038,0x8018);return StepResult::executed;
  case 0x34018: // $8018 opcode $BD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::absx>(0x0400,0x801B);return StepResult::executed;
  case 0x3401B: // $801B opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0x8034,0x801D);return StepResult::executed;
  case 0x34034: // $8034 opcode $E6, TRACE_EXECUTED
   cpu.exec<Op::INC,Mode::zp>(0x0005,0x8036);return StepResult::executed;
  case 0x34036: // $8036 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0x8012,0x8038);return StepResult::executed;
  case 0x34038: // $8038 opcode $A6, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::zp>(0x0004,0x803A);return StepResult::executed;
  case 0x3403A: // $803A opcode $A4, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::zp>(0x0007,0x803C);return StepResult::executed;
  case 0x3403C: // $803C opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x00F4,0x803E);return StepResult::executed;
  case 0x3403E: // $803E opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0200,0x8041);return StepResult::executed;
  case 0x34041: // $8041 opcode $8A, TRACE_EXECUTED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0x8042);return StepResult::executed;
  case 0x34042: // $8042 opcode $18, TRACE_EXECUTED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0x8043);return StepResult::executed;
  case 0x34043: // $8043 opcode $69, TRACE_EXECUTED
   cpu.exec<Op::ADC,Mode::imm>(0x00C4,0x8045);return StepResult::executed;
  case 0x34045: // $8045 opcode $AA, TRACE_EXECUTED
   cpu.exec<Op::TAX,Mode::imp>(0x0000,0x8046);return StepResult::executed;
  case 0x34046: // $8046 opcode $88, TRACE_EXECUTED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0x8047);return StepResult::executed;
  case 0x34047: // $8047 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0x803C,0x8049);return StepResult::executed;
  case 0x34049: // $8049 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0x804A);return StepResult::executed;
  case 0x3E00B: // $E00B opcode $D8, TRACE_EXECUTED
   cpu.exec<Op::CLD,Mode::imp>(0x0000,0xE00C);return StepResult::executed;
  case 0x3E00C: // $E00C opcode $78, TRACE_EXECUTED
   cpu.exec<Op::SEI,Mode::imp>(0x0000,0xE00D);return StepResult::executed;
  case 0x3E00D: // $E00D opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x2002,0xE010);return StepResult::executed;
  case 0x3E010: // $E010 opcode $10, TRACE_EXECUTED
   cpu.exec<Op::BPL,Mode::rel>(0xE00D,0xE012);return StepResult::executed;
  case 0x3E012: // $E012 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x2002,0xE015);return StepResult::executed;
  case 0x3E015: // $E015 opcode $10, TRACE_EXECUTED
   cpu.exec<Op::BPL,Mode::rel>(0xE012,0xE017);return StepResult::executed;
  case 0x3E017: // $E017 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x00FF,0xE019);return StepResult::executed;
  case 0x3E019: // $E019 opcode $9A, TRACE_EXECUTED
   cpu.exec<Op::TXS,Mode::imp>(0x0000,0xE01A);return StepResult::executed;
  case 0x3E01A: // $E01A opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE16C,0xE01D);return StepResult::executed;
  case 0x3E01D: // $E01D opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE151,0xE020);return StepResult::executed;
  case 0x3E020: // $E020 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE021);return StepResult::executed;
  case 0x3E021: // $E021 opcode $8A, TRACE_EXECUTED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0xE022);return StepResult::executed;
  case 0x3E022: // $E022 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0000,0xE024);return StepResult::executed;
  case 0x3E024: // $E024 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0001,0xE026);return StepResult::executed;
  case 0x3E026: // $E026 opcode $A0, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xE028);return StepResult::executed;
  case 0x3E028: // $E028 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0008,0xE02A);return StepResult::executed;
  case 0x3E02A: // $E02A opcode $91, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::indy>(0x0000,0xE02C);return StepResult::executed;
  case 0x3E02C: // $E02C opcode $C8, TRACE_EXECUTED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xE02D);return StepResult::executed;
  case 0x3E02D: // $E02D opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE02A,0xE02F);return StepResult::executed;
  case 0x3E02F: // $E02F opcode $E6, TRACE_EXECUTED
   cpu.exec<Op::INC,Mode::zp>(0x0001,0xE031);return StepResult::executed;
  case 0x3E031: // $E031 opcode $E4, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::zp>(0x0001,0xE033);return StepResult::executed;
  case 0x3E033: // $E033 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE02A,0xE035);return StepResult::executed;
  case 0x3E035: // $E035 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE037);return StepResult::executed;
  case 0x3E037: // $E037 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x9003,0xE03A);return StepResult::executed;
  case 0x3E03A: // $E03A opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE211,0xE03D);return StepResult::executed;
  case 0x3E03D: // $E03D opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE15C,0xE040);return StepResult::executed;
  case 0x3E040: // $E040 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0020,0xE042);return StepResult::executed;
  case 0x3E042: // $E042 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0021,0xE044);return StepResult::executed;
  case 0x3E044: // $E044 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xB003,0xE047);return StepResult::executed;
  case 0x3E047: // $E047 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE2C4,0xE04A);return StepResult::executed;
  case 0x3E04A: // $E04A opcode $58, TRACE_EXECUTED
   cpu.exec<Op::CLI,Mode::imp>(0x0000,0xE04B);return StepResult::executed;
  case 0x3E057: // $E057 opcode $48, TRACE_EXECUTED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xE058);return StepResult::executed;
  case 0x3E058: // $E058 opcode $8A, TRACE_EXECUTED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0xE059);return StepResult::executed;
  case 0x3E059: // $E059 opcode $48, TRACE_EXECUTED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xE05A);return StepResult::executed;
  case 0x3E05A: // $E05A opcode $98, TRACE_EXECUTED
   cpu.exec<Op::TYA,Mode::imp>(0x0000,0xE05B);return StepResult::executed;
  case 0x3E05B: // $E05B opcode $48, TRACE_EXECUTED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xE05C);return StepResult::executed;
  case 0x3E05C: // $E05C opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x2002,0xE05F);return StepResult::executed;
  case 0x3E05F: // $E05F opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0041,0xE061);return StepResult::executed;
  case 0x3E061: // $E061 opcode $49, TRACE_EXECUTED
   cpu.exec<Op::EOR,Mode::imm>(0x00FF,0xE063);return StepResult::executed;
  case 0x3E063: // $E063 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xF000,0xE066);return StepResult::executed;
  case 0x3E066: // $E066 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0040,0xE068);return StepResult::executed;
  case 0x3E068: // $E068 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xF001,0xE06B);return StepResult::executed;
  case 0x3E06B: // $E06B opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0042,0xE06D);return StepResult::executed;
  case 0x3E06D: // $E06D opcode $49, TRACE_EXECUTED
   cpu.exec<Op::EOR,Mode::imm>(0x00FF,0xE06F);return StepResult::executed;
  case 0x3E06F: // $E06F opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xF000,0xE072);return StepResult::executed;
  case 0x3E072: // $E072 opcode $58, TRACE_EXECUTED
   cpu.exec<Op::CLI,Mode::imp>(0x0000,0xE073);return StepResult::executed;
  case 0x3E073: // $E073 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0043,0xE075);return StepResult::executed;
  case 0x3E075: // $E075 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x006A,0xE077);return StepResult::executed;
  case 0x3E077: // $E077 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0021,0xE079);return StepResult::executed;
  case 0x3E079: // $E079 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xB003,0xE07C);return StepResult::executed;
  case 0x3E07C: // $E07C opcode $A4, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::zp>(0x001C,0xE07E);return StepResult::executed;
  case 0x3E07E: // $E07E opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE0D7,0xE080);return StepResult::executed;
  case 0x3E080: // $E080 opcode $E6, TRACE_EXECUTED
   cpu.exec<Op::INC,Mode::zp>(0x001C,0xE082);return StepResult::executed;
  case 0x3E082: // $E082 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE084);return StepResult::executed;
  case 0x3E084: // $E084 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2003,0xE087);return StepResult::executed;
  case 0x3E087: // $E087 opcode $A0, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::imm>(0x0002,0xE089);return StepResult::executed;
  case 0x3E089: // $E089 opcode $8C, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::abs>(0x4014,0xE08C);return StepResult::executed;
  case 0x3E08C: // $E08C opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE16C,0xE08F);return StepResult::executed;
  case 0x3E08F: // $E08F opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xED46,0xE092);return StepResult::executed;
  case 0x3E092: // $E092 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FE,0xE094);return StepResult::executed;
  case 0x3E094: // $E094 opcode $A6, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::zp>(0x001D,0xE096);return StepResult::executed;
  case 0x3E096: // $E096 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0xE09E,0xE098);return StepResult::executed;
  case 0x3E098: // $E098 opcode $C6, TRACE_EXECUTED
   cpu.exec<Op::DEC,Mode::zp>(0x001D,0xE09A);return StepResult::executed;
  case 0x3E09A: // $E09A opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0xE09E,0xE09C);return StepResult::executed;
  case 0x3E09C: // $E09C opcode $29, TRACE_EXECUTED
   cpu.exec<Op::AND,Mode::imm>(0x00E7,0xE09E);return StepResult::executed;
  case 0x3E09E: // $E09E opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2001,0xE0A1);return StepResult::executed;
  case 0x3E0A1: // $E0A1 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE131,0xE0A4);return StepResult::executed;
  case 0x3E0A4: // $E0A4 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D6,0xE0A7);return StepResult::executed;
  case 0x3E0A7: // $E0A7 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0072,0xE0A9);return StepResult::executed;
  case 0x3E0A9: // $E0A9 opcode $10, TRACE_EXECUTED
   cpu.exec<Op::BPL,Mode::rel>(0xE0B1,0xE0AB);return StepResult::executed;
  case 0x3E0B1: // $E0B1 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xE0B3);return StepResult::executed;
  case 0x3E0B3: // $E0B3 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x006C,0xE0B5);return StepResult::executed;
  case 0x3E0B5: // $E0B5 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xE0B7);return StepResult::executed;
  case 0x3E0B7: // $E0B7 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x006D,0xE0B9);return StepResult::executed;
  case 0x3E0B9: // $E0B9 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE238,0xE0BC);return StepResult::executed;
  case 0x3E0BC: // $E0BC opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE264,0xE0BF);return StepResult::executed;
  case 0x3E0BF: // $E0BF opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE35C,0xE0C2);return StepResult::executed;
  case 0x3E0C2: // $E0C2 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x000D,0xE0C4);return StepResult::executed;
  case 0x3E0C4: // $E0C4 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE0C7);return StepResult::executed;
  case 0x3E0C7: // $E0C7 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xE0CA);return StepResult::executed;
  case 0x3E0CA: // $E0CA opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE0CC);return StepResult::executed;
  case 0x3E0CC: // $E0CC opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xEC72,0xE0CF);return StepResult::executed;
  case 0x3E0CF: // $E0CF opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x001C,0xE0D1);return StepResult::executed;
  case 0x3E0D1: // $E0D1 opcode $68, TRACE_EXECUTED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xE0D2);return StepResult::executed;
  case 0x3E0D2: // $E0D2 opcode $A8, TRACE_EXECUTED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xE0D3);return StepResult::executed;
  case 0x3E0D3: // $E0D3 opcode $68, TRACE_EXECUTED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xE0D4);return StepResult::executed;
  case 0x3E0D4: // $E0D4 opcode $AA, TRACE_EXECUTED
   cpu.exec<Op::TAX,Mode::imp>(0x0000,0xE0D5);return StepResult::executed;
  case 0x3E0D5: // $E0D5 opcode $68, TRACE_EXECUTED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xE0D6);return StepResult::executed;
  case 0x3E0D6: // $E0D6 opcode $40, TRACE_EXECUTED
   cpu.exec<Op::RTI,Mode::imp>(0x0000,0xE0D7);return StepResult::executed;
  case 0x3E131: // $E131 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x2002,0xE134);return StepResult::executed;
  case 0x3E134: // $E134 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0020,0xE136);return StepResult::executed;
  case 0x3E136: // $E136 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2006,0xE139);return StepResult::executed;
  case 0x3E139: // $E139 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE13B);return StepResult::executed;
  case 0x3E13B: // $E13B opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2006,0xE13E);return StepResult::executed;
  case 0x3E13E: // $E13E opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x2002,0xE141);return StepResult::executed;
  case 0x3E141: // $E141 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FD,0xE143);return StepResult::executed;
  case 0x3E143: // $E143 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2005,0xE146);return StepResult::executed;
  case 0x3E146: // $E146 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FC,0xE148);return StepResult::executed;
  case 0x3E148: // $E148 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2005,0xE14B);return StepResult::executed;
  case 0x3E14B: // $E14B opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FF,0xE14D);return StepResult::executed;
  case 0x3E14D: // $E14D opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2000,0xE150);return StepResult::executed;
  case 0x3E150: // $E150 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE151);return StepResult::executed;
  case 0x3E151: // $E151 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x000F,0xE153);return StepResult::executed;
  case 0x3E153: // $E153 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4015,0xE156);return StepResult::executed;
  case 0x3E156: // $E156 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x00C0,0xE158);return StepResult::executed;
  case 0x3E158: // $E158 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x4017,0xE15B);return StepResult::executed;
  case 0x3E15B: // $E15B opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE15C);return StepResult::executed;
  case 0x3E15C: // $E15C opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x00B0,0xE15E);return StepResult::executed;
  case 0x3E15E: // $E15E opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x00FF,0xE160);return StepResult::executed;
  case 0x3E160: // $E160 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2000,0xE163);return StepResult::executed;
  case 0x3E163: // $E163 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x001E,0xE165);return StepResult::executed;
  case 0x3E165: // $E165 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x00FE,0xE167);return StepResult::executed;
  case 0x3E167: // $E167 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0005,0xE169);return StepResult::executed;
  case 0x3E169: // $E169 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xE16B);return StepResult::executed;
  case 0x3E16B: // $E16B opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE16C);return StepResult::executed;
  case 0x3E16C: // $E16C opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FF,0xE16E);return StepResult::executed;
  case 0x3E16E: // $E16E opcode $29, TRACE_EXECUTED
   cpu.exec<Op::AND,Mode::imm>(0x007F,0xE170);return StepResult::executed;
  case 0x3E170: // $E170 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2000,0xE173);return StepResult::executed;
  case 0x3E173: // $E173 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE175);return StepResult::executed;
  case 0x3E175: // $E175 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2006,0xE178);return StepResult::executed;
  case 0x3E178: // $E178 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2006,0xE17B);return StepResult::executed;
  case 0x3E17B: // $E17B opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FE,0xE17D);return StepResult::executed;
  case 0x3E17D: // $E17D opcode $29, TRACE_EXECUTED
   cpu.exec<Op::AND,Mode::imm>(0x00E7,0xE17F);return StepResult::executed;
  case 0x3E17F: // $E17F opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2001,0xE182);return StepResult::executed;
  case 0x3E182: // $E182 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE183);return StepResult::executed;
  case 0x3E211: // $E211 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xE213);return StepResult::executed;
  case 0x3E213: // $E213 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0026,0xE215);return StepResult::executed;
  case 0x3E215: // $E215 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0023,0xE217);return StepResult::executed;
  case 0x3E217: // $E217 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0025,0xE219);return StepResult::executed;
  case 0x3E219: // $E219 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xE21B);return StepResult::executed;
  case 0x3E21B: // $E21B opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE21E);return StepResult::executed;
  case 0x3E21E: // $E21E opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x87AE,0xE221);return StepResult::executed;
  case 0x3E221: // $E221 opcode $4C, TRACE_EXECUTED
   cpu.exec<Op::JMP,Mode::abs>(0xE25B,0xE224);return StepResult::executed;
  case 0x3E238: // $E238 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xE23A);return StepResult::executed;
  case 0x3E23A: // $E23A opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0026,0xE23C);return StepResult::executed;
  case 0x3E23C: // $E23C opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xE23E);return StepResult::executed;
  case 0x3E23E: // $E23E opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE241);return StepResult::executed;
  case 0x3E241: // $E241 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0x89E2,0xE244);return StepResult::executed;
  case 0x3E244: // $E244 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE246);return StepResult::executed;
  case 0x3E246: // $E246 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0026,0xE248);return StepResult::executed;
  case 0x3E248: // $E248 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE249);return StepResult::executed;
  case 0x3E25B: // $E25B opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE25D);return StepResult::executed;
  case 0x3E25D: // $E25D opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0026,0xE25F);return StepResult::executed;
  case 0x3E25F: // $E25F opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0025,0xE261);return StepResult::executed;
  case 0x3E261: // $E261 opcode $4C, TRACE_EXECUTED
   cpu.exec<Op::JMP,Mode::abs>(0xE2D0,0xE264);return StepResult::executed;
  case 0x3E264: // $E264 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0xE266);return StepResult::executed;
  case 0x3E266: // $E266 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE29B,0xE269);return StepResult::executed;
  case 0x3E269: // $E269 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0002,0xE26B);return StepResult::executed;
  case 0x3E26B: // $E26B opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE29B,0xE26E);return StepResult::executed;
  case 0x3E26E: // $E26E opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0000,0xE270);return StepResult::executed;
  case 0x3E270: // $E270 opcode $C5, TRACE_EXECUTED
   cpu.exec<Op::CMP,Mode::zp>(0x0002,0xE272);return StepResult::executed;
  case 0x3E272: // $E272 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE290,0xE274);return StepResult::executed;
  case 0x3E274: // $E274 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0001,0xE276);return StepResult::executed;
  case 0x3E276: // $E276 opcode $C5, TRACE_EXECUTED
   cpu.exec<Op::CMP,Mode::zp>(0x0003,0xE278);return StepResult::executed;
  case 0x3E278: // $E278 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE290,0xE27A);return StepResult::executed;
  case 0x3E27A: // $E27A opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0xE27C);return StepResult::executed;
  case 0x3E27C: // $E27C opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE280,0xE27F);return StepResult::executed;
  case 0x3E27F: // $E27F opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE280);return StepResult::executed;
  case 0x3E280: // $E280 opcode $B5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zpx>(0x0000,0xE282);return StepResult::executed;
  case 0x3E282: // $E282 opcode $A8, TRACE_EXECUTED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xE283);return StepResult::executed;
  case 0x3E283: // $E283 opcode $55, TRACE_EXECUTED
   cpu.exec<Op::EOR,Mode::zpx>(0x00FA,0xE285);return StepResult::executed;
  case 0x3E285: // $E285 opcode $35, TRACE_EXECUTED
   cpu.exec<Op::AND,Mode::zpx>(0x0000,0xE287);return StepResult::executed;
  case 0x3E287: // $E287 opcode $95, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zpx>(0x0028,0xE289);return StepResult::executed;
  case 0x3E289: // $E289 opcode $95, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zpx>(0x00F8,0xE28B);return StepResult::executed;
  case 0x3E28B: // $E28B opcode $94, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::zpx>(0x002A,0xE28D);return StepResult::executed;
  case 0x3E28D: // $E28D opcode $94, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::zpx>(0x00FA,0xE28F);return StepResult::executed;
  case 0x3E28F: // $E28F opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE290);return StepResult::executed;
  case 0x3E29B: // $E29B opcode $A0, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::imm>(0x0001,0xE29D);return StepResult::executed;
  case 0x3E29D: // $E29D opcode $8C, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::abs>(0x4016,0xE2A0);return StepResult::executed;
  case 0x3E2A0: // $E2A0 opcode $88, TRACE_EXECUTED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xE2A1);return StepResult::executed;
  case 0x3E2A1: // $E2A1 opcode $8C, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::abs>(0x4016,0xE2A4);return StepResult::executed;
  case 0x3E2A4: // $E2A4 opcode $A0, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::imm>(0x0008,0xE2A6);return StepResult::executed;
  case 0x3E2A6: // $E2A6 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x4016,0xE2A9);return StepResult::executed;
  case 0x3E2A9: // $E2A9 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0004,0xE2AB);return StepResult::executed;
  case 0x3E2AB: // $E2AB opcode $4A, TRACE_EXECUTED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xE2AC);return StepResult::executed;
  case 0x3E2AC: // $E2AC opcode $05, TRACE_EXECUTED
   cpu.exec<Op::ORA,Mode::zp>(0x0004,0xE2AE);return StepResult::executed;
  case 0x3E2AE: // $E2AE opcode $4A, TRACE_EXECUTED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xE2AF);return StepResult::executed;
  case 0x3E2AF: // $E2AF opcode $36, TRACE_EXECUTED
   cpu.exec<Op::ROL,Mode::zpx>(0x0000,0xE2B1);return StepResult::executed;
  case 0x3E2B1: // $E2B1 opcode $AD, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::abs>(0x4017,0xE2B4);return StepResult::executed;
  case 0x3E2B4: // $E2B4 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0005,0xE2B6);return StepResult::executed;
  case 0x3E2B6: // $E2B6 opcode $4A, TRACE_EXECUTED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xE2B7);return StepResult::executed;
  case 0x3E2B7: // $E2B7 opcode $05, TRACE_EXECUTED
   cpu.exec<Op::ORA,Mode::zp>(0x0005,0xE2B9);return StepResult::executed;
  case 0x3E2B9: // $E2B9 opcode $4A, TRACE_EXECUTED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xE2BA);return StepResult::executed;
  case 0x3E2BA: // $E2BA opcode $36, TRACE_EXECUTED
   cpu.exec<Op::ROL,Mode::zpx>(0x0001,0xE2BC);return StepResult::executed;
  case 0x3E2BC: // $E2BC opcode $88, TRACE_EXECUTED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xE2BD);return StepResult::executed;
  case 0x3E2BD: // $E2BD opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE2A6,0xE2BF);return StepResult::executed;
  case 0x3E2BF: // $E2BF opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE2C0);return StepResult::executed;
  case 0x3E2C4: // $E2C4 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x001E,0xE2C6);return StepResult::executed;
  case 0x3E2C6: // $E2C6 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xC000,0xE2C9);return StepResult::executed;
  case 0x3E2C9: // $E2C9 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE2CA);return StepResult::executed;
  case 0x3E2D0: // $E2D0 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0023,0xE2D2);return StepResult::executed;
  case 0x3E2D2: // $E2D2 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x8000,0xE2D5);return StepResult::executed;
  case 0x3E2D5: // $E2D5 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE2D6);return StepResult::executed;
  case 0x3E2D6: // $E2D6 opcode $A4, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::zp>(0x006F,0xE2D8);return StepResult::executed;
  case 0x3E2D8: // $E2D8 opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0xE2E6,0xE2DA);return StepResult::executed;
  case 0x3E2E6: // $E2E6 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE32B,0xE2E9);return StepResult::executed;
  case 0x3E2E9: // $E2E9 opcode $4C, TRACE_EXECUTED
   cpu.exec<Op::JMP,Mode::abs>(0xE347,0xE2EC);return StepResult::executed;
  case 0x3E32B: // $E32B opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE331,0xE32E);return StepResult::executed;
  case 0x3E32E: // $E32E opcode $4C, TRACE_EXECUTED
   cpu.exec<Op::JMP,Mode::abs>(0xE33C,0xE331);return StepResult::executed;
  case 0x3E331: // $E331 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x003A,0xE333);return StepResult::executed;
  case 0x3E333: // $E333 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xD002,0xE336);return StepResult::executed;
  case 0x3E336: // $E336 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x003B,0xE338);return StepResult::executed;
  case 0x3E338: // $E338 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xD003,0xE33B);return StepResult::executed;
  case 0x3E33B: // $E33B opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE33C);return StepResult::executed;
  case 0x3E33C: // $E33C opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0038,0xE33E);return StepResult::executed;
  case 0x3E33E: // $E33E opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xD000,0xE341);return StepResult::executed;
  case 0x3E341: // $E341 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0039,0xE343);return StepResult::executed;
  case 0x3E343: // $E343 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xD001,0xE346);return StepResult::executed;
  case 0x3E346: // $E346 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE347);return StepResult::executed;
  case 0x3E347: // $E347 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x003C,0xE349);return StepResult::executed;
  case 0x3E349: // $E349 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xE000,0xE34C);return StepResult::executed;
  case 0x3E34C: // $E34C opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x003F,0xE34E);return StepResult::executed;
  case 0x3E34E: // $E34E opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xE003,0xE351);return StepResult::executed;
  case 0x3E351: // $E351 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x003D,0xE353);return StepResult::executed;
  case 0x3E353: // $E353 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xE001,0xE356);return StepResult::executed;
  case 0x3E356: // $E356 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x003E,0xE358);return StepResult::executed;
  case 0x3E358: // $E358 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0xE002,0xE35B);return StepResult::executed;
  case 0x3E35B: // $E35B opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE35C);return StepResult::executed;
  case 0x3E35C: // $E35C opcode $E6, TRACE_EXECUTED
   cpu.exec<Op::INC,Mode::zp>(0x001B,0xE35E);return StepResult::executed;
  case 0x3E35E: // $E35E opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x0018,0xE360);return StepResult::executed;
  case 0x3E360: // $E360 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE7FB,0xE363);return StepResult::executed;
  case 0x3E383: // $E383 opcode $A6, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::zp>(0x0019,0xE385);return StepResult::executed;
  case 0x3E385: // $E385 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE394,0xE387);return StepResult::executed;
  case 0x3E387: // $E387 opcode $86, TRACE_EXECUTED
   cpu.exec<Op::STX,Mode::zp>(0x001F,0xE389);return StepResult::executed;
  case 0x3E389: // $E389 opcode $20, TRACE_EXECUTED
   cpu.exec<Op::JSR,Mode::abs>(0xE7B2,0xE38C);return StepResult::executed;
  case 0x3E38C: // $E38C opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE38E);return StepResult::executed;
  case 0x3E38E: // $E38E opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x07EC,0xE391);return StepResult::executed;
  case 0x3E391: // $E391 opcode $E6, TRACE_EXECUTED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE393);return StepResult::executed;
  case 0x3E393: // $E393 opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE394);return StepResult::executed;
  case 0x3E394: // $E394 opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xE395);return StepResult::executed;
  case 0x3E395: // $E395 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE3A8,0xE397);return StepResult::executed;
  case 0x3E397: // $E397 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xE399);return StepResult::executed;
  case 0x3E399: // $E399 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE39C);return StepResult::executed;
  case 0x3E39C: // $E39C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xA9D5,0xE39F);return StepResult::executed;
  case 0x3E39F: // $E39F opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xE3A1);return StepResult::executed;
  case 0x3E3A1: // $E3A1 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0030,0xE3A3);return StepResult::executed;
  case 0x3E3A3: // $E3A3 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE3A7,0xE3A5);return StepResult::executed;
  case 0x3E3A5: // $E3A5 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE3A7);return StepResult::executed;
  case 0x3E3A7: // $E3A7 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE3A8);return StepResult::executed;
  case 0x3E3A8: // $E3A8 opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xE3A9);return StepResult::executed;
  case 0x3E3A9: // $E3A9 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE3CC,0xE3AB);return StepResult::executed;
  case 0x3E3AB: // $E3AB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7B2,0xE3AE);return StepResult::executed;
  case 0x3E3AE: // $E3AE opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xE3B0);return StepResult::executed;
  case 0x3E3B0: // $E3B0 opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0038,0xE3B2);return StepResult::executed;
  case 0x3E3B2: // $E3B2 opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xE3B3);return StepResult::executed;
  case 0x3E3B3: // $E3B3 opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0039,0xE3B5);return StepResult::executed;
  case 0x3E3B5: // $E3B5 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0070,0xE3B7);return StepResult::executed;
  case 0x3E3B7: // $E3B7 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003C,0xE3B9);return StepResult::executed;
  case 0x3E3B9: // $E3B9 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0041,0xE3BB);return StepResult::executed;
  case 0x3E3BB: // $E3BB opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003D,0xE3BD);return StepResult::executed;
  case 0x3E3BD: // $E3BD opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0071,0xE3BF);return StepResult::executed;
  case 0x3E3BF: // $E3BF opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003E,0xE3C1);return StepResult::executed;
  case 0x3E3C1: // $E3C1 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0072,0xE3C3);return StepResult::executed;
  case 0x3E3C3: // $E3C3 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003F,0xE3C5);return StepResult::executed;
  case 0x3E3C5: // $E3C5 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE3C7);return StepResult::executed;
  case 0x3E3C7: // $E3C7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0020,0xE3C9);return StepResult::executed;
  case 0x3E3C9: // $E3C9 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0021,0xE3CB);return StepResult::executed;
  case 0x3E3CB: // $E3CB opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE3CC);return StepResult::executed;
  case 0x3E3CC: // $E3CC opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xE3CD);return StepResult::executed;
  case 0x3E3CD: // $E3CD opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE3E2,0xE3CF);return StepResult::executed;
  case 0x3E3CF: // $E3CF opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEB44,0xE3D2);return StepResult::executed;
  case 0x3E3D2: // $E3D2 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE56E,0xE3D5);return StepResult::executed;
  case 0x3E3D5: // $E3D5 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE3D7);return StepResult::executed;
  case 0x3E3D7: // $E3D7 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE3D8);return StepResult::executed;
  case 0x3E3D8: // $E3D8 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE3DA);return StepResult::executed;
  case 0x3E3DA: // $E3DA opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE558,0xE3DD);return StepResult::executed;
  case 0x3E3DD: // $E3DD opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000F,0xE3DF);return StepResult::executed;
  case 0x3E3DF: // $E3DF opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE558,0xE3E2);return StepResult::executed;
  case 0x3E3E2: // $E3E2 opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xE3E3);return StepResult::executed;
  case 0x3E3E3: // $E3E3 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE416,0xE3E5);return StepResult::executed;
  case 0x3E3E5: // $E3E5 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE55D,0xE3E8);return StepResult::executed;
  case 0x3E3E8: // $E3E8 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE3D8,0xE3EA);return StepResult::executed;
  case 0x3E3EA: // $E3EA opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE3EC);return StepResult::executed;
  case 0x3E3EC: // $E3EC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE3EF);return StepResult::executed;
  case 0x3E3EF: // $E3EF opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8A8A,0xE3F2);return StepResult::executed;
  case 0x3E3F2: // $E3F2 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xE3F4);return StepResult::executed;
  case 0x3E3F4: // $E3F4 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0020,0xE3F6);return StepResult::executed;
  case 0x3E3F6: // $E3F6 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE403,0xE3F8);return StepResult::executed;
  case 0x3E3F8: // $E3F8 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0074,0xE3FA);return StepResult::executed;
  case 0x3E3FA: // $E3FA opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE249,0xE3FD);return StepResult::executed;
  case 0x3E3FD: // $E3FD opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0068,0xE3FF);return StepResult::executed;
  case 0x3E3FF: // $E3FF opcode $49, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::imm>(0x0001,0xE401);return StepResult::executed;
  case 0x3E401: // $E401 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xE403);return StepResult::executed;
  case 0x3E403: // $E403 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xE405);return StepResult::executed;
  case 0x3E405: // $E405 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0xE407);return StepResult::executed;
  case 0x3E407: // $E407 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE415,0xE409);return StepResult::executed;
  case 0x3E409: // $E409 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002A,0xE40B);return StepResult::executed;
  case 0x3E40B: // $E40B opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00C0,0xE40D);return StepResult::executed;
  case 0x3E40D: // $E40D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE3DD,0xE40F);return StepResult::executed;
  case 0x3E40F: // $E40F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0080,0xE411);return StepResult::executed;
  case 0x3E411: // $E411 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0032,0xE413);return StepResult::executed;
  case 0x3E413: // $E413 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE415);return StepResult::executed;
  case 0x3E415: // $E415 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE416);return StepResult::executed;
  case 0x3E416: // $E416 opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x0068,0xE418);return StepResult::executed;
  case 0x3E418: // $E418 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0032,0xE41A);return StepResult::executed;
  case 0x3E41A: // $E41A opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0008,0xE41C);return StepResult::executed;
  case 0x3E41C: // $E41C opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE425,0xE41E);return StepResult::executed;
  case 0x3E41E: // $E41E opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xE434,0xE421);return StepResult::executed;
  case 0x3E421: // $E421 opcode $09, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::imm>(0x0080,0xE423);return StepResult::executed;
  case 0x3E423: // $E423 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE428,0xE425);return StepResult::executed;
  case 0x3E425: // $E425 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xE434,0xE428);return StepResult::executed;
  case 0x3E428: // $E428 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEC54,0xE42B);return StepResult::executed;
  case 0x3E42B: // $E42B opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0032,0xE42D);return StepResult::executed;
  case 0x3E42D: // $E42D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE415,0xE42F);return StepResult::executed;
  case 0x3E42F: // $E42F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xE431);return StepResult::executed;
  case 0x3E431: // $E431 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE558,0xE434);return StepResult::executed;
  case 0x3E436: // $E436 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE437);return StepResult::executed;
  case 0x3E437: // $E437 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0068,0xE439);return StepResult::executed;
  case 0x3E439: // $E439 opcode $48, HISTORICALLY_VERIFIED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xE43A);return StepResult::executed;
  case 0x3E43A: // $E43A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7B2,0xE43D);return StepResult::executed;
  case 0x3E43D: // $E43D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE43F);return StepResult::executed;
  case 0x3E43F: // $E43F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001F,0xE441);return StepResult::executed;
  case 0x3E441: // $E441 opcode $68, HISTORICALLY_VERIFIED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xE442);return StepResult::executed;
  case 0x3E442: // $E442 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xE444);return StepResult::executed;
  case 0x3E444: // $E444 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xE446);return StepResult::executed;
  case 0x3E446: // $E446 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE558,0xE449);return StepResult::executed;
  case 0x3E449: // $E449 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE44B);return StepResult::executed;
  case 0x3E44B: // $E44B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xE44D);return StepResult::executed;
  case 0x3E44D: // $E44D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7B6,0xE450);return StepResult::executed;
  case 0x3E450: // $E450 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE710,0xE453);return StepResult::executed;
  case 0x3E453: // $E453 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE63D,0xE456);return StepResult::executed;
  case 0x3E456: // $E456 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE551,0xE459);return StepResult::executed;
  case 0x3E459: // $E459 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xE45B);return StepResult::executed;
  case 0x3E45B: // $E45B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xE45D);return StepResult::executed;
  case 0x3E45D: // $E45D opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x0019,0xE45F);return StepResult::executed;
  case 0x3E45F: // $E45F opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE464,0xE461);return StepResult::executed;
  case 0x3E461: // $E461 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE463);return StepResult::executed;
  case 0x3E463: // $E463 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE464);return StepResult::executed;
  case 0x3E464: // $E464 opcode $88, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xE465);return StepResult::executed;
  case 0x3E465: // $E465 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE47F,0xE467);return StepResult::executed;
  case 0x3E467: // $E467 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7A7,0xE46A);return StepResult::executed;
  case 0x3E46A: // $E46A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE63D,0xE46D);return StepResult::executed;
  case 0x3E46D: // $E46D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEB82,0xE470);return StepResult::executed;
  case 0x3E470: // $E470 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0037,0xE472);return StepResult::executed;
  case 0x3E472: // $E472 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE496,0xE474);return StepResult::executed;
  case 0x3E474: // $E474 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xE476);return StepResult::executed;
  case 0x3E476: // $E476 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE479);return StepResult::executed;
  case 0x3E479: // $E479 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8957,0xE47C);return StepResult::executed;
  case 0x3E47C: // $E47C opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE47E);return StepResult::executed;
  case 0x3E47E: // $E47E opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE47F);return StepResult::executed;
  case 0x3E47F: // $E47F opcode $88, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xE480);return StepResult::executed;
  case 0x3E480: // $E480 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE489,0xE482);return StepResult::executed;
  case 0x3E482: // $E482 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xE484);return StepResult::executed;
  case 0x3E484: // $E484 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0032,0xE486);return StepResult::executed;
  case 0x3E486: // $E486 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE488);return StepResult::executed;
  case 0x3E488: // $E488 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE489);return StepResult::executed;
  case 0x3E489: // $E489 opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0032,0xE48B);return StepResult::executed;
  case 0x3E48B: // $E48B opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE495,0xE48D);return StepResult::executed;
  case 0x3E48D: // $E48D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0004,0xE48F);return StepResult::executed;
  case 0x3E48F: // $E48F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0018,0xE491);return StepResult::executed;
  case 0x3E491: // $E491 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE493);return StepResult::executed;
  case 0x3E493: // $E493 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xE495);return StepResult::executed;
  case 0x3E495: // $E495 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE496);return StepResult::executed;
  case 0x3E496: // $E496 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0006,0xE498);return StepResult::executed;
  case 0x3E498: // $E498 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE558,0xE49B);return StepResult::executed;
  case 0x3E49B: // $E49B opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x0019,0xE49D);return StepResult::executed;
  case 0x3E49D: // $E49D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE4D5,0xE49F);return StepResult::executed;
  case 0x3E49F: // $E49F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0067,0xE4A1);return StepResult::executed;
  case 0x3E4A1: // $E4A1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE249,0xE4A4);return StepResult::executed;
  case 0x3E4A4: // $E4A4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE4A6);return StepResult::executed;
  case 0x3E4A6: // $E4A6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE4A9);return StepResult::executed;
  case 0x3E4A9: // $E4A9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8ED0,0xE4AC);return StepResult::executed;
  case 0x3E4AC: // $E4AC opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xE4AE);return StepResult::executed;
  case 0x3E4AE: // $E4AE opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0038,0xE4B0);return StepResult::executed;
  case 0x3E4B0: // $E4B0 opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xE4B1);return StepResult::executed;
  case 0x3E4B1: // $E4B1 opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0039,0xE4B3);return StepResult::executed;
  case 0x3E4B3: // $E4B3 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0040,0xE4B5);return StepResult::executed;
  case 0x3E4B5: // $E4B5 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003C,0xE4B7);return StepResult::executed;
  case 0x3E4B7: // $E4B7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0041,0xE4B9);return StepResult::executed;
  case 0x3E4B9: // $E4B9 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003D,0xE4BB);return StepResult::executed;
  case 0x3E4BB: // $E4BB opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0043,0xE4BD);return StepResult::executed;
  case 0x3E4BD: // $E4BD opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x003F,0xE4BF);return StepResult::executed;
  case 0x3E4BF: // $E4BF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0003,0xE4C1);return StepResult::executed;
  case 0x3E4C1: // $E4C1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEC54,0xE4C4);return StepResult::executed;
  case 0x3E4C4: // $E4C4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0027,0xE4C6);return StepResult::executed;
  case 0x3E4C6: // $E4C6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEC54,0xE4C9);return StepResult::executed;
  case 0x3E4C9: // $E4C9 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0028,0xE4CB);return StepResult::executed;
  case 0x3E4CB: // $E4CB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEC54,0xE4CE);return StepResult::executed;
  case 0x3E4CE: // $E4CE opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE4D0);return StepResult::executed;
  case 0x3E4D0: // $E4D0 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xE4D2);return StepResult::executed;
  case 0x3E4D2: // $E4D2 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0019,0xE4D4);return StepResult::executed;
  case 0x3E4D4: // $E4D4 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE4D5);return StepResult::executed;
  case 0x3E4D5: // $E4D5 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE4D7);return StepResult::executed;
  case 0x3E4D7: // $E4D7 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE4DA);return StepResult::executed;
  case 0x3E4DA: // $E4DA opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8A81,0xE4DD);return StepResult::executed;
  case 0x3E4DD: // $E4DD opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xE4DF);return StepResult::executed;
  case 0x3E4DF: // $E4DF opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0020,0xE4E1);return StepResult::executed;
  case 0x3E4E1: // $E4E1 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE4EE,0xE4E3);return StepResult::executed;
  case 0x3E4E3: // $E4E3 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0074,0xE4E5);return StepResult::executed;
  case 0x3E4E5: // $E4E5 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE249,0xE4E8);return StepResult::executed;
  case 0x3E4E8: // $E4E8 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0068,0xE4EA);return StepResult::executed;
  case 0x3E4EA: // $E4EA opcode $49, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::imm>(0x0001,0xE4EC);return StepResult::executed;
  case 0x3E4EC: // $E4EC opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xE4EE);return StepResult::executed;
  case 0x3E4EE: // $E4EE opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xE4F0);return StepResult::executed;
  case 0x3E4F0: // $E4F0 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0xE4F2);return StepResult::executed;
  case 0x3E4F2: // $E4F2 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE4D4,0xE4F4);return StepResult::executed;
  case 0x3E4F4: // $E4F4 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0068,0xE4F6);return StepResult::executed;
  case 0x3E4F6: // $E4F6 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE4FD,0xE4F8);return StepResult::executed;
  case 0x3E4F8: // $E4F8 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xE4FA);return StepResult::executed;
  case 0x3E4FA: // $E4FA opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE558,0xE4FD);return StepResult::executed;
  case 0x3E4FD: // $E4FD opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7A7,0xE500);return StepResult::executed;
  case 0x3E500: // $E500 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE502);return StepResult::executed;
  case 0x3E502: // $E502 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE505);return StepResult::executed;
  case 0x3E505: // $E505 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8EA0,0xE508);return StepResult::executed;
  case 0x3E508: // $E508 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE63D,0xE50B);return StepResult::executed;
  case 0x3E50B: // $E50B opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE48D,0xE50E);return StepResult::executed;
  case 0x3E50E: // $E50E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE510);return StepResult::executed;
  case 0x3E510: // $E510 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE513);return StepResult::executed;
  case 0x3E513: // $E513 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xA38D,0xE516);return StepResult::executed;
  case 0x3E516: // $E516 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xE518);return StepResult::executed;
  case 0x3E518: // $E518 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE51B);return StepResult::executed;
  case 0x3E51B: // $E51B opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xA513,0xE51E);return StepResult::executed;
  case 0x3E51E: // $E51E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xE520);return StepResult::executed;
  case 0x3E520: // $E520 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE523);return StepResult::executed;
  case 0x3E523: // $E523 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xAFA4,0xE526);return StepResult::executed;
  case 0x3E526: // $E526 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xE528);return StepResult::executed;
  case 0x3E528: // $E528 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE52B);return StepResult::executed;
  case 0x3E52B: // $E52B opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xB4CC,0xE52E);return StepResult::executed;
  case 0x3E52E: // $E52E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE4FD,0xE531);return StepResult::executed;
  case 0x3E531: // $E531 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xE533);return StepResult::executed;
  case 0x3E533: // $E533 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE536);return StepResult::executed;
  case 0x3E536: // $E536 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xBBEA,0xE539);return StepResult::executed;
  case 0x3E539: // $E539 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE53B);return StepResult::executed;
  case 0x3E53B: // $E53B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE53E);return StepResult::executed;
  case 0x3E53E: // $E53E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x8974,0xE541);return StepResult::executed;
  case 0x3E541: // $E541 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xE543);return StepResult::executed;
  case 0x3E543: // $E543 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE546);return StepResult::executed;
  case 0x3E546: // $E546 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xB195,0xE549);return StepResult::executed;
  case 0x3E549: // $E549 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xE54B);return StepResult::executed;
  case 0x3E54B: // $E54B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE54E);return StepResult::executed;
  case 0x3E54E: // $E54E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xB7D2,0xE551);return StepResult::executed;
  case 0x3E551: // $E551 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0018,0xE553);return StepResult::executed;
  case 0x3E553: // $E553 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE555);return StepResult::executed;
  case 0x3E555: // $E555 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0019,0xE557);return StepResult::executed;
  case 0x3E557: // $E557 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE558);return StepResult::executed;
  case 0x3E558: // $E558 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0018,0xE55A);return StepResult::executed;
  case 0x3E55A: // $E55A opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE553,0xE55D);return StepResult::executed;
  case 0x3E55D: // $E55D opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0032,0xE55F);return StepResult::executed;
  case 0x3E55F: // $E55F opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x0033,0xE561);return StepResult::executed;
  case 0x3E561: // $E561 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xE56D,0xE563);return StepResult::executed;
  case 0x3E563: // $E563 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0032,0xE565);return StepResult::executed;
  case 0x3E565: // $E565 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xE569,0xE567);return StepResult::executed;
  case 0x3E567: // $E567 opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0033,0xE569);return StepResult::executed;
  case 0x3E569: // $E569 opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0032,0xE56B);return StepResult::executed;
  case 0x3E56B: // $E56B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xE56D);return StepResult::executed;
  case 0x3E56D: // $E56D opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE56E);return StepResult::executed;
  case 0x3E56E: // $E56E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE570);return StepResult::executed;
  case 0x3E570: // $E570 opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0001,0xE572);return StepResult::executed;
  case 0x3E572: // $E572 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0032,0xE574);return StepResult::executed;
  case 0x3E574: // $E574 opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0033,0xE576);return StepResult::executed;
  case 0x3E576: // $E576 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE577);return StepResult::executed;
  case 0x3E62D: // $E62D opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0024,0xE62F);return StepResult::executed;
  case 0x3E62F: // $E62F opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE2D0,0xE632);return StepResult::executed;
  case 0x3E63D: // $E63D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000D,0xE63F);return StepResult::executed;
  case 0x3E63F: // $E63F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2CA,0xE642);return StepResult::executed;
  case 0x3E642: // $E642 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB69D,0xE645);return StepResult::executed;
  case 0x3E645: // $E645 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE62D,0xE648);return StepResult::executed;
  case 0x3E710: // $E710 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE712);return StepResult::executed;
  case 0x3E712: // $E712 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xE715);return StepResult::executed;
  case 0x3E715: // $E715 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x8F1E,0xE718);return StepResult::executed;
  case 0x3E7A7: // $E7A7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE7A9);return StepResult::executed;
  case 0x3E7A9: // $E7A9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2CA,0xE7AC);return StepResult::executed;
  case 0x3E7AC: // $E7AC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8FFC,0xE7AF);return StepResult::executed;
  case 0x3E7AF: // $E7AF opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE62D,0xE7B2);return StepResult::executed;
  case 0x3E7B2: // $E7B2 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0028,0xE7B4);return StepResult::executed;
  case 0x3E7B4: // $E7B4 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE7B8,0xE7B6);return StepResult::executed;
  case 0x3E7B6: // $E7B6 opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x004D,0xE7B8);return StepResult::executed;
  case 0x3E7B8: // $E7B8 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE7BA);return StepResult::executed;
  case 0x3E7BA: // $E7BA opcode $95, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zpx>(0x0000,0xE7BC);return StepResult::executed;
  case 0x3E7BC: // $E7BC opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE7BD);return StepResult::executed;
  case 0x3E7BD: // $E7BD opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x00E0,0xE7BF);return StepResult::executed;
  case 0x3E7BF: // $E7BF opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE7BA,0xE7C1);return StepResult::executed;
  case 0x3E7C1: // $E7C1 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0xE7C3);return StepResult::executed;
  case 0x3E7C3: // $E7C3 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0400,0xE7C6);return StepResult::executed;
  case 0x3E7C6: // $E7C6 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0500,0xE7C9);return StepResult::executed;
  case 0x3E7C9: // $E7C9 opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x00F6,0xE7CB);return StepResult::executed;
  case 0x3E7CB: // $E7CB opcode $B0, TRACE_EXECUTED
   cpu.exec<Op::BCS,Mode::rel>(0xE7D0,0xE7CD);return StepResult::executed;
  case 0x3E7CD: // $E7CD opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0700,0xE7D0);return StepResult::executed;
  case 0x3E7D0: // $E7D0 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE7D1);return StepResult::executed;
  case 0x3E7D1: // $E7D1 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE7C3,0xE7D3);return StepResult::executed;
  case 0x3E7D3: // $E7D3 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE7D5);return StepResult::executed;
  case 0x3E7D5: // $E7D5 opcode $AA, TRACE_EXECUTED
   cpu.exec<Op::TAX,Mode::imp>(0x0000,0xE7D6);return StepResult::executed;
  case 0x3E7D6: // $E7D6 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0600,0xE7D9);return StepResult::executed;
  case 0x3E7D9: // $E7D9 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE7DA);return StepResult::executed;
  case 0x3E7DA: // $E7DA opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x00A0,0xE7DC);return StepResult::executed;
  case 0x3E7DC: // $E7DC opcode $90, TRACE_EXECUTED
   cpu.exec<Op::BCC,Mode::rel>(0xE7D6,0xE7DE);return StepResult::executed;
  case 0x3E7DE: // $E7DE opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x00E0,0xE7E0);return StepResult::executed;
  case 0x3E7E0: // $E7E0 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0600,0xE7E3);return StepResult::executed;
  case 0x3E7E3: // $E7E3 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE7E4);return StepResult::executed;
  case 0x3E7E4: // $E7E4 opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE7E0,0xE7E6);return StepResult::executed;
  case 0x3E7E6: // $E7E6 opcode $A2, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0xE7E8);return StepResult::executed;
  case 0x3E7E8: // $E7E8 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0300,0xE7EB);return StepResult::executed;
  case 0x3E7EB: // $E7EB opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE7EC);return StepResult::executed;
  case 0x3E7EC: // $E7EC opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x00C0,0xE7EE);return StepResult::executed;
  case 0x3E7EE: // $E7EE opcode $D0, TRACE_EXECUTED
   cpu.exec<Op::BNE,Mode::rel>(0xE7E8,0xE7F0);return StepResult::executed;
  case 0x3E7F0: // $E7F0 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xE7F2);return StepResult::executed;
  case 0x3E7F2: // $E7F2 opcode $AA, TRACE_EXECUTED
   cpu.exec<Op::TAX,Mode::imp>(0x0000,0xE7F3);return StepResult::executed;
  case 0x3E7F3: // $E7F3 opcode $95, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zpx>(0x00F0,0xE7F5);return StepResult::executed;
  case 0x3E7F5: // $E7F5 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xE7F6);return StepResult::executed;
  case 0x3E7F6: // $E7F6 opcode $E0, TRACE_EXECUTED
   cpu.exec<Op::CPX,Mode::imm>(0x0008,0xE7F8);return StepResult::executed;
  case 0x3E7F8: // $E7F8 opcode $90, TRACE_EXECUTED
   cpu.exec<Op::BCC,Mode::rel>(0xE7F3,0xE7FA);return StepResult::executed;
  case 0x3E7FA: // $E7FA opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE7FB);return StepResult::executed;
  case 0x3E7FB: // $E7FB opcode $0A, TRACE_EXECUTED
   cpu.exec<Op::ASL,Mode::acc>(0x0000,0xE7FC);return StepResult::executed;
  case 0x3E7FC: // $E7FC opcode $84, TRACE_EXECUTED
   cpu.exec<Op::STY,Mode::zp>(0x0003,0xE7FE);return StepResult::executed;
  case 0x3E7FE: // $E7FE opcode $A8, TRACE_EXECUTED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xE7FF);return StepResult::executed;
  case 0x3E7FF: // $E7FF opcode $C8, TRACE_EXECUTED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xE800);return StepResult::executed;
  case 0x3E800: // $E800 opcode $68, TRACE_EXECUTED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xE801);return StepResult::executed;
  case 0x3E801: // $E801 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0000,0xE803);return StepResult::executed;
  case 0x3E803: // $E803 opcode $68, TRACE_EXECUTED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xE804);return StepResult::executed;
  case 0x3E804: // $E804 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0001,0xE806);return StepResult::executed;
  case 0x3E806: // $E806 opcode $B1, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xE808);return StepResult::executed;
  case 0x3E808: // $E808 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0002,0xE80A);return StepResult::executed;
  case 0x3E80A: // $E80A opcode $C8, TRACE_EXECUTED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xE80B);return StepResult::executed;
  case 0x3E80B: // $E80B opcode $B1, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xE80D);return StepResult::executed;
  case 0x3E80D: // $E80D opcode $A4, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::zp>(0x0003,0xE80F);return StepResult::executed;
  case 0x3E80F: // $E80F opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x0003,0xE811);return StepResult::executed;
  case 0x3E811: // $E811 opcode $6C, TRACE_EXECUTED
   cpu.exec<Op::JMP,Mode::ind>(0x0002,0xE814);return StepResult::executed;
  case 0x3E827: // $E827 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xE828);return StepResult::executed;
  case 0x3E828: // $E828 opcode $75, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zpx>(0x0000,0xE82A);return StepResult::executed;
  case 0x3E82A: // $E82A opcode $95, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zpx>(0x0000,0xE82C);return StepResult::executed;
  case 0x3E82C: // $E82C opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xE830,0xE82E);return StepResult::executed;
  case 0x3E82E: // $E82E opcode $F6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zpx>(0x0001,0xE830);return StepResult::executed;
  case 0x3E830: // $E830 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xE831);return StepResult::executed;
  case 0x3EB44: // $EB44 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE211,0xEB47);return StepResult::executed;
  case 0x3EB47: // $EB47 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEB82,0xEB4A);return StepResult::executed;
  case 0x3EB4A: // $EB4A opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0002,0xEB4C);return StepResult::executed;
  case 0x3EB4C: // $EB4C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xEB4E);return StepResult::executed;
  case 0x3EB4E: // $EB4E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEB60,0xEB51);return StepResult::executed;
  case 0x3EB51: // $EB51 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0005,0xEB53);return StepResult::executed;
  case 0x3EB53: // $EB53 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEC54,0xEB56);return StepResult::executed;
  case 0x3EB56: // $EB56 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xEB58);return StepResult::executed;
  case 0x3EB58: // $EB58 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEC54,0xEB5B);return StepResult::executed;
  case 0x3EB5B: // $EB5B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0026,0xEB5D);return StepResult::executed;
  case 0x3EB5D: // $EB5D opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xEC54,0xEB60);return StepResult::executed;
  case 0x3EB60: // $EB60 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2CA,0xEB63);return StepResult::executed;
  case 0x3EB63: // $EB63 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEB84,0xEB66);return StepResult::executed;
  case 0x3EB66: // $EB66 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0024,0xEB68);return StepResult::executed;
  case 0x3EB68: // $EB68 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE2D0,0xEB6B);return StepResult::executed;
  case 0x3EB82: // $EB82 opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0xEB84);return StepResult::executed;
  case 0x3EB84: // $EB84 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0xEBF7,0xEB87);return StepResult::executed;
  case 0x3EB87: // $EB87 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0000,0xEB89);return StepResult::executed;
  case 0x3EB89: // $EB89 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0xEBF8,0xEB8C);return StepResult::executed;
  case 0x3EB8C: // $EB8C opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0001,0xEB8E);return StepResult::executed;
  case 0x3EB8E: // $EB8E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE16C,0xEB91);return StepResult::executed;
  case 0x3EB91: // $EB91 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xEB93);return StepResult::executed;
  case 0x3EB93: // $EB93 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x00FD,0xEB95);return StepResult::executed;
  case 0x3EB95: // $EB95 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x00FC,0xEB97);return StepResult::executed;
  case 0x3EB97: // $EB97 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x2002,0xEB9A);return StepResult::executed;
  case 0x3EB9A: // $EB9A opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0001,0xEB9C);return StepResult::executed;
  case 0x3EB9C: // $EB9C opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xEB9E);return StepResult::executed;
  case 0x3EB9E: // $EB9E opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x2006,0xEBA1);return StepResult::executed;
  case 0x3EBA1: // $EBA1 opcode $88, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xEBA2);return StepResult::executed;
  case 0x3EBA2: // $EBA2 opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xEBA4);return StepResult::executed;
  case 0x3EBA4: // $EBA4 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x2006,0xEBA7);return StepResult::executed;
  case 0x3EBA7: // $EBA7 opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0000,0xEBA9);return StepResult::executed;
  case 0x3EBA9: // $EBA9 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xEBAB);return StepResult::executed;
  case 0x3EBAB: // $EBAB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE827,0xEBAE);return StepResult::executed;
  case 0x3EBAE: // $EBAE opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xEBB0);return StepResult::executed;
  case 0x3EBB0: // $EBB0 opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xEBB2);return StepResult::executed;
  case 0x3EBB2: // $EBB2 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x00FF,0xEBB4);return StepResult::executed;
  case 0x3EBB4: // $EBB4 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xEBF4,0xEBB6);return StepResult::executed;
  case 0x3EBB6: // $EBB6 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x007F,0xEBB8);return StepResult::executed;
  case 0x3EBB8: // $EBB8 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xEBEC,0xEBBA);return StepResult::executed;
  case 0x3EBBA: // $EBBA opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xEBBB);return StepResult::executed;
  case 0x3EBBB: // $EBBB opcode $10, HISTORICALLY_VERIFIED
   cpu.exec<Op::BPL,Mode::rel>(0xEBDA,0xEBBD);return StepResult::executed;
  case 0x3EBBD: // $EBBD opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x007F,0xEBBF);return StepResult::executed;
  case 0x3EBBF: // $EBBF opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0002,0xEBC1);return StepResult::executed;
  case 0x3EBC1: // $EBC1 opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0001,0xEBC3);return StepResult::executed;
  case 0x3EBC3: // $EBC3 opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xEBC5);return StepResult::executed;
  case 0x3EBC5: // $EBC5 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x2007,0xEBC8);return StepResult::executed;
  case 0x3EBC8: // $EBC8 opcode $C4, HISTORICALLY_VERIFIED
   cpu.exec<Op::CPY,Mode::zp>(0x0002,0xEBCA);return StepResult::executed;
  case 0x3EBCA: // $EBCA opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xEBCF,0xEBCC);return StepResult::executed;
  case 0x3EBCC: // $EBCC opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xEBCD);return StepResult::executed;
  case 0x3EBCD: // $EBCD opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xEBC3,0xEBCF);return StepResult::executed;
  case 0x3EBCF: // $EBCF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xEBD1);return StepResult::executed;
  case 0x3EBD1: // $EBD1 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xEBD2);return StepResult::executed;
  case 0x3EBD2: // $EBD2 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0002,0xEBD4);return StepResult::executed;
  case 0x3EBD4: // $EBD4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE827,0xEBD7);return StepResult::executed;
  case 0x3EBD7: // $EBD7 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xEBAE,0xEBDA);return StepResult::executed;
  case 0x3EBDA: // $EBDA opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0001,0xEBDC);return StepResult::executed;
  case 0x3EBDC: // $EBDC opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0002,0xEBDE);return StepResult::executed;
  case 0x3EBDE: // $EBDE opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0000,0xEBE0);return StepResult::executed;
  case 0x3EBE0: // $EBE0 opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x0002,0xEBE2);return StepResult::executed;
  case 0x3EBE2: // $EBE2 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x2007,0xEBE5);return StepResult::executed;
  case 0x3EBE5: // $EBE5 opcode $88, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xEBE6);return StepResult::executed;
  case 0x3EBE6: // $EBE6 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xEBE2,0xEBE8);return StepResult::executed;
  case 0x3EBE8: // $EBE8 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xEBEA);return StepResult::executed;
  case 0x3EBEA: // $EBEA opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xEBD4,0xEBEC);return StepResult::executed;
  case 0x3EBEC: // $EBEC opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xEBEE);return StepResult::executed;
  case 0x3EBEE: // $EBEE opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE827,0xEBF1);return StepResult::executed;
  case 0x3EBF1: // $EBF1 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xEB97,0xEBF4);return StepResult::executed;
  case 0x3EBF4: // $EBF4 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xED89,0xEBF7);return StepResult::executed;
  case 0x3EC72: // $EC72 opcode $A6, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::zp>(0x001E,0xEC74);return StepResult::executed;
  case 0x3EC74: // $EC74 opcode $9D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::absx>(0x0300,0xEC77);return StepResult::executed;
  case 0x3EC77: // $EC77 opcode $E8, TRACE_EXECUTED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xEC78);return StepResult::executed;
  case 0x3EC78: // $EC78 opcode $86, TRACE_EXECUTED
   cpu.exec<Op::STX,Mode::zp>(0x001E,0xEC7A);return StepResult::executed;
  case 0x3EC7A: // $EC7A opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xEC7B);return StepResult::executed;
  case 0x3ED46: // $ED46 opcode $A0, TRACE_EXECUTED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xED48);return StepResult::executed;
  case 0x3ED48: // $ED48 opcode $BE, TRACE_EXECUTED
   cpu.exec<Op::LDX,Mode::absy>(0x0300,0xED4B);return StepResult::executed;
  case 0x3ED4B: // $ED4B opcode $F0, TRACE_EXECUTED
   cpu.exec<Op::BEQ,Mode::rel>(0xED82,0xED4D);return StepResult::executed;
  case 0x3ED82: // $ED82 opcode $A9, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xED84);return StepResult::executed;
  case 0x3ED84: // $ED84 opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x0300,0xED87);return StepResult::executed;
  case 0x3ED87: // $ED87 opcode $85, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::zp>(0x001E,0xED89);return StepResult::executed;
  case 0x3ED89: // $ED89 opcode $A5, TRACE_EXECUTED
   cpu.exec<Op::LDA,Mode::zp>(0x00FF,0xED8B);return StepResult::executed;
  case 0x3ED8B: // $ED8B opcode $8D, TRACE_EXECUTED
   cpu.exec<Op::STA,Mode::abs>(0x2000,0xED8E);return StepResult::executed;
  case 0x3ED8E: // $ED8E opcode $60, TRACE_EXECUTED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xED8F);return StepResult::executed;
  case 0x3EF93: // $EF93 opcode $DE, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::absx>(0x057C,0xEF96);return StepResult::executed;
  case 0x3EF96: // $EF96 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xEF99,0xEF98);return StepResult::executed;
  case 0x3EF98: // $EF98 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xEF99);return StepResult::executed;
  case 0x3EF99: // $EF99 opcode $BC, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::absx>(0x048C,0xEF9C);return StepResult::executed;
  case 0x3EF9C: // $EF9C opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xEFD2,0xEF9F);return StepResult::executed;
  case 0x3EF9F: // $EF9F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0008,0xEFA1);return StepResult::executed;
  case 0x3EFA1: // $EFA1 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xEFD3,0xEFA4);return StepResult::executed;
  case 0x3EFA4: // $EFA4 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0009,0xEFA6);return StepResult::executed;
  case 0x3EFA6: // $EFA6 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x05AA,0xEFA9);return StepResult::executed;
  case 0x3EFA9: // $EFA9 opcode $0A, HISTORICALLY_VERIFIED
   cpu.exec<Op::ASL,Mode::acc>(0x0000,0xEFAA);return StepResult::executed;
  case 0x3EFAA: // $EFAA opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xEFAB);return StepResult::executed;
  case 0x3EFAB: // $EFAB opcode $7D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::absx>(0x05AA,0xEFAE);return StepResult::executed;
  case 0x3EFAE: // $EFAE opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xEFAF);return StepResult::executed;
  case 0x3EFAF: // $EFAF opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0008,0xEFB1);return StepResult::executed;
  case 0x3EFB1: // $EFB1 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xEFB2);return StepResult::executed;
  case 0x3EFB2: // $EFB2 opcode $7D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::absx>(0x0593,0xEFB5);return StepResult::executed;
  case 0x3EFB5: // $EFB5 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0400,0xEFB8);return StepResult::executed;
  case 0x3EFB8: // $EFB8 opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xEFB9);return StepResult::executed;
  case 0x3EFB9: // $EFB9 opcode $B1, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::indy>(0x0008,0xEFBB);return StepResult::executed;
  case 0x3EFBB: // $EFBB opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x057C,0xEFBE);return StepResult::executed;
  case 0x3EFBE: // $EFBE opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xEFBF);return StepResult::executed;
  case 0x3EFBF: // $EFBF opcode $FE, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::absx>(0x0593,0xEFC2);return StepResult::executed;
  case 0x3EFC2: // $EFC2 opcode $FE, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::absx>(0x0593,0xEFC5);return StepResult::executed;
  case 0x3EFC5: // $EFC5 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0593,0xEFC8);return StepResult::executed;
  case 0x3EFC8: // $EFC8 opcode $D1, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::indy>(0x0008,0xEFCA);return StepResult::executed;
  case 0x3EFCA: // $EFCA opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xEFD1,0xEFCC);return StepResult::executed;
  case 0x3EFCC: // $EFCC opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xEFCE);return StepResult::executed;
  case 0x3EFCE: // $EFCE opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0593,0xEFD1);return StepResult::executed;
  case 0x3EFD1: // $EFD1 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xEFD2);return StepResult::executed;
  case 0x3F390: // $F390 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF6AE,0xF393);return StepResult::executed;
  case 0x3F393: // $F393 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002D,0xF395);return StepResult::executed;
  case 0x3F395: // $F395 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF398,0xF397);return StepResult::executed;
  case 0x3F397: // $F397 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF398);return StepResult::executed;
  case 0x3F398: // $F398 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002C,0xF39A);return StepResult::executed;
  case 0x3F39A: // $F39A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7FB,0xF39D);return StepResult::executed;
  case 0x3F3DD: // $F3DD opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF3DF);return StepResult::executed;
  case 0x3F3DF: // $F3DF opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF3E1);return StepResult::executed;
  case 0x3F3E1: // $F3E1 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF3E3);return StepResult::executed;
  case 0x3F3E3: // $F3E3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF3E6);return StepResult::executed;
  case 0x3F3E6: // $F3E6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9046,0xF3E9);return StepResult::executed;
  case 0x3F3E9: // $F3E9 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE63D,0xF3EC);return StepResult::executed;
  case 0x3F3EC: // $F3EC opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF3EE);return StepResult::executed;
  case 0x3F3EE: // $F3EE opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF3F1);return StepResult::executed;
  case 0x3F3F1: // $F3F1 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x9080,0xF3F4);return StepResult::executed;
  case 0x3F3F4: // $F3F4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF3F6);return StepResult::executed;
  case 0x3F3F6: // $F3F6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF3F9);return StepResult::executed;
  case 0x3F3F9: // $F3F9 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x9023,0xF3FC);return StepResult::executed;
  case 0x3F3FC: // $F3FC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEB82,0xF3FF);return StepResult::executed;
  case 0x3F3FF: // $F3FF opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF401);return StepResult::executed;
  case 0x3F401: // $F401 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF402);return StepResult::executed;
  case 0x3F402: // $F402 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF404);return StepResult::executed;
  case 0x3F404: // $F404 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF406);return StepResult::executed;
  case 0x3F406: // $F406 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2C4,0xF409);return StepResult::executed;
  case 0x3F409: // $F409 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE870,0xF40C);return StepResult::executed;
  case 0x3F40C: // $F40C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE580,0xF40F);return StepResult::executed;
  case 0x3F40F: // $F40F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD03C,0xF412);return StepResult::executed;
  case 0x3F412: // $F412 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF414);return StepResult::executed;
  case 0x3F414: // $F414 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF417);return StepResult::executed;
  case 0x3F417: // $F417 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8571,0xF41A);return StepResult::executed;
  case 0x3F41A: // $F41A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x85A1,0xF41D);return StepResult::executed;
  case 0x3F41D: // $F41D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x862B,0xF420);return StepResult::executed;
  case 0x3F420: // $F420 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD0CD,0xF423);return StepResult::executed;
  case 0x3F423: // $F423 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0007,0xF425);return StepResult::executed;
  case 0x3F425: // $F425 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF428);return StepResult::executed;
  case 0x3F428: // $F428 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB4C8,0xF42B);return StepResult::executed;
  case 0x3F42B: // $F42B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF42D);return StepResult::executed;
  case 0x3F42D: // $F42D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF430);return StepResult::executed;
  case 0x3F430: // $F430 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9557,0xF433);return StepResult::executed;
  case 0x3F433: // $F433 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF454,0xF435);return StepResult::executed;
  case 0x3F435: // $F435 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0065,0xF437);return StepResult::executed;
  case 0x3F437: // $F437 opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xF446,0xF439);return StepResult::executed;
  case 0x3F439: // $F439 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD83,0xF43C);return StepResult::executed;
  case 0x3F43C: // $F43C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF778,0xF43F);return StepResult::executed;
  case 0x3F43F: // $F43F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF441);return StepResult::executed;
  case 0x3F441: // $F441 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x008A,0xF443);return StepResult::executed;
  case 0x3F443: // $F443 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF445);return StepResult::executed;
  case 0x3F445: // $F445 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF446);return StepResult::executed;
  case 0x3F446: // $F446 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD7B,0xF449);return StepResult::executed;
  case 0x3F449: // $F449 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF77D,0xF44C);return StepResult::executed;
  case 0x3F44C: // $F44C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF44E);return StepResult::executed;
  case 0x3F44E: // $F44E opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x008A,0xF450);return StepResult::executed;
  case 0x3F450: // $F450 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0004,0xF452);return StepResult::executed;
  case 0x3F452: // $F452 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF486,0xF454);return StepResult::executed;
  case 0x3F454: // $F454 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x007A,0xF456);return StepResult::executed;
  case 0x3F456: // $F456 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00F0,0xF458);return StepResult::executed;
  case 0x3F458: // $F458 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0010,0xF45A);return StepResult::executed;
  case 0x3F45A: // $F45A opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF47A,0xF45C);return StepResult::executed;
  case 0x3F45C: // $F45C opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0020,0xF45E);return StepResult::executed;
  case 0x3F45E: // $F45E opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF435,0xF460);return StepResult::executed;
  case 0x3F460: // $F460 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0030,0xF462);return StepResult::executed;
  case 0x3F462: // $F462 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF435,0xF464);return StepResult::executed;
  case 0x3F464: // $F464 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0040,0xF466);return StepResult::executed;
  case 0x3F466: // $F466 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF46F,0xF468);return StepResult::executed;
  case 0x3F468: // $F468 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0070,0xF46A);return StepResult::executed;
  case 0x3F46A: // $F46A opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF489,0xF46C);return StepResult::executed;
  case 0x3F46C: // $F46C opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF435,0xF46F);return StepResult::executed;
  case 0x3F46F: // $F46F opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xF471);return StepResult::executed;
  case 0x3F471: // $F471 opcode $8C, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::abs>(0x0780,0xF474);return StepResult::executed;
  case 0x3F474: // $F474 opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xF475);return StepResult::executed;
  case 0x3F475: // $F475 opcode $8C, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::abs>(0x0781,0xF478);return StepResult::executed;
  case 0x3F478: // $F478 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF435,0xF47A);return StepResult::executed;
  case 0x3F47A: // $F47A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD83,0xF47D);return StepResult::executed;
  case 0x3F47D: // $F47D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF778,0xF480);return StepResult::executed;
  case 0x3F480: // $F480 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF482);return StepResult::executed;
  case 0x3F482: // $F482 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0061,0xF484);return StepResult::executed;
  case 0x3F484: // $F484 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0009,0xF486);return StepResult::executed;
  case 0x3F486: // $F486 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF488);return StepResult::executed;
  case 0x3F488: // $F488 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF489);return StepResult::executed;
  case 0x3F489: // $F489 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0013,0xF48B);return StepResult::executed;
  case 0x3F48B: // $F48B opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF486,0xF48D);return StepResult::executed;
  case 0x3F48D: // $F48D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF48F);return StepResult::executed;
  case 0x3F48F: // $F48F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF491);return StepResult::executed;
  case 0x3F491: // $F491 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x008A,0xF493);return StepResult::executed;
  case 0x3F493: // $F493 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF4A0,0xF495);return StepResult::executed;
  case 0x3F495: // $F495 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF497);return StepResult::executed;
  case 0x3F497: // $F497 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF49A);return StepResult::executed;
  case 0x3F49A: // $F49A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8BDD,0xF49D);return StepResult::executed;
  case 0x3F49D: // $F49D opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x008A,0xF49F);return StepResult::executed;
  case 0x3F49F: // $F49F opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF4A0);return StepResult::executed;
  case 0x3F4A0: // $F4A0 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCDAE,0xF4A3);return StepResult::executed;
  case 0x3F4A3: // $F4A3 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF4A6,0xF4A5);return StepResult::executed;
  case 0x3F4A5: // $F4A5 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF4A6);return StepResult::executed;
  case 0x3F4A6: // $F4A6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCFC3,0xF4A9);return StepResult::executed;
  case 0x3F4A9: // $F4A9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE599,0xF4AC);return StepResult::executed;
  case 0x3F4AC: // $F4AC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF4DF,0xF4AF);return StepResult::executed;
  case 0x3F4AF: // $F4AF opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x007A,0xF4B1);return StepResult::executed;
  case 0x3F4B1: // $F4B1 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00F0,0xF4B3);return StepResult::executed;
  case 0x3F4B3: // $F4B3 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0010,0xF4B5);return StepResult::executed;
  case 0x3F4B5: // $F4B5 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF4D2,0xF4B7);return StepResult::executed;
  case 0x3F4B7: // $F4B7 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0020,0xF4B9);return StepResult::executed;
  case 0x3F4B9: // $F4B9 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF4CD,0xF4BB);return StepResult::executed;
  case 0x3F4BB: // $F4BB opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0030,0xF4BD);return StepResult::executed;
  case 0x3F4BD: // $F4BD opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF4C2,0xF4BF);return StepResult::executed;
  case 0x3F4BF: // $F4BF opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF4C1);return StepResult::executed;
  case 0x3F4C1: // $F4C1 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF4C2);return StepResult::executed;
  case 0x3F4C2: // $F4C2 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF4C4);return StepResult::executed;
  case 0x3F4C4: // $F4C4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF4C7);return StepResult::executed;
  case 0x3F4C7: // $F4C7 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9622,0xF4CA);return StepResult::executed;
  case 0x3F4CA: // $F4CA opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF4BF,0xF4CD);return StepResult::executed;
  case 0x3F4CD: // $F4CD opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000F,0xF4CF);return StepResult::executed;
  case 0x3F4CF: // $F4CF opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF4D1);return StepResult::executed;
  case 0x3F4D1: // $F4D1 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF4D2);return StepResult::executed;
  case 0x3F4D2: // $F4D2 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF4D4);return StepResult::executed;
  case 0x3F4D4: // $F4D4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF4D7);return StepResult::executed;
  case 0x3F4D7: // $F4D7 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9649,0xF4DA);return StepResult::executed;
  case 0x3F4DA: // $F4DA opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF4DC);return StepResult::executed;
  case 0x3F4DC: // $F4DC opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF4DE);return StepResult::executed;
  case 0x3F4DE: // $F4DE opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF4DF);return StepResult::executed;
  case 0x3F4DF: // $F4DF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF4E1);return StepResult::executed;
  case 0x3F4E1: // $F4E1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF4E4);return StepResult::executed;
  case 0x3F4E4: // $F4E4 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xBC0B,0xF4E7);return StepResult::executed;
  case 0x3F4E7: // $F4E7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF4E9);return StepResult::executed;
  case 0x3F4E9: // $F4E9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF4EC);return StepResult::executed;
  case 0x3F4EC: // $F4EC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9525,0xF4EF);return StepResult::executed;
  case 0x3F4EF: // $F4EF opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xF531,0xF4F1);return StepResult::executed;
  case 0x3F4F1: // $F4F1 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0010,0xF4F3);return StepResult::executed;
  case 0x3F4F3: // $F4F3 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF4F5);return StepResult::executed;
  case 0x3F4F5: // $F4F5 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF4F7);return StepResult::executed;
  case 0x3F4F7: // $F4F7 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xF4F9);return StepResult::executed;
  case 0x3F4F9: // $F4F9 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF4FA);return StepResult::executed;
  case 0x3F4FA: // $F4FA opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00C4,0xF4FC);return StepResult::executed;
  case 0x3F4FC: // $F4FC opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF506,0xF4FE);return StepResult::executed;
  case 0x3F4FE: // $F4FE opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x00C4,0xF500);return StepResult::executed;
  case 0x3F500: // $F500 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF531,0xF502);return StepResult::executed;
  case 0x3F502: // $F502 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF504);return StepResult::executed;
  case 0x3F504: // $F504 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xF506);return StepResult::executed;
  case 0x3F506: // $F506 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF508);return StepResult::executed;
  case 0x3F508: // $F508 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF50B);return StepResult::executed;
  case 0x3F50B: // $F50B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB7D9,0xF50E);return StepResult::executed;
  case 0x3F50E: // $F50E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF531,0xF511);return StepResult::executed;
  case 0x3F511: // $F511 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x001B,0xF513);return StepResult::executed;
  case 0x3F513: // $F513 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0007,0xF515);return StepResult::executed;
  case 0x3F515: // $F515 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0002,0xF517);return StepResult::executed;
  case 0x3F517: // $F517 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF521,0xF519);return StepResult::executed;
  case 0x3F519: // $F519 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF51B);return StepResult::executed;
  case 0x3F51B: // $F51B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF51E);return StepResult::executed;
  case 0x3F51E: // $F51E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x84A0,0xF521);return StepResult::executed;
  case 0x3F521: // $F521 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xF523);return StepResult::executed;
  case 0x3F523: // $F523 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF526);return StepResult::executed;
  case 0x3F526: // $F526 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xA993,0xF529);return StepResult::executed;
  case 0x3F529: // $F529 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF52B);return StepResult::executed;
  case 0x3F52B: // $F52B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF52E);return StepResult::executed;
  case 0x3F52E: // $F52E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8514,0xF531);return StepResult::executed;
  case 0x3F531: // $F531 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF578,0xF534);return StepResult::executed;
  case 0x3F534: // $F534 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF577,0xF536);return StepResult::executed;
  case 0x3F536: // $F536 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF538);return StepResult::executed;
  case 0x3F538: // $F538 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF53B);return StepResult::executed;
  case 0x3F53B: // $F53B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8E38,0xF53E);return StepResult::executed;
  case 0x3F53E: // $F53E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF540);return StepResult::executed;
  case 0x3F540: // $F540 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF543);return StepResult::executed;
  case 0x3F543: // $F543 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8A0A,0xF546);return StepResult::executed;
  case 0x3F546: // $F546 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00BC,0xF548);return StepResult::executed;
  case 0x3F548: // $F548 opcode $0D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::abs>(0x0565,0xF54B);return StepResult::executed;
  case 0x3F54B: // $F54B opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xF577,0xF54D);return StepResult::executed;
  case 0x3F54D: // $F54D opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0075,0xF54F);return StepResult::executed;
  case 0x3F54F: // $F54F opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF554,0xF551);return StepResult::executed;
  case 0x3F551: // $F551 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD14A,0xF554);return StepResult::executed;
  case 0x3F554: // $F554 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF556);return StepResult::executed;
  case 0x3F556: // $F556 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF559);return StepResult::executed;
  case 0x3F559: // $F559 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xAF5F,0xF55C);return StepResult::executed;
  case 0x3F55C: // $F55C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF55E);return StepResult::executed;
  case 0x3F55E: // $F55E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF561);return StepResult::executed;
  case 0x3F561: // $F561 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x808F,0xF564);return StepResult::executed;
  case 0x3F564: // $F564 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xF566);return StepResult::executed;
  case 0x3F566: // $F566 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF569);return StepResult::executed;
  case 0x3F569: // $F569 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFDE4,0xF56C);return StepResult::executed;
  case 0x3F56C: // $F56C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF56E);return StepResult::executed;
  case 0x3F56E: // $F56E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF571);return StepResult::executed;
  case 0x3F571: // $F571 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9F7B,0xF574);return StepResult::executed;
  case 0x3F574: // $F574 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xF577);return StepResult::executed;
  case 0x3F577: // $F577 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF578);return StepResult::executed;
  case 0x3F578: // $F578 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002E,0xF57A);return StepResult::executed;
  case 0x3F57A: // $F57A opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF5A6,0xF57C);return StepResult::executed;
  case 0x3F57C: // $F57C opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0028,0xF57E);return StepResult::executed;
  case 0x3F57E: // $F57E opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0020,0xF580);return StepResult::executed;
  case 0x3F580: // $F580 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF5A6,0xF582);return StepResult::executed;
  case 0x3F582: // $F582 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xF584);return StepResult::executed;
  case 0x3F584: // $F584 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF587);return StepResult::executed;
  case 0x3F587: // $F587 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x82AC,0xF58A);return StepResult::executed;
  case 0x3F58A: // $F58A opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF5A6,0xF58C);return StepResult::executed;
  case 0x3F58C: // $F58C opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002C,0xF58E);return StepResult::executed;
  case 0x3F58E: // $F58E opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x001B,0xF590);return StepResult::executed;
  case 0x3F590: // $F590 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF5A6,0xF592);return StepResult::executed;
  case 0x3F592: // $F592 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000D,0xF594);return StepResult::executed;
  case 0x3F594: // $F594 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF597);return StepResult::executed;
  case 0x3F597: // $F597 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB528,0xF59A);return StepResult::executed;
  case 0x3F59A: // $F59A opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xF5A6,0xF59C);return StepResult::executed;
  case 0x3F59C: // $F59C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF59E);return StepResult::executed;
  case 0x3F59E: // $F59E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5A1);return StepResult::executed;
  case 0x3F5A1: // $F5A1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x84A2,0xF5A4);return StepResult::executed;
  case 0x3F5A4: // $F5A4 opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xF5A5);return StepResult::executed;
  case 0x3F5A5: // $F5A5 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF5A6);return StepResult::executed;
  case 0x3F5A6: // $F5A6 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xF5A7);return StepResult::executed;
  case 0x3F5A7: // $F5A7 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF5A8);return StepResult::executed;
  case 0x3F5A8: // $F5A8 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF5AA);return StepResult::executed;
  case 0x3F5AA: // $F5AA opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF5AC);return StepResult::executed;
  case 0x3F5AC: // $F5AC opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x008A,0xF5AE);return StepResult::executed;
  case 0x3F5AE: // $F5AE opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF5B3,0xF5B0);return StepResult::executed;
  case 0x3F5B0: // $F5B0 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF495,0xF5B3);return StepResult::executed;
  case 0x3F5B3: // $F5B3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCC47,0xF5B6);return StepResult::executed;
  case 0x3F5B6: // $F5B6 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF5B9,0xF5B8);return StepResult::executed;
  case 0x3F5B8: // $F5B8 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF5B9);return StepResult::executed;
  case 0x3F5B9: // $F5B9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF4DF,0xF5BC);return StepResult::executed;
  case 0x3F5BC: // $F5BC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCF51,0xF5BF);return StepResult::executed;
  case 0x3F5BF: // $F5BF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF5C1);return StepResult::executed;
  case 0x3F5C1: // $F5C1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5C4);return StepResult::executed;
  case 0x3F5C4: // $F5C4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x81FC,0xF5C7);return StepResult::executed;
  case 0x3F5C7: // $F5C7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF5C9);return StepResult::executed;
  case 0x3F5C9: // $F5C9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5CC);return StepResult::executed;
  case 0x3F5CC: // $F5CC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9CE8,0xF5CF);return StepResult::executed;
  case 0x3F5CF: // $F5CF opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF5D1);return StepResult::executed;
  case 0x3F5D1: // $F5D1 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF5D2);return StepResult::executed;
  case 0x3F5D2: // $F5D2 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF578,0xF5D5);return StepResult::executed;
  case 0x3F5D5: // $F5D5 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF61C,0xF5D7);return StepResult::executed;
  case 0x3F5D7: // $F5D7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF5D9);return StepResult::executed;
  case 0x3F5D9: // $F5D9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5DC);return StepResult::executed;
  case 0x3F5DC: // $F5DC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8E38,0xF5DF);return StepResult::executed;
  case 0x3F5DF: // $F5DF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF5E1);return StepResult::executed;
  case 0x3F5E1: // $F5E1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5E4);return StepResult::executed;
  case 0x3F5E4: // $F5E4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8A0A,0xF5E7);return StepResult::executed;
  case 0x3F5E7: // $F5E7 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0565,0xF5EA);return StepResult::executed;
  case 0x3F5EA: // $F5EA opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x00BC,0xF5EC);return StepResult::executed;
  case 0x3F5EC: // $F5EC opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xF61C,0xF5EE);return StepResult::executed;
  case 0x3F5EE: // $F5EE opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCB0B,0xF5F1);return StepResult::executed;
  case 0x3F5F1: // $F5F1 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF5F3);return StepResult::executed;
  case 0x3F5F3: // $F5F3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5F6);return StepResult::executed;
  case 0x3F5F6: // $F5F6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8559,0xF5F9);return StepResult::executed;
  case 0x3F5F9: // $F5F9 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF5FB);return StepResult::executed;
  case 0x3F5FB: // $F5FB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF5FE);return StepResult::executed;
  case 0x3F5FE: // $F5FE opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xAF5F,0xF601);return StepResult::executed;
  case 0x3F601: // $F601 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xF603);return StepResult::executed;
  case 0x3F603: // $F603 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF606);return StepResult::executed;
  case 0x3F606: // $F606 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFDE4,0xF609);return StepResult::executed;
  case 0x3F609: // $F609 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF60B);return StepResult::executed;
  case 0x3F60B: // $F60B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF60E);return StepResult::executed;
  case 0x3F60E: // $F60E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8266,0xF611);return StepResult::executed;
  case 0x3F611: // $F611 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF613);return StepResult::executed;
  case 0x3F613: // $F613 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF616);return StepResult::executed;
  case 0x3F616: // $F616 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9EA7,0xF619);return StepResult::executed;
  case 0x3F619: // $F619 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xF61C);return StepResult::executed;
  case 0x3F61C: // $F61C opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF61D);return StepResult::executed;
  case 0x3F61D: // $F61D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF61F);return StepResult::executed;
  case 0x3F61F: // $F61F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF621);return StepResult::executed;
  case 0x3F621: // $F621 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2C4,0xF624);return StepResult::executed;
  case 0x3F624: // $F624 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD3A9,0xF627);return StepResult::executed;
  case 0x3F627: // $F627 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0007,0xF629);return StepResult::executed;
  case 0x3F629: // $F629 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF62B);return StepResult::executed;
  case 0x3F62B: // $F62B opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF62C);return StepResult::executed;
  case 0x3F62C: // $F62C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF62E);return StepResult::executed;
  case 0x3F62E: // $F62E opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF630);return StepResult::executed;
  case 0x3F630: // $F630 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE72E,0xF633);return StepResult::executed;
  case 0x3F633: // $F633 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xF635);return StepResult::executed;
  case 0x3F635: // $F635 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF637);return StepResult::executed;
  case 0x3F637: // $F637 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF638);return StepResult::executed;
  case 0x3F638: // $F638 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF63A);return StepResult::executed;
  case 0x3F63A: // $F63A opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF63C);return StepResult::executed;
  case 0x3F63C: // $F63C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD475,0xF63F);return StepResult::executed;
  case 0x3F63F: // $F63F opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF642,0xF641);return StepResult::executed;
  case 0x3F641: // $F641 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF642);return StepResult::executed;
  case 0x3F642: // $F642 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD52C,0xF645);return StepResult::executed;
  case 0x3F645: // $F645 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xF647);return StepResult::executed;
  case 0x3F647: // $F647 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0061,0xF649);return StepResult::executed;
  case 0x3F649: // $F649 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF64B);return StepResult::executed;
  case 0x3F64B: // $F64B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x008A,0xF64D);return StepResult::executed;
  case 0x3F64D: // $F64D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF64F);return StepResult::executed;
  case 0x3F64F: // $F64F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF651);return StepResult::executed;
  case 0x3F651: // $F651 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF652);return StepResult::executed;
  case 0x3F652: // $F652 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF653);return StepResult::executed;
  case 0x3F653: // $F653 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF655);return StepResult::executed;
  case 0x3F655: // $F655 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF658);return StepResult::executed;
  case 0x3F658: // $F658 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x9BB0,0xF65B);return StepResult::executed;
  case 0x3F65B: // $F65B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xF65D);return StepResult::executed;
  case 0x3F65D: // $F65D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF660);return StepResult::executed;
  case 0x3F660: // $F660 opcode $AE, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::abs>(0x07EC,0xF663);return StepResult::executed;
  case 0x3F663: // $F663 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF67F,0xF665);return StepResult::executed;
  case 0x3F665: // $F665 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xF668);return StepResult::executed;
  case 0x3F668: // $F668 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x07EC,0xF66B);return StepResult::executed;
  case 0x3F66B: // $F66B opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF67E,0xF66D);return StepResult::executed;
  case 0x3F66D: // $F66D opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x07ED,0xF670);return StepResult::executed;
  case 0x3F670: // $F670 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x007F,0xF672);return StepResult::executed;
  case 0x3F672: // $F672 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x000C,0xF674);return StepResult::executed;
  case 0x3F674: // $F674 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF67E,0xF676);return StepResult::executed;
  case 0x3F676: // $F676 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF678);return StepResult::executed;
  case 0x3F678: // $F678 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF67B);return StepResult::executed;
  case 0x3F67B: // $F67B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8E38,0xF67E);return StepResult::executed;
  case 0x3F67E: // $F67E opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF67F);return StepResult::executed;
  case 0x3F67F: // $F67F opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xF680);return StepResult::executed;
  case 0x3F680: // $F680 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF688,0xF682);return StepResult::executed;
  case 0x3F682: // $F682 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x827F,0xF685);return StepResult::executed;
  case 0x3F685: // $F685 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF69A,0xF688);return StepResult::executed;
  case 0x3F688: // $F688 opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xF689);return StepResult::executed;
  case 0x3F689: // $F689 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF691,0xF68B);return StepResult::executed;
  case 0x3F68B: // $F68B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x83BA,0xF68E);return StepResult::executed;
  case 0x3F68E: // $F68E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF69A,0xF691);return StepResult::executed;
  case 0x3F691: // $F691 opcode $CA, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEX,Mode::imp>(0x0000,0xF692);return StepResult::executed;
  case 0x3F692: // $F692 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF69A,0xF694);return StepResult::executed;
  case 0x3F694: // $F694 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8446,0xF697);return StepResult::executed;
  case 0x3F697: // $F697 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF69A,0xF69A);return StepResult::executed;
  case 0x3F69A: // $F69A opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x07EE,0xF69D);return StepResult::executed;
  case 0x3F69D: // $F69D opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF6AB,0xF69F);return StepResult::executed;
  case 0x3F69F: // $F69F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF6A1);return StepResult::executed;
  case 0x3F6A1: // $F6A1 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x07ED,0xF6A4);return StepResult::executed;
  case 0x3F6A4: // $F6A4 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x07EE,0xF6A7);return StepResult::executed;
  case 0x3F6A7: // $F6A7 opcode $EE, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::abs>(0x07EC,0xF6AA);return StepResult::executed;
  case 0x3F6AA: // $F6AA opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF6AB);return StepResult::executed;
  case 0x3F6AB: // $F6AB opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x9488,0xF6AE);return StepResult::executed;
  case 0x3F6AE: // $F6AE opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x001F,0xF6B0);return StepResult::executed;
  case 0x3F6B0: // $F6B0 opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x002E,0xF6B2);return StepResult::executed;
  case 0x3F6B2: // $F6B2 opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x001D,0xF6B4);return StepResult::executed;
  case 0x3F6B4: // $F6B4 opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x00A8,0xF6B6);return StepResult::executed;
  case 0x3F6B6: // $F6B6 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF6E3,0xF6B8);return StepResult::executed;
  case 0x3F6B8: // $F6B8 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xF6BA);return StepResult::executed;
  case 0x3F6BA: // $F6BA opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x002D,0xF6BC);return StepResult::executed;
  case 0x3F6BC: // $F6BC opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF6CB,0xF6BE);return StepResult::executed;
  case 0x3F6BE: // $F6BE opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0xF6C0);return StepResult::executed;
  case 0x3F6C0: // $F6C0 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF6E3,0xF6C2);return StepResult::executed;
  case 0x3F6C2: // $F6C2 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xF6C4);return StepResult::executed;
  case 0x3F6C4: // $F6C4 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002D,0xF6C6);return StepResult::executed;
  case 0x3F6C6: // $F6C6 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x004F,0xF6C8);return StepResult::executed;
  case 0x3F6C8: // $F6C8 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE249,0xF6CB);return StepResult::executed;
  case 0x3F6CB: // $F6CB opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002C,0xF6CD);return StepResult::executed;
  case 0x3F6CD: // $F6CD opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x000A,0xF6CF);return StepResult::executed;
  case 0x3F6CF: // $F6CF opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF6D9,0xF6D1);return StepResult::executed;
  case 0x3F6D1: // $F6D1 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF6D3);return StepResult::executed;
  case 0x3F6D3: // $F6D3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF6D6);return StepResult::executed;
  case 0x3F6D6: // $F6D6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x84A0,0xF6D9);return StepResult::executed;
  case 0x3F6D9: // $F6D9 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00F8,0xF6DB);return StepResult::executed;
  case 0x3F6DB: // $F6DB opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0xF6DD);return StepResult::executed;
  case 0x3F6DD: // $F6DD opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF6E3,0xF6DF);return StepResult::executed;
  case 0x3F6DF: // $F6DF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF6E1);return StepResult::executed;
  case 0x3F6E1: // $F6E1 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002D,0xF6E3);return StepResult::executed;
  case 0x3F6E3: // $F6E3 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF6E4);return StepResult::executed;
  case 0x3F6E4: // $F6E4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF6E6);return StepResult::executed;
  case 0x3F6E6: // $F6E6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF6E9);return StepResult::executed;
  case 0x3F6E9: // $F6E9 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xB8AD,0xF6EC);return StepResult::executed;
  case 0x3F6EC: // $F6EC opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF6EE);return StepResult::executed;
  case 0x3F6EE: // $F6EE opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF6F1);return StepResult::executed;
  case 0x3F6F1: // $F6F1 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x90F3,0xF6F4);return StepResult::executed;
  case 0x3F6F4: // $F6F4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF6F6);return StepResult::executed;
  case 0x3F6F6: // $F6F6 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xF6F8);return StepResult::executed;
  case 0x3F6F8: // $F6F8 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2C4,0xF6FB);return StepResult::executed;
  case 0x3F6FB: // $F6FB opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF6FD);return StepResult::executed;
  case 0x3F6FD: // $F6FD opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF6FE);return StepResult::executed;
  case 0x3F6FE: // $F6FE opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF700);return StepResult::executed;
  case 0x3F700: // $F700 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF703);return StepResult::executed;
  case 0x3F703: // $F703 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xB1CD,0xF706);return StepResult::executed;
  case 0x3F706: // $F706 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF708);return StepResult::executed;
  case 0x3F708: // $F708 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0003,0xF70A);return StepResult::executed;
  case 0x3F70A: // $F70A opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0054,0xF70C);return StepResult::executed;
  case 0x3F70C: // $F70C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF70E);return StepResult::executed;
  case 0x3F70E: // $F70E opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0053,0xF710);return StepResult::executed;
  case 0x3F710: // $F710 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF718,0xF713);return StepResult::executed;
  case 0x3F713: // $F713 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE63D,0xF716);return StepResult::executed;
  case 0x3F716: // $F716 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF718);return StepResult::executed;
  case 0x3F718: // $F718 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF71A);return StepResult::executed;
  case 0x3F71A: // $F71A opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF71C);return StepResult::executed;
  case 0x3F71C: // $F71C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF778,0xF71F);return StepResult::executed;
  case 0x3F71F: // $F71F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF721);return StepResult::executed;
  case 0x3F721: // $F721 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x00C6,0xF723);return StepResult::executed;
  case 0x3F723: // $F723 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF724);return StepResult::executed;
  case 0x3F724: // $F724 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002C,0xF726);return StepResult::executed;
  case 0x3F726: // $F726 opcode $48, HISTORICALLY_VERIFIED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xF727);return StepResult::executed;
  case 0x3F727: // $F727 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF739,0xF72A);return StepResult::executed;
  case 0x3F72A: // $F72A opcode $68, HISTORICALLY_VERIFIED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xF72B);return StepResult::executed;
  case 0x3F72B: // $F72B opcode $C5, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::zp>(0x002C,0xF72D);return StepResult::executed;
  case 0x3F72D: // $F72D opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF736,0xF72F);return StepResult::executed;
  case 0x3F72F: // $F72F opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF731);return StepResult::executed;
  case 0x3F731: // $F731 opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0080,0xF733);return StepResult::executed;
  case 0x3F733: // $F733 opcode $8C, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::abs>(0x0438,0xF736);return StepResult::executed;
  case 0x3F736: // $F736 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF738);return StepResult::executed;
  case 0x3F738: // $F738 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF739);return StepResult::executed;
  case 0x3F739: // $F739 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF73B);return StepResult::executed;
  case 0x3F73B: // $F73B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF73D);return StepResult::executed;
  case 0x3F73D: // $F73D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF73F);return StepResult::executed;
  case 0x3F73F: // $F73F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF742);return StepResult::executed;
  case 0x3F742: // $F742 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB3DA,0xF745);return StepResult::executed;
  case 0x3F745: // $F745 opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xF723,0xF747);return StepResult::executed;
  case 0x3F747: // $F747 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE580,0xF74A);return StepResult::executed;
  case 0x3F74A: // $F74A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD03C,0xF74D);return StepResult::executed;
  case 0x3F74D: // $F74D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF74F);return StepResult::executed;
  case 0x3F74F: // $F74F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF752);return StepResult::executed;
  case 0x3F752: // $F752 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8571,0xF755);return StepResult::executed;
  case 0x3F755: // $F755 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x85A1,0xF758);return StepResult::executed;
  case 0x3F758: // $F758 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD8C3,0xF75B);return StepResult::executed;
  case 0x3F75B: // $F75B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0007,0xF75D);return StepResult::executed;
  case 0x3F75D: // $F75D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF760);return StepResult::executed;
  case 0x3F760: // $F760 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB4C8,0xF763);return StepResult::executed;
  case 0x3F763: // $F763 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF765);return StepResult::executed;
  case 0x3F765: // $F765 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF768);return StepResult::executed;
  case 0x3F768: // $F768 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9557,0xF76B);return StepResult::executed;
  case 0x3F76B: // $F76B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD567,0xF76E);return StepResult::executed;
  case 0x3F76E: // $F76E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF77D,0xF771);return StepResult::executed;
  case 0x3F771: // $F771 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF773);return StepResult::executed;
  case 0x3F773: // $F773 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x008A,0xF775);return StepResult::executed;
  case 0x3F775: // $F775 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF777);return StepResult::executed;
  case 0x3F777: // $F777 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF778);return StepResult::executed;
  case 0x3F778: // $F778 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0020,0xF77A);return StepResult::executed;
  case 0x3F77A: // $F77A opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF77F,0xF77D);return StepResult::executed;
  case 0x3F77D: // $F77D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0024,0xF77F);return StepResult::executed;
  case 0x3F77F: // $F77F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0021,0xF781);return StepResult::executed;
  case 0x3F781: // $F781 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF782);return StepResult::executed;
  case 0x3F782: // $F782 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x002C,0xF784);return StepResult::executed;
  case 0x3F784: // $F784 opcode $48, HISTORICALLY_VERIFIED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xF785);return StepResult::executed;
  case 0x3F785: // $F785 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF792,0xF788);return StepResult::executed;
  case 0x3F788: // $F788 opcode $68, HISTORICALLY_VERIFIED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xF789);return StepResult::executed;
  case 0x3F789: // $F789 opcode $C5, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::zp>(0x002C,0xF78B);return StepResult::executed;
  case 0x3F78B: // $F78B opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF78F,0xF78D);return StepResult::executed;
  case 0x3F78D: // $F78D opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF78F);return StepResult::executed;
  case 0x3F78F: // $F78F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF791);return StepResult::executed;
  case 0x3F791: // $F791 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF792);return StepResult::executed;
  case 0x3F792: // $F792 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF794);return StepResult::executed;
  case 0x3F794: // $F794 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF796);return StepResult::executed;
  case 0x3F796: // $F796 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x008A,0xF798);return StepResult::executed;
  case 0x3F798: // $F798 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF79D,0xF79A);return StepResult::executed;
  case 0x3F79A: // $F79A opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF495,0xF79D);return StepResult::executed;
  case 0x3F79D: // $F79D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCDAE,0xF7A0);return StepResult::executed;
  case 0x3F7A0: // $F7A0 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF7A3,0xF7A2);return StepResult::executed;
  case 0x3F7A2: // $F7A2 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF7A3);return StepResult::executed;
  case 0x3F7A3: // $F7A3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD889,0xF7A6);return StepResult::executed;
  case 0x3F7A6: // $F7A6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE599,0xF7A9);return StepResult::executed;
  case 0x3F7A9: // $F7A9 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0071,0xF7AB);return StepResult::executed;
  case 0x3F7AB: // $F7AB opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF7B4,0xF7AD);return StepResult::executed;
  case 0x3F7AD: // $F7AD opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0071,0xF7AF);return StepResult::executed;
  case 0x3F7AF: // $F7AF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x006C,0xF7B1);return StepResult::executed;
  case 0x3F7B1: // $F7B1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE249,0xF7B4);return StepResult::executed;
  case 0x3F7B4: // $F7B4 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x002C,0xF7B6);return StepResult::executed;
  case 0x3F7B6: // $F7B6 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF7B7);return StepResult::executed;
  case 0x3F7B7: // $F7B7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0008,0xF7B9);return StepResult::executed;
  case 0x3F7B9: // $F7B9 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002A,0xF7BB);return StepResult::executed;
  case 0x3F7BB: // $F7BB opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0028,0xF7BD);return StepResult::executed;
  case 0x3F7BD: // $F7BD opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE653,0xF7C0);return StepResult::executed;
  case 0x3F7C0: // $F7C0 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0565,0xF7C3);return StepResult::executed;
  case 0x3F7C3: // $F7C3 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0002,0xF7C5);return StepResult::executed;
  case 0x3F7C5: // $F7C5 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF7F7,0xF7C7);return StepResult::executed;
  case 0x3F7C7: // $F7C7 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE577,0xF7CA);return StepResult::executed;
  case 0x3F7CA: // $F7CA opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0016,0xF7CC);return StepResult::executed;
  case 0x3F7CC: // $F7CC opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF7CE);return StepResult::executed;
  case 0x3F7CE: // $F7CE opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF7CF);return StepResult::executed;
  case 0x3F7CF: // $F7CF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF7D1);return StepResult::executed;
  case 0x3F7D1: // $F7D1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF7D4);return StepResult::executed;
  case 0x3F7D4: // $F7D4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9525,0xF7D7);return StepResult::executed;
  case 0x3F7D7: // $F7D7 opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xF7E2,0xF7D9);return StepResult::executed;
  case 0x3F7D9: // $F7D9 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0010,0xF7DB);return StepResult::executed;
  case 0x3F7DB: // $F7DB opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF7DD);return StepResult::executed;
  case 0x3F7DD: // $F7DD opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0008,0xF7DF);return StepResult::executed;
  case 0x3F7DF: // $F7DF opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0068,0xF7E1);return StepResult::executed;
  case 0x3F7E1: // $F7E1 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF7E2);return StepResult::executed;
  case 0x3F7E2: // $F7E2 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xF578,0xF7E5);return StepResult::executed;
  case 0x3F7E5: // $F7E5 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF830,0xF7E7);return StepResult::executed;
  case 0x3F7E7: // $F7E7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF7E9);return StepResult::executed;
  case 0x3F7E9: // $F7E9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF7EC);return StepResult::executed;
  case 0x3F7EC: // $F7EC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8E38,0xF7EF);return StepResult::executed;
  case 0x3F7EF: // $F7EF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF7F1);return StepResult::executed;
  case 0x3F7F1: // $F7F1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF7F4);return StepResult::executed;
  case 0x3F7F4: // $F7F4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8A0A,0xF7F7);return StepResult::executed;
  case 0x3F7F7: // $F7F7 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0565,0xF7FA);return StepResult::executed;
  case 0x3F7FA: // $F7FA opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x00BC,0xF7FC);return StepResult::executed;
  case 0x3F7FC: // $F7FC opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xF830,0xF7FE);return StepResult::executed;
  case 0x3F7FE: // $F7FE opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0075,0xF800);return StepResult::executed;
  case 0x3F800: // $F800 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF805,0xF802);return StepResult::executed;
  case 0x3F802: // $F802 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD570,0xF805);return StepResult::executed;
  case 0x3F805: // $F805 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF807);return StepResult::executed;
  case 0x3F807: // $F807 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF80A);return StepResult::executed;
  case 0x3F80A: // $F80A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB34F,0xF80D);return StepResult::executed;
  case 0x3F80D: // $F80D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF80F);return StepResult::executed;
  case 0x3F80F: // $F80F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF812);return StepResult::executed;
  case 0x3F812: // $F812 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xAF5F,0xF815);return StepResult::executed;
  case 0x3F815: // $F815 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF817);return StepResult::executed;
  case 0x3F817: // $F817 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF81A);return StepResult::executed;
  case 0x3F81A: // $F81A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x808F,0xF81D);return StepResult::executed;
  case 0x3F81D: // $F81D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xF81F);return StepResult::executed;
  case 0x3F81F: // $F81F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF822);return StepResult::executed;
  case 0x3F822: // $F822 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFDE4,0xF825);return StepResult::executed;
  case 0x3F825: // $F825 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF827);return StepResult::executed;
  case 0x3F827: // $F827 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF82A);return StepResult::executed;
  case 0x3F82A: // $F82A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9F7B,0xF82D);return StepResult::executed;
  case 0x3F82D: // $F82D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xF830);return StepResult::executed;
  case 0x3F830: // $F830 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF831);return StepResult::executed;
  case 0x3F831: // $F831 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF833);return StepResult::executed;
  case 0x3F833: // $F833 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF836);return StepResult::executed;
  case 0x3F836: // $F836 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x92DE,0xF839);return StepResult::executed;
  case 0x3F839: // $F839 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF83B);return StepResult::executed;
  case 0x3F83B: // $F83B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF83E);return StepResult::executed;
  case 0x3F83E: // $F83E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x92BD,0xF841);return StepResult::executed;
  case 0x3F841: // $F841 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF843);return StepResult::executed;
  case 0x3F843: // $F843 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF846);return StepResult::executed;
  case 0x3F846: // $F846 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0x9524,0xF849);return StepResult::executed;
  case 0x3F849: // $F849 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0068,0xF84B);return StepResult::executed;
  case 0x3F84B: // $F84B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7FB,0xF84E);return StepResult::executed;
  case 0x3F86E: // $F86E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE57B,0xF871);return StepResult::executed;
  case 0x3F871: // $F871 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE785,0xF874);return StepResult::executed;
  case 0x3F874: // $F874 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF876);return StepResult::executed;
  case 0x3F876: // $F876 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF877);return StepResult::executed;
  case 0x3F877: // $F877 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0008,0xF879);return StepResult::executed;
  case 0x3F879: // $F879 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002A,0xF87B);return StepResult::executed;
  case 0x3F87B: // $F87B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0028,0xF87D);return StepResult::executed;
  case 0x3F87D: // $F87D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE653,0xF880);return StepResult::executed;
  case 0x3F880: // $F880 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xD570,0xF883);return StepResult::executed;
  case 0x3F883: // $F883 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0008,0xF885);return StepResult::executed;
  case 0x3F885: // $F885 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002A,0xF887);return StepResult::executed;
  case 0x3F887: // $F887 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0028,0xF889);return StepResult::executed;
  case 0x3F889: // $F889 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE653,0xF88C);return StepResult::executed;
  case 0x3F88C: // $F88C opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xD14A,0xF88F);return StepResult::executed;
  case 0x3F88F: // $F88F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF891);return StepResult::executed;
  case 0x3F891: // $F891 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF893);return StepResult::executed;
  case 0x3F893: // $F893 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD3A9,0xF896);return StepResult::executed;
  case 0x3F896: // $F896 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF898);return StepResult::executed;
  case 0x3F898: // $F898 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF899);return StepResult::executed;
  case 0x3F899: // $F899 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF89B);return StepResult::executed;
  case 0x3F89B: // $F89B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF89D);return StepResult::executed;
  case 0x3F89D: // $F89D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7F0,0xF8A0);return StepResult::executed;
  case 0x3F8A0: // $F8A0 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF8A2);return StepResult::executed;
  case 0x3F8A2: // $F8A2 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF8A5);return StepResult::executed;
  case 0x3F8A5: // $F8A5 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8F47,0xF8A8);return StepResult::executed;
  case 0x3F8A8: // $F8A8 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE72E,0xF8AB);return StepResult::executed;
  case 0x3F8AB: // $F8AB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE57B,0xF8AE);return StepResult::executed;
  case 0x3F8AE: // $F8AE opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF8B0);return StepResult::executed;
  case 0x3F8B0: // $F8B0 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF8B1);return StepResult::executed;
  case 0x3F8B1: // $F8B1 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF8B3);return StepResult::executed;
  case 0x3F8B3: // $F8B3 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF8B5);return StepResult::executed;
  case 0x3F8B5: // $F8B5 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE870,0xF8B8);return StepResult::executed;
  case 0x3F8B8: // $F8B8 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE580,0xF8BB);return StepResult::executed;
  case 0x3F8BB: // $F8BB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD03C,0xF8BE);return StepResult::executed;
  case 0x3F8BE: // $F8BE opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000E,0xF8C0);return StepResult::executed;
  case 0x3F8C0: // $F8C0 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF8C3);return StepResult::executed;
  case 0x3F8C3: // $F8C3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8571,0xF8C6);return StepResult::executed;
  case 0x3F8C6: // $F8C6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x85A1,0xF8C9);return StepResult::executed;
  case 0x3F8C9: // $F8C9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x862B,0xF8CC);return StepResult::executed;
  case 0x3F8CC: // $F8CC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD0CD,0xF8CF);return StepResult::executed;
  case 0x3F8CF: // $F8CF opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0007,0xF8D1);return StepResult::executed;
  case 0x3F8D1: // $F8D1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF8D4);return StepResult::executed;
  case 0x3F8D4: // $F8D4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB4C8,0xF8D7);return StepResult::executed;
  case 0x3F8D7: // $F8D7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF8D9);return StepResult::executed;
  case 0x3F8D9: // $F8D9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF8DC);return StepResult::executed;
  case 0x3F8DC: // $F8DC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9557,0xF8DF);return StepResult::executed;
  case 0x3F8DF: // $F8DF opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD83,0xF8E2);return StepResult::executed;
  case 0x3F8E2: // $F8E2 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF8E4);return StepResult::executed;
  case 0x3F8E4: // $F8E4 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x008A,0xF8E6);return StepResult::executed;
  case 0x3F8E6: // $F8E6 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF8E8);return StepResult::executed;
  case 0x3F8E8: // $F8E8 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF8E9);return StepResult::executed;
  case 0x3F8E9: // $F8E9 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF8EB);return StepResult::executed;
  case 0x3F8EB: // $F8EB opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x001D,0xF8ED);return StepResult::executed;
  case 0x3F8ED: // $F8ED opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x008A,0xF8EF);return StepResult::executed;
  case 0x3F8EF: // $F8EF opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF8F4,0xF8F1);return StepResult::executed;
  case 0x3F8F1: // $F8F1 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF495,0xF8F4);return StepResult::executed;
  case 0x3F8F4: // $F8F4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCDAE,0xF8F7);return StepResult::executed;
  case 0x3F8F7: // $F8F7 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF8FA,0xF8F9);return StepResult::executed;
  case 0x3F8F9: // $F8F9 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF8FA);return StepResult::executed;
  case 0x3F8FA: // $F8FA opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCFC3,0xF8FD);return StepResult::executed;
  case 0x3F8FD: // $F8FD opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0010,0xF8FF);return StepResult::executed;
  case 0x3F8FF: // $F8FF opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0043,0xF901);return StepResult::executed;
  case 0x3F901: // $F901 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0003,0xF903);return StepResult::executed;
  case 0x3F903: // $F903 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0040,0xF905);return StepResult::executed;
  case 0x3F905: // $F905 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0034,0xF907);return StepResult::executed;
  case 0x3F907: // $F907 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x000C,0xF909);return StepResult::executed;
  case 0x3F909: // $F909 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF90F,0xF90B);return StepResult::executed;
  case 0x3F90B: // $F90B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x00A0,0xF90D);return StepResult::executed;
  case 0x3F90D: // $F90D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF911,0xF90F);return StepResult::executed;
  case 0x3F90F: // $F90F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0090,0xF911);return StepResult::executed;
  case 0x3F911: // $F911 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0042,0xF913);return StepResult::executed;
  case 0x3F913: // $F913 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE599,0xF916);return StepResult::executed;
  case 0x3F916: // $F916 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF918);return StepResult::executed;
  case 0x3F918: // $F918 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF919);return StepResult::executed;
  case 0x3F919: // $F919 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0008,0xF91B);return StepResult::executed;
  case 0x3F91B: // $F91B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002A,0xF91D);return StepResult::executed;
  case 0x3F91D: // $F91D opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0028,0xF91F);return StepResult::executed;
  case 0x3F91F: // $F91F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE653,0xF922);return StepResult::executed;
  case 0x3F922: // $F922 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD14A,0xF925);return StepResult::executed;
  case 0x3F925: // $F925 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF927);return StepResult::executed;
  case 0x3F927: // $F927 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF92A);return StepResult::executed;
  case 0x3F92A: // $F92A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xAF5F,0xF92D);return StepResult::executed;
  case 0x3F92D: // $F92D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xF92F);return StepResult::executed;
  case 0x3F92F: // $F92F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF932);return StepResult::executed;
  case 0x3F932: // $F932 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x808F,0xF935);return StepResult::executed;
  case 0x3F935: // $F935 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xF937);return StepResult::executed;
  case 0x3F937: // $F937 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF93A);return StepResult::executed;
  case 0x3F93A: // $F93A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFDE4,0xF93D);return StepResult::executed;
  case 0x3F93D: // $F93D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF93F);return StepResult::executed;
  case 0x3F93F: // $F93F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF942);return StepResult::executed;
  case 0x3F942: // $F942 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9F7B,0xF945);return StepResult::executed;
  case 0x3F945: // $F945 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xF948);return StepResult::executed;
  case 0x3F948: // $F948 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0565,0xF94B);return StepResult::executed;
  case 0x3F94B: // $F94B opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0002,0xF94D);return StepResult::executed;
  case 0x3F94D: // $F94D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF959,0xF94F);return StepResult::executed;
  case 0x3F94F: // $F94F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0012,0xF951);return StepResult::executed;
  case 0x3F951: // $F951 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0043,0xF953);return StepResult::executed;
  case 0x3F953: // $F953 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0002,0xF955);return StepResult::executed;
  case 0x3F955: // $F955 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0040,0xF957);return StepResult::executed;
  case 0x3F957: // $F957 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF959);return StepResult::executed;
  case 0x3F959: // $F959 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF95A);return StepResult::executed;
  case 0x3F95A: // $F95A opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE577,0xF95D);return StepResult::executed;
  case 0x3F95D: // $F95D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCFC3,0xF960);return StepResult::executed;
  case 0x3F960: // $F960 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0003,0xF962);return StepResult::executed;
  case 0x3F962: // $F962 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xF964);return StepResult::executed;
  case 0x3F964: // $F964 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF965);return StepResult::executed;
  case 0x3F965: // $F965 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0068,0xF967);return StepResult::executed;
  case 0x3F967: // $F967 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7FB,0xF96A);return StepResult::executed;
  case 0x3F97E: // $F97E opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0035,0xF980);return StepResult::executed;
  case 0x3F980: // $F980 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE723,0xF983);return StepResult::executed;
  case 0x3F983: // $F983 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE57B,0xF986);return StepResult::executed;
  case 0x3F986: // $F986 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF988);return StepResult::executed;
  case 0x3F988: // $F988 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF98B);return StepResult::executed;
  case 0x3F98B: // $F98B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8CB4,0xF98E);return StepResult::executed;
  case 0x3F98E: // $F98E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF990);return StepResult::executed;
  case 0x3F990: // $F990 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x0470,0xF993);return StepResult::executed;
  case 0x3F993: // $F993 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD03C,0xF996);return StepResult::executed;
  case 0x3F996: // $F996 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xD0CD,0xF999);return StepResult::executed;
  case 0x3F999: // $F999 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0007,0xF99B);return StepResult::executed;
  case 0x3F99B: // $F99B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF99E);return StepResult::executed;
  case 0x3F99E: // $F99E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB4C8,0xF9A1);return StepResult::executed;
  case 0x3F9A1: // $F9A1 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD64,0xF9A4);return StepResult::executed;
  case 0x3F9A4: // $F9A4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF9A6);return StepResult::executed;
  case 0x3F9A6: // $F9A6 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF9A9);return StepResult::executed;
  case 0x3F9A9: // $F9A9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9557,0xF9AC);return StepResult::executed;
  case 0x3F9AC: // $F9AC opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x007A,0xF9AE);return StepResult::executed;
  case 0x3F9AE: // $F9AE opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00F0,0xF9B0);return StepResult::executed;
  case 0x3F9B0: // $F9B0 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0030,0xF9B2);return StepResult::executed;
  case 0x3F9B2: // $F9B2 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF9B7,0xF9B4);return StepResult::executed;
  case 0x3F9B4: // $F9B4 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF9B6);return StepResult::executed;
  case 0x3F9B6: // $F9B6 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF9B7);return StepResult::executed;
  case 0x3F9B7: // $F9B7 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xF9B9);return StepResult::executed;
  case 0x3F9B9: // $F9B9 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xF9BC);return StepResult::executed;
  case 0x3F9BC: // $F9BC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9622,0xF9BF);return StepResult::executed;
  case 0x3F9BF: // $F9BF opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF9B4,0xF9C2);return StepResult::executed;
  case 0x3F9C2: // $F9C2 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD8C,0xF9C5);return StepResult::executed;
  case 0x3F9C5: // $F9C5 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xF9D0,0xF9C7);return StepResult::executed;
  case 0x3F9C7: // $F9C7 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0062,0xF9C9);return StepResult::executed;
  case 0x3F9C9: // $F9C9 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF9CF,0xF9CB);return StepResult::executed;
  case 0x3F9CB: // $F9CB opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0057,0xF9CD);return StepResult::executed;
  case 0x3F9CD: // $F9CD opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0057,0xF9CF);return StepResult::executed;
  case 0x3F9CF: // $F9CF opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF9D0);return StepResult::executed;
  case 0x3F9D0: // $F9D0 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF9D2);return StepResult::executed;
  case 0x3F9D2: // $F9D2 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0062,0xF9D4);return StepResult::executed;
  case 0x3F9D4: // $F9D4 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF9CB,0xF9D6);return StepResult::executed;
  case 0x3F9D6: // $F9D6 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF9D7);return StepResult::executed;
  case 0x3F9D7: // $F9D7 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0062,0xF9D9);return StepResult::executed;
  case 0x3F9D9: // $F9D9 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xF9EA,0xF9DB);return StepResult::executed;
  case 0x3F9DB: // $F9DB opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0438,0xF9DE);return StepResult::executed;
  case 0x3F9DE: // $F9DE opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xF9DF);return StepResult::executed;
  case 0x3F9DF: // $F9DF opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0001,0xF9E1);return StepResult::executed;
  case 0x3F9E1: // $F9E1 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x0438,0xF9E4);return StepResult::executed;
  case 0x3F9E4: // $F9E4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFB7A,0xF9E7);return StepResult::executed;
  case 0x3F9E7: // $F9E7 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xF9F6,0xF9EA);return StepResult::executed;
  case 0x3F9EA: // $F9EA opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0438,0xF9ED);return StepResult::executed;
  case 0x3F9ED: // $F9ED opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xF9EE);return StepResult::executed;
  case 0x3F9EE: // $F9EE opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0001,0xF9F0);return StepResult::executed;
  case 0x3F9F0: // $F9F0 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x0438,0xF9F3);return StepResult::executed;
  case 0x3F9F3: // $F9F3 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFB88,0xF9F6);return StepResult::executed;
  case 0x3F9F6: // $F9F6 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xF9F8);return StepResult::executed;
  case 0x3F9F8: // $F9F8 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x007F,0xF9FA);return StepResult::executed;
  case 0x3F9FA: // $F9FA opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xF9FE,0xF9FC);return StepResult::executed;
  case 0x3F9FC: // $F9FC opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xF9FE);return StepResult::executed;
  case 0x3F9FE: // $F9FE opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xF9FF);return StepResult::executed;
  case 0x3F9FF: // $F9FF opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xFA01);return StepResult::executed;
  case 0x3FA01: // $FA01 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFA03);return StepResult::executed;
  case 0x3FA03: // $FA03 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFA06);return StepResult::executed;
  case 0x3FA06: // $FA06 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x84A0,0xFA09);return StepResult::executed;
  case 0x3FA09: // $FA09 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8013,0xFA0C);return StepResult::executed;
  case 0x3FA0C: // $FA0C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8373,0xFA0F);return StepResult::executed;
  case 0x3FA0F: // $FA0F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0009,0xFA11);return StepResult::executed;
  case 0x3FA11: // $FA11 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE249,0xFA14);return StepResult::executed;
  case 0x3FA14: // $FA14 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x003C,0xFA16);return StepResult::executed;
  case 0x3FA16: // $FA16 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0032,0xFA18);return StepResult::executed;
  case 0x3FA18: // $FA18 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xFA1A);return StepResult::executed;
  case 0x3FA1A: // $FA1A opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xFA1C);return StepResult::executed;
  case 0x3FA1C: // $FA1C opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0013,0xFA1E);return StepResult::executed;
  case 0x3FA1E: // $FA1E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEF7F,0xFA21);return StepResult::executed;
  case 0x3FA21: // $FA21 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFA23);return StepResult::executed;
  case 0x3FA23: // $FA23 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0400,0xFA26);return StepResult::executed;
  case 0x3FA26: // $FA26 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0454,0xFA29);return StepResult::executed;
  case 0x3FA29: // $FA29 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x041C,0xFA2C);return StepResult::executed;
  case 0x3FA2C: // $FA2C opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0008,0xFA2E);return StepResult::executed;
  case 0x3FA2E: // $FA2E opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00F0,0xFA30);return StepResult::executed;
  case 0x3FA30: // $FA30 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x041C,0xFA33);return StepResult::executed;
  case 0x3FA33: // $FA33 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0062,0xFA35);return StepResult::executed;
  case 0x3FA35: // $FA35 opcode $0A, HISTORICALLY_VERIFIED
   cpu.exec<Op::ASL,Mode::acc>(0x0000,0xFA36);return StepResult::executed;
  case 0x3FA36: // $FA36 opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFA37);return StepResult::executed;
  case 0x3FA37: // $FA37 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xFAA6,0xFA3A);return StepResult::executed;
  case 0x3FA3A: // $FA3A opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0438,0xFA3D);return StepResult::executed;
  case 0x3FA3D: // $FA3D opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xFAA7,0xFA40);return StepResult::executed;
  case 0x3FA40: // $FA40 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x04A8,0xFA43);return StepResult::executed;
  case 0x3FA43: // $FA43 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFA45);return StepResult::executed;
  case 0x3FA45: // $FA45 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x005F,0xFA47);return StepResult::executed;
  case 0x3FA47: // $FA47 opcode $AC, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::abs>(0x054E,0xFA4A);return StepResult::executed;
  case 0x3FA4A: // $FA4A opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x041C,0xFA4D);return StepResult::executed;
  case 0x3FA4D: // $FA4D opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFA4E);return StepResult::executed;
  case 0x3FA4E: // $FA4E opcode $F9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::absy>(0xFAA2,0xFA51);return StepResult::executed;
  case 0x3FA51: // $FA51 opcode $0A, HISTORICALLY_VERIFIED
   cpu.exec<Op::ASL,Mode::acc>(0x0000,0xFA52);return StepResult::executed;
  case 0x3FA52: // $FA52 opcode $26, HISTORICALLY_VERIFIED
   cpu.exec<Op::ROL,Mode::zp>(0x005F,0xFA54);return StepResult::executed;
  case 0x3FA54: // $FA54 opcode $0A, HISTORICALLY_VERIFIED
   cpu.exec<Op::ASL,Mode::acc>(0x0000,0xFA55);return StepResult::executed;
  case 0x3FA55: // $FA55 opcode $26, HISTORICALLY_VERIFIED
   cpu.exec<Op::ROL,Mode::zp>(0x005F,0xFA57);return StepResult::executed;
  case 0x3FA57: // $FA57 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00E0,0xFA59);return StepResult::executed;
  case 0x3FA59: // $FA59 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x005E,0xFA5B);return StepResult::executed;
  case 0x3FA5B: // $FA5B opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x0062,0xFA5D);return StepResult::executed;
  case 0x3FA5D: // $FA5D opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xFAA0,0xFA60);return StepResult::executed;
  case 0x3FA60: // $FA60 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFA61);return StepResult::executed;
  case 0x3FA61: // $FA61 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x005E,0xFA63);return StepResult::executed;
  case 0x3FA63: // $FA63 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x005E,0xFA65);return StepResult::executed;
  case 0x3FA65: // $FA65 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0072,0xFA67);return StepResult::executed;
  case 0x3FA67: // $FA67 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0001,0xFA69);return StepResult::executed;
  case 0x3FA69: // $FA69 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0000,0xFA6B);return StepResult::executed;
  case 0x3FA6B: // $FA6B opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0062,0xFA6D);return StepResult::executed;
  case 0x3FA6D: // $FA6D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFA73,0xFA6F);return StepResult::executed;
  case 0x3FA6F: // $FA6F opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0024,0xFA71);return StepResult::executed;
  case 0x3FA71: // $FA71 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFA75,0xFA73);return StepResult::executed;
  case 0x3FA73: // $FA73 opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0020,0xFA75);return StepResult::executed;
  case 0x3FA75: // $FA75 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xFA77);return StepResult::executed;
  case 0x3FA77: // $FA77 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0001,0xFA79);return StepResult::executed;
  case 0x3FA79: // $FA79 opcode $45, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::zp>(0x0000,0xFA7B);return StepResult::executed;
  case 0x3FA7B: // $FA7B opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFA81,0xFA7D);return StepResult::executed;
  case 0x3FA7D: // $FA7D opcode $8A, HISTORICALLY_VERIFIED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0xFA7E);return StepResult::executed;
  case 0x3FA7E: // $FA7E opcode $49, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::imm>(0x0004,0xFA80);return StepResult::executed;
  case 0x3FA80: // $FA80 opcode $AA, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAX,Mode::imp>(0x0000,0xFA81);return StepResult::executed;
  case 0x3FA81: // $FA81 opcode $8A, HISTORICALLY_VERIFIED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0xFA82);return StepResult::executed;
  case 0x3FA82: // $FA82 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFA83);return StepResult::executed;
  case 0x3FA83: // $FA83 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x005F,0xFA85);return StepResult::executed;
  case 0x3FA85: // $FA85 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x005F,0xFA87);return StepResult::executed;
  case 0x3FA87: // $FA87 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x05EB,0xFA8A);return StepResult::executed;
  case 0x3FA8A: // $FA8A opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x005E,0xFA8C);return StepResult::executed;
  case 0x3FA8C: // $FA8C opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x05D4,0xFA8F);return StepResult::executed;
  case 0x3FA8F: // $FA8F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE83D,0xFA92);return StepResult::executed;
  case 0x3FA92: // $FA92 opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0006,0xFA94);return StepResult::executed;
  case 0x3FA94: // $FA94 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFA96);return StepResult::executed;
  case 0x3FA96: // $FA96 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0300,0xFA99);return StepResult::executed;
  case 0x3FA99: // $FA99 opcode $E8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xFA9A);return StepResult::executed;
  case 0x3FA9A: // $FA9A opcode $88, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEY,Mode::imp>(0x0000,0xFA9B);return StepResult::executed;
  case 0x3FA9B: // $FA9B opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFA96,0xFA9D);return StepResult::executed;
  case 0x3FA9D: // $FA9D opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE86B,0xFAA0);return StepResult::executed;
  case 0x3FAAA: // $FAAA opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0032,0xFAAC);return StepResult::executed;
  case 0x3FAAC: // $FAAC opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFABA,0xFAAE);return StepResult::executed;
  case 0x3FAAE: // $FAAE opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFAB0);return StepResult::executed;
  case 0x3FAB0: // $FAB0 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEF7A,0xFAB3);return StepResult::executed;
  case 0x3FAB3: // $FAB3 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0030,0xFAB5);return StepResult::executed;
  case 0x3FAB5: // $FAB5 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0032,0xFAB7);return StepResult::executed;
  case 0x3FAB7: // $FAB7 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xFAB9);return StepResult::executed;
  case 0x3FAB9: // $FAB9 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFABA);return StepResult::executed;
  case 0x3FABA: // $FABA opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0013,0xFABC);return StepResult::executed;
  case 0x3FABC: // $FABC opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEF93,0xFABF);return StepResult::executed;
  case 0x3FABF: // $FABF opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0593,0xFAC2);return StepResult::executed;
  case 0x3FAC2: // $FAC2 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFAB9,0xFAC4);return StepResult::executed;
  case 0x3FAC4: // $FAC4 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0080,0xFAC6);return StepResult::executed;
  case 0x3FAC6: // $FAC6 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x057C,0xFAC9);return StepResult::executed;
  case 0x3FAC9: // $FAC9 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFACA);return StepResult::executed;
  case 0x3FACA: // $FACA opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0032,0xFACC);return StepResult::executed;
  case 0x3FACC: // $FACC opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFADA,0xFACE);return StepResult::executed;
  case 0x3FACE: // $FACE opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000C,0xFAD0);return StepResult::executed;
  case 0x3FAD0: // $FAD0 opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0001,0xFAD2);return StepResult::executed;
  case 0x3FAD2: // $FAD2 opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0013,0xFAD4);return StepResult::executed;
  case 0x3FAD4: // $FAD4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEF7F,0xFAD7);return StepResult::executed;
  case 0x3FAD7: // $FAD7 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xFAD9);return StepResult::executed;
  case 0x3FAD9: // $FAD9 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFADA);return StepResult::executed;
  case 0x3FADA: // $FADA opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0062,0xFADC);return StepResult::executed;
  case 0x3FADC: // $FADC opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFAE6,0xFADE);return StepResult::executed;
  case 0x3FADE: // $FADE opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0438,0xFAE1);return StepResult::executed;
  case 0x3FAE1: // $FAE1 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFAE2);return StepResult::executed;
  case 0x3FAE2: // $FAE2 opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0001,0xFAE4);return StepResult::executed;
  case 0x3FAE4: // $FAE4 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFAEC,0xFAE6);return StepResult::executed;
  case 0x3FAE6: // $FAE6 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x0438,0xFAE9);return StepResult::executed;
  case 0x3FAE9: // $FAE9 opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFAEA);return StepResult::executed;
  case 0x3FAEA: // $FAEA opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0001,0xFAEC);return StepResult::executed;
  case 0x3FAEC: // $FAEC opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x0438,0xFAEF);return StepResult::executed;
  case 0x3FAEF: // $FAEF opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xEF91,0xFAF2);return StepResult::executed;
  case 0x3FAF2: // $FAF2 opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0013,0xFAF4);return StepResult::executed;
  case 0x3FAF4: // $FAF4 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEF93,0xFAF7);return StepResult::executed;
  case 0x3FAF7: // $FAF7 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0593,0xFAFA);return StepResult::executed;
  case 0x3FAFA: // $FAFA opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFB03,0xFAFC);return StepResult::executed;
  case 0x3FAFC: // $FAFC opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x057C,0xFAFF);return StepResult::executed;
  case 0x3FAFF: // $FAFF opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0001,0xFB01);return StepResult::executed;
  case 0x3FB01: // $FB01 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFB04,0xFB03);return StepResult::executed;
  case 0x3FB03: // $FB03 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFB04);return StepResult::executed;
  case 0x3FB04: // $FB04 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x0068,0xFB06);return StepResult::executed;
  case 0x3FB06: // $FB06 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0009,0xFB08);return StepResult::executed;
  case 0x3FB08: // $FB08 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE249,0xFB0B);return StepResult::executed;
  case 0x3FB0B: // $FB0B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFB0D);return StepResult::executed;
  case 0x3FB0D: // $FB0D opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0400,0xFB10);return StepResult::executed;
  case 0x3FB10: // $FB10 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCD76,0xFB13);return StepResult::executed;
  case 0x3FB13: // $FB13 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x05D4,0xFB16);return StepResult::executed;
  case 0x3FB16: // $FB16 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x005E,0xFB18);return StepResult::executed;
  case 0x3FB18: // $FB18 opcode $AD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::abs>(0x05EB,0xFB1B);return StepResult::executed;
  case 0x3FB1B: // $FB1B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x005F,0xFB1D);return StepResult::executed;
  case 0x3FB1D: // $FB1D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE83D,0xFB20);return StepResult::executed;
  case 0x3FB20: // $FB20 opcode $A0, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::imm>(0x0000,0xFB22);return StepResult::executed;
  case 0x3FB22: // $FB22 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xFB31,0xFB25);return StepResult::executed;
  case 0x3FB25: // $FB25 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0300,0xFB28);return StepResult::executed;
  case 0x3FB28: // $FB28 opcode $E8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xFB29);return StepResult::executed;
  case 0x3FB29: // $FB29 opcode $C8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INY,Mode::imp>(0x0000,0xFB2A);return StepResult::executed;
  case 0x3FB2A: // $FB2A opcode $C0, HISTORICALLY_VERIFIED
   cpu.exec<Op::CPY,Mode::imm>(0x0006,0xFB2C);return StepResult::executed;
  case 0x3FB2C: // $FB2C opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFB22,0xFB2E);return StepResult::executed;
  case 0x3FB2E: // $FB2E opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xE86B,0xFB31);return StepResult::executed;
  case 0x3FB37: // $FB37 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xFB39);return StepResult::executed;
  case 0x3FB39: // $FB39 opcode $45, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::zp>(0x0072,0xFB3B);return StepResult::executed;
  case 0x3FB3B: // $FB3B opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0002,0xFB3D);return StepResult::executed;
  case 0x3FB3D: // $FB3D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFB3F);return StepResult::executed;
  case 0x3FB3F: // $FB3F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0053,0xFB41);return StepResult::executed;
  case 0x3FB41: // $FB41 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0055,0xFB43);return StepResult::executed;
  case 0x3FB43: // $FB43 opcode $AC, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::abs>(0x04A8,0xFB46);return StepResult::executed;
  case 0x3FB46: // $FB46 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFB4A,0xFB48);return StepResult::executed;
  case 0x3FB48: // $FB48 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x006E,0xFB4A);return StepResult::executed;
  case 0x3FB4A: // $FB4A opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0054,0xFB4C);return StepResult::executed;
  case 0x3FB4C: // $FB4C opcode $45, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::zp>(0x0002,0xFB4E);return StepResult::executed;
  case 0x3FB4E: // $FB4E opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0001,0xFB50);return StepResult::executed;
  case 0x3FB50: // $FB50 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFB56,0xFB52);return StepResult::executed;
  case 0x3FB52: // $FB52 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0090,0xFB54);return StepResult::executed;
  case 0x3FB54: // $FB54 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFB58,0xFB56);return StepResult::executed;
  case 0x3FB56: // $FB56 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0080,0xFB58);return StepResult::executed;
  case 0x3FB58: // $FB58 opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x0072,0xFB5A);return StepResult::executed;
  case 0x3FB5A: // $FB5A opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0072,0xFB5C);return StepResult::executed;
  case 0x3FB5C: // $FB5C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xCFC3,0xFB5F);return StepResult::executed;
  case 0x3FB5F: // $FB5F opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x007A,0xFB61);return StepResult::executed;
  case 0x3FB61: // $FB61 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00F0,0xFB63);return StepResult::executed;
  case 0x3FB63: // $FB63 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0030,0xFB65);return StepResult::executed;
  case 0x3FB65: // $FB65 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFB6F,0xFB67);return StepResult::executed;
  case 0x3FB67: // $FB67 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFB69);return StepResult::executed;
  case 0x3FB69: // $FB69 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFB6C);return StepResult::executed;
  case 0x3FB6C: // $FB6C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x9622,0xFB6F);return StepResult::executed;
  case 0x3FB6F: // $FB6F opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE599,0xFB72);return StepResult::executed;
  case 0x3FB72: // $FB72 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE577,0xFB75);return StepResult::executed;
  case 0x3FB75: // $FB75 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0003,0xFB77);return StepResult::executed;
  case 0x3FB77: // $FB77 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x002C,0xFB79);return StepResult::executed;
  case 0x3FB79: // $FB79 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFB7A);return StepResult::executed;
  case 0x3FB7A: // $FB7A opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xFB7C);return StepResult::executed;
  case 0x3FB7C: // $FB7C opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFB7D);return StepResult::executed;
  case 0x3FB7D: // $FB7D opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0001,0xFB7F);return StepResult::executed;
  case 0x3FB7F: // $FB7F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0053,0xFB81);return StepResult::executed;
  case 0x3FB81: // $FB81 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xFB83);return StepResult::executed;
  case 0x3FB83: // $FB83 opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0000,0xFB85);return StepResult::executed;
  case 0x3FB85: // $FB85 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0054,0xFB87);return StepResult::executed;
  case 0x3FB87: // $FB87 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFB88);return StepResult::executed;
  case 0x3FB88: // $FB88 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xFB8A);return StepResult::executed;
  case 0x3FB8A: // $FB8A opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFB8B);return StepResult::executed;
  case 0x3FB8B: // $FB8B opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0001,0xFB8D);return StepResult::executed;
  case 0x3FB8D: // $FB8D opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0053,0xFB8F);return StepResult::executed;
  case 0x3FB8F: // $FB8F opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xFB91);return StepResult::executed;
  case 0x3FB91: // $FB91 opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0000,0xFB93);return StepResult::executed;
  case 0x3FB93: // $FB93 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0054,0xFB95);return StepResult::executed;
  case 0x3FB95: // $FB95 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFB96);return StepResult::executed;
  case 0x3FBF6: // $FBF6 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0010,0xFBF8);return StepResult::executed;
  case 0x3FBF8: // $FBF8 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFBF9);return StepResult::executed;
  case 0x3FBF9: // $FBF9 opcode $7D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::absx>(0x0438,0xFBFC);return StepResult::executed;
  case 0x3FBFC: // $FBFC opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0010,0xFBFE);return StepResult::executed;
  case 0x3FBFE: // $FBFE opcode $98, HISTORICALLY_VERIFIED
   cpu.exec<Op::TYA,Mode::imp>(0x0000,0xFBFF);return StepResult::executed;
  case 0x3FBFF: // $FBFF opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFC00);return StepResult::executed;
  case 0x3FC00: // $FC00 opcode $7D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::absx>(0x041C,0xFC03);return StepResult::executed;
  case 0x3FC03: // $FC03 opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFC04);return StepResult::executed;
  case 0x3FC04: // $FC04 opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0033,0xFC06);return StepResult::executed;
  case 0x3FC06: // $FC06 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0011,0xFC08);return StepResult::executed;
  case 0x3FC08: // $FC08 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFC0E,0xFC0A);return StepResult::executed;
  case 0x3FC0A: // $FC0A opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xFC0C);return StepResult::executed;
  case 0x3FC0C: // $FC0C opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFC10,0xFC0E);return StepResult::executed;
  case 0x3FC0E: // $FC0E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFC10);return StepResult::executed;
  case 0x3FC10: // $FC10 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0013,0xFC12);return StepResult::executed;
  case 0x3FC12: // $FC12 opcode $A4, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDY,Mode::zp>(0x0010,0xFC14);return StepResult::executed;
  case 0x3FC14: // $FC14 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFCA2,0xFC17);return StepResult::executed;
  case 0x3FC1F: // $FC1F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0010,0xFC21);return StepResult::executed;
  case 0x3FC21: // $FC21 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0065,0xFC23);return StepResult::executed;
  case 0x3FC23: // $FC23 opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xFBF6,0xFC25);return StepResult::executed;
  case 0x3FC25: // $FC25 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0010,0xFC27);return StepResult::executed;
  case 0x3FC27: // $FC27 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0080,0xFC29);return StepResult::executed;
  case 0x3FC29: // $FC29 opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFC2F,0xFC2B);return StepResult::executed;
  case 0x3FC2B: // $FC2B opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xFC2D);return StepResult::executed;
  case 0x3FC2D: // $FC2D opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFC31,0xFC2F);return StepResult::executed;
  case 0x3FC2F: // $FC2F opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFC31);return StepResult::executed;
  case 0x3FC31: // $FC31 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0005,0xFC33);return StepResult::executed;
  case 0x3FC33: // $FC33 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0470,0xFC36);return StepResult::executed;
  case 0x3FC36: // $FC36 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0001,0xFC38);return StepResult::executed;
  case 0x3FC38: // $FC38 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFC47,0xFC3A);return StepResult::executed;
  case 0x3FC3A: // $FC3A opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0438,0xFC3D);return StepResult::executed;
  case 0x3FC3D: // $FC3D opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0021,0xFC3F);return StepResult::executed;
  case 0x3FC3F: // $FC3F opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFC45,0xFC41);return StepResult::executed;
  case 0x3FC41: // $FC41 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xFC43);return StepResult::executed;
  case 0x3FC43: // $FC43 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFC47,0xFC45);return StepResult::executed;
  case 0x3FC45: // $FC45 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xFC47);return StepResult::executed;
  case 0x3FC47: // $FC47 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0011,0xFC49);return StepResult::executed;
  case 0x3FC49: // $FC49 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0010,0xFC4B);return StepResult::executed;
  case 0x3FC4B: // $FC4B opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFC4C);return StepResult::executed;
  case 0x3FC4C: // $FC4C opcode $7D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::absx>(0x0438,0xFC4F);return StepResult::executed;
  case 0x3FC4F: // $FC4F opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0010,0xFC51);return StepResult::executed;
  case 0x3FC51: // $FC51 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0011,0xFC53);return StepResult::executed;
  case 0x3FC53: // $FC53 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0005,0xFC55);return StepResult::executed;
  case 0x3FC55: // $FC55 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0014,0xFC57);return StepResult::executed;
  case 0x3FC57: // $FC57 opcode $98, HISTORICALLY_VERIFIED
   cpu.exec<Op::TYA,Mode::imp>(0x0000,0xFC58);return StepResult::executed;
  case 0x3FC58: // $FC58 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFC59);return StepResult::executed;
  case 0x3FC59: // $FC59 opcode $7D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::absx>(0x041C,0xFC5C);return StepResult::executed;
  case 0x3FC5C: // $FC5C opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFC5D);return StepResult::executed;
  case 0x3FC5D: // $FC5D opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0020,0xFC5F);return StepResult::executed;
  case 0x3FC5F: // $FC5F opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFC7D,0xFC61);return StepResult::executed;
  case 0x3FC61: // $FC61 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x00C0,0xFC63);return StepResult::executed;
  case 0x3FC63: // $FC63 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFC7D,0xFC65);return StepResult::executed;
  case 0x3FC65: // $FC65 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0011,0xFC67);return StepResult::executed;
  case 0x3FC67: // $FC67 opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFC69);return StepResult::executed;
  case 0x3FC69: // $FC69 opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFC6B);return StepResult::executed;
  case 0x3FC6B: // $FC6B opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFC6D);return StepResult::executed;
  case 0x3FC6D: // $FC6D opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFC6F);return StepResult::executed;
  case 0x3FC6F: // $FC6F opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xFC71);return StepResult::executed;
  case 0x3FC71: // $FC71 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFC72);return StepResult::executed;
  case 0x3FC72: // $FC72 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0010,0xFC74);return StepResult::executed;
  case 0x3FC74: // $FC74 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0013,0xFC76);return StepResult::executed;
  case 0x3FC76: // $FC76 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xFC78);return StepResult::executed;
  case 0x3FC78: // $FC78 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0014,0xFC7A);return StepResult::executed;
  case 0x3FC7A: // $FC7A opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFD0E,0xFC7D);return StepResult::executed;
  case 0x3FC7D: // $FC7D opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFC7F);return StepResult::executed;
  case 0x3FC7F: // $FC7F opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFC80);return StepResult::executed;
  case 0x3FC80: // $FC80 opcode $68, HISTORICALLY_VERIFIED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xFC81);return StepResult::executed;
  case 0x3FC81: // $FC81 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFC82);return StepResult::executed;
  case 0x3FC82: // $FC82 opcode $6D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::abs>(0x0438,0xFC85);return StepResult::executed;
  case 0x3FC85: // $FC85 opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFC86);return StepResult::executed;
  case 0x3FC86: // $FC86 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0013,0xFC88);return StepResult::executed;
  case 0x3FC88: // $FC88 opcode $8A, HISTORICALLY_VERIFIED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0xFC89);return StepResult::executed;
  case 0x3FC89: // $FC89 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFC8A);return StepResult::executed;
  case 0x3FC8A: // $FC8A opcode $6D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::abs>(0x041C,0xFC8D);return StepResult::executed;
  case 0x3FC8D: // $FC8D opcode $C5, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::zp>(0x00CD,0xFC8F);return StepResult::executed;
  case 0x3FC8F: // $FC8F opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFC7D,0xFC91);return StepResult::executed;
  case 0x3FC91: // $FC91 opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFC92);return StepResult::executed;
  case 0x3FC92: // $FC92 opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0033,0xFC94);return StepResult::executed;
  case 0x3FC94: // $FC94 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0011,0xFC96);return StepResult::executed;
  case 0x3FC96: // $FC96 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFC9C,0xFC98);return StepResult::executed;
  case 0x3FC98: // $FC98 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xFC9A);return StepResult::executed;
  case 0x3FC9A: // $FC9A opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFC9E,0xFC9C);return StepResult::executed;
  case 0x3FC9C: // $FC9C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFC9E);return StepResult::executed;
  case 0x3FC9E: // $FC9E opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0013,0xFCA0);return StepResult::executed;
  case 0x3FCA0: // $FCA0 opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0010,0xFCA2);return StepResult::executed;
  case 0x3FCA2: // $FCA2 opcode $98, HISTORICALLY_VERIFIED
   cpu.exec<Op::TYA,Mode::imp>(0x0000,0xFCA3);return StepResult::executed;
  case 0x3FCA3: // $FCA3 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFCA4);return StepResult::executed;
  case 0x3FCA4: // $FCA4 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFCA5);return StepResult::executed;
  case 0x3FCA5: // $FCA5 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFCA6);return StepResult::executed;
  case 0x3FCA6: // $FCA6 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFCA7);return StepResult::executed;
  case 0x3FCA7: // $FCA7 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFCA8);return StepResult::executed;
  case 0x3FCA8: // $FCA8 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0012,0xFCAA);return StepResult::executed;
  case 0x3FCAA: // $FCAA opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0013,0xFCAC);return StepResult::executed;
  case 0x3FCAC: // $FCAC opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xFCBB,0xFCAE);return StepResult::executed;
  case 0x3FCAE: // $FCAE opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCAF);return StepResult::executed;
  case 0x3FCAF: // $FCAF opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xFCB1);return StepResult::executed;
  case 0x3FCB1: // $FCB1 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0011,0xFCB3);return StepResult::executed;
  case 0x3FCB3: // $FCB3 opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFCC8,0xFCB5);return StepResult::executed;
  case 0x3FCB5: // $FCB5 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCB6);return StepResult::executed;
  case 0x3FCB6: // $FCB6 opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0010,0xFCB8);return StepResult::executed;
  case 0x3FCB8: // $FCB8 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFCCF,0xFCBB);return StepResult::executed;
  case 0x3FCBB: // $FCBB opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCBC);return StepResult::executed;
  case 0x3FCBC: // $FCBC opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xFCBE);return StepResult::executed;
  case 0x3FCBE: // $FCBE opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0011,0xFCC0);return StepResult::executed;
  case 0x3FCC0: // $FCC0 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFCC8,0xFCC2);return StepResult::executed;
  case 0x3FCC2: // $FCC2 opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFCC3);return StepResult::executed;
  case 0x3FCC3: // $FCC3 opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0010,0xFCC5);return StepResult::executed;
  case 0x3FCC5: // $FCC5 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFCCF,0xFCC8);return StepResult::executed;
  case 0x3FCC8: // $FCC8 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x00F0,0xFCCA);return StepResult::executed;
  case 0x3FCCA: // $FCCA opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFCCF,0xFCCC);return StepResult::executed;
  case 0x3FCCC: // $FCCC opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCCD);return StepResult::executed;
  case 0x3FCCD: // $FCCD opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0010,0xFCCF);return StepResult::executed;
  case 0x3FCCF: // $FCCF opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00F0,0xFCD1);return StepResult::executed;
  case 0x3FCD1: // $FCD1 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFCD2);return StepResult::executed;
  case 0x3FCD2: // $FCD2 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCD3);return StepResult::executed;
  case 0x3FCD3: // $FCD3 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0012,0xFCD5);return StepResult::executed;
  case 0x3FCD5: // $FCD5 opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFCD6);return StepResult::executed;
  case 0x3FCD6: // $FCD6 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0010,0xFCD8);return StepResult::executed;
  case 0x3FCD8: // $FCD8 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0xFCDA);return StepResult::executed;
  case 0x3FCDA: // $FCDA opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFD40,0xFCDC);return StepResult::executed;
  case 0x3FCDC: // $FCDC opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFD32,0xFCDE);return StepResult::executed;
  case 0x3FCDE: // $FCDE opcode $48, HISTORICALLY_VERIFIED
   cpu.exec<Op::PHA,Mode::imp>(0x0000,0xFCDF);return StepResult::executed;
  case 0x3FCDF: // $FCDF opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0065,0xFCE1);return StepResult::executed;
  case 0x3FCE1: // $FCE1 opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xFC80,0xFCE3);return StepResult::executed;
  case 0x3FCE3: // $FCE3 opcode $68, HISTORICALLY_VERIFIED
   cpu.exec<Op::PLA,Mode::imp>(0x0000,0xFCE4);return StepResult::executed;
  case 0x3FCE4: // $FCE4 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCE5);return StepResult::executed;
  case 0x3FCE5: // $FCE5 opcode $6D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::abs>(0x0438,0xFCE8);return StepResult::executed;
  case 0x3FCE8: // $FCE8 opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFCE9);return StepResult::executed;
  case 0x3FCE9: // $FCE9 opcode $8A, HISTORICALLY_VERIFIED
   cpu.exec<Op::TXA,Mode::imp>(0x0000,0xFCEA);return StepResult::executed;
  case 0x3FCEA: // $FCEA opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFCEB);return StepResult::executed;
  case 0x3FCEB: // $FCEB opcode $6D, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::abs>(0x041C,0xFCEE);return StepResult::executed;
  case 0x3FCEE: // $FCEE opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFCEF);return StepResult::executed;
  case 0x3FCEF: // $FCEF opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x0020,0xFCF1);return StepResult::executed;
  case 0x3FCF1: // $FCF1 opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFD4A,0xFCF3);return StepResult::executed;
  case 0x3FCF3: // $FCF3 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x00C0,0xFCF5);return StepResult::executed;
  case 0x3FCF5: // $FCF5 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFD4A,0xFCF7);return StepResult::executed;
  case 0x3FCF7: // $FCF7 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0011,0xFCF9);return StepResult::executed;
  case 0x3FCF9: // $FCF9 opcode $84, HISTORICALLY_VERIFIED
   cpu.exec<Op::STY,Mode::zp>(0x0010,0xFCFB);return StepResult::executed;
  case 0x3FCFB: // $FCFB opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFCFD);return StepResult::executed;
  case 0x3FCFD: // $FCFD opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFCFF);return StepResult::executed;
  case 0x3FCFF: // $FCFF opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFD01);return StepResult::executed;
  case 0x3FD01: // $FD01 opcode $46, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::zp>(0x0011,0xFD03);return StepResult::executed;
  case 0x3FD03: // $FD03 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0053,0xFD05);return StepResult::executed;
  case 0x3FD05: // $FD05 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFD06);return StepResult::executed;
  case 0x3FD06: // $FD06 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0010,0xFD08);return StepResult::executed;
  case 0x3FD08: // $FD08 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0013,0xFD0A);return StepResult::executed;
  case 0x3FD0A: // $FD0A opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0054,0xFD0C);return StepResult::executed;
  case 0x3FD0C: // $FD0C opcode $69, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::imm>(0x0000,0xFD0E);return StepResult::executed;
  case 0x3FD0E: // $FD0E opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0014,0xFD10);return StepResult::executed;
  case 0x3FD10: // $FD10 opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFD11);return StepResult::executed;
  case 0x3FD11: // $FD11 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0013,0xFD13);return StepResult::executed;
  case 0x3FD13: // $FD13 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD14);return StepResult::executed;
  case 0x3FD14: // $FD14 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD15);return StepResult::executed;
  case 0x3FD15: // $FD15 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD16);return StepResult::executed;
  case 0x3FD16: // $FD16 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD17);return StepResult::executed;
  case 0x3FD17: // $FD17 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD18);return StepResult::executed;
  case 0x3FD18: // $FD18 opcode $19, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::absy>(0xFD62,0xFD1B);return StepResult::executed;
  case 0x3FD1B: // $FD1B opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x000C,0xFD1D);return StepResult::executed;
  case 0x3FD1D: // $FD1D opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFD24,0xFD1F);return StepResult::executed;
  case 0x3FD1F: // $FD1F opcode $E9, HISTORICALLY_VERIFIED
   cpu.exec<Op::SBC,Mode::imm>(0x000C,0xFD21);return StepResult::executed;
  case 0x3FD21: // $FD21 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFD1B,0xFD24);return StepResult::executed;
  case 0x3FD24: // $FD24 opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFD25);return StepResult::executed;
  case 0x3FD25: // $FD25 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0xFD4D,0xFD28);return StepResult::executed;
  case 0x3FD28: // $FD28 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFD29);return StepResult::executed;
  case 0x3FD29: // $FD29 opcode $65, HISTORICALLY_VERIFIED
   cpu.exec<Op::ADC,Mode::zp>(0x0011,0xFD2B);return StepResult::executed;
  case 0x3FD2B: // $FD2B opcode $A8, HISTORICALLY_VERIFIED
   cpu.exec<Op::TAY,Mode::imp>(0x0000,0xFD2C);return StepResult::executed;
  case 0x3FD2C: // $FD2C opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0013,0xFD2E);return StepResult::executed;
  case 0x3FD2E: // $FD2E opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0010,0xFD30);return StepResult::executed;
  case 0x3FD30: // $FD30 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFD40,0xFD32);return StepResult::executed;
  case 0x3FD32: // $FD32 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFD34);return StepResult::executed;
  case 0x3FD34: // $FD34 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x00A2,0xFD36);return StepResult::executed;
  case 0x3FD36: // $FD36 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0x06E0,0xFD39);return StepResult::executed;
  case 0x3FD39: // $FD39 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD3A);return StepResult::executed;
  case 0x3FD3A: // $FD3A opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD3B);return StepResult::executed;
  case 0x3FD3B: // $FD3B opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD3C);return StepResult::executed;
  case 0x3FD3C: // $FD3C opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFD3D);return StepResult::executed;
  case 0x3FD3D: // $FD3D opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0000,0xFD3F);return StepResult::executed;
  case 0x3FD3F: // $FD3F opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFD40);return StepResult::executed;
  case 0x3FD40: // $FD40 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0001,0xFD42);return StepResult::executed;
  case 0x3FD42: // $FD42 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x00A2,0xFD44);return StepResult::executed;
  case 0x3FD44: // $FD44 opcode $B9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absy>(0x06E0,0xFD47);return StepResult::executed;
  case 0x3FD47: // $FD47 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x000F,0xFD49);return StepResult::executed;
  case 0x3FD49: // $FD49 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFD4A);return StepResult::executed;
  case 0x3FD4A: // $FD4A opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFD4C);return StepResult::executed;
  case 0x3FD4C: // $FD4C opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFD4D);return StepResult::executed;
  case 0x3FDE4: // $FDE4 opcode $E6, HISTORICALLY_VERIFIED
   cpu.exec<Op::INC,Mode::zp>(0x00A0,0xFDE6);return StepResult::executed;
  case 0x3FDE6: // $FDE6 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x00FF,0xFDE8);return StepResult::executed;
  case 0x3FDE8: // $FDE8 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x008F,0xFDEA);return StepResult::executed;
  case 0x3FDEA: // $FDEA opcode $A2, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::imm>(0x0001,0xFDEC);return StepResult::executed;
  case 0x3FDEC: // $FDEC opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x054E,0xFDEF);return StepResult::executed;
  case 0x3FDEF: // $FDEF opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFE6E,0xFDF1);return StepResult::executed;
  case 0x3FDF1: // $FDF1 opcode $86, HISTORICALLY_VERIFIED
   cpu.exec<Op::STX,Mode::zp>(0x0069,0xFDF3);return StepResult::executed;
  case 0x3FDF3: // $FDF3 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xFDF5);return StepResult::executed;
  case 0x3FDF5: // $FDF5 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFDF8);return StepResult::executed;
  case 0x3FDF8: // $FDF8 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x80E3,0xFDFB);return StepResult::executed;
  case 0x3FDFB: // $FDFB opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xB1F8,0xFDFE);return StepResult::executed;
  case 0x3FDFE: // $FDFE opcode $A6, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::zp>(0x0069,0xFE00);return StepResult::executed;
  case 0x3FE00: // $FE00 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x054E,0xFE03);return StepResult::executed;
  case 0x3FE03: // $FE03 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFE6E,0xFE05);return StepResult::executed;
  case 0x3FE05: // $FE05 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0030,0xFE07);return StepResult::executed;
  case 0x3FE07: // $FE07 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFE16,0xFE09);return StepResult::executed;
  case 0x3FE09: // $FE09 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0009,0xFE0B);return StepResult::executed;
  case 0x3FE0B: // $FE0B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFE0E);return StepResult::executed;
  case 0x3FE0E: // $FE0E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xFE11);return StepResult::executed;
  case 0x3FE11: // $FE11 opcode $A6, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::zp>(0x0069,0xFE13);return StepResult::executed;
  case 0x3FE13: // $FE13 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFE34,0xFE16);return StepResult::executed;
  case 0x3FE16: // $FE16 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0470,0xFE19);return StepResult::executed;
  case 0x3FE19: // $FE19 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0002,0xFE1B);return StepResult::executed;
  case 0x3FE1B: // $FE1B opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFE23,0xFE1D);return StepResult::executed;
  case 0x3FE1D: // $FE1D opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFE8C,0xFE20);return StepResult::executed;
  case 0x3FE20: // $FE20 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFE63,0xFE23);return StepResult::executed;
  case 0x3FE23: // $FE23 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x054E,0xFE26);return StepResult::executed;
  case 0x3FE26: // $FE26 opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xFE31,0xFE28);return StepResult::executed;
  case 0x3FE28: // $FE28 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0069,0xFE2A);return StepResult::executed;
  case 0x3FE2A: // $FE2A opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFE36,0xFE2C);return StepResult::executed;
  case 0x3FE2C: // $FE2C opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xFF56,0xFE2F);return StepResult::executed;
  case 0x3FE2F: // $FE2F opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFE63,0xFE31);return StepResult::executed;
  case 0x3FE31: // $FE31 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xBD11,0xFE34);return StepResult::executed;
  case 0x3FE34: // $FE34 opcode $A6, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDX,Mode::zp>(0x0069,0xFE36);return StepResult::executed;
  case 0x3FE36: // $FE36 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x054E,0xFE39);return StepResult::executed;
  case 0x3FE39: // $FE39 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0058,0xFE3B);return StepResult::executed;
  case 0x3FE3B: // $FE3B opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFE45,0xFE3D);return StepResult::executed;
  case 0x3FE3D: // $FE3D opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0030,0xFE3F);return StepResult::executed;
  case 0x3FE3F: // $FE3F opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFE45,0xFE41);return StepResult::executed;
  case 0x3FE41: // $FE41 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x00A8,0xFE43);return StepResult::executed;
  case 0x3FE43: // $FE43 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFE63,0xFE45);return StepResult::executed;
  case 0x3FE45: // $FE45 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0470,0xFE48);return StepResult::executed;
  case 0x3FE48: // $FE48 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0040,0xFE4A);return StepResult::executed;
  case 0x3FE4A: // $FE4A opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFE54,0xFE4C);return StepResult::executed;
  case 0x3FE4C: // $FE4C opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xFE4E);return StepResult::executed;
  case 0x3FE4E: // $FE4E opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFE51);return StepResult::executed;
  case 0x3FE51: // $FE51 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8001,0xFE54);return StepResult::executed;
  case 0x3FE54: // $FE54 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x054E,0xFE57);return StepResult::executed;
  case 0x3FE57: // $FE57 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFE6E,0xFE59);return StepResult::executed;
  case 0x3FE59: // $FE59 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0470,0xFE5C);return StepResult::executed;
  case 0x3FE5C: // $FE5C opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0020,0xFE5E);return StepResult::executed;
  case 0x3FE5E: // $FE5E opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFE63,0xFE60);return StepResult::executed;
  case 0x3FE60: // $FE60 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xEF93,0xFE63);return StepResult::executed;
  case 0x3FE63: // $FE63 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000B,0xFE65);return StepResult::executed;
  case 0x3FE65: // $FE65 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFE68);return StepResult::executed;
  case 0x3FE68: // $FE68 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x8161,0xFE6B);return StepResult::executed;
  case 0x3FE6B: // $FE6B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x826C,0xFE6E);return StepResult::executed;
  case 0x3FE6E: // $FE6E opcode $E8, HISTORICALLY_VERIFIED
   cpu.exec<Op::INX,Mode::imp>(0x0000,0xFE6F);return StepResult::executed;
  case 0x3FE6F: // $FE6F opcode $E0, HISTORICALLY_VERIFIED
   cpu.exec<Op::CPX,Mode::imm>(0x0013,0xFE71);return StepResult::executed;
  case 0x3FE71: // $FE71 opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFE76,0xFE73);return StepResult::executed;
  case 0x3FE73: // $FE73 opcode $4C, HISTORICALLY_VERIFIED
   cpu.exec<Op::JMP,Mode::abs>(0xFDEC,0xFE76);return StepResult::executed;
  case 0x3FE76: // $FE76 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x000A,0xFE78);return StepResult::executed;
  case 0x3FE78: // $FE78 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE2D0,0xFE7B);return StepResult::executed;
  case 0x3FE7B: // $FE7B opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0x84EA,0xFE7E);return StepResult::executed;
  case 0x3FE7E: // $FE7E opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x0089,0xFE80);return StepResult::executed;
  case 0x3FE80: // $FE80 opcode $30, HISTORICALLY_VERIFIED
   cpu.exec<Op::BMI,Mode::rel>(0xFE8B,0xFE82);return StepResult::executed;
  case 0x3FE82: // $FE82 opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0089,0xFE84);return StepResult::executed;
  case 0x3FE84: // $FE84 opcode $10, HISTORICALLY_VERIFIED
   cpu.exec<Op::BPL,Mode::rel>(0xFE8B,0xFE86);return StepResult::executed;
  case 0x3FE86: // $FE86 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0000,0xFE88);return StepResult::executed;
  case 0x3FE88: // $FE88 opcode $8D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::abs>(0x0417,0xFE8B);return StepResult::executed;
  case 0x3FE8B: // $FE8B opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFE8C);return StepResult::executed;
  case 0x3FE8C: // $FE8C opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0565,0xFE8F);return StepResult::executed;
  case 0x3FE8F: // $FE8F opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFE90);return StepResult::executed;
  case 0x3FE90: // $FE90 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFE91);return StepResult::executed;
  case 0x3FE91: // $FE91 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFE92);return StepResult::executed;
  case 0x3FE92: // $FE92 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFE93);return StepResult::executed;
  case 0x3FE93: // $FE93 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFE94);return StepResult::executed;
  case 0x3FE94: // $FE94 opcode $4A, HISTORICALLY_VERIFIED
   cpu.exec<Op::LSR,Mode::acc>(0x0000,0xFE95);return StepResult::executed;
  case 0x3FE95: // $FE95 opcode $20, HISTORICALLY_VERIFIED
   cpu.exec<Op::JSR,Mode::abs>(0xE7FB,0xFE98);return StepResult::executed;
  case 0x3FE9E: // $FE9E opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0080,0xFEA0);return StepResult::executed;
  case 0x3FEA0: // $FEA0 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x05D8,0xFEA3);return StepResult::executed;
  case 0x3FEA3: // $FEA3 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0004,0xFEA5);return StepResult::executed;
  case 0x3FEA5: // $FEA5 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0454,0xFEA8);return StepResult::executed;
  case 0x3FEA8: // $FEA8 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0565,0xFEAB);return StepResult::executed;
  case 0x3FEAB: // $FEAB opcode $09, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::imm>(0x0040,0xFEAD);return StepResult::executed;
  case 0x3FEAD: // $FEAD opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0565,0xFEB0);return StepResult::executed;
  case 0x3FEB0: // $FEB0 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFEB1);return StepResult::executed;
  case 0x3FEB1: // $FEB1 opcode $DE, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::absx>(0x05D8,0xFEB4);return StepResult::executed;
  case 0x3FEB4: // $FEB4 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFEC5,0xFEB6);return StepResult::executed;
  case 0x3FEB6: // $FEB6 opcode $A9, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::imm>(0x0008,0xFEB8);return StepResult::executed;
  case 0x3FEB8: // $FEB8 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x05D8,0xFEBB);return StepResult::executed;
  case 0x3FEBB: // $FEBB opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0565,0xFEBE);return StepResult::executed;
  case 0x3FEBE: // $FEBE opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00BF,0xFEC0);return StepResult::executed;
  case 0x3FEC0: // $FEC0 opcode $09, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::imm>(0x0080,0xFEC2);return StepResult::executed;
  case 0x3FEC2: // $FEC2 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0565,0xFEC5);return StepResult::executed;
  case 0x3FEC5: // $FEC5 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFEC6);return StepResult::executed;
  case 0x3FEC6: // $FEC6 opcode $A5, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::zp>(0x001B,0xFEC8);return StepResult::executed;
  case 0x3FEC8: // $FEC8 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x0003,0xFECA);return StepResult::executed;
  case 0x3FECA: // $FECA opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFEC5,0xFECC);return StepResult::executed;
  case 0x3FECC: // $FECC opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0454,0xFECF);return StepResult::executed;
  case 0x3FECF: // $FECF opcode $49, HISTORICALLY_VERIFIED
   cpu.exec<Op::EOR,Mode::imm>(0x0004,0xFED1);return StepResult::executed;
  case 0x3FED1: // $FED1 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0454,0xFED4);return StepResult::executed;
  case 0x3FED4: // $FED4 opcode $DE, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::absx>(0x05D8,0xFED7);return StepResult::executed;
  case 0x3FED7: // $FED7 opcode $D0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BNE,Mode::rel>(0xFEC5,0xFED9);return StepResult::executed;
  case 0x3FED9: // $FED9 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0470,0xFEDC);return StepResult::executed;
  case 0x3FEDC: // $FEDC opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00FD,0xFEDE);return StepResult::executed;
  case 0x3FEDE: // $FEDE opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0470,0xFEE1);return StepResult::executed;
  case 0x3FEE1: // $FEE1 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0454,0xFEE4);return StepResult::executed;
  case 0x3FEE4: // $FEE4 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00FB,0xFEE6);return StepResult::executed;
  case 0x3FEE6: // $FEE6 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0454,0xFEE9);return StepResult::executed;
  case 0x3FEE9: // $FEE9 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFEEA);return StepResult::executed;
  case 0x3FF56: // $FF56 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x054E,0xFF59);return StepResult::executed;
  case 0x3FF59: // $FF59 opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0038,0xFF5B);return StepResult::executed;
  case 0x3FF5B: // $FF5B opcode $90, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCC,Mode::rel>(0xFF79,0xFF5D);return StepResult::executed;
  case 0x3FF5D: // $FF5D opcode $C9, HISTORICALLY_VERIFIED
   cpu.exec<Op::CMP,Mode::imm>(0x0058,0xFF5F);return StepResult::executed;
  case 0x3FF5F: // $FF5F opcode $B0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BCS,Mode::rel>(0xFF78,0xFF61);return StepResult::executed;
  case 0x3FF61: // $FF61 opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0565,0xFF64);return StepResult::executed;
  case 0x3FF64: // $FF64 opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x003F,0xFF66);return StepResult::executed;
  case 0x3FF66: // $FF66 opcode $F0, HISTORICALLY_VERIFIED
   cpu.exec<Op::BEQ,Mode::rel>(0xFF78,0xFF68);return StepResult::executed;
  case 0x3FF68: // $FF68 opcode $85, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::zp>(0x0017,0xFF6A);return StepResult::executed;
  case 0x3FF6A: // $FF6A opcode $C6, HISTORICALLY_VERIFIED
   cpu.exec<Op::DEC,Mode::zp>(0x0017,0xFF6C);return StepResult::executed;
  case 0x3FF6C: // $FF6C opcode $BD, HISTORICALLY_VERIFIED
   cpu.exec<Op::LDA,Mode::absx>(0x0565,0xFF6F);return StepResult::executed;
  case 0x3FF6F: // $FF6F opcode $29, HISTORICALLY_VERIFIED
   cpu.exec<Op::AND,Mode::imm>(0x00C0,0xFF71);return StepResult::executed;
  case 0x3FF71: // $FF71 opcode $05, HISTORICALLY_VERIFIED
   cpu.exec<Op::ORA,Mode::zp>(0x0017,0xFF73);return StepResult::executed;
  case 0x3FF73: // $FF73 opcode $9D, HISTORICALLY_VERIFIED
   cpu.exec<Op::STA,Mode::absx>(0x0565,0xFF76);return StepResult::executed;
  case 0x3FF76: // $FF76 opcode $38, HISTORICALLY_VERIFIED
   cpu.exec<Op::SEC,Mode::imp>(0x0000,0xFF77);return StepResult::executed;
  case 0x3FF77: // $FF77 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFF78);return StepResult::executed;
  case 0x3FF78: // $FF78 opcode $18, HISTORICALLY_VERIFIED
   cpu.exec<Op::CLC,Mode::imp>(0x0000,0xFF79);return StepResult::executed;
  case 0x3FF79: // $FF79 opcode $60, HISTORICALLY_VERIFIED
   cpu.exec<Op::RTS,Mode::imp>(0x0000,0xFF7A);return StepResult::executed;
 default:return StepResult::unresolved;
 }
}
}
