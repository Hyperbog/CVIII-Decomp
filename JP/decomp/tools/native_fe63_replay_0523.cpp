// Compare original Mesen CPU continuation against ROM-free native source lift.
// Intentionally excludes hardware JSR/RTS stack bytes ($0100-$01FF).
#include "scheduler_actor_reset_0523.hpp"
#include <array>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string_view>

namespace {
using Ram = std::array<std::uint8_t, 0x800>;
Ram load(const char* path) {
    Ram r{};
    std::ifstream f(path, std::ios::binary);
    if (!f || !f.read(reinterpret_cast<char*>(r.data()), r.size()) ||
        f.peek() != std::char_traits<char>::eof())
        throw std::runtime_error("Expected exact 2048-byte original Mesen RAM dump");
    return r;
}
unsigned number(const char* arg) {
    const std::string_view value{arg};
    const auto start = value.starts_with("0x") ? value.substr(2) : value;
    unsigned result = 0;
    const auto [end, error] = std::from_chars(start.data(), start.data() + start.size(), result, 16);
    if (error != std::errc{} || end != start.data() + start.size())
        throw std::invalid_argument("Invalid hexadecimal register argument");
    return result;
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 13) {
            std::cerr << "usage: native_fe63_replay_0523 before.bin after.bin "
                "entryX entryA entryY entryP expectedPC expectedA expectedX "
                "expectedY expectedP expectedBank (hexadecimal)\n";
            return 2;
        }
        auto original = load(argv[2]);
        auto actual = load(argv[1]);
        const auto x = number(argv[3]);
        const auto a = number(argv[4]);
        const auto y = number(argv[5]);
        const auto p = number(argv[6]);
        if ((x | a | y | p) > 0xffu) throw std::invalid_argument("Invalid 8-bit CPU register");
        const auto result = cv3::scheduler_fe63_to_next_0523(actual,
            static_cast<std::uint8_t>(x), static_cast<std::uint8_t>(a),
            static_cast<std::uint8_t>(y), static_cast<std::uint8_t>(p));
        unsigned bad = 0, ram_bad = 0, compared = 0;
        for (unsigned i = 0; i < actual.size(); ++i) {
            if (i >= 0x100u && i < 0x200u) continue;
            ++compared;
            if (actual[i] != original[i]) {
                if (bad < 8) std::cerr << "RAM mismatch at $" << std::hex << i
                    << ": native=" << unsigned(actual[i])
                    << " original=" << unsigned(original[i]) << '\n';
                ++bad;
                ++ram_bad;
            }
        }
        const unsigned expected[] = {number(argv[7]), number(argv[8]),
            number(argv[9]), number(argv[10]), number(argv[11]), number(argv[12])};
        const unsigned got[] = {result.next_pc, result.a, result.x,
            result.y, result.p, result.prg16_bank};
        for (unsigned i = 0; i < 6; ++i) if (got[i] != expected[i]) {
            std::cerr << "CPU/mapper field " << i << " native=" << std::hex
                << got[i] << " original=" << expected[i] << '\n';
            ++bad;
        }
        std::cout << (bad ? "FAIL" : "PASS") << " 0523 original-source replay: "
            << (compared - ram_bad) << "/"
            << compared << " RAM bytes examined; mismatches=" << bad << '\n';
        return bad ? 1 : 0;
    } catch (const std::exception& e) {
        std::cerr << "0523 replay unavailable: " << e.what() << '\n';
        return 2;
    }
}
