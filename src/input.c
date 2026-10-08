#include "input.h"

u16 keys_held, keys_down, keys_up;

void Input_Update(void)
{
    u16 now = (u16)(~REG_KEYINPUT & KEY_ANY);
    keys_down = now & ~keys_held;
    keys_up = keys_held & ~now;
    keys_held = now;
}
