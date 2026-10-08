#ifndef BULLETS_H
#define BULLETS_H
#include "gba.h"

#define MAX_BULLETS  32
#define MAX_EBULLETS 12

enum { BT_BULLET, BT_PELLET, BT_ARC, BT_RAY };

typedef struct {
    u8  active, type, pierce, hit_mask_dummy;
    s32 x, y;               /* 8.8 */
    s16 vx, vy;             /* 8.8 px / frame */
    s16 life;
    u16 dmg;
    u32 hit;                /* bitmask of enemies already hit (pierce) */
} Bullet;

typedef struct {
    u8 active; u8 frame;
    s32 x, y; s16 vx, vy; s16 life;
    u8 dmg;
} EBullet;

extern Bullet bullets[MAX_BULLETS];
extern EBullet ebullets[MAX_EBULLETS];

void Bullets_Init(void);
void Bullets_Spawn(s32 x, s32 y, u8 angle, int speed16, int dmg, int pierce, int range, int type);
void Bullets_SpawnEnemy(s32 x, s32 y, s32 tx, s32 ty, int dmg);
void Bullets_Update(void);
int  Bullets_Count(void);

#endif
