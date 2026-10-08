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
#ifdef BOT_SMART
    {
        /* mortal kiting bot: run away from the closest zombie, strafe when nothing is close, buy doors with spare points */
        int px = player.x >> 8, py = player.y >> 8, best = -1, bd = 999;
        for (int i = 0; i < MAX_ENEMIES; i++) {
            Enemy *e = &enemies[i];
            if (!e->active || e->state == ES_DEAD) continue;
            int d = (int)Dist((e->x >> 8) - px, (e->y >> 8) - py);
            if (d < bd) { bd = d; best = i; }
        }
        u16 k = KEY_A;
        if (best >= 0 && bd < 70) {
            Enemy *e = &enemies[best];
            int dx = px - (e->x >> 8), dy = py - (e->y >> 8);
            int ax = ABS(dx), ay = ABS(dy);
            u16 want = 0;
            if (ax * 2 > ay) want |= dx > 0 ? KEY_RIGHT : KEY_LEFT;
            if (ay * 2 > ax) want |= dy > 0 ? KEY_DOWN : KEY_UP;
            /* blocked? slide along the wall instead */
            int tx = px + ((want & KEY_RIGHT) ? 12 : 0) - ((want & KEY_LEFT) ? 12 : 0);
            int ty = py + ((want & KEY_DOWN) ? 10 : 0) - ((want & KEY_UP) ? 10 : 0);
            if (Map_SolidPx(tx, ty) || bot_t % 90 < 20) want = (want & (KEY_LEFT | KEY_RIGHT)) ? (dy >= 0 ? KEY_DOWN : KEY_UP) : (dx >= 0 ? KEY_RIGHT : KEY_LEFT);
            k |= want;
            if (bd < 18) k |= KEY_B;
        } else if (bot_t % 120 < 60) {
            k |= bot_dir;
        }
        if (bot_t % 50 == 0) {
            static const u16 dirs[9] = { 0, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP | KEY_LEFT, KEY_UP | KEY_RIGHT, KEY_DOWN | KEY_LEFT, KEY_DOWN | KEY_RIGHT };
            bot_dir = dirs[bot_rand() % 9];
        }
        if (bot_t % 400 == 9) k |= KEY_R;
        if (G.score >= 600 && bot_t % 1500 == 0) { /* spend: handled by cheat-free logic -> nothing */ }
        return k;
    }
#endif
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
