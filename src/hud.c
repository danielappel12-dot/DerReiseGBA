#include "game.h"
#include "prof.h"

/* ------------------------------------------------------------------ HUD layer */
void Hud_Clear(void)
{
    memset32(hud_map, 0, 512);
}

IWRAM_CODE void Hud_Tile(int x, int y, int tile, int pal)
{
    if (x < 0 || x >= 32 || y < 0 || y >= 32) return;
    hud_map[y * 32 + x] = (u16)(tile | (pal << 12));
}

IWRAM_CODE void Hud_Text(int x, int y, const char *s, int pal)
{
    for (; *s; s++, x++) {
        int c = (u8)*s;
        if (c < 32 || c >= 128) c = '?';
        if (c == ' ') { continue; }          /* keep what is underneath (transparent) */
        Hud_Tile(x, y, CB1_FONT + (c - 32), pal);
    }
}

void Hud_TextC(int y, const char *s, int pal)
{
    int n = strlen_(s);
    Hud_Text((30 - n) / 2, y, s, pal);
}

IWRAM_CODE void Hud_Num(int x, int y, u32 v, int width, int pal, char pad)
{
    char buf[14];
    UInt2Str(buf, v, width, pad);
    Hud_Text(x, y, buf, pal);
}

static int big_index(char c)
{
    const char *set = BIG_CHARS;
    if (c >= 'a' && c <= 'z') c -= 32;
    for (int i = 0; set[i]; i++) if (set[i] == c) return i;
    return BIG_COUNT - 1;       /* blank */
}

void Hud_Big(int x, int y, const char *s, int pal)
{
    for (; *s; s++, x += 2) {
        int i = big_index(*s);
        int t = CB1_BIG + i * 4;
        Hud_Tile(x, y, t, pal);
        Hud_Tile(x + 1, y, t + 1, pal);
        Hud_Tile(x, y + 1, t + 2, pal);
        Hud_Tile(x + 1, y + 1, t + 3, pal);
    }
}

void Hud_BigC(int y, const char *s, int pal)
{
    int n = strlen_(s);
    Hud_Big((30 - n * 2) / 2, y, s, pal);
}

void Hud_Bar(int x, int y, int tiles, int value, int maxv, int pal)
{
    int total = tiles * 8;
    int fill = maxv > 0 ? (value * total) / maxv : 0;
    if (value > 0 && fill == 0) fill = 1;
    for (int i = 0; i < tiles; i++) {
        int f = fill - i * 8;
        f = CLAMP(f, 0, 8);
        Hud_Tile(x + i, y, UI_BAR_0 + f, pal);
    }
}

void Hud_Box(int x, int y, int w, int h)
{
    for (int j = 0; j < h; j++) {
        for (int i = 0; i < w; i++) {
            int t;
            int top = (j == 0), bot = (j == h - 1), lef = (i == 0), rig = (i == w - 1);
            if (top && lef) t = UI_PANEL_TL; else if (top && rig) t = UI_PANEL_TR;
            else if (bot && lef) t = UI_PANEL_BL; else if (bot && rig) t = UI_PANEL_BR;
            else if (top) t = UI_PANEL_T; else if (bot) t = UI_PANEL_B;
            else if (lef) t = UI_PANEL_L; else if (rig) t = UI_PANEL_R; else t = UI_PANEL_C;
            Hud_Tile(x + i, y + j, t, HC_GRAY);
        }
    }
}


/* ------------------------------------------------------------------ gameplay HUD */
static const char *msg1, *msg2;
static int msg_t, msg_color, msg_t_max;

void Hud_Message(const char *l1, const char *l2, int color, int frames)
{
    msg1 = l1; msg2 = l2; msg_t = frames; msg_t_max = frames; msg_color = color;
}

static int hud_banner_pal;
static const char *hud_banner_text;

void Hud_Banner(const char *text, int color)
{
    hud_banner_text = text;
    hud_banner_pal = color;
}

/* word wrap a long message into centred lines of at most 28 characters */
static void wrapped(const char *s, int y, int pal)
{
    char line[32];
    int n = 0;
    while (*s) {
        int wl = 0;
        while (s[wl] && s[wl] != ' ') wl++;
        if (n && n + 1 + wl > 28) { line[n] = 0; Hud_TextC(y++, line, pal); n = 0; }
        if (n) line[n++] = ' ';
        for (int i = 0; i < wl && n < 30; i++) line[n++] = s[i];
        s += wl;
        while (*s == ' ') s++;
    }
    if (n) { line[n] = 0; Hud_TextC(y, line, pal); }
}

void Hud_Update(void)
{
    if (msg_t) msg_t--;
}

static void draw_score_block(void)
{
    Hud_Text(0, 0, "POINTS", HC_GRAY);
    Hud_Text(7, 0, "$", HC_YELLOW);
    Hud_Num(8, 0, G.score, 6, HC_WHITE, '0');
    Hud_Text(0, 1, "WAVE", HC_GRAY);
    Hud_Num(5, 1, rounds.wave, 2, HC_ORANGE, '0');
    if (G.score_gain_t) {
        Hud_Text(15, 0, "+$", HC_YELLOW);
        Hud_Num(17, 0, G.score_gain, 1, HC_YELLOW, ' ');
    }
}

void Hud_Game(void)
{
    Hud_Clear();
    Player *p = &player;
    draw_score_block();

    /* ---- objective: find / activate the generator until the power is on */
    {
        int ox, oy, oc; const char *lab;
        if (Objective_Get(&ox, &oy, &lab, &oc) && p->state == PS_ALIVE) {
            int pal = ((G.frame >> 4) & 1) ? HC_YELLOW : HC_ORANGE;
            Hud_Text(9, 1, lab, pal);
            if (oc > 0) { Hud_Text(9 + strlen_(lab) + 1, 1, "$", pal); Hud_Num(9 + strlen_(lab) + 2, 1, oc, 1, pal, ' '); }
        }
    }

    /* ---- top right: zombies left in this wave */
    {
        Hud_Text(21, 0, "ZOMBIES", HC_GRAY);
        Hud_Num(28, 0, enemy_count_alive + rounds.to_spawn, 2, HC_RED, ' ');
    }

    /* ---- bottom left: health */
    int low = p->hp * 4 < p->maxhp;
    int hp_pal = low ? ((G.frame >> 3) & 1 ? HC_RED : HC_ORANGE) : HC_GREEN;
    Hud_Tile(0, 18, UI_ICON_HEART, HC_RED);
    Hud_Num(1, 18, p->hp, 3, hp_pal, ' ');
    Hud_Bar(5, 18, 5, p->hp, p->maxhp, hp_pal);
    /* owned perks: logo column down the left side (colours match the perk machines) */
    {
        static const u8 perk_pal[PERK_COUNT] = { HC_RED, HC_YELLOW, HC_CYAN, HC_GREEN, HC_ORANGE };
        int py = 8;
        for (int i = 0; i < PERK_COUNT; i++)
            if (p->perks & (1 << i)) Hud_Tile(0, py++, UI_PERK_0 + i, perk_pal[i]);
    }

    /* ---- bottom right: weapon + ammo */
    WeaponSlot *s = &p->wpn[p->cur];
    const WeaponDef *w = &weapon_defs[s->id];
    char nbuf[20];
    {   /* Pack-a-Punched weapons are shown in cyan with a '+' */
        int k = 0;
        for (const char *q = w->name; *q; q++) nbuf[k++] = *q;
        if (s->pap) nbuf[k++] = '+';
        nbuf[k] = 0;
        Hud_Text(30 - k, 18, nbuf, s->pap ? HC_CYAN : HC_WHITE);
    }
    if (s->mag == 0 && s->reserve == 0) {
        if ((G.frame >> 2) & 1) Hud_Text(24, 19, "EMPTY", HC_RED);
        else Hud_Text(24, 19, "EMPTY", HC_ORANGE);
    } else {
        int amp = HC_WHITE;
        if (p->empty_flash && ((G.frame >> 2) & 1)) amp = HC_RED;
        else if (s->mag <= Weapon_MagSize(s) / 4) amp = HC_ORANGE;
        Hud_Num(21, 19, s->mag, 3, amp, '0');
        Hud_Text(24, 19, "/", HC_GRAY);
        Hud_Num(25, 19, s->reserve, 3, HC_GRAY, '0');
        Hud_Tile(29, 19, UI_ICON_BULLET, HC_YELLOW);
    }
    if (p->reload_t) {
        const WeaponDef *wd = w;
        int total = wd->reload;
        if (p->perks & (1 << PERK_QUICK_HANDS)) total = (total * 6) / 10;
        Hud_Text(21, 17, "RELOAD", HC_YELLOW);
        Hud_Bar(21 + 6 > 28 ? 21 : 27, 17, 3, total - p->reload_t, total, HC_YELLOW);
    }
    if (p->wpn[p->cur ^ 1].id != 255) {
        const char *nm = weapon_defs[p->wpn[p->cur ^ 1].id].name;
        int nl = strlen_(nm) + (p->wpn[p->cur ^ 1].pap ? 1 : 0);
        if (!p->reload_t) {
            Hud_Text(30 - nl - 2, 17, "L:", HC_GRAY); Hud_Text(30 - nl, 17, nm, HC_GRAY);
            if (p->wpn[p->cur ^ 1].pap) Hud_Text(29, 17, "+", HC_CYAN);
        }
    }

    /* ---- bonus kill feedback */
    if (G.kill_tag_t) {
        G.kill_tag_t--;
        if (!(G.kill_tag_t & 4) || G.kill_tag_t > 30)
            Hud_TextC(11, G.kill_tag == 1 ? "HEADSHOT +150" : "MELEE KILL +130", G.kill_tag == 1 ? HC_ORANGE : HC_CYAN);
    }

    /* ---- power-up timers (top centre) */
    int row = 2;
    if (p->overdrive_t) { Hud_Text(0, row, "OVERDRIVE", HC_ORANGE); Hud_Num(10, row, p->overdrive_t / 60 + 1, 2, HC_ORANGE, ' '); row++; }
    if (p->double_t)    { Hud_Text(0, row, "2X POINTS", HC_YELLOW); Hud_Num(10, row, p->double_t / 60 + 1, 2, HC_YELLOW, ' '); row++; }
    if (p->insta_t)     { Hud_Text(0, row, "INSTA KILL", HC_RED); Hud_Num(11, row, p->insta_t / 60 + 1, 2, HC_RED, ' '); row++; }

    /* ---- area name on entry is handled by the caller via Hud_Message */
    /* ---- interaction prompt */
    if (p->last_interact >= 0 && p->state == PS_ALIVE) Interact_Draw(p->last_interact);

    /* ---- message line */
    if (msg_t) {
        int pal = msg_color;
        if (msg_t < 12 && (msg_t & 2)) pal = HC_GRAY;
        if (msg1) {
            if (strlen_(msg1) > 28 || (msg2 == 0 && strlen_(msg1) > 22)) wrapped(msg1, 9, pal);
            else Hud_TextC(9, msg1, pal);
        }
        if (msg2) Hud_TextC(10, msg2, HC_WHITE);
    }
    /* ---- banner */
    if (hud_banner_text) {
        Hud_BigC(5, hud_banner_text, hud_banner_pal);
    }
    hud_banner_text = 0;
}

#ifdef DEBUG
void Hud_Debug(void)
{
    extern u8 __bss_end;
    char b[8];
    Hud_Text(0, 3, "FPS", HC_CYAN);  Hud_Num(4, 3, G.fps, 2, HC_WHITE, ' '); Hud_Text(6, 3, "LOW", HC_CYAN); Hud_Num(10, 3, G.fps_low, 2, HC_WHITE, ' ');
    Hud_Text(14, 3, "X", HC_CYAN);   Hud_Num(15, 3, player.x >> 8, 3, HC_WHITE, ' ');
    Hud_Text(19, 3, "Y", HC_CYAN);   Hud_Num(20, 3, player.y >> 8, 3, HC_WHITE, ' ');
    Hud_Text(0, 4, "EN", HC_CYAN);   Hud_Num(3, 4, enemy_count_alive, 2, HC_WHITE, ' ');
    Hud_Text(7, 4, "BL", HC_CYAN);   Hud_Num(10, 4, Bullets_Count(), 2, HC_WHITE, ' ');
    Hud_Text(14, 4, "W", HC_CYAN);   Hud_Num(15, 4, rounds.wave, 2, HC_WHITE, ' ');
    Hud_Text(0, 5, "HP", HC_CYAN);   Hud_Num(3, 5, player.hp, 3, HC_WHITE, ' ');
    Hud_Text(8, 5, "$", HC_CYAN);  Hud_Num(10, 5, G.score, 4, HC_WHITE, ' ');
    Hud_Text(0, 6, "GOD", HC_CYAN);  Hud_Text(4, 6, G.god ? "ON" : "OFF", HC_WHITE);
    Hud_Text(14, 5, weapon_defs[player.wpn[player.cur].id].name, HC_YELLOW);
    u32 free_iw = 0x03007800u - (u32)&__bss_end;
    Hud_Text(9, 6, "IWRAM FREE", HC_CYAN); UInt2Str(b, free_iw, 1, '0'); Hud_Text(20, 6, b, HC_WHITE);
    Hud_Text(0, 7, "PL", HC_CYAN);  Hud_Num(3, 7, prof_shown[PF_PLAYER] / 1000, 3, HC_WHITE, ' ');
    Hud_Text(7, 7, "EN", HC_CYAN);  Hud_Num(10, 7, prof_shown[PF_ENEMY] / 1000, 3, HC_WHITE, ' ');
    Hud_Text(14, 7, "BU", HC_CYAN); Hud_Num(17, 7, prof_shown[PF_BULLET] / 1000, 3, HC_WHITE, ' ');
    Hud_Text(0, 8, "NV", HC_CYAN);  Hud_Num(3, 8, prof_shown[PF_NAV] / 1000, 3, HC_WHITE, ' ');
    Hud_Text(7, 8, "RD", HC_CYAN);  Hud_Num(10, 8, prof_shown[PF_RENDER] / 1000, 3, HC_WHITE, ' ');
    Hud_Text(0, 9, "TOT", HC_CYAN); Hud_Num(4, 9, prof_shown[PF_TOTAL] / 1000, 3, HC_WHITE, ' ');
    Hud_Text(8, 9, "KC MAX/2S OF 280", HC_GRAY);
}
#else
void Hud_Debug(void) {}
#endif
