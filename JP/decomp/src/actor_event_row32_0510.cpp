#include "actor_event_row32_0510.hpp"
#include "actor_slot_0509.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
constexpr std::uint8_t kRow32=0x32;
constexpr std::uint8_t kType=0x3d;     // original $91EC + $32
constexpr std::uint8_t kScript=0x13;   // original $9194 + $32
constexpr std::uint8_t kAttribute=0x01;// original $924E + $3D
constexpr std::uint8_t kAI=0x20;       // original raw $0B:$A02D+$05/+$25
}
Row32Result run_row32_event(std::array<std::uint8_t,0x800>& ram,
                             std::uint8_t source_x) {
    if(source_x>=6 || ram[0x69]!=source_x ||
       ram[0x07c2u+source_x]!=kRow32 ||
       (ram[0x07c8u+source_x]&0x0f)!=0)
        throw std::invalid_argument("row $32 handler source-entry contract");

    // $8501-$8520: two-level ROM word indirection to $8B2C. This entry is
    // qualified by the caller; source table values are original ROM bytes.
    ram[0x00]=0x26; ram[0x01]=0x8b; // $8523 + $32*2 => $8B26
    ram[0x02]=0x2c; ram[0x03]=0x8b; // ($8B26),Y=0 => $8B2C

    // $8B2C-$8B2F: return immediately when the caller's high bit is nonzero.
    if (ram[0x07e0u+source_x]!=0)
        return {Row32Outcome::Guarded,0,0};

    // $8D5E-$8D75: original event coordinates and row-$32 type/script pair.
    ram[0x00]=ram[0x07dau+source_x];
    ram[0x01]=ram[0x07d4u+source_x];
    ram[0x02]=kScript;
    ram[0x03]=kType;

    // $8DC1-$8DE6: no more than 3 of this type among actor slots 1..8.
    // This counter is distinct from the first-free scanner's 12 slots.
    ram[0x0d]=3;
    ram[0x0e]=0;
    for(std::uint8_t x=1; x<9; ++x) {
        if(ram[0x054eu+x]==kType)
            ram[0x0e]=static_cast<std::uint8_t>(ram[0x0e]+1);
    }
    const auto matching=ram[0x0e];
    const auto slot=matching<3 ? scan_actor_slot(ram) : ActorSlotScan{false,13,1};
    if(!slot.available) {
        // $8B37 -> $8B48: unsuccessful creation sets whole event byte 2.
        ram[0x07c8u+source_x]=2;
        return {Row32Outcome::AtLimit,0,matching};
    }
    const auto x=slot.x;
    // $8D76-$8D90: original fixed-$FF24 18-field reset followed by
    // explicit actor frame, position, script and type stores.
    clear_actor_eighteen_fields(ram,x);
    ram[0x0400u+x]=0;
    ram[0x0438u+x]=ram[0x00];
    ram[0x041cu+x]=ram[0x01];
    ram[0x05efu+x]=ram[0x02];
    ram[0x054eu+x]=ram[0x03];

    // $9244: type-indexed attribute. $E77A -> bank $0B:$A00F then $E62D:
    // type $3D indexes original $A02D table (both relevant entries $20).
    ram[0x067bu+x]=kAttribute;
    ram[0x24]=ram[0x23];  // original mapper helper preserves prior bank
    ram[0x0657u+x]=kAI;

    // $8B50-$8B73: mark actor and encode destination actor slot in
    // originating source object's event high nibble. $85D8 adds one.
    ram[0x0470u+x]=static_cast<std::uint8_t>(ram[0x0470u+x]|0x04);
    ram[0x0645u+x]=ram[0x69];
    ram[0x06]=static_cast<std::uint8_t>(x<<4);
    ram[0x07c8u+source_x]=static_cast<std::uint8_t>(
        (ram[0x07c8u+source_x]&0x0f)|ram[0x06]);
    ram[0x07c8u+source_x]=static_cast<std::uint8_t>(ram[0x07c8u+source_x]+1);
    return {Row32Outcome::Spawned,x,matching};
}
} // namespace cv3
