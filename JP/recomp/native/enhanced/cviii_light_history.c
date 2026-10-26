/* Host-only authoring undo/redo. Never snapshot NES machine state.
 * No heap allocation; history depth is bounded independent of save slots.
 */
#include "cviii_lighting.h"
#include <string.h>
#define CVIII_HISTORY_CAP 16
static CviiiLighting undo[CVIII_HISTORY_CAP],redo[CVIII_HISTORY_CAP];
static int undo_count,redo_count;
void cviii_light_history_reset(void){undo_count=redo_count=0;}
static void append(CviiiLighting *items,int *count,const CviiiLighting *state){
    if(*count==CVIII_HISTORY_CAP){
        memmove(items,items+1,(CVIII_HISTORY_CAP-1)*sizeof items[0]);
        --*count;
    }
    items[(*count)++]=*state;
}
void cviii_light_history_push(const CviiiLighting *s){
    if(!s)return;
    /* Consecutive duplicate snapshots only waste editor undo capacity. */
    if(undo_count && !memcmp(&undo[undo_count-1],s,sizeof *s))return;
    append(undo,&undo_count,s);
    redo_count=0;
}
int cviii_light_history_undo(CviiiLighting *s){
    if(!s || !undo_count)return 0;
    append(redo,&redo_count,s);
    int editor=s->edit;
    *s=undo[--undo_count];
    s->edit=editor;s->dragging=0;
    return 1;
}
int cviii_light_history_redo(CviiiLighting *s){
    if(!s || !redo_count)return 0;
    append(undo,&undo_count,s);
    int editor=s->edit;
    *s=redo[--redo_count];
    s->edit=editor;s->dragging=0;
    return 1;
}
int cviii_light_history_can_undo(void){return undo_count>0;}
int cviii_light_history_can_redo(void){return redo_count>0;}
