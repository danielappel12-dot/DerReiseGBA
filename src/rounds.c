#include "game.h"

Rounds rounds;

int Rounds_DifficultyTier(void) { return rounds.wave / 10; }

/* hit points: linear to wave 15, then slower; every 10 waves adds a flat 20 % tier bonus */
int Rounds_EnemyHpPercent(int wave)
{
    int w = wave < 1 ? 1 : wave;
    int pct = 100 + 9 * (w - 1);
    if (w > 15) pct = 100 + 9 * 14 + 5 * (w - 15);
    pct += 20 * (w / 10);
    return pct;
}

int Rounds_EnemySpeedPercent(int wave)
{
    int w = wave < 1 ? 1 : wave;
    int pct = 100 + 2 * (w - 1);
    if (pct > 140) pct = 140 + (w - 21) / 4;
    if (pct > 165) pct = 165;
    return pct;
}

void Rounds_Reset(void)
{
    memset(&rounds, 0, sizeof(rounds));
}

static int wave_total(int w)
{
    int n = 4 + 2 * w;                 /* wave 1 = 6 */
    if (w > 30) n = 64 + (w - 30);
    if (n > 99) n = 99;
    return n;
}

static int alive_cap(int w)
{
    int c = 6 + w;
    if (c > 24) c = 24 + (w - 18) / 3;
    if (c > MAX_ENEMIES) c = MAX_ENEMIES;
    return c;
}

void Rounds_StartWave(int wave)
{
    rounds.wave = (u16)wave;
    rounds.total = (u16)wave_total(wave);
    rounds.to_spawn = rounds.total;
    rounds.phase = RP_START;
    rounds.timer = 0;
    rounds.spawn_timer = 30;
    rounds.banner = 1;
    G.state_frame = 0;
}

static int pick_type(int w)
{
    int r = RandRange(100);
    if (w <= 5) return (w == 5 && r < 12) ? E_RUSHER : E_SHAMBLER;
    int special = MIN(65, 8 + (w - 6) * 3);           /* % chance of a non-shambler */
    if (w >= 16) special = MIN(80, special + 6);
    if (r >= special) return E_SHAMBLER;
    /* choose among unlocked specials */
    int pool[6], n = 0;
    pool[n++] = E_RUSHER;
    pool[n++] = E_RUSHER;
    if (w >= 8) pool[n++] = E_BRUTE;
    if (w >= 11) pool[n++] = E_SPITTER;
    if (w >= 13) pool[n++] = E_STALKER;
    if (w >= 16) pool[n++] = E_STALKER;
    int t = pool[RandRange(n)];
    if (t == E_BRUTE) {
        /* at most one brute per 4 enemies on screen early */
        int brutes = 0;
        for (int i = 0; i < MAX_ENEMIES; i++) if (enemies[i].active && enemies[i].type == E_BRUTE && enemies[i].state != ES_DEAD) brutes++;
        if (brutes >= 1 + w / 8) t = E_RUSHER;
    }
    return t;
}

/* choose an open spawn point away from the player, preferably out of sight */
static int choose_spawn(void)
{
    int px = player.x >> 8, py = player.y >> 8;
    int best = -1;
    for (int tries = 0; tries < 14; tries++) {
        int i = RandRange(NUM_SPAWNS);
        const SpawnPoint *sp = &map_spawns[i];
        if (!Map_AreaOpen(sp->area)) continue;
        int sx = sp->x * 8 + 4, sy = sp->y * 8 + 4;
        u32 d = Dist(sx - px, sy - py);
        if (d < 96) continue;                          /* minimum spawn distance */
        if (Nav_Dist(sp->x, sp->y) >= 255 && Nav_Ready()) continue;
        /* do not spawn on top of another zombie */
        int clash = 0;
        for (int j = 0; j < MAX_ENEMIES; j++) {
            Enemy *e = &enemies[j];
            if (e->active && e->state != ES_DEAD && ABS((e->x >> 8) - sx) < 10 && ABS((e->y >> 8) - sy) < 10) { clash = 1; break; }
        }
        if (clash) continue;
        best = i;
        if (!Col_LineClear(px, py - 6, sx, sy - 6)) break;     /* prefer hidden spawn points */
    }
    return best;
}

static int spawn_interval(int w)
{
    int v = 66 - w * 2;
    if (w > 20) v -= (w - 20) / 2;
    return v < 14 ? 14 : v;
}

void Rounds_Update(void)
{
    switch (rounds.phase) {
    case RP_START:
        rounds.timer++;
        if (rounds.timer < 80) rounds.banner = 1;          /* WAVE n */
        else if (rounds.timer < 140) rounds.banner = 2;    /* READY? */
        else { rounds.banner = 0; rounds.phase = RP_RUNNING; Audio_PlaySfx(SFX_WAVE_START); }
        if (rounds.timer == 2) Audio_PlaySfx(SFX_WAVE_START);
        break;
    case RP_RUNNING: {
        if (rounds.to_spawn > 0) {
            if (rounds.spawn_timer) rounds.spawn_timer--;
            if (rounds.spawn_timer == 0 && enemy_count_alive < alive_cap(rounds.wave)) {
                int sp = choose_spawn();
                if (sp >= 0) {
                    int t = pick_type(rounds.wave);
                    Enemy *e = Enemy_Spawn(t, map_spawns[sp].x, map_spawns[sp].y, rounds.wave);
                    if (e) {
                        rounds.to_spawn--;
                        Fx_Spawn(FXK_PUFF, e->x >> 8, (e->y >> 8) - 4, 0, -20, 12);
                        enemy_count_alive++;
                    }
                }
                rounds.spawn_timer = (u16)spawn_interval(rounds.wave);
                /* later waves occasionally burst */
                if (rounds.wave >= 6 && RandRange(100) < 25) rounds.spawn_timer >>= 2;
            }
        }
        if (rounds.to_spawn == 0 && enemy_count_alive == 0) {
            rounds.phase = RP_COMPLETE;
            rounds.timer = 0;
            rounds.banner = 3;
            Audio_PlaySfx(SFX_WAVE_CLEAR);
        }
        break;
    }
    case RP_COMPLETE:
        rounds.timer++;
        if (rounds.timer >= 190) Rounds_StartWave(rounds.wave + 1);
        break;
    }
}
