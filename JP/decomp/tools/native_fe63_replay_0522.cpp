// Compare original-Mesen FE63 before/after CPU-state captures with
// ROM-free structured native lift. Exclude stack modified by JSR/RTS.
#include "scheduler_fe63_0522.hpp"
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
        throw std::runtime_error("Expected exactly 2048 bytes in Mesen RAM capture");
    return r;
}
unsigned number(const char* arg) {
    const std::string_view value{arg};
    const auto s = value.starts_with("0x") ? value.substr(2) : value;
    unsigned n = 0;
    const auto [end, ec] = std::from_chars(s.data(), s.data() + s.size(), n, 16);
    if (ec != std::errc{} || end != s.data() + s.size())
        throw std::invalid_argument("Invalid hexadecimal register argument");
    return n;
}
}
int main(int argc, char** argv) {
    try {
        if (argc != 13) {
            std::cerr << "usage: native_fe63_replay_0522 before.bin after.bin "
                "entryX entryA entryY entryP expectedPC expectedA expectedX "
                "expectedY expectedP expectedBank (hex)\n";
            return 2;
        }
        auto before = load(argv[1]);
        const auto after = load(argv[2]);
        const unsigned entry[] = {number(argv[3]), number(argv[4]),
                                  number(argv[5]), number(argv[6])};
        for (auto reg : entry) if (reg > 255) throw std::invalid_argument("Register exceeds 8 bits");
        const auto result = cv3::scheduler_fe63_to_next_0522(before,
            static_cast<std::uint8_t>(entry[0]), static_cast<std::uint8_t>(entry[1]),
            static_cast<std::uint8_t>(entry[2]), static_cast<std::uint8_t>(entry[3]));
        unsigned ram_bad = 0, bad = 0, checked = 0;
        for (unsigned i = 0; i < before.size(); ++i) {
            if (i >= 0x100 && i < 0x200) continue;
            ++checked;
            if (before[i] != after[i]) {
                if (ram_bad < 8) std::cerr << "RAM $" << std::hex << i
                    << ": native=" << unsigned(before[i])
                    << " original=" << unsigned(after[i]) << '\n';
                ++ram_bad;
                ++bad;
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
        std::cout << (bad ? "FAIL" : "PASS") << " 0522 replay: "
            << (checked-ram_bad) << "/" << checked
            << " nonstack RAM bytes; total mismatches=" << bad << '\n';
        return bad ? 1 : 0;
    } catch (const std::exception& e) {
        std::cerr << "0522 replay unavailable: " << e.what() << '\n';
        return 2;
    }
}
