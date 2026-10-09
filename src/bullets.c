#include "bullets.h"
#include "enemy.h"
#include "player.h"
#include "effects.h"
#include "audio.h"
#include "map.h"
#include "utils.h"

Bullet bullets[MAX_BULLETS] IWRAM_DATA;
EBullet ebullets[MAX_EBULLETS] IWRAM_DATA;

void Bullets_Init(void)
{
    memset(bullets, 0, sizeof(bullets));
    memset(ebullets, 0, sizeof(ebullets));
}

void Bullets_Spawn(s32 x, s32 y, u8 angle, int speed16, int dmg, int pierce, int range, int type)
{
    for (int i = 0; i < MAX_BULLETS; i++) {
        Bullet *b = &bullets[i];
        if (b->active) continue;
        int sp = speed16 << 4;          /* 1/16 px -> 8.8 */
        b->active = 1;
        b->type = (u8)type;
        b->pierce = (u8)pierce;
        b->x = x; b->y = y;
        b->vx = (s16)((Cos(angle) * sp) >> 8);
        b->vy = (s16)((Sin(angle) * sp) >> 8);
        b->life = (s16)((range << 8) / (sp ? sp : 1));
        b->dmg = (u16)dmg;
        b->hit = 0;
        b->bounces = (type == BT_BOUNCE) ? 4 : 0;
        return;
    }
}

void Bullets_SpawnEnemy(s32 x, s32 y, s32 tx, s32 ty, int dmg)
{
    for (int i = 0; i < MAX_EBULLETS; i++) {
        EBullet *b = &ebullets[i];
        if (b->active) continue;
        u8 a = Atan2((ty - y) >> 4, (tx - x) >> 4);
        b->active = 1;
        b->x = x; b->y = y;
        b->vx = (s16)((Cos(a) * 330) >> 8);
        b->vy = (s16)((Sin(a) * 330) >> 8);
        b->life = 150;
        b->dmg = (u8)dmg;
        b->frame = 0;
        return;
    }
}

int Bullets_Count(void)
{
    int n = 0;
    for (int i = 0; i < MAX_BULLETS; i++) n += bullets[i].active;
    return n;
}

static void arc_chain(Enemy *src, int dmg, int from_angle)
{
    int sx = src->x >> 8, sy = (src->y >> 8) - 6;
    int hits = 0;
    u32 used = 1u << (src - enemies);
    for (int n = 0; n < 3; n++) {
        int best = -1; u32 bd = 64;
        for (int i = 0; i < MAX_ENEMIES; i++) {
            Enemy *e = &enemies[i];
            if (!e->active || e->state == ES_DEAD || e->hidden || (used & (1u << i))) continue;
            u32 d = Dist((e->x >> 8) - sx, ((e->y >> 8) - 6) - sy);
            if (d < bd) { bd = d; best = i; }
        }
        if (best < 0) break;
        Enemy *t = &enemies[best];
        used |= 1u << best;
        Fx_Arc(sx, sy, t->x >> 8, (t->y >> 8) - 6);
        sx = t->x >> 8; sy = (t->y >> 8) - 6;
        Enemy_Damage(t, dmg, 0, 0, from_angle);
        hits++;
    }
    (void)hits;
}

/* area damage around a rocket impact */
static void explode(int x, int y, int dmg)
{
    Fx_Explosion(x, y - 8);
    Fx_Shake(7);
    Audio_PlaySfx(SFX_EXPLOSION);
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD || e->hidden) continue;
        int d = (int)Dist((e->x >> 8) - x, ((e->y >> 8) - 6) - y);
        if (d > 34) continue;
        Enemy_Damage(e, d < 16 ? dmg : dmg / 2, 0, 0, Atan2(((e->y >> 8) - 6) - y, (e->x >> 8) - x));
    }
}

IWRAM_CODE static int hit_enemies(Bullet *b)
{
    int bx = b->x >> 8, by = b->y >> 8;
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD || e->hidden) continue;
        if (b->hit & (1u << i)) continue;
        int ex = e->x >> 8, ey = e->y >> 8;
        int dx = bx - ex;
        int dy = by - ey;
        int wx = 7, up = 12;
        if (e->type == E_BRUTE) { wx = 11; up = 18; }
        else if (e->type == E_RUSHER) { up = 11; }
        if (dx > wx || dx < -wx || dy > 4 || dy < -up) continue;
        b->hit |= 1u << i;
        int crit = (b->type == BT_BULLET && RandRange(100) < 9);
        int ang = Atan2(b->vy, b->vx);
        if (b->type == BT_ROCKET) { explode(bx, by, b->dmg); return 1; }
        if (b->type == BT_ARC) {
            Enemy_Damage(e, b->dmg, 0, 0, ang);
            arc_chain(e, b->dmg * 3 / 4, ang);
            Fx_Sparks(bx, by - 4, 3);
            return 1;
        }
        Enemy_Damage(e, crit ? b->dmg * 2 : b->dmg, crit, 0, ang);
        if (b->pierce <= 1) return 1;
        b->pierce--;
    }
    return 0;
}

void Bullets_Update(void)
{
    for (int i = 0; i < MAX_BULLETS; i++) {
        Bullet *b = &bullets[i];
        if (!b->active) continue;
        for (int step = 0; step < 2; step++) {
            b->x += b->vx >> 1;
            b->y += b->vy >> 1;
            int bx = b->x >> 8, by = b->y >> 8;
            if (Map_SolidPx(bx, by)) {
                if (b->type == BT_ROCKET) { explode(bx - (b->vx >> 7), by - (b->vy >> 7), b->dmg); b->active = 0; break; }
                if (b->type == BT_BOUNCE && b->bounces) {
                    /* reflect off whichever axis hit the wall, restart from the last free position */
                    s32 ox = b->x - (b->vx >> 1), oy = b->y - (b->vy >> 1);
                    int hx = Map_SolidPx(bx, (int)(oy >> 8)), hy = Map_SolidPx((int)(ox >> 8), by);
                    if (hx || !hy) b->vx = (s16)-b->vx;
                    if (hy || !hx) b->vy = (s16)-b->vy;
                    b->x = ox; b->y = oy;
                    b->bounces--;
                    b->hit = 0;
                    Fx_Sparks(bx, by, 2);
                    continue;
                }
                Fx_Sparks(bx - (b->vx >> 7), by - (b->vy >> 7), 2);
                b->active = 0;
                break;
            }
            if (hit_enemies(b)) { b->active = 0; break; }
        }
        if (b->active && --b->life <= 0) b->active = 0;
        if (b->active && b->type == BT_RAY && (i & 1)) Fx_Spawn(FXK_PUFF, b->x >> 8, (b->y >> 8) - 8, 0, 0, 5);
    }
    /* enemy projectiles (spit) */
    for (int i = 0; i < MAX_EBULLETS; i++) {
        EBullet *b = &ebullets[i];
        if (!b->active) continue;
        b->x += b->vx; b->y += b->vy;
        b->frame++;
        int bx = b->x >> 8, by = b->y >> 8;
        if (Map_SolidPx(bx, by) || --b->life <= 0) {
            Fx_Spawn(FXK_PUFF, bx, by - 6, 0, 0, 6);
            b->active = 0;
            continue;
        }
        int px = player.x >> 8, py = player.y >> 8;
        int dx = bx - px, dy = by - (py - 8);
        if (player.state == PS_ALIVE && dx > -7 && dx < 7 && dy > -10 && dy < 8) {
            Player_Hurt(b->dmg, bx, by);
            Fx_Spawn(FXK_PUFF, bx, by - 6, 0, 0, 6);
            b->active = 0;
        }
    }
}
