#pragma once
// NTSC OAM DMA, bounded to CPU internal RAM and mirrors $0000-$1FFF.
// Implements 513/514 CPU-cycle stalls and 256 OAM byte transfers.
// No DMC arbitration, open bus, $2003 live register, or non-RAM reads.
#include <array>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace jpstatic {
struct RamOamDmaByte {
 uint16_t source=0;
 uint8_t destination=0, value=0;
 uint64_t get_cycle=0, put_cycle=0;
};
class RamOamDma {
 public:
  void set_get_cycle_parity(unsigned parity) {
   if(parity>1)throw std::runtime_error("OAM DMA requires explicit get/put CPU phase");
   get_parity_=parity;
   phase_known_=true;
  }
  void set_oam_address_for_test(uint8_t address) {oam_address_=address;}
  void write_oam_address(uint8_t address) {oam_address_=address;}
  // OAMDATA direct access is allowed only by the PPU-side blanking gate.
  uint8_t read_oam_data() const {return oam_[oam_address_];}
  void write_oam_data(uint8_t value) {oam_[oam_address_++]=value;}
  uint8_t oam_address() const {return oam_address_;}
  const std::array<uint8_t,256>& oam() const {return oam_;}
  const std::vector<RamOamDmaByte>& last_bytes() const {return bytes_;}
  bool pending() const {return pending_;}
  uint8_t source_page() const {return source_page_;}
  unsigned get_cycle_parity() const {return get_parity_;}
  uint64_t completed_transfers() const {return completed_transfers_;}
  unsigned last_stall_cycles() const {return last_stall_cycles_;}
  void request(uint8_t source_page) {
   if(!phase_known_)throw std::runtime_error("OAM DMA get/put phase unspecified");
   if(source_page>=0x20)
    throw std::runtime_error("OAM DMA source outside supported mirrored internal RAM");
   source_page_=source_page;  // Last $4014 write wins before next CPU read.
   pending_=true;
  }
  template<typename Clock> unsigned complete(uint64_t cpu_cycles,
        const std::array<uint8_t,2048>& ram,Clock clock) {
   if(!pending_)return 0;
   pending_=false;
   const bool alignment=(((cpu_cycles+1u)&1u)==get_parity_);
   unsigned elapsed=0;
   auto tick=[&](){clock(1);++elapsed;};
   // Mandatory CPU read-halt attempt and optional get/put alignment.
   tick();
   if(alignment)tick();
   bytes_.clear();
   bytes_.reserve(256);
   for(unsigned i=0;i<256;++i) {
    const uint16_t from=uint16_t((unsigned(source_page_)<<8)|i);
    tick(); // CPU-memory get cycle.
    const uint8_t value=ram[from&0x07ffu];
    const uint64_t get_at=cpu_cycles+elapsed;
    tick(); // OAMDATA put cycle.
    const uint64_t put_at=cpu_cycles+elapsed;
    bytes_.push_back(RamOamDmaByte{from,oam_address_,value,get_at,put_at});
    oam_[oam_address_++]=value; // 8-bit OAMADDR wraps naturally.
   }
   last_stall_cycles_=elapsed;
   ++completed_transfers_;
   if(elapsed!=(alignment?514u:513u))
    throw std::runtime_error("OAM DMA stall accounting drift");
   return elapsed;
  }
 private:
  std::array<uint8_t,256> oam_{};
  std::vector<RamOamDmaByte> bytes_;
  uint8_t oam_address_=0,source_page_=0;
  unsigned get_parity_=0,last_stall_cycles_=0;
  bool phase_known_=false,pending_=false;
  uint64_t completed_transfers_=0;
};
}  // namespace jpstatic
