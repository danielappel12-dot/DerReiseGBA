/* mystery.h - the MYSTERY BOX: pay, watch it roll through the arsenal, take what it lands on */
#ifndef MYSTERY_H
#define MYSTERY_H
#include "gba.h"

#define BOX_PRICE 950

enum { BOX_IDLE, BOX_ROLLING, BOX_READY };

void Box_Reset(void);
void Box_Update(void);
int  Box_State(void);
int  Box_Shown(void);          /* weapon id currently floating above the box */
void Box_Use(void);            /* B held at the box (pays / takes the weapon) */

#endif
