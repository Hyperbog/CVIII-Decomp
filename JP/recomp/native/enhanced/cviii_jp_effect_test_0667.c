#ifdef NDEBUG
#undef NDEBUG
#endif
#include "cviii_jp_effect_state_0667.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void){
 uint8_t before[2048]={0}, after[2048]={0};
 uint8_t used=0;
 CviiiJp0667Effect d={2,0xd7,{0xa5,0x80,0x5c},3};
 assert(cviii_jp0667_effect(before,sizeof before,&d,after,sizeof after,&used));
 assert(used==4&&after[0x0112+2]==7&&after[0x017e + 2]==0xa0&&after[0x0175+2]==5);
 assert(after[0x01b7+2]==0x80&&after[0x0187+2]==0&&after[0x03d9+2]==12&&after[0x03de + 2]==5);
 CviiiJp0667Effect e6={1,0xe6,{0xc5,0,0},1};
 assert(cviii_jp0667_effect(before,sizeof before,&e6,after,sizeof after,&used));
 assert(used==2&&after[0x0113]==0xc5);
 before[0x018e + 1]=0x80;
 assert(cviii_jp0667_effect(before,sizeof before,&e6,after,sizeof after,&used));
 assert(after[0x0113]==5);
 CviiiJp0667Effect eb={0,0xeb,{0x51,0x31,0},2};
 before[0x112]=169;
 assert(cviii_jp0667_effect(before,sizeof before,&eb,after,sizeof after,&used));
 assert(used==3&&after[0x03ed]==252); /* 6502 carry retained! */
 eb.arguments[0]=0;eb.argument_count=1;
 assert(cviii_jp0667_effect(before,sizeof before,&eb,after,sizeof after,&used));
 assert(used==2);
 memset(after,0xa5,sizeof after);used=0x5a;
 CviiiJp0667Effect unsupported={0,0xed,{0,0,0},1};
 assert(!cviii_jp0667_effect(before,sizeof before,&unsupported,after,sizeof after,&used));
 for(unsigned i=0;i<sizeof after;i++) assert(after[i]==0xa5);
 assert(used==0x5a);
 CviiiJp0667Effect bad={8,0xe0,{0,0,0},0};
 assert(!cviii_jp0667_effect(before,sizeof before,&bad,after,sizeof after,&used));
 puts("PASS JP0667 synthetic D/E effects: original carry/width, local RAM and fail-closed unknown E handlers");
 return 0;
}
