#ifndef PLAYER_H
#define PLAYER_H
#include "gba.h"
#include "weapons.h"

enum { PS_ALIVE, PS_DYING, PS_DEAD };
enum { POSE_NONE, POSE_SHOOT, POSE_RELOAD, POSE_INTERACT };
enum { VIEW_DOWN, VIEW_UP, VIEW_SIDE };
enum { PERK_IRON_HEART, PERK_QUICK_HANDS, PERK_STEADY_AIM, PERK_SECOND_WIND, PERK_FIELD_MEDIC, PERK_COUNT };

#define PLAYER_BASE_HP 100
#define PLAYER_HW 5            /* footprint half width */
#define PLAYER_HU 5            /* footprint height */

typedef struct Player {
    s32 x, y;                  /* feet position, 8.8 px */
    u8  state;
    u8  view, flip;            /* sprite view and horizontal flip */
    u8  aim;                   /* aim angle 0..255 */
    u8  face_angle;            /* last movement direction angle */
    u8  moving;
    u8  anim_t, anim_f;
    u8  pose, pose_t;
    u8  hurt_t, inv_t;
    s16 hp, maxhp;
    u16 fire_cd, reload_t, melee_cd;
    WeaponSlot wpn[2];
    u8  cur;
    u8  perks;                 /* bit per PERK_* */
    u16 overdrive_t, double_t, insta_t;
    u16 regen_wait;
    u8  regen_tick;
    s8  target;                /* enemy index or -1 */
    u8  lock;                  /* player forced target via R */
    u8  dmg_dir[4];            /* up, down, left, right indicator timers */
    u8  hold;                  /* B hold counter for interactions */
    u8  dying_t;
    u8  empty_flash;
    u8  muzzle_t;
    s8  last_interact;         /* index of active interaction zone or -1 */
    u16 last_dmg_t;
} Player;

extern Player player;

void Player_Init(void);
void Player_Update(void);
void Player_Hurt(int dmg, int from_x, int from_y);
int  Player_SpeedFx(void);
int  Player_Dead(void);
void Player_AddScore(int pts);
void Player_Heal(int hp);
void Player_ApplyPerk(int perk);

#endif
