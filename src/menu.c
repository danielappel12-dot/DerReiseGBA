/* menu.c - title, main menu, options, controls, high scores, pause, status, game over */
#include "game.h"

static int sel;
static int ctrl_page;
static int confirm_erase;

extern u8 bg_title_loaded;

static void time_str(char *b, u32 frames)
{
    u32 s = frames / 60;
    int n = UInt2Str(b, s / 60, 2, '0');
    b[n++] = ':';
    UInt2Str(b + n, s % 60, 2, '0');
}

static void finish_run(void)
{
    /* record the finished run: best wave / score / kills / time */
    int wave = rounds.wave;
    G.new_best = 0;
    if (G.score > save.best_score) { save.best_score = G.score; G.new_best = G.score > 0; }
    if ((u32)wave > save.best_wave) { save.best_wave = (u16)wave; if (G.score > 0) G.new_best = 1; }
    if (G.kills > save.best_kills) save.best_kills = G.kills;
    if (G.play_frames > save.best_time) save.best_time = G.play_frames;
    save.total_kills += G.kills;
    save.games_played++;
    Save_Save();
}

static void list_item(int row, const char *text, int idx, int pal_on, int pal_off)
{
    int n = strlen_(text);
    int x = (30 - n) / 2;
    if (idx == sel) {
        Hud_Tile(x - 2, row, CB1_FONT + ('>' - 32), HC_YELLOW);
        Hud_Text(x, row, text, pal_on);
    } else {
        Hud_Text(x, row, text, pal_off);
    }
}

static int nav(int count)
{
    if (KeyPressed(KEY_UP))   { sel = (sel + count - 1) % count; Audio_PlaySfx(SFX_MENU_MOVE); }
    if (KeyPressed(KEY_DOWN)) { sel = (sel + 1) % count; Audio_PlaySfx(SFX_MENU_MOVE); }
    return KeyPressed(KEY_A);
}

void Menu_Enter(int st)
{
    sel = 0;
    confirm_erase = 0;
    ctrl_page = 0;
    switch (st) {
    case ST_TITLE: case ST_MENU:
        if (!bg_title_loaded) Video_LoadTitleBg();
        Video_ModeTitle();
        Video_SetBlend(VID_BLEND_BLACK, 6);
        Video_SetScroll(0, 0);
        Audio_SetMusic(MUS_MENU);
        Audio_SetTension(0);
        break;
    case ST_OPTIONS: case ST_CONTROLS: case ST_HIGH_SCORE: {
        int dim = (st == ST_CONTROLS) ? 14 : 10;      /* controls: nearly black so the text is easy to read */
        if (G.prev_state == ST_PAUSED) { Video_ModeMenu(); Video_SetBlend(VID_BLEND_BLACK, dim); }
        else {
            if (!bg_title_loaded) Video_LoadTitleBg();
            Video_ModeMenu();
            Video_SetBlend(VID_BLEND_BLACK, dim);
            Video_SetScroll(0, 0);
        }
        break;
    }
    case ST_PAUSED:
        Video_SetBlend(VID_BLEND_BLACK, 7);
        break;
    case ST_STATUS:
        Video_SetBlend(VID_BLEND_BLACK, 8);
        break;
    case ST_GAME_OVER:
        finish_run();
        Video_SetBlend(VID_BLEND_BLACK, 9);
        Audio_SetMusic(MUS_GAMEOVER);
        Audio_SetTension(0);
        break;
    }
}

static void back_to_world(void)
{
    /* leave pause / status: world is still in VRAM */
    Video_ModeGame();
    Video_SetBlend(VID_BLEND_NONE, 0);
    G.state = (u8)(rounds.phase == RP_START ? ST_ROUND_START : (rounds.phase == RP_COMPLETE ? ST_ROUND_COMPLETE : ST_PLAYING));
    G.state_frame = 0;
    Audio_SetMusic(MUS_GAME);
}

void Menu_Update(void)
{
    switch (G.state) {
    case ST_TITLE:
        Video_AnimTitle(G.frame);
        if (KeyPressed(KEY_START) || KeyPressed(KEY_A)) { Audio_PlaySfx(SFX_MENU_SELECT); Game_SetState(ST_MENU); }
        break;
    case ST_MENU:
        Video_AnimTitle(G.frame);
        if (nav(4) | KeyPressed(KEY_START)) {
            Audio_PlaySfx(SFX_MENU_SELECT);
            switch (sel) {
            case 0: Game_NewRun(); return;
            case 1: Game_SetState(ST_OPTIONS); break;
            case 2: Game_SetState(ST_CONTROLS); break;
            case 3: Game_SetState(ST_HIGH_SCORE); break;
            }
        }
        if (KeyPressed(KEY_B)) Game_SetState(ST_TITLE);
        break;
    case ST_CONTROLS:
        if (ctrl_page == 0 && (KeyPressed(KEY_A) || KeyPressed(KEY_RIGHT))) { ctrl_page = 1; Audio_PlaySfx(SFX_MENU_MOVE); break; }
        if (ctrl_page == 1 && KeyPressed(KEY_LEFT)) { ctrl_page = 0; Audio_PlaySfx(SFX_MENU_MOVE); break; }
        if ((ctrl_page == 1 && KeyPressed(KEY_A)) || KeyPressed(KEY_B) || KeyPressed(KEY_START)) {
            Audio_PlaySfx(SFX_MENU_SELECT);
            if (!save.seen_controls) { save.seen_controls = 1; Save_Save(); Game_SetState(ST_TITLE); }
            else if (G.prev_state == ST_PAUSED) { G.state = ST_PAUSED; sel = 1; }
            else Game_SetState(ST_MENU);
        }
        break;
    case ST_HIGH_SCORE:
        if (KeyPressed(KEY_A) || KeyPressed(KEY_B) || KeyPressed(KEY_START)) { Audio_PlaySfx(SFX_MENU_SELECT); Game_SetState(ST_MENU); }
        break;
    case ST_OPTIONS: {
        int act = nav(6);
        int left = KeyPressed(KEY_LEFT), right = KeyPressed(KEY_RIGHT);
        int chg = act || left || right;
        if (KeyPressed(KEY_B)) { Save_Save(); Audio_PlaySfx(SFX_MENU_SELECT); G.prev_state == ST_PAUSED ? (void)(G.state = ST_PAUSED) : Game_SetState(ST_MENU); break; }
        if (sel != 4) confirm_erase = 0;
        if (chg) {
            switch (sel) {
            case 0: save.music_on ^= 1; Audio_Enable(save.music_on, save.sfx_on); Audio_SetMusic(MUS_MENU); break;
            case 1: save.sfx_on ^= 1; Audio_Enable(save.music_on, save.sfx_on); Audio_PlaySfx(SFX_MENU_SELECT); break;
            case 2: save.minimap_on ^= 1; G.show_map = save.minimap_on; Audio_PlaySfx(SFX_MENU_SELECT); break;
            case 3:
                if (left) save.aim_range = (u8)((save.aim_range + 2) % 3); else save.aim_range = (u8)((save.aim_range + 1) % 3);
                Audio_PlaySfx(SFX_MENU_SELECT);
                break;
            case 4:
                if (act) {
                    if (confirm_erase) { Save_Clear(); Audio_Enable(save.music_on, save.sfx_on); confirm_erase = 0; Audio_PlaySfx(SFX_DENIED); }
                    else confirm_erase = 1;
                }
                break;
            case 5:
                if (act) { Save_Save(); Audio_PlaySfx(SFX_MENU_SELECT); G.prev_state == ST_PAUSED ? (void)(G.state = ST_PAUSED) : Game_SetState(ST_MENU); }
                break;
            }
        }
        break;
    }
    case ST_PAUSED:
        if (KeyPressed(KEY_START) || KeyPressed(KEY_B)) { Audio_PlaySfx(SFX_MENU_SELECT); back_to_world(); return; }
        if (nav(4)) {
            Audio_PlaySfx(SFX_MENU_SELECT);
            switch (sel) {
            case 0: back_to_world(); return;
            case 1: Game_SetState(ST_CONTROLS); break;
            case 2: Game_SetState(ST_OPTIONS); break;
            case 3: finish_run(); bg_title_loaded = 0; Game_SetState(ST_MENU); break;
            }
        }
        break;
    case ST_STATUS:
        if (KeyPressed(KEY_A)) { G.show_map ^= 1; Audio_PlaySfx(SFX_MENU_SELECT); }
        if (KeyPressed(KEY_B) || KeyPressed(KEY_SELECT) || KeyPressed(KEY_START)) { Audio_PlaySfx(SFX_MENU_SELECT); back_to_world(); return; }
        break;
    case ST_GAME_OVER:
        if (nav(2)) {
            Audio_PlaySfx(SFX_MENU_SELECT);
            if (sel == 0) Game_NewRun();
            else { bg_title_loaded = 0; Game_SetState(ST_MENU); }
            return;
        }
        break;
    }
}

static void draw_controls(void)
{
    Hud_BigC(0, ctrl_page ? "HOW TO PLAY" : "CONTROLS", HC_ORANGE);
    Hud_Box(0, 2, 30, 17);
    if (ctrl_page == 0) {
        static const char *const k[][2] = {
            { "D-PAD", "MOVE" }, { "A", "FIRE (HOLD)" }, { "B", "RELOAD / MELEE" }, { "B HOLD", "BUY / USE / OPEN" },
            { "L", "SWITCH WEAPON" }, { "R", "CYCLE TARGET" }, { "START", "PAUSE" }, { "SELECT", "STATUS + MAP" },
        };
        for (int i = 0; i < 8; i++) {
            Hud_Text(3, 3 + i * 2, k[i][0], HC_YELLOW);
            Hud_Text(12, 3 + i * 2, k[i][1], HC_WHITE);
        }
    } else {
        static const char *const t[] = {
            "A FIRES. AUTO-AIM LOCKS", "ONTO THE NEAREST ZOMBIE.", "KILLS EARN POINTS.",
            "SPEND THEM ON DOORS AND GUNS", "FIND THE GENERATOR AND", "SWITCH THE POWER ON.", "THEN BUY PERKS (GEMS).",
        };
        for (int i = 0; i < 7; i++) Hud_TextC(4 + i * 2, t[i], i >= 4 ? HC_YELLOW : HC_WHITE);
    }
    if ((G.frame >> 4) & 1) Hud_TextC(19, ctrl_page ? "A: START" : "A: NEXT PAGE", HC_WHITE);
}

void Menu_Draw(void)
{
    Hud_Clear();
    char b[16];
    switch (G.state) {
    case ST_TITLE:
        Spr_Begin();
        Hud_Box(5, 8, 20, 12);
        Hud_TextC(9, "ENDLESS SURVIVAL", HC_CYAN);
        if ((G.frame >> 5) & 1) Hud_TextC(13, "PRESS START", HC_YELLOW);
        if (save.best_wave) { Hud_Text(9, 17, "BEST WAVE", HC_GRAY); Hud_Num(19, 17, save.best_wave, 2, HC_ORANGE, ' '); }
        Hud_Text(0, 19, "V1.0", HC_GRAY);
        break;
    case ST_MENU:
        Spr_Begin();
        Hud_Box(5, 8, 20, 12);
        Hud_TextC(9, "ENDLESS SURVIVAL", HC_CYAN);
        list_item(11, "START", 0, HC_YELLOW, HC_WHITE);
        list_item(13, "OPTIONS", 1, HC_YELLOW, HC_WHITE);
        list_item(15, "CONTROLS", 2, HC_YELLOW, HC_WHITE);
        list_item(17, "HIGH SCORES", 3, HC_YELLOW, HC_WHITE);
        break;
    case ST_CONTROLS:
        Spr_Begin();
        draw_controls();
        break;
    case ST_HIGH_SCORE:
        Spr_Begin();
        Hud_BigC(1, "HIGH SCORES", HC_ORANGE);
        Hud_Box(1, 4, 28, 14);
        Hud_Text(3, 6, "HIGHEST WAVE", HC_WHITE);   Hud_Num(21, 6, save.best_wave, 6, HC_ORANGE, ' ');
        Hud_Text(3, 8, "MOST POINTS", HC_WHITE);  Hud_Text(20, 8, "$", HC_YELLOW); Hud_Num(21, 8, save.best_score, 6, HC_YELLOW, ' ');
        Hud_Text(3, 10, "MOST KILLS", HC_WHITE);    Hud_Num(21, 10, save.best_kills, 6, HC_WHITE, ' ');
        Hud_Text(3, 12, "LONGEST SURVIVAL", HC_WHITE); time_str(b, save.best_time); Hud_Text(22, 12, b, HC_CYAN);
        Hud_Text(3, 14, "TOTAL KILLS", HC_GRAY);   Hud_Num(21, 14, save.total_kills, 6, HC_GREEN, ' ');
        Hud_Text(3, 16, "GAMES PLAYED", HC_GRAY);  Hud_Num(21, 16, save.games_played, 6, HC_GRAY, ' ');
        Hud_TextC(19, "PRESS A", HC_GRAY);
        break;
    case ST_OPTIONS: {
        Spr_Begin();
        Hud_BigC(1, "OPTIONS", HC_ORANGE);
        static const char *const aim[3] = { "SHORT", "MEDIUM", "LONG" };
        Hud_Box(2, 5, 26, 14);
        int y = 7;
        Hud_Text(5, y, "MUSIC", HC_WHITE);       Hud_Text(19, y, save.music_on ? "ON" : "OFF", save.music_on ? HC_GREEN : HC_RED);
        Hud_Text(5, y + 2, "SOUND FX", HC_WHITE); Hud_Text(19, y + 2, save.sfx_on ? "ON" : "OFF", save.sfx_on ? HC_GREEN : HC_RED);
        Hud_Text(5, y + 4, "MINIMAP", HC_WHITE);  Hud_Text(19, y + 4, save.minimap_on ? "ON" : "OFF", save.minimap_on ? HC_GREEN : HC_RED);
        Hud_Text(5, y + 6, "AIM RANGE", HC_WHITE); Hud_Text(19, y + 6, aim[save.aim_range % 3], HC_CYAN);
        Hud_Text(5, y + 8, confirm_erase ? "SURE? PRESS A" : "ERASE SAVE", confirm_erase ? HC_RED : HC_WHITE);
        Hud_Text(5, y + 10, "BACK", HC_WHITE);
        Hud_Tile(3, y + sel * 2, CB1_FONT + ('>' - 32), HC_YELLOW);
        break;
    }
    case ST_PAUSED:
        Hud_BigC(3, "PAUSED", HC_YELLOW);
        list_item(8, "RESUME", 0, HC_YELLOW, HC_WHITE);
        list_item(10, "CONTROLS", 1, HC_YELLOW, HC_WHITE);
        list_item(12, "OPTIONS", 2, HC_YELLOW, HC_WHITE);
        list_item(14, "QUIT", 3, HC_YELLOW, HC_WHITE);
        break;
    case ST_STATUS: {
        Hud_Box(0, 0, 22, 20);
        Hud_Text(2, 1, "STATUS", HC_ORANGE);
        Hud_Text(2, 3, "POINTS", HC_GRAY); Hud_Text(9, 3, "$", HC_YELLOW); Hud_Num(10, 3, G.score, 6, HC_WHITE, '0');
        Hud_Text(2, 5, "WAVE", HC_GRAY);   Hud_Num(7, 5, rounds.wave, 2, HC_ORANGE, '0');
        Hud_Text(11, 5, "KILLS", HC_GRAY); Hud_Num(17, 5, G.kills, 3, HC_WHITE, ' ');
        Hud_Text(2, 7, "TIME", HC_GRAY);   time_str(b, G.play_frames); Hud_Text(7, 7, b, HC_WHITE);
        Hud_Text(13, 7, "HP", HC_GRAY);    Hud_Num(16, 7, player.hp, 3, HC_GREEN, ' '); Hud_Text(19, 7, "/", HC_GRAY); Hud_Num(20, 7, player.maxhp, 3, HC_GREEN, ' ');
        Hud_Text(2, 9, "WEAPONS", HC_YELLOW);
        int wrow = 10;
        for (int i = 0; i < 2; i++) {
            if (player.wpn[i].id == 255) continue;
            Hud_Text(2, wrow, weapon_defs[player.wpn[i].id].name, i == player.cur ? HC_WHITE : HC_GRAY);
            Hud_Num(16, wrow, player.wpn[i].mag, 2, HC_GRAY, '0'); Hud_Text(18, wrow, "/", HC_GRAY);
            Hud_Num(19, wrow, player.wpn[i].reserve, 3, HC_GRAY, '0');
            wrow += 2;
        }
        Hud_Text(2, 14, "PERKS", HC_YELLOW);
        int row = 15;
        for (int i = 0; i < PERK_COUNT; i++)
            if (player.perks & (1 << i)) {
                static const u8 pp[PERK_COUNT] = { HC_RED, HC_YELLOW, HC_CYAN, HC_GREEN, HC_ORANGE };
                Hud_Tile(2, row, UI_PERK_0 + i, pp[i]);
                Hud_Text(4, row, perk_defs[i].name, HC_WHITE);
                row += 1;
                if (row > 17) break;
            }
        if (row == 15) Hud_Text(2, 15, "NONE", HC_GRAY);
        Hud_Text(2, 18, G.show_map ? "A: MAP OFF" : "A: MAP ON", HC_GRAY);
        Hud_Text(14, 18, "B: BACK", HC_GRAY);
        break;
    }
    case ST_GAME_OVER: {
        Hud_BigC(2, "SYSTEM FAILURE", HC_RED);
        Hud_Box(6, 5, 18, 14);
        Hud_Text(9, 6, "WAVE", HC_GRAY);   Hud_Num(16, 6, rounds.wave, 2, HC_ORANGE, '0');
        Hud_Text(9, 8, "POINTS", HC_GRAY); Hud_Text(16, 8, "$", HC_YELLOW); Hud_Num(17, 8, G.score, 6, HC_YELLOW, '0');
        Hud_Text(9, 10, "KILLS", HC_GRAY); Hud_Num(16, 10, G.kills, 3, HC_WHITE, '0');
        Hud_Text(9, 12, "TIME", HC_GRAY);  time_str(b, G.play_frames); Hud_Text(16, 12, b, HC_WHITE);
        if (G.new_best && ((G.frame >> 3) & 1)) Hud_TextC(14, "NEW BEST!", HC_GREEN);
        list_item(16, "TRY AGAIN", 0, HC_YELLOW, HC_WHITE);
        list_item(18, "MAIN MENU", 1, HC_YELLOW, HC_WHITE);
        break;
    }
    default: break;
    }
}
