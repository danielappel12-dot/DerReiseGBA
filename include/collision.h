#ifndef COLLISION_H
#define COLLISION_H
#include "gba.h"

/* Footprint boxes: x in [px-hw, px+hw), y in [py-hu, py).  (px,py) = feet position in pixels. */
#define COL_HIT_X 1
#define COL_HIT_Y 2

int Col_BoxSolid(int px, int py, int hw, int hu);
/* move a feet position (8.8 fixed) by (dx,dy) (8.8) with wall sliding; returns COL_HIT_* bits */
int Col_Move(s32 *x, s32 *y, s32 dx, s32 dy, int hw, int hu);
/* tile based line of sight between two pixel points (1 = clear) */
int Col_LineClear(int x0, int y0, int x1, int y1);

#endif
