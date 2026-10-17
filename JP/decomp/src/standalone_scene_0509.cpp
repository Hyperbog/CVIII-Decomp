#include "standalone_scene_0509.hpp"
#include <stdexcept>

namespace cv3 {
namespace {
constexpr std::array<std::array<std::uint8_t,3>,4> kSprites{{
    {{0x38,0xB5,0xF8}},{{0xF5,0xA2,0x63}},{{0xF8,0xE6,0x70}},{{0xCA,0x86,0xDF}}
}};
constexpr std::array<std::uint8_t,3> kBgSky{0x12,0x23,0x39};
constexpr std::array<std::uint8_t,3> kBgFloor{0x31,0x45,0x57};
}
void StandaloneScene0509::put_ptr(std::array<std::uint8_t,0x4000>& b,std::uint16_t addr,std::uint16_t value){
    b[addr-0x8000]=std::uint8_t(value);b[addr-0x7FFF]=std::uint8_t(value>>8);
}
void StandaloneScene0509::configure_synthetic_resources(){
    // Private test-created descriptor graph, NOT retail sprite art or a dump:
    // selector 0 -> set $9000 -> descriptor $9100; selector 2 -> $9020->$9140.
    put_ptr(synthetic_descriptors_,0x817F,0x9000);
    put_ptr(synthetic_descriptors_,0x8181,0x9020);
    put_ptr(synthetic_descriptors_,0x9002,0x9100);
    put_ptr(synthetic_descriptors_,0x9022,0x9140);
    for (unsigned t=0;t<2;++t){
        const std::uint16_t addr=std::uint16_t(t?0x9140:0x9100);
        const std::uint8_t tile=std::uint8_t(t?0x20:0x10);
        auto *d=synthetic_descriptors_.data()+addr-0x8000;
        d[0]=4;
        for(unsigned i=0;i<4;++i){
            d[1+i*4]=std::uint8_t((i/2)*16); // arithmetic-shift -> 0,0,8,8
            d[2+i*4]=std::uint8_t(tile+i);
            d[3+i*4]=std::uint8_t(t);
            d[4+i*4]=std::uint8_t((i%2)*8);
        }
        // Procedural CHR source (real 2bpp planar format); no game assets.
        for(unsigned i=0;i<4;++i){
            for(unsigned y=0;y<8;++y){
                std::uint8_t plane0=0,plane1=0;
                for(unsigned x=0;x<8;++x){
                    const unsigned c=((x==0||x==7||y==0||y==7)?3:
                         (((x+y+i+t)%5==0)?0:(((x^y^i^t)&1)?1:2)));
                    plane0|=std::uint8_t((c&1)<<(7-x));
                    plane1|=std::uint8_t(((c>>1)&1)<<(7-x));
                }
                synthetic_chr_[(tile+i)*16+y]=plane0;
                synthetic_chr_[(tile+i)*16+y+8]=plane1;
            }
        }
    }
}
void StandaloneScene0509::stage_object(std::uint8_t slot,std::uint8_t selector,
                                       std::uint8_t x,std::uint8_t y){
    ram_[0x0400u+slot]=2; // 6502 OAM assembler frame selector is word offset.
    ram_[0x041Cu+slot]=y;
    ram_[0x0438u+slot]=x;
    ram_[0x0454u+slot]=0;
    ram_[0x0470u+slot]=0;
    ram_[0x048Cu+slot]=selector;
    ram_[0x04A8u+slot]=1; // non-mirrored demonstration object
}
StandaloneScene0509::StandaloneScene0509(){
    configure_synthetic_resources();
    stage_object(0,0,x_,y_);
    const auto slot=scan_actor_slot(ram_);
    if(!slot.available || slot.x!=1)throw std::logic_error("synthetic actor slot init");
    ram_[0x054Eu+slot.x]=1;
    stage_object(slot.x,2,enemy_x_,enemy_y_);
    ram_[0x22]=0xBC;
    OamContext ctx{ram_,synthetic_descriptors_};
    oam_status_=build_oam_shadow(ctx);
}
void StandaloneScene0509::step(std::uint8_t input){
    ++frame_;
    // Illustration movement ONLY. This is not reconstructed Castlevania III physics.
    if(bool(input&Right)!=bool(input&Left)){
        x_=static_cast<std::uint8_t>(x_+((input&Right)?1:-1));
    }
    y_=std::uint8_t((input&Jump)?88:105);
    stage_object(0,0,x_,y_);
    if ((input&RemoveEnemy) && enemy_present_){
        clear_actor_eighteen_fields(ram_,1);
        ram_[0x054F]=0;  // harness-owned occupied flag, not cleared by $FF24
        ram_[0x0401]=0;  // harness-owned visible flag, not cleared by $FF24
        enemy_present_=false;
    }
    if(enemy_present_ && distance_below(x_,enemy_x_,17) &&
       distance_below(y_,enemy_y_,17))++contact_frames_;
    ram_[0x22]=0xBC; // fix OAM rotation offset for deterministic host preview.
    OamContext ctx{ram_,synthetic_descriptors_};
    oam_status_=build_oam_shadow(ctx);
}
std::vector<std::uint8_t> StandaloneScene0509::render_rgb() const {
    std::vector<std::uint8_t> pix(kWidth*kHeight*3);
    // Generic synthetic stage backdrop, not PPU background nametable rendering.
    for(unsigned y=0;y<kHeight;++y){
        for(unsigned x=0;x<kWidth;++x){
            const bool floor=y>=140 || (y>=118&&y<123&&x>=112&&x<220);
            const auto& base=floor?kBgFloor:kBgSky;
            const auto k=std::size_t((y*kWidth+x)*3);
            for(int i=0;i<3;++i)pix[k+i]=std::uint8_t(base[i]+(x%32==0?9:0));
        }
    }
    // Generic NES 8x8 sprite compositor for the native OAM shadow. A real PPU
    // also implements background priority, sprite zero hit, 8x16, and scroll.
    for(unsigned y=0;y<kHeight;++y){
        std::array<bool,kWidth> claimed{};
        unsigned on_scanline=0;
        for(unsigned i=0;i<64;++i){
            const auto off=0x200u+i*4;
            const unsigned sy=unsigned(ram_[off])+1; // NES OAM Y is top minus 1
            if(ram_[off]==0xF4||y<sy||y>=sy+8)continue;
            if(++on_scanline>8)break;
            const unsigned tile=ram_[off+1],attr=ram_[off+2];
            unsigned tile_y=y-sy;
            if(attr&0x80)tile_y=7-tile_y;
            const unsigned sx=ram_[off+3];
            for(unsigned c=0;c<8;++c){
                if(sx+c>=kWidth || claimed[sx+c])continue;
                unsigned tx=(attr&0x40)?7-c:c;
                const auto low=synthetic_chr_[tile*16+tile_y];
                const auto high=synthetic_chr_[tile*16+8+tile_y];
                const unsigned v=((low>>(7-tx))&1)|(((high>>(7-tx))&1)<<1);
                if(!v)continue;
                claimed[sx+c]=true;
                const auto& col=kSprites[attr&3];
                const auto pos=(y*kWidth+sx+c)*3;
                for(int k=0;k<3;++k){
                    const unsigned rgb=unsigned(col[k])*(v+1)/4+30;
                    pix[pos+k]=std::uint8_t(rgb>255?255:rgb);
                }
            }
        }
    }
    return pix;
}
std::uint64_t StandaloneScene0509::fnv1a64(const std::vector<std::uint8_t>& pixels) noexcept{
    std::uint64_t h=0xcbf29ce484222325ull;
    for(const auto p:pixels){h^=p;h*=0x100000001b3ull;}
    return h;
}
} // namespace cv3
