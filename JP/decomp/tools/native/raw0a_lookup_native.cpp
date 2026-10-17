// Bank $0A $801E-$8046 pointer-lookup *semantic* translation to portable C++.
// Input is a user-supplied authenticated original 16-KiB physical bank and
// a TSV of known-local selector triples. Does not execute a whole game or CPU.
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
std::string hex4(uint16_t x) {
    constexpr char digits[]="0123456789ABCDEF";
    std::string s(4,'0');
    for (int i=3;i>=0;--i) {s[static_cast<size_t>(i)]=digits[x&15];x>>=4;}
    return s;
}
class Bank {
    std::array<uint8_t,16384> bytes_{};
public:
    explicit Bank(const char* path) {
        std::ifstream f(path,std::ios::binary);
        if (!f.read(reinterpret_cast<char*>(bytes_.data()),static_cast<std::streamsize>(bytes_.size())))
            throw std::runtime_error("cannot read exact physical 16KiB bank");
        if (f.get() != std::char_traits<char>::eof())
            throw std::runtime_error("physical bank has trailing bytes");
    }
    uint8_t byte(uint16_t a) const {
        if (a<0x8000 || a>=0xC000) throw std::runtime_error("mapped PRG access outside raw0A");
        return bytes_.at(static_cast<size_t>(a-0x8000));
    }
    uint16_t word(uint16_t a) const {
        if (a==0xBFFF) throw std::runtime_error("word crosses physical mapper window");
        return static_cast<uint16_t>(byte(a) | (static_cast<uint16_t>(byte(static_cast<uint16_t>(a+1))) << 8));
    }
};
uint16_t add_index(uint16_t addr,unsigned selector) {
    if (selector>127) throw std::runtime_error("selector outside locally bounded input");
    const unsigned offset=selector*2u;
    if (addr+offset>0xBFFE) throw std::runtime_error("indexed word crosses bank");
    return static_cast<uint16_t>(addr+offset);
}
}

int main(int argc,char**argv) {
    if (argc!=3) {std::cerr<<"usage: raw0a_lookup_native physical_raw0a.bin cases.tsv\n";return 2;}
    try {
        const Bank bank(argv[1]);
        std::ifstream cases(argv[2]);
        if (!cases) throw std::runtime_error("cannot read selector cases");
        int stage=0,second=0,third=0;
        unsigned step=0;
        // The original instruction sequence computes three 16-bit pointers via
        // the $92AE word array, indirect pointers $06/$07 and $04/$05, and
        // outputs $95/$96. This is the direct *host translation*, not a 6502 emulator.
        while (cases>>stage>>second>>third) {
            if(stage<0||second<0||third<0||stage>127||second>127||third>127)
                throw std::runtime_error("negative or unbounded selector");
            const uint16_t p1=bank.word(add_index(0x92AE,static_cast<unsigned>(stage)));
            const uint16_t p2=bank.word(add_index(p1,static_cast<unsigned>(second)));
            const uint16_t leaf=bank.word(add_index(p2,static_cast<unsigned>(third)));
            std::cout<<"{\"step\":"<<step++
                     <<",\"physical_bank\":\"NES:JP:VRC6:raw0A\""
                     <<",\"pc\":\"801E-8046\""
                     <<",\"selectors\":["<<stage<<","<<second<<","<<third<<"]"
                     <<",\"stage_ptr\":\""<<hex4(p1)<<"\""
                     <<",\"second_ptr\":\""<<hex4(p2)<<"\""
                     <<",\"leaf_ptr\":\""<<hex4(leaf)<<"\"}\n";
        }
        if(!cases.eof())throw std::runtime_error("malformed selector input");
        if(step==0)throw std::runtime_error("empty cases not proof of native parity");
        return 0;
    } catch(const std::exception&e) {
        std::cerr<<"native raw0A lookup error: "<<e.what()<<"\n";
        return 1;
    }
}
