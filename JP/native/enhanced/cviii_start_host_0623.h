/* JP0623: game-owned pure menu state adapter called by pinned SDL host.
 * The platform executes returned actions via existing safe save/load/quit. */
#ifndef CVIII_START_HOST_0623_H
#define CVIII_START_HOST_0623_H
int cviii_pause_active(void);
int cviii_pause_toggle(void);
void cviii_pause_close(void);
void cviii_pause_move(int direction); /* -1 up, +1 down */
int cviii_pause_accept(void); /* CviiiStartAction enum, 0 if no action */
#endif
