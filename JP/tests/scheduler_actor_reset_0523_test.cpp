#include "scheduler_actor_reset_0523.hpp"
#ifdef NDEBUG
#undef NDEBUG
#endif
#include <array>
#include <cassert>
#include <cstdint>
#include <stdexcept>

int main() {
    constexpr std::array<std::uint8_t, 8> types{
        0, 0x2f, 0x30, 0x4d, 0x65, 0x66, 0x80, 0xff};
    constexpr std::array<std::uint8_t, 4> positions{0, 0xf7, 0xf8, 0xff};
    constexpr std::array<std::uint8_t, 3> statuses{0x00, 0x4d, 0xff};
    unsigned cases = 0, resets = 0, unsupported = 0;
    for (unsigned x = 0x0d; x <= 0x12; ++x)
    for (unsigned attr = 0; attr < 256; ++attr)
    for (auto type : types)
    for (auto pos : positions)
    for (auto p : statuses) {
        std::array<std::uint8_t, 0x800> r{};
        r.fill(0x5a);
        r[0x23] = 0x66;
        r[0x054eu+x] = type;
        r[0x041cu+x] = pos;
        r[0x0470u+x] = static_cast<std::uint8_t>(attr);
        const auto before = r;
        const bool needs_reset = (type>=0x30 && type<0x66 && pos>=0xf8);
        const bool blocked = needs_reset && type==0x4d;
        try {
            const auto got = cv3::scheduler_fe63_to_next_0523(r,
                static_cast<std::uint8_t>(x), 0xa5, 0x49, p);
            assert(!blocked);
            ++cases;
            auto expect = before;
            expect[0x23] = 0x0b;
            const auto expected_a = needs_reset ? 0u :
                (type>=0x30 && type<0x66 ? unsigned(pos) : unsigned(type));
            if (needs_reset) {
                ++resets;
                expect[0x054eu+x] = 0;
                expect[0x0470u+x] = 0;
                expect[0x0400u+x] = 0;
                expect[0x05efu+x] = 0;
            } else {
                expect[0x0470u+x] = (attr & 0x09u) ?
                    static_cast<std::uint8_t>(attr | 0x80u) :
                    static_cast<std::uint8_t>(attr & 0x7fu);
            }
            assert(r == expect);
            const auto d=static_cast<std::uint8_t>((x+1u)-0x13u);
            const auto expected_p=static_cast<std::uint8_t>((p & ~0x83u) |
                (x==0x12 ? 0x03u : 0u) | (d & 0x80u));
            assert(got.next_pc == (x==0x12 ? 0xfe75 : 0xfdec));
            assert(got.a == expected_a && got.x == x+1u);
            assert(got.y == 0x49 && got.p == expected_p);
            assert(got.prg16_bank == 0x0b);
        } catch (const std::invalid_argument&) {
            assert(blocked && r==before);
            ++unsupported;
        }
    }
    for (unsigned x : {0u, 1u, 12u, 19u, 255u}) {
        std::array<std::uint8_t,0x800> r{};
        const auto before=r;
        try {
            (void)cv3::scheduler_fe63_to_next_0523(r,
                static_cast<std::uint8_t>(x),0,0,0);
            assert(false);
        } catch(const std::invalid_argument&) {assert(r==before);}
    }
    assert(cases==138240u && resets==18432u && unsupported==9216u);
}
