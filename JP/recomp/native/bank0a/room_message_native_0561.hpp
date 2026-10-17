#pragma once
// Human-readable native C++ port of original JP raw0A $B8CC-$B908.
// 6502 selector: $07F6/$0781 -> 2 group roots at $B909,
// $07A0 -> one of 5 message pointers, $07A5 -> byte/FF terminator.
// $EC47 rendering/copy is an EXTERNAL DEPENDENCY, not implemented here.
// Source bank supplied privately at runtime; no original ROM embedded.
#include <array>
#include <cstdint>
#include <stdexcept>

namespace jpstatic {
struct Room0aMessageResult {
 uint16_t group_pointer=0;
 uint16_t message_pointer=0;
 uint8_t value=0;
 bool terminal=false;
 unsigned next_offset=0;
};
class Room0aMessageSelector0561 {
 public:
  explicit Room0aMessageSelector0561(const std::array<uint8_t,16384>& bank)
   :bank_(bank) {
   group_roots_[0]=word(0xb909);
   group_roots_[1]=word(0xb90b);
   if(group_roots_[0]!=0xb90d || group_roots_[1]!=0xb917)
    throw std::runtime_error("original raw0A two-group message table drift");
   for(unsigned i=0;i<10;++i)message_roots_[i]=word(0xb90d+2*i);
   if(message_roots_[0]!=0xb921 || message_roots_[9]!=0xb935)
    throw std::runtime_error("original raw0A message roots outside evidence extent");
   unsigned total=0;
   for(unsigned i=0;i<10;++i) {
    const unsigned first=message_roots_[i];
    const unsigned next=i+1<10?message_roots_[i+1]:0xb937;
    if(next<=first || next-first<2 || next-first>3 ||
       byte(next-1)!=0xff)
     throw std::runtime_error("raw0A message must contain 1-2 data bytes and FF");
    for(unsigned at=first;at+1<next;++at)
     if(byte(at)==0xff)
      throw std::runtime_error("raw0A message contains early FF");
    lengths_[i]=next-first;
    total+=lengths_[i];
   }
   if(total!=22)
    throw std::runtime_error("raw0A must contain 22 bytes across 10 messages");
  }
  // Flags are original RAM $07F6 and $0781; the 6502 selects group 1
  // when either is nonzero, otherwise group 0.
  Room0aMessageResult lookup(uint8_t flag07f6,uint8_t flag0781,
                            unsigned stage07a0,unsigned offset07a5) const {
   if(stage07a0>=5)
    throw std::runtime_error("raw0A message stage out of bounded table");
   const unsigned group=(flag07f6 || flag0781)?1u:0u;
   const unsigned index=group*5u+stage07a0;
   if(offset07a5>=lengths_[index])
    throw std::runtime_error("raw0A message byte index escapes terminated stream");
   const uint8_t value=byte(unsigned(message_roots_[index])+offset07a5);
   const bool done=value==0xff;
   return Room0aMessageResult{
    group_roots_[group],message_roots_[index],value,done,
    offset07a5+(done?0u:1u)
   };
  }
  unsigned message_length(unsigned group,unsigned stage) const {
   if(group>=2 || stage>=5)
    throw std::runtime_error("raw0A message selector outside table");
   return lengths_[group*5u+stage];
  }
 private:
  uint8_t byte(unsigned address) const {
   if(address<0x8000 || address>=0xc000)
    throw std::runtime_error("raw0A message byte escapes physical bank");
   return bank_[address-0x8000];
  }
  uint16_t word(unsigned address) const {
   if(address<0x8000 || address+1>=0xc000)
    throw std::runtime_error("raw0A word escapes physical bank");
   return uint16_t(unsigned(byte(address))|(unsigned(byte(address+1))<<8));
  }
  const std::array<uint8_t,16384>& bank_;
  std::array<uint16_t,2> group_roots_{};
  std::array<uint16_t,10> message_roots_{};
  std::array<unsigned,10> lengths_{};
};
} // namespace jpstatic
