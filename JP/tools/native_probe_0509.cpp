// Original-ROM native mapped-CPU smoke runner. Intentionally headless and
// explicitly NOT a standalone reconstructed game or pixel-accurate emulator.
#include "native_machine_0509.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <cstdint>

int main(int argc,char** argv){
    if(argc<2||argc>4){std::cerr<<"Usage: native_probe_0509 ORIGINAL_JP_ROM.nes [MAX_STEPS] [TRACE_FILE]\n";return 2;}
    try{
        std::ifstream input(argv[1],std::ios::binary);
        if(!input)throw std::runtime_error("no ROM file");
        std::vector<std::uint8_t> rom((std::istreambuf_iterator<char>(input)),{});
        if(rom.size()!=393232||rom[0]!='N'||rom[1]!='E'||rom[2]!='S'||rom[3]!=0x1A||
            rom[4]!=16||rom[5]!=16||((rom[6]>>4)!=8) || ((rom[7]&0xF0)!=0x10))
            throw std::runtime_error("expected unmodified NES format, 256 KiB PRG, 128 KiB CHR and Mapper24; SHA-256 must additionally be checked by wrapper");
        auto prg=std::span<const std::uint8_t>(rom.data()+16,262144);
        auto chr=std::span<const std::uint8_t>(rom.data()+16+262144,131072);
        cv3::NativeMachine0509 machine(prg,chr);
        const auto max=argc>2?std::stoull(argv[2]):10000ull;
        if(max>20000000ull)throw std::runtime_error("native probe bounded to 20 million instructions");
        std::ofstream trace;
        if(argc>3){trace.open(argv[3]);if(!trace)throw std::runtime_error("cannot write trace");}
        for(std::uint64_t i=0;i<max;++i){
            const auto s=machine.cpu_state();
            if(trace)trace<<std::hex<<std::uppercase<<s.pc<<' '<<unsigned(s.a)<<' '<<unsigned(s.x)<<' '<<unsigned(s.y)<<' '<<unsigned(s.p)<<' '<<unsigned(s.sp)<<std::dec<<' '<<machine.cycles()<<'\n';
            machine.step();
        }
        const auto s=machine.cpu_state();
        std::cout<<"NATIVE_2A03_HEADLESS_TEST steps="<<machine.executed_instructions()
            <<" pc="<<std::hex<<std::uppercase<<s.pc<<std::dec
            <<" cycles="<<machine.cycles()<<" frames="<<machine.frames()
            <<" nmis="<<machine.nmis()<<" irqs="<<machine.irqs()
            <<" selector18="<<unsigned(machine.ram_at(0x18))
            <<" room19="<<unsigned(machine.ram_at(0x19))
            <<" bank16="<<unsigned(machine.mapper().prg16_bank())<<'\n';
        return 0;
    }catch(const std::exception& e){std::cerr<<"NATIVE_2A03_PROBE_ERROR "<<e.what()<<'\n';return 1;}
}
