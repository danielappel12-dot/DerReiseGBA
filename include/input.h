#ifndef INPUT_H
#define INPUT_H
#include "gba.h"

extern u16 keys_held, keys_down, keys_up;

void Input_Update(void);
#define KeyHeld(k)    (keys_held & (k))
#define KeyPressed(k) (keys_down & (k))
#define KeyReleased(k) (keys_up & (k))

#endif
