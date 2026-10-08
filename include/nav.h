#ifndef NAV_H
#define NAV_H
#include "gba.h"

/* Grid flow field toward the player, built incrementally (breadth first search). */
void Nav_Reset(void);
void Nav_Update(int target_tx, int target_ty, int budget);
/* best neighbouring direction from tile (tx,ty): returns 1 and fills dir (-1..1) or 0 when unreachable */
int  Nav_Step(int tx, int ty, int *dirx, int *diry);
int  Nav_Dist(int tx, int ty);           /* path length in tiles (255 = unreachable) */
int  Nav_Ready(void);

#endif
