#include "game.h"

Player player;

static const s8 dir_dx[8] = { 1, 1, 0, -1, -1, -1, 0, 1 };
static const s8 dir_dy[8] = { 0, 1, 1, 1, 0, -1, -1, -1 };

static u8 aim_ranges[3] = { 80, 120, 168 };

void Player_Init(void)
{
    Player *p = &player;
    memset(p, 0, sizeof(*p));
    p->x = ((s32)map_player_start[0] * 8 + 4) << 8;
    p->y = ((s32)map_player_start[1] * 8 + 7) << 8;
    p->state = PS_ALIVE;
    p->hp = p->maxhp = PLAYER_BASE_HP;
    p->face_angle = 192;
    p->aim = 192;
    p->view = VIEW_UP;
    p->target = -1;
    p->last_interact = -1;
    Weapon_Reset(p);
}

void Player_AddScore(int pts) { Game_AddScore(pts); }

void Player_Heal(int hp)
{
    player.hp = (s16)MIN(player.maxhp, player.hp + hp);
}

int Player_SpeedFx(void)
{
    int s = 330;
    if (player.perks & (1 << PERK_SECOND_WIND)) s = 372;
    return s;
}

int Player_Dead(void) { return player.state == PS_DEAD; }

void Player_Hurt(int dmg, int fx, int fy)
{
    Player *p = &player;
    if (p->state != PS_ALIVE || p->inv_t || G.god) return;
    p->hp -= (s16)dmg;
    p->inv_t = 22;
    p->hurt_t = 16;
    p->regen_wait = (p->perks & (1 << PERK_FIELD_MEDIC)) ? 120 : 300;
    Fx_Flash(5);
    Fx_Shake(5);
    Fx_Blood(p->x >> 8, p->y >> 8, 4);
    int dx = fx - (p->x >> 8), dy = fy - ((p->y >> 8) - 8);
    int dir;
    if (ABS(dx) > ABS(dy)) dir = dx < 0 ? 2 : 3;
    else dir = dy < 0 ? 0 : 1;
    p->dmg_dir[dir] = 40;
    if (p->hp <= 0) {
        p->hp = 0;
        p->state = PS_DYING;
        p->dying_t = 0;
        Audio_PlaySfx(SFX_PLAYER_DOWN);
        Fx_Shake(10);
        Fx_Flash(10);
        Audio_SetTension(0);
        Audio_SetMusic(MUS_NONE);
    } else {
        Audio_PlaySfx(SFX_PLAYER_HURT);
    }
}

void Player_ApplyPerk(int perk)
{
    player.perks |= (u8)(1 << perk);
    if (perk == PERK_IRON_HEART) {
        player.maxhp = 150;
        player.hp = (s16)MIN(150, player.hp + 50);
    }
}

static void view_from_angle(u8 ang, u8 *view, u8 *flip)
{
    int c = Cos(ang), s = Sin(ang);
    if (ABS(s) > ABS(c)) { *view = s > 0 ? VIEW_DOWN : VIEW_UP; }
    else { *view = VIEW_SIDE; *flip = c < 0; }
}

static int target_valid(int idx, int range)
{
    if (idx < 0) return 0;
    Enemy *e = &enemies[idx];
    if (!e->active || e->state == ES_DEAD || e->hidden) return 0;
    int dx = (e->x >> 8) - (player.x >> 8), dy = (e->y >> 8) - (player.y >> 8);
    if ((int)Dist(dx, dy) > range + 12) return 0;
    return Col_LineClear(player.x >> 8, (player.y >> 8) - 6, e->x >> 8, (e->y >> 8) - 6);
}

static void cycle_target(int range)
{
    /* next enemy farther away than the current one (wraps to the nearest) */
    int px = player.x >> 8, py = player.y >> 8;
    int cur_d = -1;
    if (player.target >= 0) {
        Enemy *c = &enemies[player.target];
        cur_d = (int)Dist((c->x >> 8) - px, (c->y >> 8) - py);
    }
    int best = -1, bd = 9999, first = -1, fd = 9999;
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD || e->hidden || i == player.target) continue;
        int d = (int)Dist((e->x >> 8) - px, (e->y >> 8) - py);
        if (d > range) continue;
        if (!Col_LineClear(px, py - 6, e->x >> 8, (e->y >> 8) - 6)) continue;
        if (d < fd) { fd = d; first = i; }
        if (d >= cur_d && d < bd) { bd = d; best = i; }
    }
    if (best < 0) best = first;
    if (best >= 0) { player.target = (s8)best; player.lock = 1; Audio_PlaySfx(SFX_MENU_MOVE); }
}

void Player_Update(void)
{
    Player *p = &player;
    if (p->state == PS_DEAD) return;
    if (p->state == PS_DYING) {
        if (p->dying_t < 255) p->dying_t++;
        if (p->dying_t > 90) p->state = PS_DEAD;
        return;
    }
    int range = aim_ranges[save.aim_range % 3];

    /* ---- timers */
    if (p->hurt_t) p->hurt_t--;
    if (p->inv_t) p->inv_t--;
    if (p->pose_t && p->pose_t != 255) { if (--p->pose_t == 0 && p->pose != POSE_RELOAD) p->pose = POSE_NONE; }
    if (p->muzzle_t) p->muzzle_t--;
    if (p->empty_flash) p->empty_flash--;
    if (p->overdrive_t) p->overdrive_t--;
    if (p->double_t) p->double_t--;
    if (p->insta_t) p->insta_t--;
    for (int i = 0; i < 4; i++) if (p->dmg_dir[i]) p->dmg_dir[i]--;

    /* ---- movement */
    int dx = 0, dy = 0;
    if (KeyHeld(KEY_LEFT)) dx = -1;
    if (KeyHeld(KEY_RIGHT)) dx = 1;
    if (KeyHeld(KEY_UP)) dy = -1;
    if (KeyHeld(KEY_DOWN)) dy = 1;
    int sp = Player_SpeedFx();
    s32 vx = dx * sp, vy = dy * sp;
    if (dx && dy) { vx = (vx * 181) >> 8; vy = (vy * 181) >> 8; }
    p->moving = (u8)((dx | dy) != 0);
    if (p->moving) {
        Col_Move(&p->x, &p->y, vx, vy, PLAYER_HW, PLAYER_HU);
        int idx = 0;
        for (int i = 0; i < 8; i++) if (dir_dx[i] == dx && dir_dy[i] == dy) { idx = i; break; }
        p->face_angle = (u8)(idx * 32);
        if (++p->anim_t >= 6) { p->anim_t = 0; p->anim_f = (p->anim_f + 1) & 3; }
    } else {
        p->anim_t = 0; p->anim_f = 0;
    }

    /* ---- targeting (auto aim, R cycles) */
    if (KeyPressed(KEY_R)) cycle_target(range);
    if ((G.frame & 3) == 0 || !target_valid(p->target, range)) {
        if (!(p->lock && target_valid(p->target, range))) {
            p->lock = 0;
            p->target = (s8)Enemies_NearestTo(p->x >> 8, p->y >> 8, range, 1, -1);
        }
    }
    if (p->target >= 0 && target_valid(p->target, range)) {
        Enemy *t = &enemies[p->target];
        p->aim = Atan2(((t->y >> 8) - 4) - (p->y >> 8), (t->x >> 8) - (p->x >> 8));
    } else {
        p->target = -1; p->lock = 0;
        p->aim = p->face_angle;
    }
    u8 view_ang = (p->target >= 0 || p->muzzle_t) ? p->aim : p->face_angle;
    view_from_angle(view_ang, &p->view, &p->flip);

    /* ---- weapons */
    Weapon_Update(p);
    if (KeyPressed(KEY_L)) Weapon_Switch(p);
    if (KeyHeld(KEY_A)) Weapon_TryFire(p);
    {
        WeaponSlot *s = &p->wpn[p->cur];
        if (s->mag == 0 && s->reserve > 0 && !p->reload_t && !p->fire_cd) Weapon_StartReload(p);
    }

    /* ---- B: interact (hold) / melee / reload */
    int zone = Interact_Find(p->x >> 8, p->y >> 8);
    p->last_interact = (s8)zone;
    int enemy_close = Enemies_NearestTo(p->x >> 8, p->y >> 8, 22, 0, -1) >= 0;
    if (KeyHeld(KEY_B) && zone >= 0 && !enemy_close) {
        Interact_Hold(zone);
        p->pose = POSE_INTERACT;
        p->pose_t = 3;
    } else {
        Interact_Release();
        if (KeyPressed(KEY_B)) {
            if (enemy_close) Weapon_Melee(p);
            else Weapon_StartReload(p);
        }
    }

    /* ---- health regeneration */
    if (p->regen_wait) p->regen_wait--;
    else if (p->hp < p->maxhp) {
        int every = (p->perks & (1 << PERK_FIELD_MEDIC)) ? 9 : 20;
        if (++p->regen_tick >= every) { p->regen_tick = 0; p->hp++; }
    }
}
