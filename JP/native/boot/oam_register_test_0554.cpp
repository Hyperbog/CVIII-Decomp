#include "static_6502.hpp"
#include <iostream>
#include <memory>
#include <stdexcept>
using namespace jpstatic;
static void check(bool pass,const char*label){if(!pass)throw std::runtime_error(label);}
static void direct_and_dma_shared_oam(){
 auto bus=std::make_unique<Bus>();bus->whole_prg=true;
 for(unsigned i=0;i<256;++i)bus->ram[0x200+i]=uint8_t(i^0x5au);
 Cpu c(*bus);c.enable_timed_ppu_registers();c.enable_ram_oam_dma(0);
 c.a=0xfc;c.exec<Op::STA,Mode::abs>(0x200b,0x8003); // mirrored $2003.
 check(c.oam_dma.oam_address()==0xfc && c.cycles==4,"OAMADDR mirror");
 c.a=0xaa;c.exec<Op::STA,Mode::abs>(0x2004,0x8006);
 check(c.oam_dma.oam()[0xfc]==0xaa && c.oam_dma.oam_address()==0xfd,
       "OAMDATA write increments");
 c.exec<Op::LDA,Mode::abs>(0x200c,0x8009); // mirrored $2004, read does not increment.
 check(c.a==0 && c.oam_dma.oam_address()==0xfd,"OAMDATA read leaves address unchanged");
 c.a=2;c.exec<Op::STA,Mode::abs>(0x4014,0x800c);
 check(c.oam_dma.completed_transfers()==1 && c.oam_dma.oam_address()==0xfd,
       "DMA complete with original OAMADDR");
 check(c.oam_dma.oam()[0xfc]==(0xff^0x5a) &&
       c.oam_dma.oam()[0xfd]==(0x00^0x5a) &&
       c.oam_dma.oam()[0xfe]==(0x01^0x5a),
       "DMA and $2004 share the same OAM byte array");
 c.a=0xfc;c.exec<Op::STA,Mode::abs>(0x2003,0x800f);
 c.exec<Op::LDA,Mode::abs>(0x2004,0x8012);
 check(c.a==uint8_t(0xff^0x5a) && c.oam_dma.oam_address()==0xfc,
       "read back DMA byte through OAMDATA");
 check(c.ppu_io.events().size()==5 &&
       c.ppu_io.events()[0].register_address==0x2003 &&
       c.ppu_io.events()[2].register_address==0x2004,
       "cycle-stamped PPU OAM event records");
}
static void rendering_time_rejection(){
 auto b=std::make_unique<Bus>();b->whole_prg=true;
 Cpu c(*b);c.enable_timed_ppu_registers();c.enable_ram_oam_dma(0);
 c.a=0x08;c.exec<Op::STA,Mode::abs>(0x2001,0x8003);
 check(c.ppu_clock.active_rendering(),"test must enable rendering");
 bool rejected=false;
 c.a=0x44;
 try{c.exec<Op::STA,Mode::abs>(0x2003,0x8006);}
 catch(const std::runtime_error&){rejected=true;}
 check(rejected && c.oam_dma.oam_address()==0,
       "OAMADDR during rendering must fail closed");
 rejected=false;
 try{c.exec<Op::LDA,Mode::abs>(0x2004,0x8009);}
 catch(const std::runtime_error&){rejected=true;}
 check(rejected,"OAMDATA read during rendering must fail closed");
 rejected=false;
 try{b->write(0x2003,0);}
 catch(const std::runtime_error&){rejected=true;}
 check(rejected,"failed OAM register must not leak timed access permission");
 // Rendering disabled: OAM writes now legal.
 c.a=0;c.exec<Op::STA,Mode::abs>(0x2001,0x800c);
 c.a=0x11;c.exec<Op::STA,Mode::abs>(0x2004,0x800f);
 check(c.oam_dma.oam()[0]==0x11 && c.oam_dma.oam_address()==1,
       "forced blanking permits OAMDATA write");
}
static void detached_and_legacy(){
 auto b=std::make_unique<Bus>();b->whole_prg=true;
 Cpu c(*b);c.enable_timed_ppu_registers();
 bool rejected=false;c.a=0xf0;
 try{c.exec<Op::STA,Mode::abs>(0x2003,0x8003);}
 catch(const std::runtime_error&){rejected=true;}
 check(rejected,"unattached OAM cannot be fabricated");
 c.enable_ram_oam_dma(0);
 c.exec<Op::STA,Mode::abs>(0x2003,0x8006);
 check(c.oam_dma.oam_address()==0xf0,"enable after PPU register attachment");
 auto b2=std::make_unique<Bus>();b2->whole_prg=true;Cpu legacy(*b2);
 legacy.a=0x12;legacy.exec<Op::STA,Mode::abs>(0x2003,0x8003);
 check(legacy.oam_dma.oam_address()==0 && b2->io_writes.size()==1,
       "0553 scripted driver stays unchanged");
}
int main(){
 try{
  direct_and_dma_shared_oam();
  rendering_time_rejection();
  detached_and_legacy();
  std::cout<<"PASS JP0554 OAMADDR/OAMDATA direct and DMA shared backing, blanking guard\n";
 }catch(const std::exception&e){std::cerr<<"FAIL JP0554 OAM registers: "<<e.what()<<'\n';return 1;}
}
