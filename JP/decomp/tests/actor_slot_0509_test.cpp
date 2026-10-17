#include "actor_slot_0509.hpp"
#include <array>
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <cstdint>
#include <iostream>

int main() {
    // Exhaust all 2^12 occupied/free patterns of original $054F-$055A.
    for (unsigned pattern=0;pattern<4096;++pattern) {
        std::array<std::uint8_t,0x800> ram{};
        unsigned first=13;
        for (unsigned i=0;i<12;++i) {
            ram[0x054f+i]=(pattern & (1u<<i)) ? 0x55u : 0;
            if (!ram[0x054f+i] && first==13) first=i+1;
        }
        const auto result=cv3::scan_actor_slot(ram);
        assert(result.x==first);
        assert(result.available==(first!=13));
        assert(result.a==(first==13?1:0));
        for (unsigned i=0;i<12;++i) assert(ram[0x054f+i]==((pattern & (1u<<i))?0x55u:0u));
    }
    // All indexed state writes must match the original ROM's explicit
    // STA $04F2,X ... $0645,X address list and leave unrelated bytes alone.
    for (unsigned x=0;x<256;++x) {
        std::array<std::uint8_t,0x800> r; r.fill(0xA5);
        cv3::clear_actor_four_fields(r,static_cast<std::uint8_t>(x));
        std::array<bool,0x800> touched{};
        for(auto b:cv3::kFourActorFields) touched[b+x]=true;
        for(unsigned i=0;i<r.size();++i)assert(r[i]==(touched[i]?0:0xA5));
        r.fill(0xA5);touched.fill(false);
        cv3::clear_actor_eighteen_fields(r,static_cast<std::uint8_t>(x));
        for(auto b:cv3::kFourActorFields)touched[b+x]=true;
        for(auto b:cv3::kRemainingActorFields)touched[b+x]=true;
        for(unsigned i=0;i<r.size();++i)assert(r[i]==(touched[i]?0:0xA5));
        assert(r[0x054e + x]==0xA5);
    }
    std::cout<<"PASS: 4096 slot maps + 512 complete RAM write-map checks\n";
}
