#include "game.h"

Enemy enemies[MAX_ENEMIES] IWRAM_DATA;
u8 enemy_count_alive;

/*                      hp   speed dmg rng dly hw hu  pts */
const EnemyDef enemy_defs[E_TYPES] = {
    /* SHAMBLER */ {  50, 112, 12, 15, 50, 5, 5, 100 },
    /* RUSHER   */ {  30, 288,  8, 14, 30, 4, 4, 100 },
    /* BRUTE    */ { 420,  98, 34, 22, 80, 8, 6, 100 },
    /* SPITTER  */ {  40, 132, 15,  0, 110, 5, 5, 100 },
    /* STALKER  */ {  70, 222, 20, 15, 44, 5, 5, 100 },
};

void Enemies_Init(void)
{
    memset(enemies, 0, sizeof(enemies));
    enemy_count_alive = 0;
}

int Enemy_CenterY(const Enemy *e) { return (e->y >> 8) - 6; }

Enemy *Enemy_Spawn(int type, int tx, int ty, int wave)
{
    int slot = -1, corpse = -1, ct = 999;
    for (int i = 0; i < MAX_ENEMIES; i++) {
        if (!enemies[i].active) { slot = i; break; }
        if (enemies[i].state == ES_DEAD && enemies[i].timer < ct) { ct = enemies[i].timer; corpse = i; }
    }
    if (slot < 0) slot = corpse;
    if (slot < 0) return 0;
    Enemy *e = &enemies[slot];
    const EnemyDef *d = &enemy_defs[type];
    memset(e, 0, sizeof(*e));
    e->active = 1;
    e->type = (u8)type;
    e->state = ES_IDLE;
    e->timer = 40;
    e->x = ((s32)tx * 8 + 4) << 8;
    e->y = ((s32)ty * 8 + 7) << 8;
    e->maxhp = e->hp = (s16)((d->hp * Rounds_EnemyHpPercent(wave)) / 100);
    int sp = (d->speed * Rounds_EnemySpeedPercent(wave)) / 100;
    sp += RandSigned(sp / 12);
    e->speed = (u16)sp;
    e->face = VIEW_DOWN;
    e->nav_t = (u8)RandRange(4);
    e->atk_cd = 30;
    e->special_t = (u8)(120 + RandRange(120));
    e->elite = (wave >= 10 && type != E_SPITTER && type != E_STALKER && RandRange(100) < (wave >= 20 ? 50 : 25));
    e->px = (u16)(e->x >> 8); e->py = (u16)(e->y >> 8);
    return e;
}

static void face_from(Enemy *e, int dx, int dy)
{
    if (ABS(dx) < 2 && ABS(dy) < 2) return;
    if (ABS(dy) > ABS(dx)) { e->face = dy > 0 ? VIEW_DOWN : VIEW_UP; }
    else { e->face = VIEW_SIDE; e->flip = dx < 0; }
}

static void set_velocity(Enemy *e, int dx, int dy, int speed)
{
    u32 len = Dist(dx, dy);
    if (len == 0) { e->vx = e->vy = 0; return; }
    e->vx = (s16)((dx * speed) / (s32)len);
    e->vy = (s16)((dy * speed) / (s32)len);
}

static int footprint_free(int px, int py, const EnemyDef *d)
{
    return !Col_BoxSolid(px, py, d->hw, d->hu);
}

static void kill_enemy(Enemy *e, int crit, int melee)
{
    int pts = 100;
    if (melee) pts = 130;
    else if (crit) pts = 150;
    Game_AddScore(pts);
    G.kills++;
    if (melee || crit) { G.kill_tag = (u8)(melee ? 2 : 1); G.kill_tag_t = 50; }
    e->state = ES_DEAD;
    e->timer = 70;
    e->vx = e->vy = 0;
    e->hidden = 0;
    int ex = e->x >> 8, ey = e->y >> 8;
    Fx_Blood(ex, ey, e->type == E_BRUTE ? 10 : 6);
    Audio_PlaySfx(e->type == E_BRUTE ? SFX_BRUTE_DEATH : SFX_ENEMY_DEATH);
    Pickups_MaybeDrop(ex, ey);
    if (e->type == E_BRUTE) Fx_Shake(5);
}

int Enemy_Damage(Enemy *e, int dmg, int crit, int melee, int hit_angle)
{
    if (!e->active || e->state == ES_DEAD || e->hidden) return 0;
    e->hp -= (s16)dmg;
    e->flash = 4;
    Game_AddScore(10);
    Fx_Blood(e->x >> 8, e->y >> 8, 2);
    if (e->hp <= 0) { kill_enemy(e, crit, melee); return 1; }
    Audio_PlaySfx(SFX_ENEMY_HIT);
    if (e->type != E_BRUTE) {
        e->vx = (s16)((Cos((u8)hit_angle) * 90) >> 8);
        e->vy = (s16)((Sin((u8)hit_angle) * 90) >> 8);
        if (e->state != ES_IDLE) { e->state = ES_HURT; e->timer = melee ? 14 : 5; }
    }
    return 0;
}

void Enemies_KillAll(int award)
{
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD) continue;
        if (award) kill_enemy(e, 0, 0);
        else { e->active = 0; }
    }
}

void Enemies_Clearout(int dmg)
{
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD) continue;
        int sx = (e->x >> 8) - cam_x, sy = (e->y >> 8) - cam_y;
        if (sx < -8 || sx > SCREEN_W + 8 || sy < -8 || sy > SCREEN_H + 24) continue;
        Fx_Explosion(e->x >> 8, (e->y >> 8) - 6);
        e->hidden = 0;
        Enemy_Damage(e, dmg, 0, 0, 0);
    }
}

int Enemies_NearestTo(int px, int py, int max_dist, int need_los, int skip)
{
    u32 rejected = 0;
    for (int attempt = 0; attempt < 3; attempt++) {
        int best = -1; u32 bd = (u32)max_dist + 1;
        for (int i = 0; i < MAX_ENEMIES; i++) {
            Enemy *e = &enemies[i];
            if (!e->active || e->state == ES_DEAD || e->hidden || i == skip || (rejected & (1u << i))) continue;
            int dx = (e->x >> 8) - px, dy = (e->y >> 8) - py;
            if (dx > max_dist || dx < -max_dist || dy > max_dist || dy < -max_dist) continue;
            u32 d = Dist(dx, dy);
            if (d < bd) { bd = d; best = i; }
        }
        if (best < 0) return -1;
        if (!need_los) return best;
        Enemy *e = &enemies[best];
        if (Col_LineClear(px, py - 6, e->x >> 8, (e->y >> 8) - 6)) return best;
        rejected |= 1u << best;
    }
    return -1;
}

/* ---------------------------------------------------------------- AI */
static int dmg_for(const EnemyDef *d)
{
    return d->dmg * (100 + 10 * Rounds_DifficultyTier()) / 100;
}

static void steer(Enemy *e, int slot)
{
    const EnemyDef *d = &enemy_defs[e->type];
    int ex = e->x >> 8, ey = e->y >> 8;
    int px = player.x >> 8, py = player.y >> 8;
    int dx = px - ex, dy = py - ey;
    u32 dist = Dist(dx, dy);
    int speed = e->speed;
    (void)slot;

    if (e->alt) {
        /* stuck: sidestep for a while */
        e->alt--;
        set_velocity(e, -dy * e->alt_dir, dx * e->alt_dir, speed);
        return;
    }
    if (e->type == E_SPITTER) {
        if (dist < 68) { set_velocity(e, -dx, -dy, speed); return; }          /* keep distance */
        if (dist <= 118 && Col_LineClear(ex, ey - 6, px, py - 6)) { e->vx = e->vy = 0; return; }
    }
    int sx, sy;
    if (dist < 36 && Col_LineClear(ex, ey - 4, px, py - 4)) {
        set_velocity(e, dx, dy, speed);
    } else if (Nav_Step(ex >> 3, ey >> 3, &sx, &sy)) {
        int cx = ((ex >> 3) + sx) * 8 + 4, cy = ((ey >> 3) + sy) * 8 + 4;
        set_velocity(e, cx - ex, cy - ey, speed);
        /* when the next cell centre is right here use the cell after: keeps motion smooth */
        if (ABS(cx - ex) < 2 && ABS(cy - ey) < 2) set_velocity(e, sx * 8, sy * 8, speed);
    } else {
        set_velocity(e, dx, dy, speed);
    }
    (void)d;
}

/* put an enemy on a random free tile rmin..rmax pixels from the player (stalkers, failsafe) */
int Enemy_TeleportNearPlayer(Enemy *e, int rmin, int rmax)
{
    const EnemyDef *d = &enemy_defs[e->type];
    int px = player.x >> 8, py = player.y >> 8;
    for (int t = 0; t < 16; t++) {
        int ang = RandRange(256);
        int r = rmin + RandRange(rmax - rmin + 1);
        int nx = px + ((Cos((u8)ang) * r) >> 8);
        int ny = py + ((Sin((u8)ang) * r) >> 8);
        if ((u32)nx >= 512 || (u32)ny >= 512) continue;
        if (!footprint_free(nx, ny, d)) continue;
        int ar = map_area[(ny >> 3) * MAP_W + (nx >> 3)];
        if (ar >= NUM_AREAS || !Map_AreaOpen(ar)) continue;
        e->x = (s32)nx << 8; e->y = (s32)ny << 8;
        e->px = (u16)nx; e->py = (u16)ny;
        e->stuck = 0; e->alt = 0;
        Fx_Sparks(nx, ny - 8, 4);
        return 1;
    }
    return 0;
}

static void stalker_teleport(Enemy *e) { Enemy_TeleportNearPlayer(e, 44, 84); }

IWRAM_CODE static void update_one(Enemy *e, int idx)
{
    const EnemyDef *d = &enemy_defs[e->type];
    int ex = e->x >> 8, ey = e->y >> 8;
    int px = player.x >> 8, py = player.y >> 8;
    int dx = px - ex, dy = py - ey;
    u32 dist = Dist(dx, dy);

    if (e->flash) e->flash--;
    if (e->atk_cd) e->atk_cd--;
    e->anim++;

    switch (e->state) {
    case ES_IDLE:
        if (--e->timer == 0) e->state = ES_CHASE;
        return;
    case ES_DEAD:
        if (--e->timer == 0) e->active = 0;
        return;
    case ES_HURT:
        Col_Move(&e->x, &e->y, e->vx, e->vy, d->hw, d->hu);
        e->vx = (s16)((e->vx * 3) >> 2); e->vy = (s16)((e->vy * 3) >> 2);
        if (--e->timer == 0) e->state = ES_CHASE;
        return;
    default: break;
    }

    if (player.state != PS_ALIVE) { e->vx = e->vy = 0; return; }

    /* ------------------------------------------------ special behaviours */
    if (e->type == E_STALKER) {
        if (e->state == ES_SPECIAL) {
            /* cloaked: invisible and untargetable, then reappears close to the player */
            if (--e->timer == 0) {
                stalker_teleport(e);
                e->hidden = 0;
                e->state = ES_CHASE;
                e->atk_cd = 26;
                e->special_t = (u8)(140 + RandRange(100));
                Audio_PlaySfx(SFX_TELEPORT);
            }
            return;
        }
        if (e->special_t && --e->special_t == 0 && dist > 40) {
            e->state = ES_SPECIAL; e->hidden = 1; e->timer = (u8)(50 + RandRange(30));
            e->vx = e->vy = 0;
            Fx_Sparks(ex, ey - 8, 4);
            return;
        }
        if (e->special_t == 0) e->special_t = 30;
    }

    /* ------------------------------------------------ attack */
    if (e->state == ES_ATTACK) {
        e->vx = e->vy = 0;
        face_from(e, dx, dy);
        int strike = (e->type == E_BRUTE) ? 8 : (e->type == E_SPITTER ? 6 : 5);
        if (e->timer == strike) {
            if (e->type == E_SPITTER) {
                Bullets_SpawnEnemy(e->x, e->y - TO_FX(8), player.x, player.y - TO_FX(6), dmg_for(d));
                Audio_PlaySfx(SFX_SPIT);
            } else {
                if (dist <= (u32)(d->atk_range + 8)) {
                    Player_Hurt(dmg_for(d), ex, ey);
                }
                if (e->type == E_BRUTE) Fx_Shake(4);
            }
        }
        if (e->timer == 0 || --e->timer == 0) { e->state = ES_CHASE; e->atk_cd = d->atk_delay; }
        return;
    }

    if (e->atk_cd == 0) {
        if (e->type == E_SPITTER) {
            if (dist < 150 && Col_LineClear(ex, ey - 6, px, py - 6)) {
                e->state = ES_ATTACK; e->timer = 22; e->vx = e->vy = 0;
                return;
            }
        } else if (dist <= (u32)d->atk_range) {
            e->state = ES_ATTACK;
            e->timer = (e->type == E_BRUTE) ? 26 : (e->type == E_RUSHER ? 12 : 16);
            Audio_PlaySfx(SFX_ENEMY_ATTACK);
            return;
        }
    }

    /* ------------------------------------------------ movement */
    if (e->nav_t) e->nav_t--;
    else {
        e->nav_t = 4;
        steer(e, idx);
    }
    int hit = Col_Move(&e->x, &e->y, e->vx, e->vy, d->hw, d->hu);
    if (hit && !e->alt) e->stuck += 2;
    face_from(e, e->vx, e->vy);
    if (e->state == ES_CHASE && (idx + G.frame) % 16 == 0) {
        int nx = e->x >> 8, ny = e->y >> 8;
        if (ABS(nx - (int)e->px) < 2 && ABS(ny - (int)e->py) < 2 && dist > 14) e->stuck += 6;
        else if (e->stuck > 4) e->stuck -= 4;
        e->px = (u16)nx; e->py = (u16)ny;
    }
    if (e->stuck >= 18) {
        e->stuck = 0;
        e->alt = 22;
        e->alt_dir = (s8)((Rand() & 1) ? 1 : -1);
    }
}

void Enemies_Update(void)
{
    int alive = 0;
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active) continue;
        update_one(e, i);
        if (e->active && e->state != ES_DEAD) alive++;
    }
    enemy_count_alive = (u8)alive;

    /* soft separation so zombies do not stack on the same pixel */
    for (int i = (int)(G.frame & 1); i < MAX_ENEMIES; i += 2) {      /* half of the pairs per frame */
        Enemy *a = &enemies[i];
        if (!a->active || a->state == ES_DEAD || a->state == ES_IDLE) continue;
        int ax = a->x >> 8, ay = a->y >> 8;
        for (int j = i + 1; j < MAX_ENEMIES; j++) {
            Enemy *b = &enemies[j];
            if (!b->active || b->state == ES_DEAD || b->state == ES_IDLE) continue;
            int dx = (b->x >> 8) - ax, dy = (b->y >> 8) - ay;
            int rx = 9, ry = 6;
            if (a->type == E_BRUTE || b->type == E_BRUTE) { rx = 14; ry = 9; }
            if (dx >= rx || dx <= -rx || dy >= ry || dy <= -ry) continue;
            int sx = dx > 0 ? 110 : -110, sy = dy > 0 ? 70 : -70;
            if (dx == 0) sx = (i & 1) ? 60 : -60;
            if (a->type != E_BRUTE) Col_Move(&a->x, &a->y, -sx, -sy, enemy_defs[a->type].hw, enemy_defs[a->type].hu);
            if (b->type != E_BRUTE) Col_Move(&b->x, &b->y, sx, sy, enemy_defs[b->type].hw, enemy_defs[b->type].hu);
            ax = a->x >> 8; ay = a->y >> 8;
        }
    }
}
