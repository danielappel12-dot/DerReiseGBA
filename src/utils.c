#include "utils.h"

static u32 rng_state = 0x2545F491u;

void Rand_Seed(u32 s) { rng_state = s ? s : 0x2545F491u; }

u32 Rand(void)
{
    u32 x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

s32 RandRange(s32 n)
{
    if (n <= 1) return 0;
    return (s32)((Rand() >> 8) % (u32)n);
}

s32 RandSigned(s32 n) { return RandRange(2 * n + 1) - n; }

u8 Atan2(s32 dy, s32 dx)
{
    s32 ax = ABS(dx), ay = ABS(dy);
    s32 a;
    if (ax == 0 && ay == 0) return 0;
    if (ay <= ax) a = atan_tab[(ay << 6) / ax];
    else          a = 64 - atan_tab[(ax << 6) / ay];
    if (dx < 0) a = 128 - a;
    if (dy < 0) a = 256 - a;
    return (u8)a;
}

u32 Dist(s32 dx, s32 dy)
{
    u32 ax = ABS(dx), ay = ABS(dy);
    return ax > ay ? ax + ((ay * 3) >> 3) : ay + ((ax * 3) >> 3);
}

IWRAM_CODE int UInt2Str(char *buf, u32 v, int width, char pad)
{
    char tmp[12];
    int n = 0, i;
    do { tmp[n++] = '0' + (v % 10); v /= 10; } while (v && n < 11);
    int len = n > width ? n : width;
    for (i = 0; i < len - n; i++) buf[i] = pad;
    for (i = 0; i < n; i++) buf[len - 1 - i] = tmp[i];
    buf[len] = 0;
    return len;
}

/* freestanding libc bits the compiler may call; never used on VRAM (needs 16/32 bit access) */
void *memcpy(void *dst, const void *src, size_t n)
{
    u8 *d = dst; const u8 *s = src;
    if ((((u32)d | (u32)s | n) & 3) == 0) { memcpy32(d, s, n >> 2); return dst; }
    while (n--) *d++ = *s++;
    return dst;
}

void *memset(void *dst, int c, size_t n)
{
    u8 *d = dst;
    if ((((u32)d | n) & 3) == 0) { u32 v = (u8)c * 0x01010101u; memset32(d, v, n >> 2); return dst; }
    while (n--) *d++ = (u8)c;
    return dst;
}

void *memmove(void *dst, const void *src, size_t n)
{
    u8 *d = dst; const u8 *s = src;
    if (d < s) { while (n--) *d++ = *s++; }
    else { d += n; s += n; while (n--) *--d = *--s; }
    return dst;
}

int strlen_(const char *s) { int n = 0; while (s[n]) n++; return n; }
