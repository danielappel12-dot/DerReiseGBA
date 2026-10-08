#include "input.h"

u16 keys_held, keys_down, keys_up;

#ifdef BOT
#include "game.h"
/* Self-playing stress-test input (make BOT=1): walks around, shoots, retries after death. */
static u32 bot_t, bot_seed = 12345;
static u16 bot_dir, bot_pulse;
static u32 bot_rand(void) { bot_seed = bot_seed * 1664525u + 1013904223u; return bot_seed >> 16; }

static u16 bot_keys(void)
{
    bot_t++;
    switch (G.state) {
    case ST_TITLE: case ST_MENU: case ST_CONTROLS:
        return (bot_t % 60 == 5) ? KEY_START : 0;
    case ST_GAME_OVER:
        return (bot_t % 60 == 5) ? KEY_A : 0;
    case ST_PAUSED: case ST_STATUS:
        return KEY_START;
    default: break;
    }
    if (bot_t % 50 == 0) {
        static const u16 dirs[9] = { 0, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP | KEY_LEFT,
                                     KEY_UP | KEY_RIGHT, KEY_DOWN | KEY_LEFT, KEY_DOWN | KEY_RIGHT };
        bot_dir = dirs[bot_rand() % 9];
    }
    u16 k = bot_dir | KEY_A;
    if (bot_t % 210 < 3) k |= KEY_B;
    if (bot_t % 330 == 7) k |= KEY_R;
    if (bot_t % 500 == 9) k |= KEY_L;
    (void)bot_pulse;
    return k;
}
#endif

void Input_Update(void)
{
#ifdef BOT
    u16 now = bot_keys();
#else
    u16 now = (u16)(~REG_KEYINPUT & KEY_ANY);
#endif
    keys_down = now & ~keys_held;
    keys_up = keys_held & ~now;
    keys_held = now;
}
