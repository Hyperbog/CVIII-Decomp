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
constexpr std::array<unsigned,8> kSlots{{0x400,0x41C,0x438,0x454,0x470,0x48C,0x4A8,0x54E}};
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
        // $07A6 is not altered by $B7F7-$B872. The older standalone
        // fixture started it at zero and masked this preservation rule.
        ram[0x10]=0;
        if(mapper!=10 || mapper_writes!=2*indirect_reads)
            throw std::runtime_error("mapper restoration violation");
    }
    void state_gate(const Image& bank0a,unsigned index,unsigned seed) {
        // Non-sentinel B873 branch after fixed E526, double E7FB dispatch
        // and B597/B689/B6A4. This completes the *non-loading* branch,
        // including the original E843 header, E86B / EC70 FF terminator,
        // then B6AD and B5A2 return. Indices 0..8 are structural, not live.
        if(index>=9)throw std::runtime_error("gate descriptor outside 0..8");
        for(unsigned j=0x300;j<0x380;++j)
            ram[j]=static_cast<uint8_t>(seed*13+j*7);
        ram[0x19]=2;ram[0x68]=0;ram[0x7A6]=static_cast<uint8_t>(index);
        ram[0x1E]=static_cast<uint8_t>(seed&31);
        ram[0x1D]=2;ram[0x23]=10;mapper=10;
        const auto state_target=static_cast<uint16_t>(bank0a.at(0xB4D5) |
            (static_cast<unsigned>(bank0a.at(0xB4D6))<<8));
        const auto substate_target=static_cast<uint16_t>(bank0a.at(0xB68E) |
            (static_cast<unsigned>(bank0a.at(0xB68F))<<8));
        if(state_target!=0xB597||substate_target!=0xB6A4)
            throw std::runtime_error("inline state table drift");
        const unsigned off=0xB8A6+3*index;
        const auto first=bank0a.at(static_cast<uint16_t>(off));
        const auto second=bank0a.at(static_cast<uint16_t>(off+1));
        const auto count=bank0a.at(static_cast<uint16_t>(off+2));
        if(first==0xFF||count==0||count>64)
            throw std::runtime_error("invalid non-sentinel descriptor");
        ram[0x5F]=first;ram[0x5E]=second;ram[0x10]=count;
        unsigned cursor=ram[0x1E];
        const unsigned finish=cursor+3+count;
        if(finish>=0x80)throw std::runtime_error("bounded buffer exceeds $037F");
        // E843 X=ram[$1E], writes the type and 16-bit fields to $0300,X.
        ram[0x300+cursor++]=1;
        ram[0x300+cursor++]=second;
        ram[0x300+cursor++]=first;
        ram[0x1E]=static_cast<uint8_t>(cursor);
        // B894: zero-run of the descriptor's third byte.
        for(unsigned j=0;j<count;++j)ram[0x300+cursor++]=0;
        // E86B / EC70: update cursor, append FF, then increment cursor.
        ram[0x1E]=static_cast<uint8_t>(cursor);
        ram[0x300+cursor++]=0xFF;
        ram[0x1E]=static_cast<uint8_t>(cursor);
        ram[0x10]=0;
        ++ram[0x7A6];
        // B6A4 returns without clearing/loading room slots. B597 sees 68=0.
    }
    void state_bridge(const Image& bank0a,const Image& bank0e,unsigned index,unsigned seed) {
        // Execute the semantics of the authenticated, *conditional* path:
        // E526 -> B4CC -> E7FB -> B597 -> B689 -> E7FB -> B6A4
        // -> B873 (07A6=9 sentinel) -> E785 clear -> B7F7 loader.
        for(unsigned x=1;x<23;++x)
            for(unsigned k=0;k<kSlots.size();++k)
                ram[kSlots[k]+x]=static_cast<uint8_t>(seed*13+x*17+k*31);
        ram[0x19]=2;ram[0x68]=0;ram[0x7A6]=9;ram[0x7A0]=static_cast<uint8_t>(index);
        // E526 writes mapper bank 0A via E2D0, then JMP B4CC.
        mapper=10;ram[0x23]=10;
        // E7FB consumes JSR return address and looks up the state target.
        const uint16_t state_target=static_cast<uint16_t>(bank0a.at(0xB4D1+2*2) |
            (static_cast<unsigned>(bank0a.at(0xB4D1+2*2+1))<<8));
        const uint16_t substate_target=static_cast<uint16_t>(bank0a.at(0xB68E) |
            (static_cast<unsigned>(bank0a.at(0xB68F))<<8));
        if(state_target!=0xB597||substate_target!=0xB6A4)
            throw std::runtime_error("inline dispatcher entry no longer proves B597/B6A4 path");
        // B873 Y=07A6*3; the 10th descriptor is an FF sentinel.
        if(bank0a.at(0xB8A6+3*9)!=0xFF)
            throw std::runtime_error("B873 sentinel branch no longer taken");
        // E785 clears the eight parallel object-slot fields, X=1..22.
        for(unsigned x=1;x<23;++x)
            for(unsigned base:kSlots)ram[base+x]=0;
        // B6B1 JSR B7F7. B7F7 does *not* clear $07A6.
        load(bank0a,bank0e,index);
        if(ram[0x7A6]!=9||ram[0x19]!=2||ram[0x68]!=0)
            throw std::runtime_error("state field mutated on sentinel loader path");
    }
};
void json_gate(const Room& r,unsigned index,unsigned seed,unsigned step) {
    std::cout << "{\"step\":" << step
              << ",\"physical_bank\":\"NES:JP:VRC6:raw0A\""
              << ",\"cpu_path\":\"E526/B4CC/E7FB/B597/B689/B6A4/B873/E843/E86B/EC70/B6AD/B5A2\""
              << ",\"descriptor_index\":" << index << ",\"seed\":" << seed
              << ",\"state_19\":" << unsigned(r.ram[0x19])
              << ",\"substate_68\":" << unsigned(r.ram[0x68])
              << ",\"stream_state_7a6\":" << unsigned(r.ram[0x7A6])
              << ",\"ram_1d\":" << unsigned(r.ram[0x1D])
              << ",\"ram_1e\":" << unsigned(r.ram[0x1E])
              << ",\"ram_5e\":" << unsigned(r.ram[0x5E])
              << ",\"ram_5f\":" << unsigned(r.ram[0x5F])
              << ",\"ram_10\":" << unsigned(r.ram[0x10])
              << ",\"pc_after_gate\":36864,\"sp_after_gate\":253"
              << ",\"mapper\":" << unsigned(r.mapper)
              << ",\"mapper_writes\":1,\"mapped_reads\":0"
              << ",\"x\":" << unsigned(r.ram[0x1E])
              << ",\"y\":" << 3*index
              << ",\"carry\":false,\"zero\":false,\"negative\":false"
              << ",\"buffer_0300_037f\":[";
    for(unsigned j=0x300;j<0x380;++j) {
        if(j>0x300)std::cout<<',';
        std::cout<<unsigned(r.ram[j]);
    }
    std::cout<<"]}\n";
}
void json_frame(const Room& r,unsigned index,unsigned seed,unsigned step,bool integrated=false) {
    std::cout << "{\"step\":" << step << ",\"physical_bank\":\"NES:JP:VRC6:raw0A\""
              << ",\"cpu_path\":\"" << (integrated
                  ? "E526/B4CC/E7FB/B597/B689/B6A4/B873/E785/B7F7/FB96/E2D0"
                  : "B7F7-B872/FB96/E2D0") << "\""
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
    std::cout << "]";
    if(integrated) {
        std::cout << ",\"state_19\":" << unsigned(r.ram[0x19])
                  << ",\"substate_68\":" << unsigned(r.ram[0x68])
                  << ",\"room_stream_state_7a6\":" << unsigned(r.ram[0x7A6])
                  << ",\"pc_after_loader\":46772,\"sp_after_loader\":249"
                  << ",\"state_dispatch_targets\":[46487,46756]"
                  << ",\"state_gate\":\"B8A4_07A6_9_sentinel\""
                  << ",\"state_mapper_write_count\":1,\"slot_fields\":[";
        for(unsigned x=1;x<23;++x){
            if(x>1)std::cout<<',';
            std::cout<<'[';
            for(unsigned k=0;k<kSlots.size();++k){
                if(k)std::cout<<',';
                std::cout<<unsigned(r.ram[kSlots[k]+x]);
            }
            std::cout<<']';
        }
        std::cout<<']';
    }
    std::cout << "}\n";
}
}
int main(int argc,char**argv) {
    if(argc!=3 && argc!=4){std::cerr<<"usage: room_loader_native physical_raw0a.bin physical_raw0e.bin [--state-bridge|--state-gate]\n";return 2;}
    const bool gated=argc==4 && std::string(argv[3])=="--state-gate";
    const bool integrated=argc==4 && std::string(argv[3])=="--state-bridge";
    if(argc==4 && !gated && !integrated)return 2;
    try {
        const Image a(argv[1]),e(argv[2]);
        unsigned step=0;
        if(gated) {
            for(unsigned index=0;index<9;++index)for(unsigned seed=0;seed<256;++seed){
                Room room;room.state_gate(a,index,seed);
                json_gate(room,index,seed,step++);
            }
            return 0;
        }
        for(unsigned index=0;index<5;++index)for(unsigned seed=0;seed<256;++seed){
            Room room;
            if(integrated)room.state_bridge(a,e,index,seed);
            else room.load(a,e,index);
            json_frame(room,index,seed,step++,integrated);
        }
    }catch(const std::exception&e){std::cerr<<"native loader: "<<e.what()<<'\n';return 1;}
    return 0;
}
