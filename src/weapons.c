#include "weapons.h"
#include "player.h"
#include "bullets.h"
#include "effects.h"
#include "enemy.h"
#include "audio.h"
#include "utils.h"
#include "rounds.h"

/*  name              dmg dly mag  res  rld spr spd  range pierce pel kind      rec price sfx */
const WeaponDef weapon_defs[W_COUNT] = {
    { "SERVICE-9",      20, 12, 12,  96, 42,  3,  64, 190, 1, 1, WK_BULLET, 0,    0, SFX_SHOT_PISTOL  },
    { "TRENCH SHOTGUN", 20, 36,  6,  48, 84, 14,  56,  96, 1, 6, WK_BULLET, 3,  500, SFX_SHOT_SHOTGUN },
    { "RANGER SMG",     13,  4, 30, 210, 66,  8,  66, 150, 1, 1, WK_BULLET, 0, 1000, SFX_SHOT_SMG     },
    { "HEAVY RIFLE",    95, 28,  8,  56, 88,  1,  96, 280, 3, 1, WK_BULLET, 2, 1250, SFX_SHOT_RIFLE   },
    { "ARC LAUNCHER",   55, 34,  6,  36, 96,  2,  44, 170, 1, 1, WK_ARC,    2, 2250, SFX_SHOT_ARC     },
    { "RAY GUN",        42, 9,  20,  60, 110, 0, 112, 230, 99, 1, WK_RAY,   0, 3000, SFX_SHOT_RAY     },
    /* ---- mystery box only ---- */
    { "HAND CANNON",    70, 26,  6,  42,  80,  2,  80, 220, 2, 1, WK_BULLET,    2, 0, SFX_SHOT_RIFLE   },
    { "TWIN-9",         14,  6, 24, 144,  60,  7,  66, 150, 1, 1, WK_BULLET,    0, 0, SFX_SHOT_PISTOL  },
    { "BUZZSAW",         8,  2, 90, 360, 130, 14,  64, 130, 1, 1, WK_BULLET,    0, 0, SFX_SHOT_SMG     },
    { "BLAST TUBE",    110, 52,  3,  18, 100,  1,  40, 200, 1, 1, WK_EXPLOSIVE, 4, 0, SFX_SHOT_BLAST   },
    { "EMBER THROWER",   7,  2, 60, 240, 100, 10,  34,  62, 99, 1, WK_FLAME,    0, 0, SFX_SHOT_FLAME   },
    { "BOUNCER",        30, 10, 16,  96,  70,  3,  60, 380, 1, 1, WK_BOUNCE,    0, 0, SFX_SHOT_RAY     },
    { "LONGSHOT",      150, 46,  5,  30, 100,  0, 128, 420, 4, 1, WK_BULLET,    3, 0, SFX_SHOT_RIFLE   },
};

int Weapon_MagSize(const WeaponSlot *s) { int m = weapon_defs[s->id].mag; return s->pap ? m + m / 2 : m; }
int Weapon_ReserveMax(const WeaponSlot *s) { int m = weapon_defs[s->id].reserve_max; return s->pap ? m + m / 2 : m; }
int Weapon_Damage(const WeaponSlot *s) { int d = weapon_defs[s->id].dmg; return s->pap ? d * 2 : d; }

int Weapon_Owns(const Player *p, int id)
{
    return p->wpn[0].id == id || p->wpn[1].id == id;
}

void Weapon_Reset(Player *p)
{
    p->wpn[0].id = W_SERVICE9;
    p->wpn[0].mag = weapon_defs[W_SERVICE9].mag;
    p->wpn[0].reserve = 96;
    p->wpn[0].pap = 0;
    p->wpn[1].pap = 0;
    p->wpn[1].id = 255;
    p->wpn[1].mag = 0;
    p->wpn[1].reserve = 0;
    p->cur = 0;
    p->fire_cd = p->reload_t = p->melee_cd = 0;
}

int Weapon_AmmoPrice(int id)
{
    int pr = weapon_defs[id].price / 2;
    return pr < 250 ? 250 : pr;
}

static void fill_slot(WeaponSlot *s)
{
    s->mag = (u8)Weapon_MagSize(s);
    s->reserve = (u16)Weapon_ReserveMax(s);
}

int Weapon_Punch(Player *p)
{
    WeaponSlot *s = &p->wpn[p->cur];
    if (s->pap) return 0;
    s->pap = 1;
    fill_slot(s);
    p->reload_t = 0;
    return 1;
}

int Weapon_Give(Player *p, int id)
{
    /* owned already -> refill */
    for (int i = 0; i < 2; i++) {
        if (p->wpn[i].id == id) { fill_slot(&p->wpn[i]); return 0; }
    }
    int slot = (p->wpn[1].id == 255) ? 1 : p->cur;
    p->wpn[slot].id = (u8)id;
    p->wpn[slot].pap = 0;
    fill_slot(&p->wpn[slot]);
    p->cur = (u8)slot;
    p->reload_t = 0;
    p->fire_cd = 10;
    return 1;
}

void Weapon_FillAmmo(Player *p)
{
    for (int i = 0; i < 2; i++)
        if (p->wpn[i].id != 255) fill_slot(&p->wpn[i]);
}

void Weapon_Switch(Player *p)
{
    int other = p->cur ^ 1;
    if (p->wpn[other].id == 255) return;
    p->cur = (u8)other;
    p->reload_t = 0;
    p->fire_cd = 10;
    Audio_PlaySfx(SFX_RELOAD_DONE);
}

void Weapon_StartReload(Player *p)
{
    WeaponSlot *s = &p->wpn[p->cur];
    const WeaponDef *w = &weapon_defs[s->id];
    if (p->reload_t || s->mag >= Weapon_MagSize(s) || s->reserve == 0) return;
    int t = w->reload;
    if (p->perks & (1 << PERK_QUICK_HANDS)) t = (t * 6) / 10;
    p->reload_t = (u16)t;
    p->pose = POSE_RELOAD;
    p->pose_t = 255;
    Audio_PlaySfx(SFX_RELOAD);
}

void Weapon_Update(Player *p)
{
    if (p->fire_cd) p->fire_cd--;
    if (p->melee_cd) p->melee_cd--;
    if (p->reload_t) {
        p->reload_t--;
        if (p->reload_t == 0) {
            WeaponSlot *s = &p->wpn[p->cur];
            int need = Weapon_MagSize(s) - s->mag;
            int mv = need < s->reserve ? need : s->reserve;
            s->mag = (u8)(s->mag + mv);
            s->reserve = (u16)(s->reserve - mv);
            if (p->pose == POSE_RELOAD) p->pose = POSE_NONE;
            Audio_PlaySfx(SFX_RELOAD_DONE);
        }
    }
}

int Weapon_TryFire(Player *p)
{
    WeaponSlot *s = &p->wpn[p->cur];
    const WeaponDef *w = &weapon_defs[s->id];
    if (p->reload_t || p->fire_cd) return 0;
    if (s->mag == 0) {
        p->fire_cd = 14;
        p->empty_flash = 40;
        if (s->reserve > 0) Weapon_StartReload(p);
        else Audio_PlaySfx(SFX_EMPTY);
        return 0;
    }
    s->mag--;
    int delay = w->delay;
    if (s->pap) delay = (delay * 85) / 100 ? (delay * 85) / 100 : 1;
    if (p->overdrive_t) delay = (delay + 1) >> 1;
    if (delay < 1) delay = 1;
    p->fire_cd = (u16)delay;
    int spread = w->spread;
    if (p->perks & (1 << PERK_STEADY_AIM)) spread >>= 1;
    int ang = p->aim;
    s32 mx = p->x + ((Cos((u8)ang) * 9) );
    s32 my = p->y + ((Sin((u8)ang) * 7)) - TO_FX(9);
    int type = BT_BULLET;
    switch (w->kind) {
    case WK_ARC: type = BT_ARC; break;
    case WK_RAY: type = BT_RAY; break;
    case WK_EXPLOSIVE: type = BT_ROCKET; break;
    case WK_FLAME: type = BT_FLAME; break;
    case WK_BOUNCE: type = BT_BOUNCE; break;
    default: type = w->pellets > 1 ? BT_PELLET : BT_BULLET; break;
    }
    int dmg = Weapon_Damage(s);
    for (int i = 0; i < w->pellets; i++) {
        int a = ang + (spread ? RandSigned(spread) : 0);
        Bullets_Spawn(mx, my + TO_FX(9), (u8)a, w->speed16, dmg, w->pierce, w->range, type);
    }
    Fx_Spawn(FXK_MUZZLE, mx >> 8, (my >> 8), 0, 0, 4);
    Audio_PlaySfx(w->sfx);
    Fx_Shake(w->recoil);
    p->pose = POSE_SHOOT;
    p->pose_t = 7;
    p->muzzle_t = 4;
    if (s->mag == 0 && s->reserve > 0) {
        /* automatic reload after the last round leaves the barrel */
        p->fire_cd += 6;
    }
    return 1;
}

void Weapon_Melee(Player *p)
{
    if (p->melee_cd) return;
    p->melee_cd = 26;
    int px = p->x >> 8, py = p->y >> 8;
    int ax = Cos(p->aim), ay = Sin(p->aim);
    Fx_Spawn(FXK_SLASH, px + ((ax * 14) >> 8), py - 10 + ((ay * 10) >> 8), 0, 0, 9);
    Audio_PlaySfx(SFX_MELEE);
    Fx_Shake(1);
    p->pose = POSE_SHOOT;
    p->pose_t = 8;
    int ang = p->aim;
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD || e->hidden) continue;
        int dx = (e->x >> 8) - px, dy = (e->y >> 8) - py;
        int reach = (e->type == E_BRUTE) ? 28 : 22;
        if (dx > reach || dx < -reach || dy > reach || dy < -reach) continue;
        if (Dist(dx, dy) > (u32)reach) continue;
        /* roughly in front (dot product > -0.3) */
        int dot = (dx * ax + dy * ay);
        if (dot < -(int)(Dist(dx, dy) * 70)) continue;
        /* knife damage scales so a full-health zombie dies in exactly <wave> hits (1 on wave 1, 2 on wave 2 ...) */
        int hits = rounds.wave < 1 ? 1 : rounds.wave;
        Enemy_Damage(e, (e->maxhp + hits - 1) / hits, 0, 1, ang);
    }
}
