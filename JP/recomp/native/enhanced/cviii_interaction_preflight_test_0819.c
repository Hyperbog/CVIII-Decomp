/* JP0819 synthetic original raw0B B3EC and B29D preflight only.
 * No copyrighted bank data, live game RAM or gameplay side effects. */
#include "cviii_interaction_preflight_0819.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void ok(int yes,const char *label){
 if(!yes){fprintf(stderr,"FAIL JP0819: %s\n",label);exit(1);}
}
int main(void){
 static uint8_t ram[2048],bank[16384];
 CviiiB3ec0819 p={0};
 const unsigned x=3u,type=0x7fu;
 ram[0x054eu+x]=(uint8_t)type;
 ram[0x0438u]=80u;ram[0x041cu]=95u;
 ram[0x042fu]=90u;ram[0x0438u+x]=80u;ram[0x041cu+x]=90u;
 ram[0x0561u]=0u;ram[0x04a8u]=0u;ram[0x7fu]=0u;
 bank[0xbb17u-0x8000u]=5u;
 bank[0xbb1bu-0x8000u]=4u;
 bank[0xbb1fu-0x8000u]=0u;
 bank[0xbb27u-0x8000u]=0u;
 bank[0xbb80u+type-0x8000u]=10u;
 bank[0xbc08u+type-0x8000u]=7u;
 ok(cviii_b3ec_preflight_0819(ram,bank,x,&p) &&
    p.stop_pc==0xb446u && p.decision==CVIII_0819_NEAR &&
    p.x_distance==0u && p.y_distance==0u &&
    p.clearance_x==15u && p.clearance_y==11u,
    "B3EC original table X/Y near comparison");
 ram[0x0438u+x]=210u; /* 130-pixel precondition early failure */
 ok(cviii_b3ec_preflight_0819(ram,bank,x,&p) &&
    p.decision==CVIII_0819_FAR && p.carry &&
    !p.checked_y,"B3EC initial unsigned abs delta >=128");
 ram[0x0438u+x]=100u;
 ok(cviii_b3ec_preflight_0819(ram,bank,x,&p) &&
    p.decision==CVIII_0819_FAR && !p.checked_y,
    "B3EC X clearance failure before Y");
 ram[0x0438u+x]=80u;ram[0x041cu+x]=105u;
 ok(cviii_b3ec_preflight_0819(ram,bank,x,&p) &&
    p.decision==CVIII_0819_FAR && p.checked_y &&
    p.y_distance==15u,
    "B3EC Y clearance failure");
 ram[0x041cu+x]=90u;ram[0xb7u]=1u;
 ok(cviii_b3ec_preflight_0819(ram,bank,x,&p) &&
    p.decision==CVIII_0819_UNKNOWN && p.needs_e5be &&
    p.stop_pc==0xb41fu,
    "B3EC B7 external E5BE branch deferred");
 ram[0xb7u]=0u;ram[0x0561u]=4u;
 ok(!cviii_b3ec_preflight_0819(ram,bank,x,&p),
    "unsupported sprite $BB17 group does not spill adjacent tables");
 ram[0x0561u]=0u;ram[0x04a8u]=8u;
 ok(!cviii_b3ec_preflight_0819(ram,bank,x,&p),
    "unsupported sprite pose does not read adjacent original table");
 ram[0x04a8u]=0u;
 CviiiPartnerPreflight0819 w={0};
 memset(ram+0x054eu+20u,0,3u);
 ok(cviii_partner_scan_0819(ram,bank,x,&w) &&
    w.decision==CVIII_0819_FAR && w.stop_pc==0xb31fu &&
    w.skipped_empty==3u,
    "B29D all three empty partner actor slots");
 ram[0x054eu+21u]=2u;
 ram[0x0438u+21u]=82u;
 ram[0x041cu+21u]=92u;
 bank[0xbb60u+2u-0x8000u]=4u;
 bank[0xbb6bu+2u-0x8000u]=4u;
 ok(cviii_partner_scan_0819(ram,bank,x,&w) &&
    w.decision==CVIII_0819_NEAR && w.stop_pc==0xb2b5u &&
    w.first_partner_slot==21u && w.mask==4u,
    "B29D slot21 first original near candidate, stop B727");
 ram[0x068du+x]=4u;
 ok(cviii_partner_scan_0819(ram,bank,x,&w) &&
    w.decision==CVIII_0819_FAR && w.skipped_masked==1u,
    "B323 original slot21 bit4 suppresses partner");
 ram[0x068du+x]=0u;ram[0x0438u+21u]=200u;
 ok(cviii_partner_scan_0819(ram,bank,x,&w) &&
    w.decision==CVIII_0819_FAR &&
    w.stop_pc==0xb31fu && w.tested_partners==1u,
    "B447 generic partner far X returns original scan");
 ram[0x054eu+21u]=5u;
 ok(cviii_partner_scan_0819(ram,bank,x,&w) &&
    w.decision==CVIII_0819_UNKNOWN &&
    w.stop_pc==0xb447u,
    "B447 special partner type5 requires separate $0593 X lookup");
 ram[0x054eu+21u]=2u;ram[0xb7u]=1u;
 ok(cviii_partner_scan_0819(ram,bank,x,&w) &&
    w.decision==CVIII_0819_UNKNOWN,
    "B447 original external E5BE stage never guessed");
 ok(!cviii_partner_scan_0819(ram,bank,0,&w) &&
    !cviii_b3ec_preflight_0819(ram,bank,19,&p),
    "invalid original actor slots fail closed");
 puts("PASS JP0819 original B3EC + three-slot B29D preflight predictions");
 return 0;
}
