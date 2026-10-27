/* ROM-free original PRG26:$8070 OAM owner observer regressions. */
#include <assert.h>
#include <stdio.h>
#include "../native/enhanced/cviii_nestudio_owner.h"
int main(void)
{
    CviiiNestOwnerTrace t;
    cviii_owner_reset(&t);
    assert(!cviii_owner_ready(&t));
    for(int i=0;i<64;++i)assert(t.owners[i]==CVIII_OWNER_UNKNOWN);
    cviii_owner_enter(&t,4,0x44u,64);
    cviii_owner_enter(&t,6,0xCCu,62);
    cviii_owner_finish(&t,60);
    assert(cviii_owner_ready(&t));
    assert(t.observed==2 && t.attributed==4 && t.invalid==0);
    assert(t.owners[17]==4 && t.owners[2]==4);
    assert(t.owners[51]==6 && t.owners[36]==6);
    cviii_owner_reset(&t);
    cviii_owner_enter(&t,7,0,64);
    cviii_owner_finish(&t,0); /* original non-local OAM-full exit */
    assert(cviii_owner_ready(&t) && t.attributed==64);
    for(int i=0;i<64;++i)assert(t.owners[i]==7);
    cviii_owner_reset(&t);
    cviii_owner_enter(&t,1,0,64);
    cviii_owner_finish(&t,63);
    cviii_owner_enter(&t,2,0,63); /* fabricated overlapping source */
    cviii_owner_finish(&t,62);
    assert(!cviii_owner_ready(&t) && t.invalid>0);
    cviii_owner_reset(&t);
    cviii_owner_enter(&t,28,0,64); /* no owner slot 28 */
    assert(!cviii_owner_ready(&t));
    cviii_owner_reset(&t);
    cviii_owner_enter(&t,1,1,64); /* nonaligned original OAM offset */
    assert(!cviii_owner_ready(&t));
    puts("PASS source-instruction original OAM owner boundaries");
    return 0;
}
