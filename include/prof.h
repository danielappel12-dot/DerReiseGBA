/* prof.h - tiny cycle profiler for DEBUG builds (timers 2+3 cascaded = 32 bit cycle counter) */
#ifndef PROF_H
#define PROF_H
#include "gba.h"

#ifdef DEBUG
enum { PF_PLAYER, PF_ENEMY, PF_BULLET, PF_NAV, PF_RENDER, PF_TOTAL, PF_COUNT };
extern u32 prof_shown[PF_COUNT];
void Prof_Init(void);
u32  Prof_Now(void);
void Prof_Store(int id, u32 cycles);
void Prof_Frame(void);
#define PROF_BEGIN(id) u32 _pf_##id = Prof_Now()
#define PROF_END(id)   Prof_Store(id, Prof_Now() - _pf_##id)
#else
#define PROF_BEGIN(id) do {} while (0)
#define PROF_END(id)   do {} while (0)
#endif

#endif
