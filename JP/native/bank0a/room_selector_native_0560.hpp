#pragma once
// Direct host-C++ translation of JP VRC6 physical raw0A $801E-$8046.
// Operates on user-supplied 16 KiB bank data; DOES NOT embed the game ROM.
// Original 6502: $34 -> $92AE[] -> $06/$07, $35 -> $04/$05,
//                $36 -> $95/$96. Field contents remain uninterpreted.
#include <array>
#include <cstdint>
#include <stdexcept>

namespace jpstatic {
enum class Room0aPayloadKind { four_byte_cells, seven_byte_stream };
struct Room0aSelection {
 uint16_t stage_pointer=0, middle_pointer=0, leaf_pointer=0;
 Room0aPayloadKind kind=Room0aPayloadKind::four_byte_cells;
};
class Room0aSelector0560 {
 public:
  explicit Room0aSelector0560(const std::array<uint8_t,16384>& bank):bank_(bank) {
   // A known original hierarchical table is treated as DATA, never decoded
   // as instructions. Each bound below is independently source-derived.
   for(unsigned i=0;i<15;++i)stage_roots_[i]=word(0x92ae+2*i);
   unsigned count=0;
   for(unsigned i=0;i<15;++i) {
    const uint16_t lo=stage_roots_[i];
    const uint16_t hi=i==8?0x9320:i==14?0x9b20:stage_roots_[i+1];
    const bool first=i<9;
    if(lo<(first?0x92cc:0x9af4) || hi>(first?0x9320:0x9b20) ||
       hi<=lo || ((hi-lo)&1u) || count+(hi-lo)/2>64)
     throw std::runtime_error("raw0A first/second-level table extent invalid");
    stage_begin_[i]=count;
    for(uint16_t at=lo;at<hi;at=uint16_t(at+2))
      middle_roots_[count++]=word(at);
   }
   stage_begin_[15]=count;
   if(count!=64 || stage_roots_[0]!=0x92cc || stage_roots_[9]!=0x9af4)
    throw std::runtime_error("raw0A table must have fifteen roots and 64 links");
   unsigned leaves=0;
   for(unsigned i=0;i<64;++i) {
    const uint16_t lo=middle_roots_[i];
    const uint16_t hi=i==41?0x93cc:i==63?0x9b82:middle_roots_[i+1];
    const bool first=i<42;
    if(lo<(first?0x9320:0x9b20) || hi>(first?0x93cc:0x9b82) ||
       hi<=lo || ((hi-lo)&1u))
     throw std::runtime_error("raw0A third-level selector extent invalid");
    const unsigned n=(hi-lo)/2u;
    leaf_counts_[i]=n;
    leaves+=n;
   }
   if(leaves!=135)
    throw std::runtime_error("raw0A must expose 135 locally bounded leaf choices");
  }
  Room0aSelection select(unsigned stage,unsigned second,unsigned third) const {
   if(stage>=15)throw std::runtime_error("raw0A stage selector out of range");
   const unsigned mid_index=stage_begin_[stage]+second;
   if(mid_index>=stage_begin_[stage+1])
    throw std::runtime_error("raw0A second selector out of range");
   if(third>=leaf_counts_[mid_index])
    throw std::runtime_error("raw0A third selector out of range");
   const uint16_t p1=stage_roots_[stage],p2=middle_roots_[mid_index];
   const uint16_t leaf=word(unsigned(p2)+third*2u);
   Room0aPayloadKind kind;
   if((leaf>=0x93cc && leaf<0x9af4 && (leaf-0x93cc)%4==0) ||
      (leaf>=0x9b82 && leaf<0x9f6e && (leaf-0x9b82)%4==0))
    kind=Room0aPayloadKind::four_byte_cells;
   else if(leaf>=0xab1f && leaf<0xafa4)
    kind=Room0aPayloadKind::seven_byte_stream;
   else throw std::runtime_error("raw0A leaf outside original typed data pools");
   return Room0aSelection{p1,p2,leaf,kind};
  }
 private:
  uint16_t word(unsigned cpu) const {
   if(cpu<0x8000 || cpu+1>=0xc000)
    throw std::runtime_error("raw0A data word escapes physical bank0A");
   const unsigned offset=cpu-0x8000;
   return uint16_t(unsigned(bank_[offset]) | (unsigned(bank_[offset+1])<<8));
  }
  const std::array<uint8_t,16384>& bank_;
  std::array<uint16_t,15> stage_roots_{};
  std::array<uint16_t,64> middle_roots_{};
  std::array<unsigned,16> stage_begin_{};
  std::array<unsigned,64> leaf_counts_{};
};
} // namespace jpstatic
