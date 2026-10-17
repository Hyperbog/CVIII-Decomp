#include "standalone_scene_0509.hpp"
#include <array>
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <cstdint>
#include <iostream>

int main(){
    cv3::StandaloneScene0509 a,b;
    assert(a.frame()==0&&a.enemy_present());
    assert(a.ram()[0x0200]==105); // original $0D OAM assembly sprite Y data
    assert(a.ram()[0x0201]==0x10);
    assert(a.ram()[0x0203]==48);
    assert(a.ram()[0x0200+0xC4]==105);
    assert(a.ram()[0x0201+0xC4]==0x11);
    assert(a.ram()[0x0203+0xC4]==56);
    assert(a.render_rgb().size()==256u*240*3);
    const auto initial=cv3::StandaloneScene0509::fnv1a64(a.render_rgb());
    assert(initial==12363773589731306269ull);
    cv3::StandaloneScene0509 fixture;
    for(unsigned i=0;i<120;++i)fixture.step(cv3::StandaloneScene0509::Right);
    assert(cv3::StandaloneScene0509::fnv1a64(fixture.render_rgb())==0x1722600615a58168ull);
    for(unsigned i=0;i<120;++i){
        const auto button=std::uint8_t((i<95)?cv3::StandaloneScene0509::Right:cv3::StandaloneScene0509::Jump);
        a.step(button);b.step(button);
        assert(a.last_oam_status()==cv3::OamFrameResult::Completed);
    }
    assert(a.frame()==120&&a.player_x()==143&&a.player_y()==88);
    assert(a.near_contact_frames()>0);
    assert(a.ram()==b.ram());
    const auto p=a.render_rgb(),q=b.render_rgb();
    assert(p==q && cv3::StandaloneScene0509::fnv1a64(p)!=initial);
    assert(a.enemy_present());
    a.step(cv3::StandaloneScene0509::RemoveEnemy);
    assert(!a.enemy_present());
    assert(a.ram()[0x0401]==0 && a.ram()[0x054F]==0);
    for(auto off:cv3::kFourActorFields)assert(a.ram()[off+1]==0);
    for(auto off:cv3::kRemainingActorFields)assert(a.ram()[off+1]==0);
    assert(a.ram()[0x0201]!=0x20); // enemy tiles removed from shadow
    std::cout<<"PASS: actual OAM assembler, 2bpp software pixels, deterministic 120-frame synthetic route, actor cleanup; initial pixel FNV64="<<initial<<'\n';
}
