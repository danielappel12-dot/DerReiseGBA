#include "game.h"
#include "mystery.h"

static u8 state, shown, result, next_tick;
static u16 timer;

void Box_Reset(void) { state = BOX_IDLE; timer = 0; shown = 0; }
int Box_State(void) { return state; }
int Box_Shown(void) { return shown; }

static void set_open(int open)
{
    for (int i = 0; i < NUM_BOX_CELLS; i++) {
        const PowerSwap *s = &map_box_cells[i];
        Video_QueueMapEntry(s->idx & 63, s->idx >> 6, open ? s->on : s->off);
    }
}

/* any weapon except the starter and the ones already carried */
static int pick_weapon(void)
{
    int pool[W_COUNT], n = 0;
    for (int w = 1; w < W_COUNT; w++)
        if (!Weapon_Owns(&player, w)) pool[n++] = w;
    return pool[RandRange(n)];
}

void Box_Use(void)
{
    if (state == BOX_IDLE) {
        if (G.score < BOX_PRICE) { Hud_Message("NOT ENOUGH POINTS", "MYSTERY BOX", HC_RED, 100); Audio_PlaySfx(SFX_DENIED); return; }
        G.score -= BOX_PRICE;
        result = (u8)pick_weapon();
        state = BOX_ROLLING; timer = 0; next_tick = 0;
        set_open(1);
        Audio_PlaySfx(SFX_BOX_OPEN);
    } else if (state == BOX_READY) {
        int fresh = Weapon_Give(&player, result);
        (void)fresh;
        Hud_Message(weapon_defs[result].name, "FROM THE MYSTERY BOX", HC_YELLOW, 130);
        Audio_PlaySfx(SFX_BUY);
        state = BOX_IDLE;
        set_open(0);
    }
}

void Box_Update(void)
{
    if (state == BOX_ROLLING) {
        timer++;
        if (next_tick) next_tick--;
        else {
            int w;
            do { w = 1 + RandRange(W_COUNT - 1); } while (w == shown);
            shown = (u8)w;
            next_tick = (u8)(3 + timer / 14);          /* slows down as it settles */
            Audio_PlaySfx(SFX_BOX_TICK);
        }
        if (timer >= 150) {
            shown = result;
            state = BOX_READY; timer = 0;
            Audio_PlaySfx(SFX_POWERUP);
        }
    } else if (state == BOX_READY) {
        if (++timer > 420) {                             /* not taken in time: the box closes */
            state = BOX_IDLE;
            set_open(0);
            Hud_Message("THE BOX CLOSED", 0, HC_GRAY, 80);
        }
    }
}
