#include "scheduler_linked_actor_0524.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <stdexcept>
int main() {
    constexpr std::array<std::uint8_t,4> links{0u,1u,15u,255u};
    constexpr std::array<std::uint8_t,4> attrs{0u,1u,0x80u,0xffu};
    constexpr std::array<std::uint8_t,3> owners{0u,18u,255u};
    constexpr std::array<std::uint8_t,3> ps{0u,0x4du,0xffu};
    unsigned total=0,first_cleared=0,first_skipped=0;
    for(unsigned x=13;x<=18;++x)
    for(unsigned a=0;a<256;a+=2)
    for(auto linked:links)
    for(auto linked_attr:attrs)
    for(auto owner:owners)
    for(auto p:ps) {
        std::array<std::uint8_t,0x800> ram{};
        ram.fill(0x5a);
        ram[0x23]=0x66; ram[0x69]=owner;
        ram[0x054eu+x]=0x4d; ram[0x041cu+x]=0xf8;
        ram[0x0470u+x]=static_cast<std::uint8_t>(a);
        ram[0x061du+x]=linked; ram[0x0470u+linked]=linked_attr;
        const auto before=ram;
        const auto got=cv3::scheduler_fe63_to_next_0524(ram,
            static_cast<std::uint8_t>(x),0x39,0x57,p);
        auto expected=before;
        expected[0x23]=0x0b;
        const auto old=expected[0x0470u+x];
        expected[0x0470u+x]=(old&0x09u)
          ? static_cast<std::uint8_t>(old|0x80u)
          : static_cast<std::uint8_t>(old&0x7fu);
        const bool clear_link=(expected[0x0470u+linked]&0x81u)!=0u;
        if(clear_link) {
            expected[0x0657u+linked]=0;
            expected[0x0470u+linked]=0;
            expected[0x05c1u+linked]=0;
            expected[0x0400u+linked]=0;
            expected[0x054eu+linked]=0;
            ++first_cleared;
        } else ++first_skipped;
        expected[0x0657u+owner]=0;
        expected[0x0470u+owner]=0;
        expected[0x05c1u+owner]=0;
        expected[0x0400u+owner]=0;
        expected[0x054eu+owner]=0;
        assert(ram==expected);
        const auto nx=static_cast<std::uint8_t>(owner+1u);
        const auto d=static_cast<std::uint8_t>(nx-0x13u);
        const auto expect_p=static_cast<std::uint8_t>((p&~0x83u) |
            (nx>=0x13u?1u:0u)|(nx==0x13u?2u:0u)|(d&0x80u));
        assert(got.a==0 && got.x==nx && got.y==0x57);
        assert(got.p==expect_p && got.prg16_bank==0x0b);
        assert(got.next_pc==(nx>=0x13u?0xfe75:0xfdec));
        ++total;
    }
    assert(total==110592u && first_cleared>0 && first_skipped>0);
    for(unsigned x:{0u,1u,12u,19u,255u}) {
        std::array<std::uint8_t,0x800> r{};
        const auto before=r;
        try {
            (void)cv3::scheduler_fe63_to_next_0524(r,
                static_cast<std::uint8_t>(x),0,0,0);
            assert(false);
        } catch(const std::invalid_argument&) {assert(r==before);}
    }
    for(unsigned x=13;x<=18;++x) {
        std::array<std::uint8_t,0x800> a{},b{};
        a.fill(0x5a);b=a;
        a[0x054eu+x]=0x80;b[0x054eu+x]=0x80;
        const auto lhs=cv3::scheduler_fe63_to_next_0524(a,
            static_cast<std::uint8_t>(x),0x18,0x57,0x41);
        const auto rhs=cv3::scheduler_fe63_to_next_0523(b,
            static_cast<std::uint8_t>(x),0x18,0x57,0x41);
        assert(a==b);
        assert(lhs.next_pc==rhs.next_pc && lhs.a==rhs.a &&
               lhs.x==rhs.x && lhs.y==rhs.y && lhs.p==rhs.p &&
               lhs.prg16_bank==rhs.prg16_bank);
    }
}
