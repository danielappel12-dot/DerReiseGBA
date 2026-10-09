#ifndef WEAPONS_H
#define WEAPONS_H
#include "gba.h"

enum { W_SERVICE9, W_SHOTGUN, W_SMG, W_RIFLE, W_ARC, W_RAY,
       /* mystery-box weapons */
       W_CANNON, W_TWIN, W_BUZZSAW, W_BLAST, W_EMBER, W_BOUNCER, W_LONGSHOT, W_COUNT };
enum { WK_BULLET, WK_ARC, WK_RAY, WK_EXPLOSIVE, WK_FLAME, WK_BOUNCE };

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

typedef struct { u8 id; u8 mag; u16 reserve; u8 pap; } WeaponSlot;   /* pap = Pack-a-Punched */

struct Player;
void Weapon_Reset(struct Player *p);
int  Weapon_Give(struct Player *p, int id);            /* returns 1 if new weapon, 0 if ammo refill */
void Weapon_Update(struct Player *p);                  /* reload timer / cooldown */
int  Weapon_TryFire(struct Player *p);
void Weapon_StartReload(struct Player *p);
void Weapon_Switch(struct Player *p);
void Weapon_FillAmmo(struct Player *p);
int  Weapon_AmmoPrice(int id);
int  Weapon_MagSize(const WeaponSlot *s);        /* Pack-a-Punch: x1.5 */
int  Weapon_ReserveMax(const WeaponSlot *s);
int  Weapon_Damage(const WeaponSlot *s);         /* Pack-a-Punch: x2 */
int  Weapon_Punch(struct Player *p);             /* upgrade the held weapon; 0 if already upgraded */
int  Weapon_Owns(const struct Player *p, int id);
void Weapon_Melee(struct Player *p);

#endif
