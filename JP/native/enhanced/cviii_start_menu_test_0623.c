/* JP0623 strict C11 ROM-free action table, mutability and navigation tests. */
#include "cviii_start_menu_0623.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int enabled(void *ctx){return *(int *)ctx;}
int main(void)
{
    CviiiStartMenu m={0},blank={0};
    int active=0;
    CviiiStartEntry extra={"other.debug","DEBUG",CVIII_START_EXTENSION,enabled,&active};
    assert(!cviii_start_toggle(&blank,1,1));
    assert(cviii_start_defaults(&m));
    assert(m.count==4);
    assert(!strcmp(m.entries[0].id,"core.save_state"));
    assert(!strcmp(m.entries[1].id,"core.load_state"));
    assert(!strcmp(m.entries[2].id,"core.audio"));
    assert(!strcmp(m.entries[3].id,"core.quit"));
    assert(!cviii_start_defaults(&m));
    assert(cviii_start_find(&m,"core.audio")==&m.entries[2]);
    assert(!cviii_start_find(&m,"other.absent"));
    CviiiStartEntry forbidden={"core.something","BAD",CVIII_START_EXTENSION,NULL,NULL};
    assert(!cviii_start_register(&m,&forbidden));
    CviiiStartEntry privilege={"other.save","ILLEGAL",CVIII_START_SAVE,NULL,NULL};
    assert(!cviii_start_register(&m,&privilege));
    CviiiStartEntry malformed={"bad id","BAD",CVIII_START_EXTENSION,NULL,NULL};
    assert(!cviii_start_register(&m,&malformed));
    assert(cviii_start_register(&m,&extra));
    assert(!cviii_start_register(&m,&extra));
    assert(m.count==5);
    assert(!cviii_start_toggle(&m,0,1));
    assert(!cviii_start_toggle(&m,1,0));
    assert(cviii_start_toggle(&m,1,1));
    assert(m.open && m.selected==0);
    assert(cviii_start_accept(&m)==CVIII_START_SAVE);
    assert(cviii_start_move(&m,1) && m.selected==1);
    assert(cviii_start_accept(&m)==CVIII_START_LOAD);
    assert(cviii_start_move(&m,1) && m.selected==2);
    assert(cviii_start_accept(&m)==CVIII_START_AUDIO);
    assert(cviii_start_move(&m,1) && m.selected==3);
    assert(cviii_start_accept(&m)==CVIII_START_NONE && m.quit_armed);
    assert(cviii_start_accept(&m)==CVIII_START_QUIT);
    assert(cviii_start_move(&m,1) && m.selected==4);
    assert(!m.quit_armed);
    assert(cviii_start_accept(&m)==CVIII_START_NONE);
    active=1;
    assert(cviii_start_accept(&m)==CVIII_START_EXTENSION);
    assert(cviii_start_move(&m,1)&&m.selected==0);
    assert(cviii_start_move(&m,-1)&&m.selected==4);
    cviii_start_seal(&m);
    assert(!cviii_start_register(&m,&extra));
    assert(cviii_start_toggle(&m,0,0)); /* close always permitted */
    assert(!m.open);
    assert(!cviii_start_move(&m,1));
    assert(cviii_start_accept(&m)==CVIII_START_NONE);
    assert(cviii_start_toggle(&m,1,1));
    assert(m.selected==0);
    cviii_start_close(&m);
    assert(!m.open);
    puts("PASS JP0623 stable actions, extension slots, confirm quit and modal safety");
    return 0;
}
