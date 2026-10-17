#include "../bank0a/room_message_native_0561.hpp"
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using namespace jpstatic;
static void need(bool v,const char*msg){if(!v)throw std::runtime_error(msg);}
static void put(std::array<uint8_t,16384>&b,unsigned at,unsigned value){
 if(at<0x8000 || at+1>=0xc000)throw std::runtime_error("synthetic fixture OOB");
 b[at-0x8000]=uint8_t(value);b[at+1-0x8000]=uint8_t(value>>8);
}
static std::array<uint8_t,16384> fixture(){
 std::array<uint8_t,16384> b{};
 put(b,0xb909,0xb90d);put(b,0xb90b,0xb917);
 unsigned p=0xb921;
 for(unsigned i=0;i<10;++i) {
  put(b,0xb90d+2*i,p);
  b[p++-0x8000]=uint8_t(0x30+i);
  if(i==5 || i==6)b[p++-0x8000]=uint8_t(0x70+i);
  b[p++-0x8000]=0xff;
 }
 need(p==0xb937,"original 22-byte message table shape");
 return b;
}
static void all_groups_and_termination(){
 auto b=fixture();
 Room0aMessageSelector0561 table(b);
 unsigned items=0,bytes=0;
 for(unsigned group=0;group<2;++group)for(unsigned st=0;st<5;++st) {
  unsigned offset=0;
  const unsigned expected=st+5*group;
  const unsigned payload_bytes=(expected==5 || expected==6)?2u:1u;
  for(unsigned n=0;n<payload_bytes;++n){
   auto v=table.lookup(uint8_t(group),0,st,offset);
   need(v.group_pointer==(group?0xb917:0xb90d) &&
        v.value==(offset==0?0x30+expected:(0x70+expected)),
        "native message fetch must respect group and index");
   ++bytes;
   offset=v.next_offset;
   if(v.terminal)throw std::runtime_error("unexpected early FF");
  }
  auto end=table.lookup(uint8_t(group),0,st,offset);
  need(end.terminal && end.value==0xff &&
       end.next_offset==offset &&
       table.message_length(group,st)==offset+1,
       "original FF terminator must set carry/return without increment");
  ++items;++bytes;
 }
 need(items==10&&bytes==22,"all ten bounded messages contain 22 bytes");
 auto alt=table.lookup(0,1,0,0);
 need(alt.group_pointer==0xb917&&alt.value==0x35,
      "secondary group selected by either RAM flag");
}
static void malformed_rejected(){
 auto b=fixture();Room0aMessageSelector0561 tab(b);
 auto rejects=[&](unsigned st,unsigned offset){
  try{(void)tab.lookup(0,0,st,offset);return false;}
  catch(const std::runtime_error&){return true;}
 };
 need(rejects(5,0),"stage outside five-entry table");
 need(rejects(0,3),"message index past terminator");
 b[0xb921-0x8000]=0xff;
 bool rejected=false;
 try{Room0aMessageSelector0561 bad(b);(void)bad;}
 catch(const std::runtime_error&){rejected=true;}
 need(rejected,"early terminator rejected");
 b=fixture();put(b,0xb90b,0x8000);
 rejected=false;
 try{Room0aMessageSelector0561 bad(b);(void)bad;}
 catch(const std::runtime_error&){rejected=true;}
 need(rejected,"altered original group pointers rejected");
 b=fixture();b[0xb936-0x8000]=0x00;
 rejected=false;
 try{Room0aMessageSelector0561 bad(b);(void)bad;}
 catch(const std::runtime_error&){rejected=true;}
 need(rejected,"missing terminal FF rejected");
}
int main(){
 try{
  all_groups_and_termination();malformed_rejected();
  std::cout<<"PASS JP0561 direct C++ raw0A 2-group 10-message 22-byte terminal lookup\n";
 }catch(const std::exception&e){
  std::cerr<<"FAIL JP0561 room-message translation: "<<e.what()<<'\n';return 1;
 }
}
