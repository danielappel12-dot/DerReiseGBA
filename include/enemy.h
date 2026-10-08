#ifndef ENEMY_H
#define ENEMY_H
#include "gba.h"

#define MAX_ENEMIES 32

enum { E_SHAMBLER, E_RUSHER, E_BRUTE, E_SPITTER, E_STALKER, E_TYPES };
enum { ES_IDLE, ES_CHASE, ES_ATTACK, ES_HURT, ES_DEAD, ES_SPECIAL };

typedef struct {
    u8  active, type, state, timer;
    s32 x, y;                   /* feet, 8.8 */
    s16 vx, vy;                 /* velocity 8.8 */
    u16 speed;                  /* cruise speed 8.8 px/frame */
    s16 hp, maxhp;
    u8  face, flip;
    u8  anim;
    u8  flash;                  /* hit flash frames */
    u8  atk_cd;
    u8  stuck;                  /* frames of no progress */
    u8  alt;                    /* alternate steering timer */
    s8  alt_dir;
    u8  nav_t;                  /* frames until next steering update */
    u8  elite;
    u8  hidden;                 /* stalker cloak */
    u16 px, py;                 /* position sample for stuck detection */
    u8  special_t;
    u8  spawn_area;
} Enemy;

typedef struct {
    s16 hp;
    u16 speed;                  /* 8.8 px / frame */
    u8  dmg;
    u8  atk_range;              /* px */
    u8  atk_delay;              /* frames between attacks */
    u8  hw, hu;                 /* footprint */
    u16 points;
} EnemyDef;

extern Enemy enemies[MAX_ENEMIES];
extern const EnemyDef enemy_defs[E_TYPES];
extern u8 enemy_count_alive;

void Enemies_Init(void);
Enemy *Enemy_Spawn(int type, int tx, int ty, int wave);
void Enemies_Update(void);
/* returns 1 when the enemy died */
int  Enemy_Damage(Enemy *e, int dmg, int crit, int melee, int hit_angle);
void Enemies_KillAll(int award);
int  Enemies_NearestTo(int px, int py, int max_dist, int need_los, int skip);
void Enemies_Clearout(int dmg);
int  Enemy_CenterY(const Enemy *e);
int  Enemy_TeleportNearPlayer(Enemy *e, int rmin, int rmax);

#endif
