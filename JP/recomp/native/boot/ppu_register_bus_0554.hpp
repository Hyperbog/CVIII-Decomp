#pragma once
// Opt-in direct 2C02 $2000/$2001 writes and $2002 status reads.
// A transaction is timestamped at the START of its final CPU bus cycle.
// All other PPU registers/CPU-address shapes fail closed; open bus and
// dot-level VBlank races are not emulated.
#include "ntsc_ppu_clock_0554.hpp"
#include "oam_dma_0554.hpp"
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
  void attach_oam(RamOamDma* device) {oam_=device;}
  void arm_final_cycle(){armed_=true;}
  void disarm(){armed_=false;}
  const std::vector<TimedPpuAccess>& events() const {return events_;}
  uint8_t read(uint16_t address) {
   check_armed();
   const auto reg=uint16_t(0x2000u+(address&7u));
   if(reg!=0x2002 && reg!=0x2004)
    throw std::runtime_error("unmodeled 2C02 register read");
   uint8_t result=0;
   if(reg==0x2002)result=clock_.read_status_vblank_only();
   else {
    check_oam_blanking();
    result=oam_->read_oam_data(); // Unlike writes, reads do not increment.
   }
   record(address,reg,result,false);
   return result;
  }
  void write(uint16_t address,uint8_t value) {
   check_armed();
   const auto reg=uint16_t(0x2000u+(address&7u));
   if(reg==0x2000) clock_.write_control(value);
   else if(reg==0x2001) clock_.write_mask(value);
   else if(reg==0x2003 || reg==0x2004) {
    check_oam_blanking();
    if(reg==0x2003)oam_->write_oam_address(value);
    else oam_->write_oam_data(value);
   } else throw std::runtime_error("unmodeled 2C02 register write");
   record(address,reg,value,true);
  }
 private:
  void check_oam_blanking() const {
   if(!oam_)throw std::runtime_error("OAM register needs explicitly attached OAM device");
   if(clock_.active_rendering())
    throw std::runtime_error("rendering-time OAM behavior is unmodeled");
  }
  void check_armed() const {
   if(!armed_)throw std::runtime_error("2C02 access lacks supported final CPU bus-cycle schedule");
  }
  void record(uint16_t cpu,uint16_t reg,uint8_t value,bool write) {
   events_.push_back(TimedPpuAccess{
      cpu,reg,value,write,clock_.cpu_cycles()+1,clock_.ppu_dots(),
      clock_.scanline(),clock_.dot()});
  }
  NtscPpuClock& clock_;
  RamOamDma* oam_=nullptr;
  bool armed_=false;
  std::vector<TimedPpuAccess> events_;
};
} // namespace jpstatic
