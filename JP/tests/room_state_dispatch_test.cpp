#include "../src/room_state_dispatch.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <vector>

int main(int argc, char** argv) {
    using namespace cv3;
    assert(argc==2);
    std::ifstream file(argv[1], std::ios::binary);
    assert(file.good());
    const std::vector<std::uint8_t> rom(std::istreambuf_iterator<char>{file},{});
    assert(rom.size()==393232u);
    std::array<std::uint8_t,65536> bus{};
    for(unsigned i=0;i<16384;i++)bus[0x8000+i]=rom[16+0x0A*16384+i];
    const auto read=[&](std::uint16_t a){return bus[a];};
    const std::array<std::uint16_t,12> expected={
        0xB570,0xB58C,0xB597,0xB5A3,0xB5CC,0xB5DA,
        0xB614,0xB622,0xB64E,0xB5CC,0xB5DA,0xB662};
    for(unsigned i=0;i<expected.size();i++){
        const auto got=decode_room_state(read,std::uint8_t(i),0x80);
        assert(got.pointer_entry==0xB4D1+2*i && got.destination==expected[i]);
        assert(got.final_y==0x80 && got.negative && !got.zero && !got.carry);
    }
    unsigned tested=0;
    for(unsigned selector=0;selector<256;selector++)
    for(unsigned saved_y=0;saved_y<256;saved_y++){
        const auto got=decode_room_state(read,std::uint8_t(selector),std::uint8_t(saved_y));
        const unsigned off=(selector*2)&0xFF;
        const unsigned location=0xB4D1+off;
        const auto expected_dest=std::uint16_t(bus[location]|(unsigned(bus[location+1])<<8));
        assert(got.pointer_entry==location && got.destination==expected_dest);
        assert(got.final_a==(expected_dest>>8));
        assert(got.final_y==saved_y);
        assert(got.carry==(selector>=128));
        assert(got.zero==(saved_y==0) && got.negative==(saved_y>=128));
        if(selector>=128){
            const auto alias=decode_room_state(read,std::uint8_t(selector-128),std::uint8_t(saved_y));
            assert(alias.destination==got.destination && alias.pointer_entry==got.pointer_entry);
            assert(!alias.carry && got.carry);
        }
        tested++;
    }
    assert(tested==65536u);
    // Non-table selector deliberately reads into code/data; it is not clamped.
    assert(decode_room_state(read,0x0C,0).pointer_entry==0xB4E9);
    return 0;
}
