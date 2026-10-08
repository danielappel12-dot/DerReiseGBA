#include "effects.h"
#include "utils.h"

Effect effects[MAX_EFFECTS] IWRAM_DATA;
u8 fx_shake, fx_flash;

void Fx_Init(void)
{
    memset(effects, 0, sizeof(effects));
    fx_shake = fx_flash = 0;
}

static Effect *alloc(void)
{
    for (int i = 0; i < MAX_EFFECTS; i++)
        if (!effects[i].active) return &effects[i];
    return 0;
}

void Fx_Spawn(int kind, int px, int py, int vx, int vy, int life)
{
    Effect *e = alloc();
    if (!e) return;
    e->active = 1;
    e->kind = (u8)kind;
    e->x = (s32)px << 8; e->y = (s32)py << 8;
    e->vx = (s16)vx; e->vy = (s16)vy;
    e->life = (u8)life; e->life_max = (u8)life;
    e->oy = 0;
}

void Fx_Blood(int px, int py, int n)
{
    for (int i = 0; i < n; i++)
        Fx_Spawn(FXK_BLOOD, px + RandSigned(2), py - 6 + RandSigned(3), RandSigned(150), -RandRange(200) - 40, 14 + RandRange(8));
}

void Fx_Sparks(int px, int py, int n)
{
    for (int i = 0; i < n; i++)
        Fx_Spawn(FXK_SPARK, px, py, RandSigned(180), RandSigned(180), 8 + RandRange(4));
}

void Fx_Explosion(int px, int py)
{
    Fx_Spawn(FXK_EXPLODE, px, py, 0, 0, 16);
    for (int i = 0; i < 4; i++)
        Fx_Spawn(FXK_PUFF, px + RandSigned(8), py + RandSigned(6), RandSigned(100), -RandRange(90), 16);
}

void Fx_Arc(int x0, int y0, int x1, int y1)
{
    int dx = x1 - x0, dy = y1 - y0;
    int n = (Dist(dx, dy) >> 3) + 1;
    if (n > 8) n = 8;
    for (int i = 0; i <= n; i++)
        Fx_Spawn(FXK_ARC, x0 + dx * i / n + RandSigned(1), y0 + dy * i / n + RandSigned(1), 0, 0, 6 + (i & 1));
}

void Fx_Update(void)
{
    for (int i = 0; i < MAX_EFFECTS; i++) {
        Effect *e = &effects[i];
        if (!e->active) continue;
        e->x += e->vx; e->y += e->vy;
        if (e->kind == FXK_BLOOD) e->vy += 22;      /* gravity */
        else if (e->kind == FXK_PUFF) e->vy -= 3;
        if (--e->life == 0) e->active = 0;
    }
    if (fx_shake) fx_shake--;
    if (fx_flash) fx_flash--;
}

void Fx_Shake(int amount) { if (amount > fx_shake) fx_shake = (u8)amount; }
void Fx_Flash(int amount) { if (amount > fx_flash) fx_flash = (u8)amount; }
