// ROM-free, artificial bank fixture: verifies direct native typed lookup.
// Original-JP comparison is performed by the existing 135-case driver path.
#include "../bank0a/room_selector_native_0560.hpp"
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using namespace jpstatic;
static void need(bool b,const char*msg){if(!b)throw std::runtime_error(msg);}
static void put(std::array<uint8_t,16384>& b,unsigned a,unsigned value){
 if(a<0x8000||a+1>=0xc000)throw std::runtime_error("synthetic bank write OOB");
 b[a-0x8000]=uint8_t(value);
 b[a+1-0x8000]=uint8_t(value>>8);
}
static std::array<uint8_t,16384> fixture(){
 std::array<uint8_t,16384> bank{};
 // Synthetic 15 groups -> 64 second words: first 9 groups have 42,
 // final 6 groups have 22. These are structural domains, not game bytes.
 const std::array<unsigned,15> mid_counts{
   5,5,5,5,5,5,5,5,2,4,4,4,4,4,2};
 unsigned lower=0x92cc,upper=0x9af4;
 for(unsigned st=0;st<15;++st){
  unsigned& cursor=st<9?lower:upper;
  put(bank,0x92ae + 2*st,cursor);
  cursor+=mid_counts[st]*2;
 }
 need(lower==0x9320&&upper==0x9b20,"synthetic stage counts");
 unsigned thirdlo=0x9320,thirdhi=0x9b20;
 for(unsigned mid=0;mid<64;++mid){
  unsigned& cursor=mid<42?thirdlo:thirdhi;
  const unsigned at=mid<42?0x92cc+mid*2:0x9af4+(mid-42)*2;
  put(bank,at,cursor);
  cursor+=(2u+(mid<2 || (mid>=42&&mid<47) ? 1u:0u))*2u;
 }
 need(thirdlo==0x93cc&&thirdhi==0x9b82,"synthetic third-level census");
 // Fill each leaf word with valid typed pool roots, no copyrighted bytes.
 for(unsigned i=0;i<86;++i)
  put(bank,0x9320+2*i, i%13==0?0xab1f:0x93cc+4*(i%113));
 for(unsigned i=0;i<49;++i)
  put(bank,0x9b20+2*i, i%11==0?0xab26:0x9b82+4*(i%43));
 return bank;
}
static void full_census(){
 auto b=fixture();
 Room0aSelector0560 native(b);
 unsigned verified=0,streams=0;
 const std::array<unsigned,15> sizes{5,5,5,5,5,5,5,5,2,4,4,4,4,4,2};
 unsigned middle_global=0,leaf_global=0;
 for(unsigned st=0;st<15;++st){
  for(unsigned mid=0;mid<sizes[st];++mid,++middle_global){
   unsigned third_n=2+(middle_global<2 || (middle_global>=42&&middle_global<47)?1u:0u);
   for(unsigned third=0;third<third_n;++third,++leaf_global){
    const auto v=native.select(st,mid,third);
    need(v.stage_pointer>=0x92cc&&v.middle_pointer>=0x9320,
         "native follows pointer hierarchy");
    need(v.leaf_pointer>=0x93cc&&v.leaf_pointer<0xafa4,
         "native leaf categorized");
    if(v.kind==Room0aPayloadKind::seven_byte_stream)++streams;
    ++verified;
   }
  }
 }
 need(verified==135&&middle_global==64&&leaf_global==135&&streams>0,
      "135 bounded native table selections");
}
static void negative_cases(){
 auto b=fixture();Room0aSelector0560 native(b);
 auto rejects=[&](unsigned a,unsigned c,unsigned d){
  try{(void)native.select(a,c,d);return false;}
  catch(const std::runtime_error&){return true;}
 };
 need(rejects(15,0,0),"stage index boundary");
 need(rejects(0,5,0),"middle index boundary");
 need(rejects(0,0,3),"third index boundary");
 put(b,0x92ae,0xbfff);
 bool rejected=false;
 try{Room0aSelector0560 altered(b);(void)altered;}
 catch(const std::runtime_error&){rejected=true;}
 need(rejected,"altered hierarchy must be rejected");
 auto c=fixture();put(c,0x9320,0x9000);
 Room0aSelector0560 changed(c);
 rejected=false;
 try{(void)changed.select(0,0,0);}
 catch(const std::runtime_error&){rejected=true;}
 need(rejected,"bad leaf classification must be rejected");
}
int main(){
 try{full_census();negative_cases();
  std::cout<<"PASS JP0560 high-level native room selector 135/135 synthetic triples and fail-closed bounds\n";}
 catch(const std::exception&e){
  std::cerr<<"FAIL JP0560 selector "<<e.what()<<'\n';return 1;
 }
}
