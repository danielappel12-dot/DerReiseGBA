/* utils.h - fixed point, random numbers, trig, small helpers */
#ifndef UTILS_H
#define UTILS_H
#include "gba.h"

#define FX_ONE 256
#define TO_FX(n) ((s32)(n) << 8)
#define FROM_FX(n) ((s32)(n) >> 8)

#define ABS(x)    ((x) < 0 ? -(x) : (x))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define CLAMP(v, lo, hi) ((v) < (lo) ? (lo) : ((v) > (hi) ? (hi) : (v)))
#define ARRAY_LEN(a) ((int)(sizeof(a) / sizeof((a)[0])))

extern const s16 sin_tab[256];      /* generated: sin * 256, 256 steps per turn */
extern const u8  atan_tab[65];

/* angle convention: 0 = east, 64 = south (screen y grows down), 128 = west, 192 = north */
static inline s32 Sin(u8 a) { return sin_tab[a]; }
static inline s32 Cos(u8 a) { return sin_tab[(u8)(a + 64)]; }
u8   Atan2(s32 dy, s32 dx);
u32  Dist(s32 dx, s32 dy);          /* cheap octagonal distance approximation */

void Rand_Seed(u32 s);
u32  Rand(void);
s32  RandRange(s32 n);              /* 0 .. n-1 */
s32  RandSigned(s32 n);             /* -n .. +n */

/* string helpers (HUD) */
int  UInt2Str(char *buf, u32 v, int width, char pad);   /* returns chars written */

/* memory */
void *memcpy(void *dst, const void *src, size_t n);
void *memset(void *dst, int c, size_t n);
void *memmove(void *dst, const void *src, size_t n);
int   strlen_(const char *s);

#endif
