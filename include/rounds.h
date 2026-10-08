#ifndef ROUNDS_H
#define ROUNDS_H
#include "gba.h"

enum { RP_START, RP_RUNNING, RP_COMPLETE };

typedef struct {
    u16 wave;
    u8  phase;
    u16 timer;
    u16 to_spawn;        /* enemies still to appear this wave */
    u16 total;           /* enemies in this wave */
    u16 spawn_timer;
    u8  banner;          /* 0 none, 1 WAVE n, 2 READY?, 3 CLEARED */
} Rounds;

extern Rounds rounds;

void Rounds_Reset(void);
void Rounds_StartWave(int wave);
void Rounds_Update(void);
int  Rounds_EnemyHpPercent(int wave);
int  Rounds_EnemySpeedPercent(int wave);
int  Rounds_DifficultyTier(void);

#endif
