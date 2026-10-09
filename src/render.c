/* render.c - turns the game world into OAM sprites + scroll/blend registers */
#include "game.h"

typedef struct { s16 key; u8 kind; u8 idx; } DrawItem;
enum { DI_PLAYER, DI_ENEMY, DI_PICKUP };

static const u16 enemy_tile_base[E_TYPES] = {
    SPR_SHAMBLER_BASE, SPR_RUSHER_BASE, SPR_BRUTE_BASE, SPR_SPITTER_BASE, SPR_STALKER_BASE
};
static const u8 enemy_pal[E_TYPES] = { OP_SHAMBLER, OP_RUSHER, OP_BRUTE, OP_SPITTER, OP_STALKER };
static const u8 elite_pal[E_TYPES] = { OP_ELITE_SH, OP_ELITE_RU, OP_ELITE_BR, OP_SPITTER, OP_STALKER };
static const u8 corpse_row[E_TYPES] = { 0, 1, 99, 2, 3 };

static DrawItem items[MAX_ENEMIES + MAX_PICKUPS + 2];

static void draw_player(void)
{
    Player *p = &player;
    int sx = (p->x >> 8) - 8 - cam_x;
    int sy = (p->y >> 8) - 25 - cam_y;
    int idx, flip = 0;
    int pal = OP_PLAYER;
    if (p->state != PS_ALIVE) {
        int f = p->dying_t / 22;
        if (f > 2) f = 2;
        idx = 18 + f;
        flip = 0;
        if (p->dying_t > 60 && f == 2) { /* lying */ }
    } else {
        if (p->pose == POSE_SHOOT) idx = 12 + p->view;
        else if (p->pose == POSE_RELOAD || p->pose == POSE_INTERACT) idx = 15 + p->view;
        else idx = p->view * 4 + p->anim_f;
        if (p->view == VIEW_SIDE && p->flip) flip = SPR_HFLIP;
        if (p->hurt_t && (p->hurt_t & 2)) pal = OP_HURT;
        else if (p->inv_t && (p->inv_t & 4) && !p->hurt_t) pal = OP_PLAYER;
    }
    Spr_Add(sx, sy, SZ_16x32, SPR_PLAYER_BASE + idx * 8, pal, 1, flip);
}

static void draw_enemy(Enemy *e)
{
    int ex = e->x >> 8, ey = e->y >> 8;
    int frame;
    if (e->state == ES_IDLE) { if (e->timer & 2) return; frame = 0; }
    else if (e->state == ES_ATTACK) frame = 2;
    else frame = (e->anim >> (e->type == E_RUSHER ? 2 : 3)) & 1;
    int pal = e->elite ? elite_pal[e->type] : enemy_pal[e->type];
    if (e->flash) pal = OP_FLASH;
    int flip = (e->face == VIEW_SIDE && e->flip) ? SPR_HFLIP : 0;
    int tile = enemy_tile_base[e->type];
    if (e->type == E_BRUTE) {
        Spr_Add(ex - 16 - cam_x, ey - 29 - cam_y, SZ_32x32, tile + (e->face * 3 + frame) * 16, pal, 1, flip);
    } else {
        if (e->type == E_STALKER && e->state != ES_SPECIAL && e->special_t < 14 && (e->anim & 2)) return;  /* flicker before cloaking */
        Spr_Add(ex - 8 - cam_x, ey - 25 - cam_y, SZ_16x32, tile + (e->face * 3 + frame) * 8, pal, 1, flip);
    }
}

static void draw_corpse(Enemy *e)
{
    if (e->timer < 12 && (e->timer & 2)) return;
    int ex = e->x >> 8, ey = e->y >> 8;
    int f = e->timer > 54 ? 0 : 1;
    int pal = e->elite ? elite_pal[e->type] : enemy_pal[e->type];
    if (e->type == E_BRUTE)
        Spr_Add(ex - 16 - cam_x, ey - 14 - cam_y, SZ_32x16, SPR_BRUTE_CORPSE_BASE + f * 8, pal, 2, 0);
    else
        Spr_Add(ex - 8 - cam_x, ey - 13 - cam_y, SZ_16x16, SPR_CORPSES_BASE + (corpse_row[e->type] * 2 + f) * 4, pal, 2, 0);
}

static void draw_pickup(Pickup *p)
{
    if (p->timer < 180 && ((p->timer >> 2) & 1)) return;
    int bob = ((Sin((u8)(p->phase * 6)) * 3) >> 8);
    int sx = p->x - 8 - cam_x;
    int sy = p->y - 18 - cam_y - (p->z >> 4) - 2 - bob;
    int flip = ((p->phase >> 4) & 1) ? SPR_HFLIP : 0;
    Spr_Add(sx, sy, SZ_16x16, SPR_FX_PU_AMMO + p->type * 4, OP_MISC, 1, flip);
}

static void sort_items(DrawItem *a, int n)
{
    for (int i = 1; i < n; i++) {
        DrawItem v = a[i];
        int j = i - 1;
        while (j >= 0 && a[j].key > v.key) { a[j + 1] = a[j]; j--; }
        a[j + 1] = v;
    }
}


/* ---- objective pointer (generator / its door) and perk gems ------------------------------ */
static void draw_pointer(void)
{
    int wx, wy, cost; const char *lab;
    if (player.state != PS_ALIVE || !Objective_Get(&wx, &wy, &lab, &cost)) return;
    int sx = wx - cam_x, sy = wy - cam_y;
    int bob = (Sin((u8)(G.frame * 8)) * 3) >> 8;
    if (sx > 14 && sx < SCREEN_W - 14 && sy > 22 && sy < SCREEN_H - 14) {
        /* target on screen: bouncing arrow above it */
        Spr_Add(sx - 4, sy - 24 + bob, SZ_8x8, SPR_FX_ARROW_D, OP_FX, 0, 0);
        return;
    }
    /* off screen: arrow on the screen border pointing toward it */
    int dx = wx - (player.x >> 8), dy = wy - ((player.y >> 8) - 8);
    int ax = ABS(dx), ay = ABS(dy);
    int cx = SCREEN_W / 2, cy = SCREEN_H / 2 - 4;
    int mx = cx - 14, my = cy - 14;
    int t_num = 1, t_den = 1;
    if (ax * my > ay * mx) { t_num = mx; t_den = ax ? ax : 1; } else { t_num = my; t_den = ay ? ay : 1; }
    int ex = cx + dx * t_num / t_den, ey = cy + dy * t_num / t_den;
    int oct = ((Atan2(dy, dx) + 16) >> 5) & 7;
    static const u8 frame_of[8] = { 0, 1, 2, 1, 0, 1, 2, 1 };
    static const u8 flip_of[8]  = { 0, 0, 0, SPR_HFLIP, SPR_HFLIP, SPR_HFLIP | SPR_VFLIP, SPR_VFLIP, SPR_VFLIP };
    static const u16 tiles[3] = { SPR_FX_ARROW_R, SPR_FX_ARROW_DR, SPR_FX_ARROW_D };
    Spr_Add(ex - 4, ey - 4, SZ_8x8, tiles[frame_of[oct]], OP_FX, 0, flip_of[oct]);
}

static void draw_box_weapon(void)
{
    if (Box_State() == BOX_IDLE) return;
    for (int i = 0; i < NUM_INTERACTS; i++) {
        const Interact *z = &map_interacts[i];
        if (z->kind != IK_BOX) continue;
        int cx = z->x + z->w / 2 - cam_x, top = z->y + 10 - cam_y;
        if (cx < -16 || cx > SCREEN_W + 16 || top < -30 || top > SCREEN_H + 30) return;
        int bob = (Sin((u8)(G.frame * 6)) * 2) >> 8;
        int blink = (Box_State() == BOX_READY && G.frame % 420 > 0) ? 0 : 0;
        (void)blink;
        Spr_Add(cx - 8, top - 22 + bob, SZ_16x16, SPR_FX_WICON_0 + Box_Shown() * 4, OP_MISC, 1, 0);
        return;
    }
}

static void draw_perk_gems(void)
{
    if (!power_on) return;
    for (int i = 0; i < NUM_INTERACTS; i++) {
        const Interact *z = &map_interacts[i];
        if (z->kind != IK_PERK || (player.perks & (1 << z->id))) continue;
        int cx = z->x + z->w / 2 - cam_x, cy = z->y + 10 - cam_y;      /* zone starts 10 px above the machine */
        if (cx < -16 || cx > SCREEN_W + 16 || cy < -20 || cy > SCREEN_H + 20) continue;
        int afford = G.score >= z->cost;
        int bob = (Sin((u8)(G.frame * (afford ? 10 : 5) + z->id * 40)) * 3) >> 8;
        if (!afford && ((G.frame >> 3) & 3) == 3) continue;                 /* dim blink when unaffordable */
        Spr_Add(cx - 8, cy - 14 + bob, SZ_16x16, SPR_FX_PERK_ICON_IRON + z->id * 4, OP_MISC, 1, 0);
    }
}

void World_Render(void)
{
    Spr_Begin();

    /* ---- HUD-level sprites (priority 0) */
    draw_pointer();
    if (player.state == PS_ALIVE) {
        if (player.dmg_dir[0] && (player.dmg_dir[0] & 4)) Spr_Add(116, 2, SZ_8x8, SPR_FX_DMG_U, OP_FX, 0, 0);
        if (player.dmg_dir[1] && (player.dmg_dir[1] & 4)) Spr_Add(116, 150, SZ_8x8, SPR_FX_DMG_D, OP_FX, 0, 0);
        if (player.dmg_dir[2] && (player.dmg_dir[2] & 4)) Spr_Add(2, 76, SZ_8x8, SPR_FX_DMG_L, OP_FX, 0, 0);
        if (player.dmg_dir[3] && (player.dmg_dir[3] & 4)) Spr_Add(230, 76, SZ_8x8, SPR_FX_DMG_R, OP_FX, 0, 0);
    }

    draw_perk_gems();
    draw_box_weapon();

    /* ---- reticle on the current target */
    if (player.target >= 0 && player.state == PS_ALIVE) {
        Enemy *t = &enemies[player.target];
        if (t->active && t->state != ES_DEAD)
            Spr_Add((t->x >> 8) - 4 - cam_x, (t->y >> 8) - (t->type == E_BRUTE ? 16 : 10) - cam_y, SZ_8x8, SPR_FX_RETICLE, OP_FX, 1, 0);
    }

    /* ---- effects (muzzle, sparks, blood...) */
    for (int i = 0; i < MAX_EFFECTS; i++) {
        Effect *e = &effects[i];
        if (!e->active) continue;
        int x = e->x >> 8, y = e->y >> 8;
        int age = e->life_max - e->life;
        switch (e->kind) {
        case FXK_BLOOD:
            Spr_Add(x - 4 - cam_x, y - 4 - cam_y, SZ_8x8, SPR_FX_BLOOD_0 + (age * 3) / e->life_max, OP_FX, 1, 0);
            break;
        case FXK_SPARK:
            Spr_Add(x - 4 - cam_x, y - 4 - cam_y, SZ_8x8, SPR_FX_SPARK_0 + (age * 3) / e->life_max, OP_FX, 1, 0);
            break;
        case FXK_PUFF:
            Spr_Add(x - 4 - cam_x, y - 4 - cam_y, SZ_8x8, SPR_FX_PUFF_0 + (age * 3) / e->life_max, OP_FX, 1, 0);
            break;
        case FXK_ARC:
            Spr_Add(x - 4 - cam_x, y - 4 - cam_y, SZ_8x8, SPR_FX_ARC_0 + (e->life & 1), OP_FX, 1, 0);
            break;
        case FXK_MUZZLE:
            Spr_Add(x - 8 - cam_x, y - 8 - cam_y, SZ_16x16, SPR_FX_MUZZLE_0 + (age > 1 ? 4 : 0), OP_FX, 1, 0);
            break;
        case FXK_EXPLODE:
            Spr_Add(x - 8 - cam_x, y - 8 - cam_y, SZ_16x16, SPR_FX_EXPLODE_0 + 4 * ((age * 4) / e->life_max), OP_FX, 1, 0);
            break;
        case FXK_SLASH:
            Spr_Add(x - 8 - cam_x, y - 8 - cam_y, SZ_16x16, SPR_FX_SLASH_0 + 4 * ((age * 3) / e->life_max), OP_FX, 1, 0);
            break;
        }
    }

    /* ---- projectiles */
    for (int i = 0; i < MAX_BULLETS; i++) {
        Bullet *b = &bullets[i];
        if (!b->active) continue;
        int tile = SPR_FX_BULLET;
        if (b->type == BT_ARC) tile = SPR_FX_BULLET_ARC;
        else if (b->type == BT_RAY) tile = SPR_FX_RAY;
        else if (b->type == BT_PELLET) tile = SPR_FX_BULLET;
        else if (b->type == BT_ROCKET) tile = SPR_FX_ROCKET;
        else if (b->type == BT_FLAME) tile = SPR_FX_FLAME_0 + ((b->life >> 2) & 1);
        else if (b->type == BT_BOUNCE) tile = SPR_FX_BULLET_BIG;
        else if (b->dmg >= 60) tile = SPR_FX_BULLET_BIG;
        Spr_Add((b->x >> 8) - 4 - cam_x, (b->y >> 8) - 12 - cam_y, SZ_8x8, tile, OP_FX, 1, 0);
    }
    for (int i = 0; i < MAX_EBULLETS; i++) {
        EBullet *b = &ebullets[i];
        if (!b->active) continue;
        Spr_Add((b->x >> 8) - 4 - cam_x, (b->y >> 8) - 12 - cam_y, SZ_8x8, SPR_FX_SPIT_0 + ((b->frame >> 2) & 1), OP_FX, 1, 0);
    }

    /* ---- characters, depth sorted */
    int n = 0;
    items[n].key = (s16)(player.y >> 8); items[n].kind = DI_PLAYER; items[n].idx = 0; n++;
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->state == ES_DEAD || e->hidden) continue;
        int sx = (e->x >> 8) - cam_x, sy = (e->y >> 8) - cam_y;
        if (sx < -20 || sx > SCREEN_W + 20 || sy < -4 || sy > SCREEN_H + 36) continue;
        items[n].key = (s16)(e->y >> 8); items[n].kind = DI_ENEMY; items[n].idx = (u8)i; n++;
    }
    for (int i = 0; i < MAX_PICKUPS; i++) {
        Pickup *p = &pickups[i];
        if (!p->active) continue;
        items[n].key = p->y; items[n].kind = DI_PICKUP; items[n].idx = (u8)i; n++;
    }
    sort_items(items, n);
    for (int i = n - 1; i >= 0; i--) {                  /* front-most first = lowest OAM index */
        switch (items[i].kind) {
        case DI_PLAYER: draw_player(); break;
        case DI_ENEMY:  draw_enemy(&enemies[items[i].idx]); break;
        default:        draw_pickup(&pickups[items[i].idx]); break;
        }
    }

    /* ---- floor level: shadows and corpses */
    if (player.state == PS_ALIVE)
        Spr_Add((player.x >> 8) - 8 - cam_x, (player.y >> 8) - 4 - cam_y, SZ_16x8, SPR_SHADOW_S, OP_FX, 2, 0);
    for (int i = 0; i < MAX_ENEMIES; i++) {
        Enemy *e = &enemies[i];
        if (!e->active || e->hidden) continue;
        int sx = (e->x >> 8) - cam_x, sy = (e->y >> 8) - cam_y;
        if (sx < -20 || sx > SCREEN_W + 20 || sy < -4 || sy > SCREEN_H + 36) continue;
        if (e->state == ES_DEAD) { draw_corpse(e); continue; }
        if (e->type == E_BRUTE) Spr_Add((e->x >> 8) - 16 - cam_x, (e->y >> 8) - 4 - cam_y, SZ_32x8, SPR_SHADOW_B, OP_FX, 2, 0);
        else Spr_Add((e->x >> 8) - 8 - cam_x, (e->y >> 8) - 4 - cam_y, SZ_16x8, SPR_SHADOW_S, OP_FX, 2, 0);
    }
    for (int i = 0; i < MAX_PICKUPS; i++) {
        Pickup *p = &pickups[i];
        if (p->active) Spr_Add(p->x - 8 - cam_x, p->y - 4 - cam_y, SZ_16x8, SPR_SHADOW_S, OP_FX, 2, 0);
    }

    /* ---- scroll + brightness */
    Video_SetScroll(cam_x, cam_y);
    int evy = power_on ? 2 : 5;
    if (!power_on && ((G.frame >> 4) & 7) == 0 && (G.frame & 3) < 2) evy++;      /* flicker */
    if (fx_flash) Video_SetBlend(VID_BLEND_WHITE, fx_flash > 8 ? 8 : fx_flash);
    else Video_SetBlend(VID_BLEND_BLACK, evy);
}
