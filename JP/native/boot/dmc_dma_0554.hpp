#pragma once
// CPU-read-boundary DMC DMA sample fetch, no automatic APU playback.
// The caller provides the CPU get/put phase and asserts a legal CPU read
// boundary explicitly. OAM/DMC overlap and side-effect read retries excluded.
#include <cstdint>
#include <stdexcept>

namespace jpstatic {
enum class DmcFetchKind { load, reload };
struct DmcFetchRecord {
 uint16_t source=0;
 uint8_t byte=0;
 DmcFetchKind kind=DmcFetchKind::load;
 uint64_t get_cycle=0;
 unsigned stall_cycles=0;
};
class DmcDmaSampler {
 public:
  void set_get_cycle_parity(unsigned parity) {
   if(parity>1)throw std::runtime_error("DMC DMA requires explicit CPU get parity");
   get_parity_=parity;phase_known_=true;
  }
  unsigned get_cycle_parity() const {return get_parity_;}
  void request(uint16_t source, DmcFetchKind kind) {
   if(!phase_known_)throw std::runtime_error("DMC DMA CPU phase not configured");
   // NES DMC sample reader addresses start at $C000. $8000-$BFFF
   // mapping is neither needed nor supported by this bounded interface.
   if(source<0xc000)throw std::runtime_error("DMC DMA sample address outside $C000-$FFFF");
   if(pending_)throw std::runtime_error("overlapping DMC requests unsupported");
   pending_=true;source_=source;kind_=kind;
  }
  template<typename Reader,typename Clock>
  unsigned service_at_read_boundary(uint64_t cpu_cycles,Reader read,Clock clock) {
   if(!pending_)return 0;
   // Preconditions: caller supplies a CPU read boundary at which RDY can
   // halt, with no competing OAM DMA and no CPU read-side effects.
   pending_=false;
   unsigned elapsed=0;
   auto tick=[&](){clock(1);++elapsed;};
   tick();  // CPU read-halt cycle.
   tick();  // DMC dummy cycle.
   const bool align=((cpu_cycles+elapsed+1u)&1u)!=get_parity_;
   if(align)tick();
   tick();  // DMC get.
   last_=DmcFetchRecord{source_,read(source_),kind_,cpu_cycles+elapsed,elapsed};
   ++completed_;
   if(elapsed!=(align?4u:3u))
    throw std::runtime_error("DMC DMA 3/4 cycle accounting drift");
   return elapsed;
  }
  bool pending() const {return pending_;}
  uint64_t completed_fetches() const {return completed_;}
  const DmcFetchRecord& last_fetch() const {return last_;}
 private:
  bool phase_known_=false,pending_=false;
  unsigned get_parity_=0;
  uint16_t source_=0xc000;
  DmcFetchKind kind_=DmcFetchKind::load;
  DmcFetchRecord last_{};
  uint64_t completed_=0;
};
} // namespace jpstatic
