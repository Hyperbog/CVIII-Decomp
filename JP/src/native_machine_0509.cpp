#include "native_machine_0509.hpp"
#include <algorithm>
#include <stdexcept>

namespace cv3 {
namespace {
constexpr std::uint32_t kDots=341*262, kVblank=341*241+1, kPreRender=341*261+1;
std::uint8_t pal_index(std::uint16_t a) {
    auto k=std::uint8_t(a&31);
    if((k&0x13)==0x10)k=std::uint8_t(k&0x0F);
    return k;
}
}
NativeMachine0509::NativeMachine0509(std::span<const std::uint8_t> prg,
                                     std::span<const std::uint8_t> chr)
    :mapper_(prg,chr),cpu_(*this){reset();}
void NativeMachine0509::reset(){
    ram_.fill(0);ciram_.fill(0);palette_.fill(0);oam_.fill(0);
    controller_.fill(0);shifts_.fill(0);
    ppu_ctrl_=ppu_mask_=oam_addr_=ppu_scroll_=ppu_status_=ppu_read_buffer_=0;
    ppu_addr_=0;ppu_latch_=strobe_=nmi_line_=nmi_pending_=false;
    cpu_cycles_=frames_=nmis_=irqs_=0;ppu_dot_in_frame_=dma_stall_=0;
    // The CPU power-on vectors are always in physical PRG bank31.
    cpu_.reset();cpu_cycles_=cpu_.cycle_count();
}
void NativeMachine0509::update_nmi(){
    const bool high=bool((ppu_status_&0x80)&&(ppu_ctrl_&0x80));
    if(high&&!nmi_line_)nmi_pending_=true;
    nmi_line_=high;
}
void NativeMachine0509::clocks(std::uint32_t n){
    for(std::uint32_t i=0;i<n;++i){
        irq_.step_cpu_cycle();++cpu_cycles_;
        // 3 NTSC PPU dots per CPU cycle. VBlank/NMI edges are timestamped
        // per dot; CPU instruction accesses are still NOT per-cycle modeled.
        for(int k=0;k<3;++k){
            ++ppu_dot_in_frame_;
            if(ppu_dot_in_frame_==kVblank){ppu_status_|=0x80;update_nmi();}
            if(ppu_dot_in_frame_==kPreRender){ppu_status_&=0x1F;update_nmi();}
            if(ppu_dot_in_frame_>=kDots){ppu_dot_in_frame_=0;++frames_;}
        }
    }
}
std::uint64_t NativeMachine0509::step(){
    if(nmi_pending_){nmi_pending_=false;cpu_.nmi();++nmis_;clocks(7);}
    else if(irq_.irq_pending()&&!(cpu_.registers().p&0x04)){cpu_.irq();++irqs_;clocks(7);}
    const auto cycles=cpu_.step();clocks(cycles);
    if(dma_stall_){const auto stall=dma_stall_+std::uint32_t(cpu_cycles_&1);dma_stall_=0;clocks(stall);}
    return cycles;
}
std::uint8_t NativeMachine0509::ppu_read(std::uint16_t addr){
    addr&=0x3FFF;
    if(addr<0x2000)return mapper_.ppu_read(addr);
    if(addr<0x3F00){
        const auto p=std::uint16_t(0x2000+((addr-0x2000)&0x0FFF));
        const auto offset=std::uint16_t((mapper_.ciram_a10(p)<<10)|(p&0x03FF));
        return ciram_[offset];
    }
    return palette_[pal_index(addr)];
}
void NativeMachine0509::ppu_write(std::uint16_t addr,std::uint8_t v){
    addr&=0x3FFF;
    if(addr<0x2000)return; // CHR ROM cartridge; not writable
    if(addr<0x3F00){
        const auto p=std::uint16_t(0x2000+((addr-0x2000)&0x0FFF));
        ciram_[std::uint16_t((mapper_.ciram_a10(p)<<10)|(p&0x03FF))]=v;
        return;
    }
    palette_[pal_index(addr)]=v;
}
std::uint8_t NativeMachine0509::read(std::uint16_t addr){
    if(addr<0x2000)return ram_[addr&0x7FF];
    if(addr<0x4000){
        switch(addr&7){
        case 2:{const auto out=ppu_status_;ppu_status_&=0x7F;ppu_latch_=false;update_nmi();return out;}
        case 4:return oam_[oam_addr_];
        case 7:{const auto addr_old=ppu_addr_;auto value=ppu_read(ppu_addr_);
            ppu_addr_=std::uint16_t((ppu_addr_+((ppu_ctrl_&4)?32:1))&0x3FFF);
            if(addr_old<0x3F00){const auto out=ppu_read_buffer_;ppu_read_buffer_=value;return out;}
            ppu_read_buffer_=ppu_read(std::uint16_t(addr_old-0x1000));return value;}
        default:return 0;
        }
    }
    if(addr==0x4016||addr==0x4017){const auto port=std::size_t(addr-0x4016);
        if(strobe_)return std::uint8_t(controller_[port]&1);
        const auto k=shifts_[port];if(k<8)++shifts_[port];return k<8?std::uint8_t((controller_[port]>>k)&1):1;
    }
    if(addr<0x6000)return 0; // APU and open bus are not yet emulated
    return mapper_.cpu_read(addr);
}
void NativeMachine0509::write(std::uint16_t addr,std::uint8_t v){
    if(addr<0x2000){ram_[addr&0x7FF]=v;return;}
    if(addr<0x4000){
        switch(addr&7){
        case 0:ppu_ctrl_=v;update_nmi();break;
        case 1:ppu_mask_=v;break;
        case 3:oam_addr_=v;break;
        case 4:oam_[oam_addr_++]=v;break;
        case 5:ppu_scroll_=v;ppu_latch_=!ppu_latch_;break;
        case 6:
            if(!ppu_latch_)ppu_addr_=std::uint16_t((std::uint16_t(v&0x3F)<<8)|(ppu_addr_&0xFF));
            else ppu_addr_=std::uint16_t((ppu_addr_&0x3F00)|v);
            ppu_latch_=!ppu_latch_;break;
        case 7:ppu_write(ppu_addr_,v);ppu_addr_=std::uint16_t((ppu_addr_+((ppu_ctrl_&4)?32:1))&0x3FFF);break;
        default:break;
        }
        return;
    }
    if(addr==0x4014){
        const auto saved=oam_addr_;
        for(unsigned i=0;i<256;++i)oam_[std::uint8_t(saved+i)]=read(std::uint16_t((std::uint16_t(v)<<8)|i));
        dma_stall_+=513;return;
    }
    if(addr==0x4016){strobe_=(v&1)!=0;shifts_.fill(0);return;}
    if(addr<0x6000)return; // APU register writes are not yet synthesized
    if(addr>=0xF000 && addr<=0xF002)irq_.cpu_write(addr,v);
    mapper_.cpu_write(addr,v);
}
} // namespace cv3
