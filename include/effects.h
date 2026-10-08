#ifndef EFFECTS_H
#define EFFECTS_H
#include "gba.h"

#define MAX_EFFECTS 40

enum { FXK_BLOOD, FXK_SPARK, FXK_PUFF, FXK_MUZZLE, FXK_EXPLODE, FXK_SLASH, FXK_ARC, FXK_RING };

typedef struct {
    u8 active, kind, frame_div, life_max;
    s32 x, y;           /* 8.8 world position (pixels) */
    s16 vx, vy;
    u8 life;
    s8 oy;              /* extra vertical draw offset */
} Effect;

extern Effect effects[MAX_EFFECTS];

void Fx_Init(void);
void Fx_Spawn(int kind, int px, int py, int vx, int vy, int life);
void Fx_Blood(int px, int py, int n);
void Fx_Sparks(int px, int py, int n);
void Fx_Explosion(int px, int py);
void Fx_Arc(int x0, int y0, int x1, int y1);
void Fx_Update(void);

/* screen-level effects */
void Fx_Shake(int amount);
void Fx_Flash(int amount);                  /* white flash */
extern u8 fx_shake, fx_flash;

#endif
