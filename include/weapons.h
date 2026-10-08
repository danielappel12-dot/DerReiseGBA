#ifndef WEAPONS_H
#define WEAPONS_H
#include "gba.h"

enum { W_SERVICE9, W_SHOTGUN, W_SMG, W_RIFLE, W_ARC, W_RAY, W_COUNT };
enum { WK_BULLET, WK_ARC, WK_RAY };

typedef struct {
    const char *name;
    u8  dmg;            /* per bullet / pellet */
    u8  delay;          /* frames between shots */
    u8  mag;            /* magazine size */
    u16 reserve_max;
    u8  reload;         /* frames */
    u8  spread;         /* +-angle units (256 = full circle) */
    u8  speed16;        /* bullet speed in 1/16 px per frame */
    u16 range;          /* pixels */
    u8  pierce;         /* number of enemies a bullet passes through (1 = stops at first) */
    u8  pellets;
    u8  kind;
    u8  recoil;         /* screen shake / pushback strength */
    u16 price;          /* wall-buy price (ammo refill = half) */
    u8  sfx;
} WeaponDef;

extern const WeaponDef weapon_defs[W_COUNT];

typedef struct { u8 id; u8 mag; u16 reserve; } WeaponSlot;

struct Player;
void Weapon_Reset(struct Player *p);
int  Weapon_Give(struct Player *p, int id);            /* returns 1 if new weapon, 0 if ammo refill */
void Weapon_Update(struct Player *p);                  /* reload timer / cooldown */
int  Weapon_TryFire(struct Player *p);
void Weapon_StartReload(struct Player *p);
void Weapon_Switch(struct Player *p);
void Weapon_FillAmmo(struct Player *p);
int  Weapon_AmmoPrice(int id);
void Weapon_Melee(struct Player *p);

#endif
