#include "game.h"

Pickup pickups[MAX_PICKUPS] IWRAM_DATA;

const char *const pickup_names[PU_COUNT] = { "AMMO CACHE", "OVERDRIVE", "DOUBLE SCORE", "FULL RESTORE", "CLEAROUT" };

void Pickups_Init(void) { memset(pickups, 0, sizeof(pickups)); }

void Pickups_Spawn(int type, int px, int py)
{
    int slot = -1, oldest = 99999;
    for (int i = 0; i < MAX_PICKUPS; i++) {
        if (!pickups[i].active) { slot = i; break; }
        if (pickups[i].timer < oldest) { oldest = pickups[i].timer; slot = i; }
    }
    Pickup *p = &pickups[slot];
    p->active = 1;
    p->type = (u8)type;
    p->x = (s16)px; p->y = (s16)py;
    p->timer = 600;
    p->phase = 0;
    p->bounce_v = 60;           /* 1/16 px per frame initial pop */
    p->z = 0;
}

void Pickups_MaybeDrop(int px, int py)
{
    /* 6% per kill; weights favour ammo / restore */
    if (RandRange(100) >= 6) return;
    static const u8 table[10] = { PU_AMMO, PU_AMMO, PU_RESTORE, PU_RESTORE, PU_DOUBLE, PU_DOUBLE, PU_OVERDRIVE,
                                  PU_OVERDRIVE, PU_CLEAROUT, PU_AMMO };
    Pickups_Spawn(table[RandRange(10)], px, py);
}

void Pickups_Apply(int type)
{
    switch (type) {
    case PU_AMMO:      Weapon_FillAmmo(&player); break;
    case PU_OVERDRIVE: player.overdrive_t = 600; break;
    case PU_DOUBLE:    player.double_t = 1200; break;
    case PU_RESTORE:   Player_Heal(player.maxhp); break;
    case PU_CLEAROUT:
        Enemies_Clearout(250);
        Fx_Shake(14);
        Fx_Flash(12);
        break;
    }
    Audio_PlaySfx(SFX_POWERUP);
    Fx_Flash(6);
    Hud_Message(pickup_names[type], 0, HC_YELLOW, 90);
}

void Pickups_Update(void)
{
    for (int i = 0; i < MAX_PICKUPS; i++) {
        Pickup *p = &pickups[i];
        if (!p->active) continue;
        p->phase++;
        /* little bounce after dropping */
        p->bounce_v -= 4;
        p->z += p->bounce_v;
        if (p->z < 0) { p->z = 0; p->bounce_v = (s16)((-p->bounce_v) >> 1); if (p->bounce_v < 6) p->bounce_v = 0; }
        if (--p->timer <= 0) { p->active = 0; continue; }
        if (player.state == PS_ALIVE) {
            int dx = p->x - (player.x >> 8), dy = p->y - (player.y >> 8);
            if (dx > -11 && dx < 11 && dy > -11 && dy < 11) {
                Pickups_Apply(p->type);
                p->active = 0;
            }
        }
    }
}
