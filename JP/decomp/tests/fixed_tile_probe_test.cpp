#include "../src/fixed_tile_probe.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <vector>

int main(int argc, char** argv) {
    using namespace cv3;
    assert(argc == 2);
    std::ifstream f(argv[1],std::ios::binary);
    assert(f.good());
    std::vector<std::uint8_t> rom(std::istreambuf_iterator<char>{f},{});
    assert(rom.size() == 0x60010u);
    std::array<std::uint8_t,65536> bus{};
    for (unsigned i=0;i<8192;i++) bus[0xE000u+i]=rom[16u+31u*8192u+i];
    const auto read=[&](std::uint16_t address) { return bus[address]; };
    unsigned tested=0;
    for (unsigned hi=0;hi<256;hi++) for(unsigned lo=0;lo<8;lo++)
    for(unsigned fine=0;fine<256;fine++) {
        const auto actual=fixed_tile_probe_index(read,static_cast<std::uint8_t>(lo<<5),
                      static_cast<std::uint8_t>(hi),static_cast<std::uint8_t>(fine));
        const auto source=static_cast<std::uint8_t>(bus[0xFD62u+hi] | lo);
        unsigned a=source;
        do { if(a<12)break; a=(a-12)&255u; } while(true);
        const unsigned value=bus[0xFD4Du+a];
        const unsigned sum=value+fine;
        assert(actual.or_result==source && actual.table_index==a);
        assert(actual.base_tile==value);
        assert(actual.effective_index==(sum&255u));
        assert(actual.adc_carry==(sum>255u));
        tested++;
    }
    assert(tested==524288u);
    // This must read FE61, not clamp Y or assume the source is a 12-byte table.
    assert(fixed_tile_probe_index(read,0,0xFF,0).or_result==bus[0xFE61]);
    return 0;
}
