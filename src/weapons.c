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
};

void Weapon_Reset(Player *p)
{
    p->wpn[0].id = W_SERVICE9;
    p->wpn[0].mag = weapon_defs[W_SERVICE9].mag;
    p->wpn[0].reserve = 96;
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
    s->mag = weapon_defs[s->id].mag;
    s->reserve = weapon_defs[s->id].reserve_max;
}

int Weapon_Give(Player *p, int id)
{
    /* owned already -> refill */
    for (int i = 0; i < 2; i++) {
        if (p->wpn[i].id == id) { fill_slot(&p->wpn[i]); return 0; }
    }
    int slot = (p->wpn[1].id == 255) ? 1 : p->cur;
    p->wpn[slot].id = (u8)id;
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
    if (p->reload_t || s->mag >= w->mag || s->reserve == 0) return;
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
            const WeaponDef *w = &weapon_defs[s->id];
            int need = w->mag - s->mag;
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
    if (p->overdrive_t) delay = (delay + 1) >> 1;
    p->fire_cd = (u16)delay;
    int spread = w->spread;
    if (p->perks & (1 << PERK_STEADY_AIM)) spread >>= 1;
    int ang = p->aim;
    s32 mx = p->x + ((Cos((u8)ang) * 9) );
    s32 my = p->y + ((Sin((u8)ang) * 7)) - TO_FX(9);
    int type = (w->kind == WK_ARC) ? BT_ARC : (w->kind == WK_RAY ? BT_RAY : (w->pellets > 1 ? BT_PELLET : BT_BULLET));
    for (int i = 0; i < w->pellets; i++) {
        int a = ang + (spread ? RandSigned(spread) : 0);
        Bullets_Spawn(mx, my + TO_FX(9), (u8)a, w->speed16, w->dmg, w->pierce, w->range, type);
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
