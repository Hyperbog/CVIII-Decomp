#include "../src/temporary_prg_bank_read.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <utility>
#include <vector>
int main(int argc,char** argv){
    using namespace cv3;
    assert(argc==2);
    std::ifstream file(argv[1],std::ios::binary);
    assert(file.good());
    const std::vector<std::uint8_t> rom(std::istreambuf_iterator<char>{file},{});
    assert(rom.size()==0x60010u);
    std::array<std::uint8_t,65536> ram{};
    std::uint8_t mapper=0x0A;
    std::vector<std::pair<std::uint16_t,std::uint8_t>> writes;
    auto read=[&](std::uint16_t addr)->std::uint8_t {
        if(addr>=0x8000 && addr<0xC000)
            return rom[16+std::size_t(mapper)*16384+(addr-0x8000)];
        if(addr>=0xE000)return rom[16+31*8192+(addr-0xE000)];
        return ram[addr];
    };
    auto write=[&](std::uint16_t addr,std::uint8_t v){
        writes.emplace_back(addr,v);
        if(addr==0x8000)mapper=v;
        else ram[addr]=v;
    };
    unsigned cases=0;
    for(unsigned lo=0;lo<256;lo++)for(unsigned y=0;y<256;y++){
        ram[8]=std::uint8_t(lo);ram[9]=0xBE;
        mapper=0x0A;writes.clear();
        const auto addr=std::uint16_t(0xBE00u+lo+y);
        const auto expected=addr<0xC000?
            rom[16+14*16384+(addr-0x8000)]:ram[addr];
        const auto got=temporary_prg_bank0e_read(read,write,std::uint8_t(y));
        assert(got.effective_address==addr && got.value==expected);
        assert(got.zero==(expected==0) && got.negative==((expected&0x80)!=0));
        assert(mapper==0x0A && ram[0x23]==0x0A && writes.size()==4);
        assert(writes[0]==std::make_pair(std::uint16_t(0x23),std::uint8_t(0x0E)));
        assert(writes[1]==std::make_pair(std::uint16_t(0x8000),std::uint8_t(0x0E)));
        assert(writes[2]==std::make_pair(std::uint16_t(0x23),std::uint8_t(0x0A)));
        assert(writes[3]==std::make_pair(std::uint16_t(0x8000),std::uint8_t(0x0A)));
        ++cases;
    }
    assert(cases==65536u);
    ram[8]=0xFF;ram[9]=0xFF;ram[0]=0x5A;mapper=0x0A;
    const auto wrapped=temporary_prg_bank0e_read(read,write,1);
    assert(wrapped.effective_address==0 && wrapped.value==0x5A);
    return 0;
}
