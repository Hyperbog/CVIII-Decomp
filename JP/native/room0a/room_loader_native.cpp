// Native semantic translation of original JP bank $0A CPU $B7F7-$B872.
// Preserves mapped reads ($FB96 -> $E2D0), RAM writes and object layout.
// Never claim full game, frame, IRQ, PPU or audio parity from this module.
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int kBankSize=0x4000;
class Image {
    std::array<uint8_t,kBankSize> bytes_{};
public:
    explicit Image(const std::string& filename) {
        std::ifstream input(filename, std::ios::binary);
        if (!input.read(reinterpret_cast<char*>(bytes_.data()),kBankSize))
            throw std::runtime_error("cannot read complete 16KiB image: "+filename);
        if (input.get()!=std::char_traits<char>::eof())
            throw std::runtime_error("trailing bank bytes: "+filename);
    }
    uint8_t at(uint16_t cpu) const {
        if(cpu<0x8000||cpu>=0xC000)throw std::runtime_error("unmapped bank access");
        return bytes_[static_cast<std::size_t>(cpu-0x8000)];
    }
};
struct Room {
    std::array<uint8_t,2048> ram{};
    uint8_t mapper=10;
    unsigned indirect_reads=0, mapper_writes=0;
    std::vector<std::array<unsigned,2>> mapped_accesses;
    uint16_t first_read=0,last_read=0;
    uint8_t x=1;
    bool carry=true,zero=true,negative=false;
    uint8_t read_0e(const Image& bank0e,uint16_t base,unsigned y) {
        if (mapper!=10)throw std::runtime_error("mapper not restored from prior read");
        const unsigned addr=static_cast<unsigned>(base)+y;
        if(addr<0x8000 || addr>=0xC000)throw std::runtime_error("room stream crosses mapper window");
        mapper=14; ++mapper_writes;
        uint8_t result=bank0e.at(static_cast<uint16_t>(addr));
        mapper=10; ++mapper_writes;
        if(indirect_reads==0)first_read=static_cast<uint16_t>(addr);
        last_read=static_cast<uint16_t>(addr);
        ++indirect_reads;
        mapped_accesses.push_back({addr,result});
        return result;
    }
    void load(const Image& bank0a,const Image& bank0e,unsigned index) {
        if(index>=5)throw std::runtime_error("room index outside verified 5-entry domain");
        ram[0x7A0]=static_cast<uint8_t>(index);
        ram[0x23]=10; // original fixed $E2D0 helper return bank
        const unsigned ptr_off=index*2;
        const uint16_t ptr=static_cast<uint16_t>(
            bank0a.at(static_cast<uint16_t>(0xB8C2+ptr_off)) |
            (static_cast<uint16_t>(bank0a.at(static_cast<uint16_t>(0xB8C3+ptr_off))) <<8));
        if(ptr<0x8000 || ptr>=0xC000)throw std::runtime_error("invalid room stream pointer");
        ram[8]=static_cast<uint8_t>(ptr);ram[9]=static_cast<uint8_t>(ptr>>8);
        // Original stream byte0 is read twice; same for byte1.
        const uint8_t h0=read_0e(bank0e,ptr,0);
        ram[0x34]=static_cast<uint8_t>(h0>>4);
        ram[0x35]=static_cast<uint8_t>(read_0e(bank0e,ptr,0)&0x0F);
        const uint8_t h1=read_0e(bank0e,ptr,1);
        ram[0x36]=static_cast<uint8_t>(h1>>4);
        const uint8_t l1=read_0e(bank0e,ptr,1)&0x0F;
        ram[0x54]=l1; ram[0x72]=l1&1u;
        ram[0x53]=0;
        ram[0x7A1]=read_0e(bank0e,ptr,2);
        ram[0x54E]=read_0e(bank0e,ptr,3);
        unsigned y=4;
        x=1;
        for(;;) {
            if(x>22)throw std::runtime_error("unbounded room object count");
            const auto type=read_0e(bank0e,ptr,y);
            if(type==0xFF)break;
            ram.at(0x48C+x)=type;
            ++y;
            ram.at(0x400+x)=read_0e(bank0e,ptr,y++);
            ram.at(0x438+x)=read_0e(bank0e,ptr,y++);
            ram.at(0x41C+x)=read_0e(bank0e,ptr,y++);
            ram.at(0x4A8+x)=read_0e(bank0e,ptr,y++);
            ram.at(0x54E + x)=1;
            ++x;
        }
        ram[0x7A6]=0;
        ram[0x10]=0;
        if(mapper!=10 || mapper_writes!=2*indirect_reads)
            throw std::runtime_error("mapper restoration violation");
    }
};
void json_frame(const Room& r,unsigned index,unsigned seed,unsigned step) {
    std::cout << "{\"step\":" << step << ",\"physical_bank\":\"NES:JP:VRC6:raw0A\""
              << ",\"cpu_path\":\"B7F7-B872/FB96/E2D0\""
              << ",\"room_index\":" << index << ",\"seed\":" << seed
              << ",\"header\":[" << unsigned(r.ram[0x34]) << ',' << unsigned(r.ram[0x35])
              << ',' << unsigned(r.ram[0x36]) << ',' << unsigned(r.ram[0x54])
              << ',' << unsigned(r.ram[0x72]) << ',' << unsigned(r.ram[0x7A1])
              << ',' << unsigned(r.ram[0x54E]) << "]"
              << ",\"pointer\":" << (unsigned(r.ram[9])<<8 | r.ram[8])
              << ",\"mapper\":" << unsigned(r.mapper)
              << ",\"mapper_writes\":" << r.mapper_writes
              << ",\"mapped_reads\":" << r.indirect_reads
              << ",\"first_read\":" << r.first_read << ",\"last_read\":" << r.last_read
              << ",\"object_count\":" << unsigned(r.x-1)
              << ",\"final_x\":" << unsigned(r.x)
              << ",\"ram_10\":" << unsigned(r.ram[0x10])
              << ",\"ram_53\":" << unsigned(r.ram[0x53])
              << ",\"ram_7a0\":" << unsigned(r.ram[0x7A0])
              << ",\"ram_7a6\":" << unsigned(r.ram[0x7A6])
              << ",\"ram_23\":" << unsigned(r.ram[0x23])
              << ",\"carry\":true,\"zero\":true,\"negative\":false"
              << ",\"mapped_accesses\":[";
    for(std::size_t i=0;i<r.mapped_accesses.size();++i) {
        if(i)std::cout<<',';
        std::cout<<'['<<r.mapped_accesses[i][0]<<','<<r.mapped_accesses[i][1]<<']';
    }
    std::cout << "],\"objects\":[";
    for(unsigned i=1;i<r.x;++i) {
        if(i>1)std::cout<<',';
        std::cout<<'['<<unsigned(r.ram[0x48C+i])<<','<<unsigned(r.ram[0x400+i])
                 <<','<<unsigned(r.ram[0x438+i])<<','<<unsigned(r.ram[0x41C+i])
                 <<','<<unsigned(r.ram[0x4A8+i])<<','<<unsigned(r.ram[0x54E + i])<<']';
    }
    std::cout<<"]}\n";
}
}
int main(int argc,char**argv) {
    if(argc!=3){std::cerr<<"usage: room_loader_native physical_raw0a.bin physical_raw0e.bin\n";return 2;}
    try {
        const Image a(argv[1]),e(argv[2]);
        unsigned step=0;
        for(unsigned index=0;index<5;++index)for(unsigned seed=0;seed<256;++seed){
            Room room;
            room.load(a,e,index);
            json_frame(room,index,seed,step++);
        }
    }catch(const std::exception&e){std::cerr<<"native loader: "<<e.what()<<'\n';return 1;}
    return 0;
}
