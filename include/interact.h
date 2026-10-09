#ifndef INTERACT_H
#define INTERACT_H
#include "gba.h"

void Interact_Reset(void);
int  Interact_Find(int px, int py);                    /* zone index under the player or -1 */
void Interact_Hold(int zone);                          /* B held on a zone this frame */
void Interact_Release(void);
void Interact_Draw(int zone);                          /* prompt text on the HUD layer */
/* Current objective while the power is off: the generator, or the door that leads to it.
   Returns 0 when there is nothing to point at (power already on). */
int  Objective_Get(int *wx, int *wy, const char **label, int *cost);
extern u8 interact_progress;                           /* 0..100 */

#endif
