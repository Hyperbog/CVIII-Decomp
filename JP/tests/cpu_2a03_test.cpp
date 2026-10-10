#include "cpu_2a03.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using cv3::Cpu2A03;
struct TestBus final: cv3::CpuBus {
    std::array<std::uint8_t,65536> bytes{};
    unsigned writes=0,reads=0;
    std::uint8_t read(std::uint16_t a) override {++reads;return bytes[a];}
    void write(std::uint16_t a,std::uint8_t v) override {++writes;bytes[a]=v;}
};
void test_indirect_wrap_and_stack(){
    TestBus b; Cpu2A03 c(b);
    b.bytes[0xFFFC]=0x00;b.bytes[0xFFFD]=0x80;
    b.bytes[0x8000]=0x6C;b.bytes[0x8001]=0xFF;b.bytes[0x8002]=0x04;
    b.bytes[0x04FF]=0x02;b.bytes[0x0400]=0x90;b.bytes[0x0500]=0xAA;
    b.bytes[0x9002]=0x20;b.bytes[0x9003]=0x0A;b.bytes[0x9004]=0x90;
    b.bytes[0x9005]=0x00;b.bytes[0x9006]=0xEA;
    b.bytes[0x900A]=0x60;
    c.reset();assert(c.registers().pc==0x8000&&c.cycle_count()==7);
    assert(c.step()==5&&c.registers().pc==0x9002);
    assert(c.step()==6&&c.registers().pc==0x900A&&c.registers().sp==0xFB);
    assert(b.bytes[0x1FD]==0x90&&b.bytes[0x1FC]==0x04);
    assert(c.step()==6&&c.registers().pc==0x9005&&c.registers().sp==0xFD);
    assert(c.instruction_count()==3);
}
void test_brk_rti(){
    TestBus b; Cpu2A03 c(b);
    b.bytes[0x8000]=0x00;b.bytes[0xFFFE]=0x00;b.bytes[0xFFFF]=0x90;
    b.bytes[0x9000]=0x40;
    c.set_registers({0x8000,0,0,0,0xFD,0x20});
    assert(c.step()==7&&c.registers().pc==0x9000);
    assert(b.bytes[0x1FD]==0x80&&b.bytes[0x1FC]==0x02);
    assert(b.bytes[0x1FB]&0x10);
    assert(c.cycle_count()==7);
    assert(c.step()==6&&c.registers().pc==0x8002);
    assert(!(c.registers().p&0x10));
}
void test_adc_sbc_full_domain(){
    TestBus b;Cpu2A03 c(b);
    b.bytes[0x3000]=0x69;b.bytes[0x3001]=0;
    b.bytes[0x3002]=0xE9;b.bytes[0x3003]=0;
    unsigned tests=0;
    for(unsigned a=0;a<256;a++)for(unsigned v=0;v<256;v++)for(unsigned carry=0;carry<2;carry++){
        b.bytes[0x3001]=std::uint8_t(v);b.bytes[0x3003]=std::uint8_t(v);
        for(unsigned which=0;which<2;which++){
            const std::uint16_t rhs=which?std::uint16_t(v^255):v;
            const std::uint16_t sum=std::uint16_t(a)+rhs+carry;
            const std::uint8_t out=std::uint8_t(sum);
            const bool over=bool((~(a^rhs)&(a^out)&0x80)!=0);
            c.set_registers({std::uint16_t(which?0x3002:0x3000),std::uint8_t(a),0,0,0xFD,std::uint8_t(0x28|carry)});
            assert(c.step()==2);
            auto s=c.registers();
            if(s.a!=out||bool(s.p&1)!=(sum>255)||bool(s.p&0x40)!=over||bool(s.p&2)!=(out==0)||bool(s.p&0x80)!=bool(out&128))
                throw std::runtime_error("ADC/SBC exhaustive mismatch");
            ++tests;
        }
    }
    assert(tests==262144);
    std::cout<<"binary ADC/SBC exhaustive PASS "<<tests<<" cases\n";
}
void test_branch_page_and_rmw(){
    TestBus b;Cpu2A03 c(b);
    b.bytes[0x8000]=0xD0;b.bytes[0x8001]=0xFE;
    c.set_registers({0x8000,0,0,0,0xFD,0x20});
    assert(c.step()==3&&c.registers().pc==0x8000);
    b.bytes[0x80FE]=0xD0;b.bytes[0x80FF]=0xFF;
    c.set_registers({0x80FE,0,0,0,0xFD,0x20});
    assert(c.step()==4&&c.registers().pc==0x80FF);
    b.bytes[0x8000]=0x06;b.bytes[0x8001]=0x12;b.bytes[0x12]=0x80;
    c.set_registers({0x8000,0,0,0,0xFD,0x20});const auto old=b.writes;
    assert(c.step()==5&&b.bytes[0x12]==0&&b.writes==old+2);
    assert((c.registers().p&0x03)==0x03);
    b.bytes[0x8000]=0x02;
    c.set_registers({0x8000,0,0,0,0xFD,0x24});
    bool failed=false;try{c.step();}catch(const std::runtime_error&){failed=true;}
    assert(failed);
}
void test_irq_nmi(){
    TestBus b;Cpu2A03 c(b);
    b.bytes[0xFFFA]=0x45;b.bytes[0xFFFB]=0x82;
    b.bytes[0xFFFE]=0x60;b.bytes[0xFFFF]=0x83;
    c.set_registers({0x8000,0,0,0,0xFD,0x24});c.irq();assert(c.registers().pc==0x8000);
    c.nmi();assert(c.registers().pc==0x8245&&c.cycle_count()==7);
    assert(b.bytes[0x1FD]==0x80&&b.bytes[0x1FC]==0);
    assert((b.bytes[0x1FB]&0x10)==0);
    c.set_registers({0x8000,0,0,0,0xFD,0x20});c.irq();assert(c.registers().pc==0x8360);
}
int main(){test_indirect_wrap_and_stack();test_brk_rti();test_adc_sbc_full_domain();test_branch_page_and_rmw();test_irq_nmi();std::cout<<"native 2A03 instruction regression PASS\n";}
