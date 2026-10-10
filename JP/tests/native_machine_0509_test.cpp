#include "native_machine_0509.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>

std::vector<std::uint8_t> synthetic_prg() {
    std::vector<std::uint8_t> p(262144,0xEA);
    // Fixed reset program; not copied from game ROM.
    const std::size_t fixed=31*8192;
    p[fixed+0]=0xA9;p[fixed+1]=0x01;                 // LDA #1
    p[fixed+2]=0x8D;p[fixed+3]=0x00;p[fixed+4]=0x80; // STA $8000 (raw bank1)
    p[fixed+5]=0xAD;p[fixed+6]=0x00;p[fixed+7]=0x80; // LDA $8000
    p[fixed+8]=0x8D;p[fixed+9]=0x00;p[fixed+10]=0x00;// STA $00
    p[fixed+11]=0xA9;p[fixed+12]=0x80;               // LDA #80
    p[fixed+13]=0x8D;p[fixed+14]=0x00;p[fixed+15]=0x20; // STA PPUCTRL
    p[fixed+16]=0x4C;p[fixed+17]=0x10;p[fixed+18]=0xE0; // JMP $E010
    p[fixed+32]=0xE6;p[fixed+33]=0x01; // INC $01 when NMI
    p[fixed+34]=0x40;                   // RTI
    p[31*8192+0x1FFA]=0x20;p[31*8192+0x1FFB]=0xE0;
    p[31*8192+0x1FFC]=0x00;p[31*8192+0x1FFD]=0xE0;
    p[31*8192+0x1FFE]=0x20;p[31*8192+0x1FFF]=0xE0;
    p[16384]=0x42;
    return p;
}
void test_mapped_bus(){
    const auto prg=synthetic_prg();const std::vector<std::uint8_t> chr(131072,0);
    cv3::NativeMachine0509 m(prg,chr);
    assert(m.cpu_state().pc==0xE000);
    m.step();assert(m.cpu_state().a==1);
    m.step();assert(m.mapper().prg16_bank()==1);
    m.step();assert(m.cpu_state().a==0x42);
    m.step();assert(m.ram_at(0)==0x42);
    m.set_controller1(0b10101001);
    m.write(0x4016,1);m.write(0x4016,0);
    for(unsigned i=0;i<8;i++)assert((m.read(0x4016)&1)==((0b10101001>>i)&1));
    assert(m.read(0x4016)==1);
    // Native PPUDATA mirrored nametable and palette read/write behavior.
    m.write(0x2006,0x20);m.write(0x2006,0x00);m.write(0x2007,0xCA);
    m.write(0x2006,0x28);m.write(0x2006,0x00);
    (void)m.read(0x2007);
    assert(m.read(0x2007)==0xCA);
    m.write(0x2006,0x3F);m.write(0x2006,0x10);m.write(0x2007,0x36);
    m.write(0x2006,0x3F);m.write(0x2006,0x00);
    assert(m.read(0x2007)==0x36);
    // CPU instruction / vblank NMI interplay, WITHOUT raster/frame parity claim.
    for(int i=0;i<45000&&m.nmis()==0;i++)m.step();
    assert(m.nmis()>0);
    for(int i=0;i<10;i++)m.step();
    assert(m.ram_at(1)>0);
    std::cout<<"VRC6 mapped native CPU/PPU/IRQ bus synthetic NMI PASS\n";
}
int main(){test_mapped_bus();}
