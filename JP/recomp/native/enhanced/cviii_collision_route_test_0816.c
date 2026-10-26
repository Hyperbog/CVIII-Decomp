/* JP0816 pure routing regression: no game-state writes or hitboxes. */
#include "cviii_collision_route_0816.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
static void test(int pass,const char *why){
 if(!pass){fprintf(stderr,"FAIL JP0816 route: %s\n",why);exit(1);}
}
/* Independent source-control-flow oracle uses original PC boundaries. */
static uint16_t oracle(uint8_t type,uint8_t flags,uint8_t frame,
                       uint8_t v7e,uint8_t v7d) {
  if(flags&0x11u)return 0xb1f7u;
  if(!frame)return 0xb1f7u;
  if(type>=0x83u)return 0xb1f7u;
  if(type>=0x80u)return 0xb258u;
  if(type>=0x58u && type<=0x60u)return 0xb1f7u;
  if(v7e&0xf0u)return 0xb258u;
  if(type>=0x69u){
     switch(type){
       case 0x73:return 0xb227u;
       case 0x75:return 0xb1d1u;
       case 0x6a:return 0xb106u;
       case 0x6f:return 0xb10cu;
       case 0x70:return 0xb109u;
       default:return 0xb634u;
     }
  }
  if(flags&2u)return 0xb1d8u;
  if(v7d)return 0xb258u;
  return 0xb232u;
}
int main(void){
 unsigned long cases=0;
 for(unsigned ty=0;ty<256u;ty++)
 for(unsigned f=0;f<256u;f++)
 for(unsigned frame=0;frame<2u;frame++)
 for(unsigned mode=0;mode<4u;mode++){
  const uint8_t a=(uint8_t)(mode&1u ? 0xf0u:0u);
  const uint8_t b=(uint8_t)(mode&2u ? 1u:0u);
  uint16_t got=cviii_b1f8_route_0816(
      (uint8_t)ty,(uint8_t)f,(uint8_t)frame,a,b);
  test(got==oracle((uint8_t)ty,(uint8_t)f,
             (uint8_t)frame,a,b),"original route PCs");
  cases++;
 }
 test(cviii_b1f8_route_0816(0x80,0,1,0,0)==0xb258,
      "type80 never enters B162");
 test(cviii_b1f8_route_0816(0x7f,0,1,0,0)==0xb634,
      "type7F uses special original B634 comparison");
 test(cviii_b1f8_route_0816(0x3d,0,1,0,0)==0xb232,
      "type3D can enter original B339 collision measure");
 test(cviii_b1f8_route_0816(0x80,0x81,1,0,0)==0xb1f7,
      "naturally observed flag81 type80 skips at earlier B1F8");
 test(cviii_b162_dispatch_0816(0x73)==0xb227 &&
      cviii_b162_dispatch_0816(0x75)==0xb1d1 &&
      cviii_b162_dispatch_0816(0x6a)==0xb106 &&
      cviii_b162_dispatch_0816(0x6f)==0xb10c &&
      cviii_b162_dispatch_0816(0x70)==0xb109,
      "original five explicit B162 type exceptions");
 printf("PASS JP0816 %lu original-route synthetic comparisons + 5 guards\n",cases);
 return 0;
}
