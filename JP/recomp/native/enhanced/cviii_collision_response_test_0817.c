/* JP0817 synthetic original response-state regressions, ROM-free.
 * These are bounded predicted state transitions, never guest writes. */
#include "cviii_collision_response_0817.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static void ok(int good,const char *why){
 if(!good){fprintf(stderr,"JP0817 FAIL: %s\n",why);exit(1);}
}
int main(void){
 static uint8_t ram[2048],b[16384];
 const unsigned x=3u;
 CviiiResponse0817 r={0};
 ram[0x7fu]=0u;
 ram[0x054eu+x]=0x69u;
 ram[0x0400u+x]=1u;
 ram[0x0438u]=0x50u;ram[0x0438u+x]=0x50u;
 ram[0x041cu]=0x60u;ram[0x041cu+x]=0x60u;
 b[0xbb80u+0x69u-0x8000u]=0x10u;
 b[0xbb05u-0x8000u]=0x04u;
 b[0xb97du-0x8000u]=0u;
 b[0xbc08u+0x69u-0x8000u]=0u;
 b[0xb0e3u-0x8000u]=0x31u;
 b[0xb0e2u-0x8000u]=0x21u;
 b[0xb110u-0x8000u]=0x03u; /* cleared-$AC type accumulator */
 ram[0x7eu]=1u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.next_pc==0xb258u && !r.checked_b80e && !r.write_mask,
    "B115 $7E=1 skips independent B80E contact helper");
 ram[0x7eu]=0u;
 ram[0x0438u+x]=0x90u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.next_pc==0xb258u && r.checked_b80e &&
    r.b80e_carry && !r.b80e_checked_y,
    "B80E far horizontal exits B115 without contact");
 ram[0x0438u+x]=0x50u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.next_pc==0xb249u && r.checked_b80e &&
    !r.b80e_carry && r.b80e_checked_y &&
    r.predicted_7e==0x31u && r.write_mask==CVIII_RESPONSE_7E_0817,
    "B115 type69 near writes exact B0E3 event descriptor");
 ram[0x041cu+x]=0x68u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    !r.b80e_carry && r.b80e_y==7u,
    "B80E negative vertical difference eight becomes seven via EOR FF");
 ram[0x041cu+x]=0x6au;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.b80e_carry && r.b80e_y==9u && r.next_pc==0xb258u,
    "B80E negative vertical difference ten remains far");
 ram[0x041cu+x]=0x60u;
 ram[0x054eu+x]=0x6du;ram[0x0657u+x]=2u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.predicted_7e==0x0cu && r.next_pc==0xb249u,
    "B115 type6D special chooses $0C from $0657");
 ram[0x054eu+x]=0x72u;ram[0x0606u+x]=0u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.predicted_7e==0x1cu,
    "B115 type72 special chooses $1C without $0606");
 ram[0x0606u+x]=1u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r) &&
    r.predicted_7e==0x0cu,
    "B115 type72 special chooses $0C with $0606");
 ram[0x054eu+x]=0x69u;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb18au,&r) &&
    r.next_pc==0xb249u && r.predicted_7e==0x21u &&
    r.predicted_0669==0x10u &&
    r.write_mask==(CVIII_RESPONSE_7E_0817|CVIII_RESPONSE_0669_0817),
    "B18A direct table B0E2 plus 0669 timer write");
 ram[0x054eu+x]=0x6eu;ram[0xacu]=1u;ram[0xb5u]=(uint8_t)x;
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb18au,&r) &&
    r.next_pc==0xb258u && !r.write_mask,
    "B18A $AC owner already X avoids reaction state");
 ram[0xb5u]=(uint8_t)(x+1u);
 ok(cviii_response_b115_b18a_0817(ram,b,x,0xb18au,&r) &&
    r.next_pc==0xb249u && r.predicted_ac==0u &&
    r.predicted_7e==0x03u && r.predicted_0669==0x10u &&
    r.write_mask==7u,
    "B18A clears different-owner AC, original accumulator becomes zero");
 ram[0x054eu+x]=0x73u;
 ok(!cviii_response_b115_b18a_0817(ram,b,x,0xb18au,&r),
    "B162 type73 alternate route cannot pass B634");
 ram[0x054eu+x]=0x80u;
 ok(!cviii_response_b115_b18a_0817(ram,b,x,0xb115u,&r),
    "original type80 bypasses both B115/B18A B634 routes");
 puts("PASS JP0817 bounded B115/B80E/B18A response-state decisions");
 return 0;
}
