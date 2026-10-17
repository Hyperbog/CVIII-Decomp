#pragma once
// Included inside namespace jpstatic after Op and Mode declarations.
// Official 2A03/NMOS-6502 base CPU cycles. Indexed read and branch penalties
// are applied separately by Cpu::exec; DMA stalls are intentionally excluded.
template<Op O, Mode M> constexpr unsigned base_cpu_cycles_0554() {
  if constexpr (O==Op::BRK) return 7;
  else if constexpr (O==Op::ORA || O==Op::AND || O==Op::EOR ||
                     O==Op::ADC || O==Op::SBC || O==Op::CMP || O==Op::LDA) {
    if constexpr (M==Mode::imm) return 2;
    else if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::zpx) return 4;
    else if constexpr (M==Mode::abs || M==Mode::absx || M==Mode::absy) return 4;
    else if constexpr (M==Mode::indx) return 6;
    else if constexpr (M==Mode::indy) return 5;
  } else if constexpr (O==Op::LDX) {
    if constexpr (M==Mode::imm) return 2;
    else if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::zpy || M==Mode::abs || M==Mode::absy) return 4;
  } else if constexpr (O==Op::LDY) {
    if constexpr (M==Mode::imm) return 2;
    else if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::zpx || M==Mode::abs || M==Mode::absx) return 4;
  } else if constexpr (O==Op::CPX || O==Op::CPY) {
    if constexpr (M==Mode::imm) return 2;
    else if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::abs) return 4;
  } else if constexpr (O==Op::BIT) {
    if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::abs) return 4;
  } else if constexpr (O==Op::STA) {
    if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::zpx) return 4;
    else if constexpr (M==Mode::absx || M==Mode::absy) return 5;
    else if constexpr (M==Mode::abs) return 4;
    else if constexpr (M==Mode::indx || M==Mode::indy) return 6;
  } else if constexpr (O==Op::STX) {
    if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::zpy || M==Mode::abs) return 4;
  } else if constexpr (O==Op::STY) {
    if constexpr (M==Mode::zp) return 3;
    else if constexpr (M==Mode::zpx || M==Mode::abs) return 4;
  } else if constexpr (O==Op::ASL || O==Op::LSR || O==Op::ROL || O==Op::ROR) {
    if constexpr (M==Mode::acc) return 2;
    else if constexpr (M==Mode::zp) return 5;
    else if constexpr (M==Mode::zpx || M==Mode::abs) return 6;
    else if constexpr (M==Mode::absx) return 7;
  } else if constexpr (O==Op::INC || O==Op::DEC) {
    if constexpr (M==Mode::zp) return 5;
    else if constexpr (M==Mode::zpx || M==Mode::abs) return 6;
    else if constexpr (M==Mode::absx) return 7;
  } else if constexpr (O==Op::BPL || O==Op::BMI || O==Op::BVC || O==Op::BVS ||
                       O==Op::BCC || O==Op::BCS || O==Op::BNE || O==Op::BEQ) {
    if constexpr (M==Mode::rel) return 2;
  } else if constexpr (O==Op::JMP) {
    if constexpr (M==Mode::abs) return 3;
    else if constexpr (M==Mode::ind) return 5;
  } else if constexpr (O==Op::JSR) {
    if constexpr (M==Mode::abs) return 6;
  } else if constexpr (O==Op::RTS || O==Op::RTI) {
    if constexpr (M==Mode::imp) return 6;
  } else if constexpr (O==Op::PHA || O==Op::PHP) {
    if constexpr (M==Mode::imp) return 3;
  } else if constexpr (O==Op::PLA || O==Op::PLP) {
    if constexpr (M==Mode::imp) return 4;
  } else if constexpr (O==Op::CLC || O==Op::SEC || O==Op::CLI || O==Op::SEI ||
                       O==Op::CLV || O==Op::CLD || O==Op::SED || O==Op::DEY ||
                       O==Op::INY || O==Op::DEX || O==Op::INX || O==Op::TAX ||
                       O==Op::TAY || O==Op::TXA || O==Op::TYA || O==Op::TSX ||
                       O==Op::TXS || O==Op::NOP) {
    if constexpr (M==Mode::imp) return 2;
  }
  return 0; // Unrecognized opcode/address-mode pairs fail at compile time.
}
template<Op O,Mode M> constexpr bool indexed_read_penalty_0554() {
  constexpr bool is_read=(O==Op::ORA || O==Op::AND || O==Op::EOR ||
                           O==Op::ADC || O==Op::SBC || O==Op::CMP ||
                           O==Op::LDA || O==Op::LDX || O==Op::LDY);
  return is_read && (M==Mode::absx || M==Mode::absy || M==Mode::indy);
}
