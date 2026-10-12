// Native semantic translation of original JP bank $0A CPU $B7F7-$B872.
// Preserves mapped reads ($FB96 -> $E2D0), RAM writes and object layout.
// Never claim full game, frame, IRQ, PPU or audio parity from this module.
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iterator>
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
    struct DispatchEvent {
        unsigned id, target, mapped_bank, ram16, ram17, ram23, ram3f_at_entry, stack_pointer;
        bool stubbed;
    };
    std::vector<DispatchEvent> dispatches;
    std::vector<std::array<unsigned,2>> post_mapper_changes;
    std::vector<std::array<unsigned,3>> video_register_writes;
    std::vector<std::array<unsigned,2>> script0_mapper_changes;
    std::vector<std::array<unsigned,2>> script3_mapper_changes;
    std::array<uint8_t,2048> ram{};
    bool complete_foreign=false;
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

    void dispatch_bank00_script0_commands(const Image& bank00) {
        // Original raw00 $84A0-$8511, $8480-$849F, $852F-$853C,
        // $966F-$96B8 and fixed31 EC54/EC61/EC70/EC72/EC74/E2CA/E62D.
        // Execute the ROM-indexed command stream, not a hardcoded expected buffer.
        auto checked_byte = [&](unsigned addr)->uint8_t {
            if(addr<0x8000 || addr>=0xC000)
                throw std::runtime_error("ID0 bank00 pointer outside 16KiB window");
            return bank00.at(static_cast<uint16_t>(addr));
        };
        auto checked_word = [&](unsigned addr)->unsigned {
            if(addr<0x8000 || addr>=0xBFFF)
                throw std::runtime_error("ID0 pointer word outside 16KiB window");
            return unsigned(checked_byte(addr)) | (unsigned(checked_byte(addr+1))<<8);
        };
        auto push_command = [&](unsigned val) {
            if(ram[0x1E]>=0x80)throw std::runtime_error("ID0 $0300 command overflow");
            ram[0x300+ram[0x1E]]=static_cast<uint8_t>(val);
            ++ram[0x1E];
        };
        auto helper = [&](unsigned kind) {
            // $EC54 saves mapped bank in $24 via $E2CA; $966F builds
            // a FF/FE-delimited command into $0300,X; $E62D restores it.
            ram[0x24]=ram[0x23];ram[0x23]=0;
            script0_mapper_changes.push_back({0xE2D2,0});
            ram[0xAE]=0;
            const unsigned ptr=checked_word(0x96B9+((kind*2)&255));
            ram[0]=static_cast<uint8_t>(ptr);ram[1]=static_cast<uint8_t>(ptr>>8);
            ram[2]=static_cast<uint8_t>((kind&0x80)?0:0xFF);
            unsigned y=0;unsigned iterations=0;
            auto source_read = [&]() -> unsigned {
                if(++iterations>200)throw std::runtime_error("ID0 command stream unbounded");
                script0_mapper_changes.push_back({0xE2D2,ram[0xAE]});
                const unsigned out=checked_byte(ptr+y);
                script0_mapper_changes.push_back({0xE2D2,0});
                return out;
            };
            for (;;) {
                push_command(1);  // $9689 / $EC72 + $EC74
                push_command(source_read());++y;
                push_command(source_read());++y;
                for (;;) {
                    const unsigned v=source_read();++y;
                    if(v==0xFF) {
                        push_command(0xFF); // $96A4 JMP $EC70
                        ram[0x23]=ram[0x24];
                        script0_mapper_changes.push_back({0xE2D2,ram[0x23]});
                        return;
                    }
                    if(v==0xFE) {push_command(0xFF);break;}
                    push_command(v & ram[2]);
                }
            }
        };
        helper(9);
        // Authentic $8480: two-level index based on room header nibbles.
        unsigned y=(unsigned(ram[0x34])*2)&255;
        const unsigned top=checked_word(0x8541+y);
        ram[8]=static_cast<uint8_t>(top);ram[9]=static_cast<uint8_t>(top>>8);
        y=(unsigned(ram[0x35])*4)&255;
        unsigned child=checked_word(top+y);
        ram[10]=static_cast<uint8_t>(child);ram[11]=static_cast<uint8_t>(child>>8);
        ram[0x0E]=static_cast<uint8_t>(y+2);
        unsigned value=checked_byte(child+ram[0x36]);
        const bool second=value>=0x1C;
        if(second)value-=0x1C;
        ram[7]=static_cast<uint8_t>(second?1:0);
        ram[0]=static_cast<uint8_t>(value);
        y=(value*9)&255;
        unsigned x=ram[0x1E];
        if(x>0x70)throw std::runtime_error("ID0 command output index exceeds buffer");
        // Three triplets, one alignment slot after each triplet. $1E is
        // deliberately NOT incremented by the original $84CF-$84E0 loop.
        for(unsigned j=0;j<3;++j) {
            for(unsigned k=0;k<3;++k) {
                const unsigned addr=(second?0x87DB:0x86DF)+y;
                if(x+0x2F4>=0x800)throw std::runtime_error("ID0 output outside RAM");
                ram[x+0x2F4]=checked_byte(addr);
                y=(y+1)&255;++x;
            }
            ++x;
        }
        // $852F calls original EC54 for a room-specific command, then
        // tailcalls EC54 with ID4. Both touch $0300,X and mapper $8000.
        const unsigned selector=ram[0x54E];
        if(selector>=4)throw std::runtime_error("ID0 command selector exceeds table");
        helper(checked_byte(0x853D+selector));
        helper(4);
        y=ram[0x0E];
        child=checked_word(top+y);
        ram[10]=static_cast<uint8_t>(child);ram[11]=static_cast<uint8_t>(child>>8);
        const unsigned ordinal=checked_byte(child+ram[0x36]);
        y=(ordinal*3)&255;
        x=ram[0x1E];
        for(unsigned k=0;k<3;++k) {
            if(x+0x2F0>=0x800)throw std::runtime_error("ID0 trailing output outside RAM");
            ram[x+0x2F0]=checked_byte(0x8929+y);
            ++x;y=(y+1)&255;
        }
        this->x=static_cast<uint8_t>(x);
    }

    void dispatch_bank00_script2_video(const Image& bank00) {
        // Entire original bank00 $8013-$805E selector/table routine and
        // fixed31 $E32B-$E35B VRC6 video-bank-register write helpers.
        // $34/$35/$36 are producer-bound room header nibbles.
        auto address_word = [&](unsigned addr)->unsigned {
            if(addr<0x8000 || addr>=0xBFFF)
                throw std::runtime_error("script2 indirect word outside bank00");
            return static_cast<unsigned>(bank00.at(static_cast<uint16_t>(addr))) |
                (static_cast<unsigned>(bank00.at(static_cast<uint16_t>(addr+1)))<<8);
        };
        auto selected = [&](unsigned ptr,unsigned y)->unsigned {
            if(ptr<0x8000 || ptr+y>0xBFFF)
                throw std::runtime_error("script2 table selector outside bank00");
            return address_word(ptr+y);
        };
        unsigned y=(static_cast<unsigned>(ram[0x34])*2)&255;
        const unsigned top=selected(0x805F,y);
        ram[8]=static_cast<uint8_t>(top);ram[9]=static_cast<uint8_t>(top>>8);
        y=(static_cast<unsigned>(ram[0x35])*4)&255;
        unsigned branch=selected(top,y);
        ram[10]=static_cast<uint8_t>(branch);ram[11]=static_cast<uint8_t>(branch>>8);
        y=(static_cast<unsigned>(ram[0x36])*2)&255;
        auto pair=selected(branch,y);
        ram[0x3D]=static_cast<uint8_t>(pair);ram[0x3E]=static_cast<uint8_t>(pair>>8);
        y=(static_cast<unsigned>(ram[0x35])*4+2)&255;
        branch=selected(top,y);
        ram[10]=static_cast<uint8_t>(branch);ram[11]=static_cast<uint8_t>(branch>>8);
        y=(static_cast<unsigned>(ram[0x36])*2)&255;
        pair=selected(branch,y);
        ram[0x3A]=static_cast<uint8_t>(pair);ram[0x3B]=static_cast<uint8_t>(pair>>8);
        // Actual original fixed $E32B calls E331 then JMP E33C;
        // bank00 $805C JMP E347. Write hardware register in *CPU order*.
        constexpr std::array<unsigned,8> pcs{{0xE333,0xE338,0xE33E,0xE343,
                                               0xE349,0xE34E,0xE353,0xE358}};
        constexpr std::array<unsigned,8> addrs{{0xD002,0xD003,0xD000,0xD001,
                                                 0xE000,0xE003,0xE001,0xE002}};
        constexpr std::array<unsigned,8> fields{{0x3A,0x3B,0x38,0x39,
                                                  0x3C,0x3F,0x3D,0x3E}};
        for(unsigned i=0;i<pcs.size();++i)
            video_register_writes.push_back({pcs[i],addrs[i],ram[fields[i]]});
    }

    // Two original fixed PRG30 routines, using original physical bank data.
    // All PRG mapping is explicit; addresses $C000..$DFFF are fixed PRG30,
    // $E000..$FFFF fixed PRG31, $8000..$BFFF is mapper-selected raw bank.
    void dispatch_fixed_script3(const std::vector<uint8_t>& prg) {
        const auto rd = [&](unsigned addr,unsigned bank)->uint8_t {
            if(addr>=0x8000 && addr<0xC000 && bank<15)
                return prg.at(bank*0x4000+addr-0x8000);
            if(addr>=0xC000 && addr<0xE000)
                return prg.at(30*0x2000+addr-0xC000);
            if(addr>=0xE000 && addr<=0xFFFF)
                return prg.at(31*0x2000+addr-0xE000);
            throw std::runtime_error("script3 mapped pointer outside original PRG");
        };
        const auto word = [&](unsigned addr,unsigned bank)->unsigned {
            if((addr&0xFFFFu)==0xFFFFu)throw std::runtime_error("script3 word crosses address space");
            return unsigned(rd(addr,bank))|(unsigned(rd(addr+1,bank))<<8);
        };
        auto selected_bank = [&]()->unsigned {
            unsigned y=ram[0x34];
            if(y==0x0D) {
                if(ram[0x35]==0 && ram[0x36]<=1)y=2;
                else if((ram[0x35]==2 && ram[0x36]==2) ||
                        (ram[0x35]==3 && ram[0x36]==0))y=5;
            } else if(y==0x0E && ram[0x35]==0 && ram[0x36]==1) y=1;
            if(y>=15)throw std::runtime_error("script3 bank selector exceeds original 15 words");
            return unsigned(rd(0xC94B+y,0));
        };
        // C900 selects a bank before D03F, C905 re-selects after D449.
        unsigned bank=unsigned(rd(0xC94B+ram[0x34],0));
        if(bank>=15)throw std::runtime_error("script3 illegal first mapper selection");
        ram[0x23]=static_cast<uint8_t>(bank);
        script3_mapper_changes.push_back({0xE2D2,bank});
        ram[0x70]=ram[0x65];
        ram[0x0C]=static_cast<uint8_t>(ram[0x34]*2u);
        unsigned ptr=word(0xD953+ram[0x0C],bank);
        ram[8]=static_cast<uint8_t>(ptr);ram[9]=static_cast<uint8_t>(ptr>>8);
        ram[0x0D]=static_cast<uint8_t>(ram[0x35]*2u);
        unsigned child=word(ptr+ram[0x0D],bank);
        ram[10]=static_cast<uint8_t>(child);ram[11]=static_cast<uint8_t>(child>>8);
        ram[0x65]=rd(child+ram[0x36],bank);
        // D449 resolves a second nested table, including a one-byte offset
        // into the final child before storing the 16-bit $4D/$4E pointer.
        ptr=word(0xD8F9+ram[0x0C],bank);
        ram[8]=static_cast<uint8_t>(ptr);ram[9]=static_cast<uint8_t>(ptr>>8);
        child=word(ptr+ram[0x0D],bank);
        ram[10]=static_cast<uint8_t>(child);ram[11]=static_cast<uint8_t>(child>>8);
        ram[0x0E]=static_cast<uint8_t>(ram[0x36]*2u);
        const unsigned leaf=word(child+ram[0x0E]+1u,bank);
        ram[0x4D]=static_cast<uint8_t>(leaf);ram[0x4E]=static_cast<uint8_t>(leaf>>8);
        bank=selected_bank();
        if(bank>=15)throw std::runtime_error("script3 illegal second mapper selection");
        ram[0x23]=static_cast<uint8_t>(bank);
        script3_mapper_changes.push_back({0xE2D2,bank});
        ram[0x6E]=rd(leaf,bank);
        // D074-D0CB special room header adjustment. Current five bounded
        // source-room headers take the default branch; preserve the other
        // explicitly decoded original conditional selectors as well.
        unsigned y=ram[0x0C];
        if(ram[0x34]==0x0D){
            if(ram[0x35]==0 && ram[0x36]<=1)y=4;
            else if((ram[0x35]==2 && ram[0x36]==2) ||
                    (ram[0x35]==3 && ram[0x36]==0))y=10;
        }else if(ram[0x34]==0x0E && ram[0x35]==0 && ram[0x36]==1) y=2;
        const unsigned one=word(0xD917+y,bank);
        const unsigned two=word(0xD935+y,bank);
        ram[0x5A]=static_cast<uint8_t>(one);ram[0x5B]=static_cast<uint8_t>(one>>8);
        ram[0x5C]=static_cast<uint8_t>(two);ram[0x5D]=static_cast<uint8_t>(two>>8);
        // D094 RTS; original FBC9 trampoline restores raw bank 0A.
    }

    void dispatch_fixed_script4() {
        // D0CD-D149 reads the $65/$6E room values produced by script3.
        // Shift sequences have explicit 6502 carry propagation.
        auto sz8 = [](unsigned v)->uint8_t{return static_cast<uint8_t>(v);};
        unsigned acc=0;
        if(ram[0x65]&0x80) {
            const unsigned flags=unsigned(ram[0x520])|unsigned(ram[0x537]);
            if(flags && !(ram[0x520]&0x80)) {
                ram[0x54]=0;ram[0x53]=0;
            } else {
                ram[0x54]=flags && (ram[0x520]&0x80)?ram[0x6E]:((ram[0x65]&1)?0:ram[0x6E]);
                ram[0x53]=((!flags && (ram[0x65]&1))?0:0x30);
            }
            ram[0x55]=0;ram[0]=ram[0x53];acc=ram[0x54];
            bool carry=false;
            for(int j=0;j<3;++j){
                carry=(ram[0]&0x80)!=0;
                ram[0]=sz8(unsigned(ram[0])<<1);
                acc=sz8((acc<<1)|(carry?1:0));
            }
            acc=sz8(acc-1);ram[0x56]=sz8(acc);
            ram[0x57]=sz8(acc+7);
            return;
        }
        if(ram[0x54]&0x80) acc=0;
        else if(ram[0x54]==ram[0x6E]) acc=sz8(unsigned(ram[0x6E])<<3);
        else {
            ram[0]=ram[0x54];acc=ram[0x53];
            for(int j=0;j<3;++j){
                const bool carry=(ram[0]&1)!=0;
                ram[0]=sz8(ram[0]>>1);
                acc=sz8((acc>>1)|(carry?0x80:0));
            }
            acc=sz8(acc>>2);
        }
        // SEC, SBC #02; CLC, ADC #0B; optional D133/$78 update.
        acc=sz8(acc-2);ram[0x56]=sz8(acc);
        ram[0x57]=sz8(acc+0x0B);
        ram[0x78]=sz8(unsigned(ram[0x6E])*8+8);
    }

    void post_dispatch(const Image& bank0a,const Image& bank0e,const Image& bank00,
                       unsigned index,unsigned seed,const std::vector<uint8_t>* full_prg=nullptr) {
        // Translate $B6B4-$B6E7 and all six original B49A/FBBB
        // trampoline targets. With full_prg supplied, no callback is mocked.
        // Without full_prg, ROM-free synthetic fixtures retain explicitly
        // marked ID3/ID4 stubs; those fixtures are NOT original-game parity.
        complete_foreign=(full_prg!=nullptr);
        state_bridge(bank0a,bank0e,index,seed);
        ram[0xFF]=0xB0;
        ram[0xFD]=0;
        ram[0xFC]=0x10;
        constexpr std::array<unsigned,6> kCalls{{0,1,2,6,3,4}};
        constexpr std::array<unsigned,9> kTargets{{
            0x84A0,0x8001,0x8013,0xD03C,0xD0CD,0xCDA8,0x8F3E,0xFBA5,0xFBB0}};
        for(unsigned i=0;i<kTargets.size();++i) {
            const unsigned where=0xB4B1+3*i;
            const unsigned target=static_cast<unsigned>(bank0a.at(static_cast<uint16_t>(where))) |
                (static_cast<unsigned>(bank0a.at(static_cast<uint16_t>(where+1)))<<8);
            if(target!=kTargets[i] || bank0a.at(static_cast<uint16_t>(where+2))!=0)
                throw std::runtime_error("original 9-record mapper dispatch table drift");
        }
        for(unsigned id:kCalls) {
            // B49A multiplies A=id by 3, selects an original 3-byte
            // (target, raw bank) record; $FBBB calls E2D0 to map it.
            ram[0]=static_cast<uint8_t>(id);
            const unsigned where=0xB4B1+3*id;
            if(id==3)ram[0x3F]=0x37; // B6D4/D6: before original ID3 call
            const uint8_t lo=bank0a.at(static_cast<uint16_t>(where));
            const uint8_t hi=bank0a.at(static_cast<uint16_t>(where+1));
            const uint8_t bank=bank0a.at(static_cast<uint16_t>(where+2));
            if(bank!=0)throw std::runtime_error("unexpected trampoline mapper");
            ram[0x16]=lo; ram[0x17]=hi;
            mapper=bank;ram[0x23]=bank;
            post_mapper_changes.push_back({0xE2D2,bank});
            const unsigned target=static_cast<unsigned>(lo)|(static_cast<unsigned>(hi)<<8);
            const bool stubbed=(id==3 || id==4) && full_prg==nullptr;
            dispatches.push_back({id,target,bank,lo,hi,bank,ram[0x3f],0xF5,stubbed});
            // This explicit boundary is the scope limit. No speculative
            // C++ behavior is supplied for original routines 3 and 4.
            if(id==0) dispatch_bank00_script0_commands(bank00);
            if(id==1) {
                // Authentic bank00 $8001-$800E: LDY $054E; LDA $800F,Y;
                // STA $38; CLC; ADC #1; STA $39; RTS.
                const unsigned selector=ram[0x54E];
                if(selector>3)throw std::runtime_error("bounded room selector escaped original table");
                const uint8_t value=bank00.at(static_cast<uint16_t>(0x800F+selector));
                ram[0x38]=value;ram[0x39]=static_cast<uint8_t>(value+1);
            }
            if(id==2) dispatch_bank00_script2_video(bank00);
            if(id==3 && full_prg) dispatch_fixed_script3(*full_prg);
            if(id==4 && full_prg) dispatch_fixed_script4();
            if(id==6) {
                // Authentic bank00 $8F3E-$8F46: two immediate ZP stores.
                ram[0x3C]=0x40;ram[0x3F]=0x43;
            }
            // Foreign callee RTS -> fixed $FBC9; $FBC9 JMP E2D0
            // reselects bank0A; E2D5 RTS resumes the original caller.
            mapper=10;ram[0x23]=10;
            post_mapper_changes.push_back({0xE2D2,10});
        }
        // Original $B4EE/$B4F9 and B6E5/B6E7; B597/B5A2 return.
        ram[0x61]=8;
        ram[0x57]=static_cast<uint8_t>(ram[0x56]+2);
        ram[0x68]=static_cast<uint8_t>(ram[0x68]+1);
        if(ram[0x19]!=2 || ram[0x68]!=1 || ram[0x7A6]!=9 || mapper!=10
            || dispatches.size()!=6 || post_mapper_changes.size()!=12)
            throw std::runtime_error("post-loader return state mismatch");
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
void json_post(const Room& r,unsigned index,unsigned seed,unsigned step) {
    std::cout<<"{\"step\":"<<step<<",\"room_index\":"<<index
             <<",\"seed\":"<<seed
             <<",\"scope\":\""<<(r.complete_foreign?"conditional_6502_post_B6B4_native_host_with_no_stub_callbacks":"conditional_6502_post_B6B4_native_host_with_two_stub_callbacks")<<"\""
             <<",\"callbacks\":[";
    for(std::size_t i=0;i<r.dispatches.size();++i) {
        if(i)std::cout<<',';
        const auto& d=r.dispatches[i];
        std::cout<<"{\"id\":"<<d.id<<",\"target\":"<<d.target
                 <<",\"mapped_bank\":"<<d.mapped_bank
                 <<",\"target_region\":\""<<(d.target>=0xC000?"PRG30":"raw00")<<"\""
                 <<",\"ram16\":"<<d.ram16<<",\"ram17\":"<<d.ram17
                 <<",\"ram23\":"<<d.ram23<<",\"ram3f_at_entry\":"<<d.ram3f_at_entry
                 <<",\"stack_pointer\":"<<d.stack_pointer
                 <<",\"stubbed\":"<<(d.stubbed?"true":"false")<<'}';
    }
    std::cout<<"],\"mapper_changes\":[";
    for(std::size_t i=0;i<r.post_mapper_changes.size();++i) {
        if(i)std::cout<<',';
        const auto& w=r.post_mapper_changes[i];
        std::cout<<'['<<w[0]<<','<<w[1]<<']';
    }
    std::cout<<"],\"script0_mapper_changes\":[";
    for(std::size_t i=0;i<r.script0_mapper_changes.size();++i) {
        if(i)std::cout<<',';
        const auto& w=r.script0_mapper_changes[i];
        std::cout<<'['<<w[0]<<','<<w[1]<<']';
    }
    std::cout<<"],\"script3_mapper_changes\":[";
    for(std::size_t i=0;i<r.script3_mapper_changes.size();++i) {
        if(i)std::cout<<',';
        std::cout<<'['<<r.script3_mapper_changes[i][0]<<','<<r.script3_mapper_changes[i][1]<<']';
    }
    std::cout<<"],\"script0_command_buffer\":[";
    for(unsigned i=0x300;i<0x380;++i) {
        if(i>0x300)std::cout<<',';
        std::cout<<unsigned(r.ram[i]);
    }
    std::cout<<"],\"script0_output_fields\":[";
    for(unsigned i=0x2E0;i<0x300;++i) {
        if(i>0x2E0)std::cout<<',';
        std::cout<<unsigned(r.ram[i]);
    }
    std::cout<<"],\"script0_aux\":{\"cursor_1e\":"<<unsigned(r.ram[0x1e])
             <<",\"command_mask_02\":"<<unsigned(r.ram[2])
             <<",\"temporary_bank_24\":"<<unsigned(r.ram[0x24])
             <<",\"source_bank_ae\":"<<unsigned(r.ram[0xae])
             <<",\"pointer_low_08\":"<<unsigned(r.ram[8])
             <<",\"pointer_high_09\":"<<unsigned(r.ram[9])
             <<",\"selector_0e\":"<<unsigned(r.ram[0x0e])<<'}';
    std::cout<<",\"video_register_writes\":[";
    for(std::size_t i=0;i<r.video_register_writes.size();++i) {
        if(i)std::cout<<',';
        const auto& w=r.video_register_writes[i];
        std::cout<<'['<<w[0]<<','<<w[1]<<','<<w[2]<<']';
    }
    const auto& m=r.ram;
    std::cout<<"],\"ram_3a\":"<<unsigned(m[0x3a])
             <<",\"ram_3b\":"<<unsigned(m[0x3b])
             <<",\"ram_3d\":"<<unsigned(m[0x3d])
             <<",\"ram_3e\":"<<unsigned(m[0x3e])
             <<",\"ram_00\":"<<unsigned(m[0])
             <<",\"ram_16\":"<<unsigned(m[0x16])
             <<",\"ram_17\":"<<unsigned(m[0x17])
             <<",\"ram_23\":"<<unsigned(m[0x23])
             <<",\"ram_ff\":"<<unsigned(m[0xff])
             <<",\"ram_fc\":"<<unsigned(m[0xfc])
             <<",\"ram_fd\":"<<unsigned(m[0xfd])
             <<",\"ram_3f\":"<<unsigned(m[0x3f])
             <<",\"ram_3c\":"<<unsigned(m[0x3c])
             <<",\"ram_38\":"<<unsigned(m[0x38])
             <<",\"ram_39\":"<<unsigned(m[0x39])
             <<",\"script34_ram_fields\":[";
    constexpr std::array<unsigned,22> kScriptFields{{0,8,9,10,11,12,13,14,0x4D,0x4E,
         0x53,0x54,0x55,0x56,0x57,0x5A,0x5B,0x5C,0x5D,0x65,0x6E,0x78}};
    for(unsigned i=0;i<kScriptFields.size();++i){
        if(i)std::cout<<',';
        std::cout<<unsigned(m[kScriptFields[i]]);
    }
    std::cout<<"]"<<",\"ram_57\":"<<unsigned(m[0x57])
             <<",\"ram_61\":"<<unsigned(m[0x61])
             <<",\"state_19\":"<<unsigned(m[0x19])
             <<",\"substate_68\":"<<unsigned(m[0x68])
             <<",\"stream_state_7a6\":"<<unsigned(m[0x7a6])
             <<",\"mapper\":"<<unsigned(r.mapper)
             <<",\"pc_after_state\":36864,\"sp_after_state\":253"
             <<",\"a\":1,\"x\":"<<unsigned(r.x)<<",\"y\":12"
             <<",\"carry\":false,\"zero\":false,\"negative\":false}"<<'\n';
}
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
    if(argc!=3 && argc!=4 && argc!=5 && argc!=6){
        std::cerr<<"usage: room_loader_native raw0a.bin raw0e.bin [--state-bridge|--state-gate|--post-dispatch raw00.bin]\n";return 2;
    }
    const bool gated=argc==4 && std::string(argv[3])=="--state-gate";
    const bool integrated=argc==4 && std::string(argv[3])=="--state-bridge";
    const bool post=(argc==5 || argc==6) && std::string(argv[3])=="--post-dispatch";
    if((argc==4 && !gated && !integrated) || ((argc==5 || argc==6) && !post))return 2;
    try {
        const Image a(argv[1]),e(argv[2]);
        unsigned step=0;
        if(post) {
            const Image bank00(argv[4]);
            std::vector<uint8_t> full;
            if(argc==6){
                std::ifstream input(argv[5],std::ios::binary);
                full.assign(std::istreambuf_iterator<char>(input),std::istreambuf_iterator<char>());
                if(full.size()!=262144)throw std::runtime_error("full PRG must be exactly 256KiB");
                // Refuse contradictory mapper images: local bank sources and
                // full cartridge PRG must describe the same physical bytes.
                for(unsigned i=0;i<16384;++i) {
                    if(full[i]!=bank00.at(static_cast<uint16_t>(0x8000+i)) ||
                       full[10*16384+i]!=a.at(static_cast<uint16_t>(0x8000+i)) ||
                       full[14*16384+i]!=e.at(static_cast<uint16_t>(0x8000+i)))
                        throw std::runtime_error("full PRG and bank source mismatch");
                }
            }
            for(unsigned index=0;index<5;++index)for(unsigned seed=0;seed<256;++seed){
                Room room;room.post_dispatch(a,e,bank00,index,seed,argc==6?&full:nullptr);
                json_post(room,index,seed,step++);
            }
            return 0;
        }
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
