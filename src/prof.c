#include "prof.h"

#ifdef DEBUG
u32 prof_shown[PF_COUNT];
static u32 prof_run[PF_COUNT];
static int prof_frames;

void Prof_Init(void)
{
    REG_TM2CNT_H = 0;
    REG_TM3CNT_H = 0;
    REG_TM2CNT_L = 0;
    REG_TM3CNT_L = 0;
    REG_TM3CNT_H = TM_ENABLE | TM_CASCADE;
    REG_TM2CNT_H = TM_ENABLE;          /* prescaler 1: one tick per CPU cycle */
}

u32 Prof_Now(void)
{
    u32 hi1 = REG_TM3CNT_L, lo = REG_TM2CNT_L, hi2 = REG_TM3CNT_L;
    if (hi2 != hi1 && lo < 0x8000) hi1 = hi2;
    return (hi1 << 16) | lo;
}

void Prof_Store(int id, u32 cycles)
{
    if (cycles > prof_run[id]) prof_run[id] = cycles;
}

void Prof_Frame(void)
{
    if (++prof_frames >= 120) {
        for (int i = 0; i < PF_COUNT; i++) { prof_shown[i] = prof_run[i]; prof_run[i] = 0; }
        prof_frames = 0;
    }
}
#endif
