#pragma once
// Opt-in direct 2C02 $2000/$2001 writes and $2002 status reads.
// A transaction is timestamped at the START of its final CPU bus cycle.
// All other PPU registers/CPU-address shapes fail closed; open bus and
// dot-level VBlank races are not emulated.
#include "ntsc_ppu_clock_0554.hpp"
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace jpstatic {
struct TimedPpuAccess {
 uint16_t cpu_address=0, register_address=0;
 uint8_t value=0;
 bool is_write=false;
 uint64_t cpu_cycle=0, ppu_dot=0;
 unsigned scanline=0, dot=0;
};
class ClockedPpuRegisters {
 public:
  explicit ClockedPpuRegisters(NtscPpuClock& clock):clock_(clock){}
  void arm_final_cycle(){armed_=true;}
  void disarm(){armed_=false;}
  const std::vector<TimedPpuAccess>& events() const {return events_;}
  uint8_t read(uint16_t address) {
   check_armed();
   const auto reg=uint16_t(0x2000u+(address&7u));
   if(reg!=0x2002)throw std::runtime_error("unmodeled 2C02 register read");
   const uint8_t result=clock_.read_status_vblank_only();
   record(address,reg,result,false);
   return result;
  }
  void write(uint16_t address,uint8_t value) {
   check_armed();
   const auto reg=uint16_t(0x2000u+(address&7u));
   if(reg==0x2000) clock_.write_control(value);
   else if(reg==0x2001) clock_.write_mask(value);
   else throw std::runtime_error("unmodeled 2C02 register write");
   record(address,reg,value,true);
  }
 private:
  void check_armed() const {
   if(!armed_)throw std::runtime_error("2C02 access lacks supported final CPU bus-cycle schedule");
  }
  void record(uint16_t cpu,uint16_t reg,uint8_t value,bool write) {
   events_.push_back(TimedPpuAccess{
      cpu,reg,value,write,clock_.cpu_cycles()+1,clock_.ppu_dots(),
      clock_.scanline(),clock_.dot()});
  }
  NtscPpuClock& clock_;
  bool armed_=false;
  std::vector<TimedPpuAccess> events_;
};
} // namespace jpstatic
