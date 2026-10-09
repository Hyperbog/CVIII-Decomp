#pragma once
#include <cstdint>
namespace cv3 {
// JP PRG31:$FB96-$FBA4. Models bus-observable bank writes/read, not stack timing.
// E2D0 writes A to RAM $23 then mapper register $8000.
struct TemporaryPrgReadResult {
    std::uint8_t value;
    std::uint16_t effective_address;
    bool zero;
    bool negative;
};
template<class ReadCpu8, class WriteCpu8>
[[nodiscard]] inline TemporaryPrgReadResult temporary_prg_bank0e_read(
    ReadCpu8&& read, WriteCpu8&& write, std::uint8_t y) {
    write(std::uint16_t(0x23),std::uint8_t(0x0E));
    write(std::uint16_t(0x8000),std::uint8_t(0x0E));
    const unsigned lo=read(std::uint16_t(8)), hi=read(std::uint16_t(9));
    const auto address=std::uint16_t((lo|(hi<<8))+y);
    const auto value=std::uint8_t(read(address));
    write(std::uint16_t(0x23),std::uint8_t(0x0A));
    write(std::uint16_t(0x8000),std::uint8_t(0x0A));
    return {value,address,value==0,(value&0x80u)!=0};
}
} // namespace cv3
