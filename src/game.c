/* game.c - state manager, world update, run lifecycle */
#include "game.h"

Game G;

static int cur_area = -1, area_t;
static int last_ptx = -1, last_pty = -1;
static u8 sel_combo, sel_down;
static const char *banner_text;
static char wave_text[16];

void Game_AddScore(int pts)
{
    if (player.double_t) pts *= 2;
    G.score += (u32)pts;
    if (pts >= 50) {
        if (G.score_gain_t == 0) G.score_gain = 0;
        G.score_gain += (u16)pts;
        G.score_gain_t = 50;
    }
}

void World_Reset(void)
{
    Map_Init();
    Nav_Reset();
    Bullets_Init();
    Fx_Init();
    Pickups_Init();
    Enemies_Init();
    Player_Init();
    Interact_Reset();
    Rounds_Reset();
    G.score = 0; G.kills = 0; G.play_frames = 0;
    G.score_gain = G.score_gain_t = 0;
    G.new_best = 0;
    cur_area = -1; area_t = 0;
    last_ptx = last_pty = -1;
    G.show_map = save.minimap_on;
    Cam_Init(player.x >> 8, player.y >> 8);
}

void Game_NewRun(void)
{
    Rand_Seed(REG_TM0CNT_L * 2654435761u + G.frame * 40503u + 12345u);
    World_Reset();
    Video_ModeGame();
    Map_Reveal(player.x >> 11, player.y >> 11, 7);
    Rounds_StartWave(1);
    G.state = ST_ROUND_START;
    G.state_frame = 0;
    Audio_SetMusic(MUS_GAME);
    Audio_SetTension(0);
    Hud_Message("SURVIVE.", "THE NIGHT IS LONG", HC_ORANGE, 150);
}

static void announce_area(void)
{
    int tx = player.x >> 11, ty = player.y >> 11;
    int a = map_area[ty * MAP_W + tx];
    if (a < NUM_AREAS && a != cur_area) {
        cur_area = a;
        area_t = 160;
    }
}

static void debug_cheats(void)
{
#ifdef DEBUG
    if (!KeyHeld(KEY_SELECT)) return;
    if (KeyPressed(KEY_UP))    { Enemies_KillAll(1); sel_combo = 1; }
    if (KeyPressed(KEY_DOWN))  { Player_Heal(player.maxhp); sel_combo = 1; }
    if (KeyPressed(KEY_LEFT))  { Weapon_Give(&player, (player.wpn[player.cur].id + 1) % W_COUNT); sel_combo = 1; }
    if (KeyPressed(KEY_RIGHT)) { G.score += 1000; sel_combo = 1; }
    if (KeyPressed(KEY_A))     { Enemies_KillAll(0); rounds.to_spawn = 0; Rounds_StartWave(rounds.wave + 1); sel_combo = 1; }
    if (KeyPressed(KEY_B))     { G.god ^= 1; sel_combo = 1; }
    if (KeyPressed(KEY_L))     { G.debug ^= 1; sel_combo = 1; }
    if (KeyPressed(KEY_R))     { Map_RevealAll(); Map_SetPower(1); sel_combo = 1; }
#endif
}

void World_Update(int running)
{
    Fx_Update();
    Player_Update();
    Enemies_Update();
    Bullets_Update();
    Pickups_Update();
    int ptx = player.x >> 11, pty = player.y >> 11;
    Nav_Update(ptx, pty, 460);
    if (ptx != last_ptx || pty != last_pty) {
        last_ptx = ptx; last_pty = pty;
        Map_Reveal(ptx, pty, 6);
        announce_area();
    }
    if (G.score_gain_t) G.score_gain_t--;
    if (area_t) area_t--;
    Hud_Update();
    if (running && player.state == PS_ALIVE) G.play_frames++;

    /* music intensity + low health tension layer */
    int intense = enemy_count_alive >= 12 || rounds.wave >= 12;
    Audio_SetMusic(player.state != PS_ALIVE ? MUS_NONE : (intense ? MUS_INTENSE : MUS_GAME));
    Audio_SetTension(player.state == PS_ALIVE && player.hp * 3 < player.maxhp);
}

static void render_play(void)
{
    Cam_Update(player.x >> 8, player.y >> 8, (Cos(player.face_angle) * 18) >> 8, (Sin(player.face_angle) * 12) >> 8);
    World_Render();
    banner_text = 0;
    if (player.state != PS_ALIVE && player.dying_t > 12) {
        Hud_Banner("PLAYER DOWN", HC_RED);
    } else if (rounds.banner == 1) {
        char *p = wave_text;
        const char *w = "WAVE ";
        while (*w) *p++ = *w++;
        UInt2Str(p, rounds.wave, 1, '0');
        Hud_Banner(wave_text, HC_ORANGE);
    } else if (rounds.banner == 2) Hud_Banner("READY?", HC_YELLOW);
    else if (rounds.banner == 3) Hud_Banner("WAVE CLEARED", HC_GREEN);
    Hud_Game();
    if (area_t && !rounds.banner && player.state == PS_ALIVE) {
        Hud_TextC(8, map_area_names[cur_area], (area_t & 8) && area_t < 30 ? HC_GRAY : HC_ORANGE);
    }
    if (G.debug) Hud_Debug();
}

static void update_play(void)
{
    /* SELECT: status screen on release, combos for debug cheats */
    if (KeyPressed(KEY_SELECT)) { sel_down = 1; sel_combo = 0; }
    if (sel_down && (keys_down & ~KEY_SELECT)) sel_combo = 1;
    debug_cheats();
    if (sel_down && KeyReleased(KEY_SELECT)) {
        sel_down = 0;
        if (!sel_combo) { Game_SetState(ST_STATUS); return; }
    }
    if (KeyPressed(KEY_START) && player.state == PS_ALIVE) { Game_SetState(ST_PAUSED); return; }

    int running = (rounds.phase != RP_START);
    World_Update(running);
    if (player.state == PS_ALIVE) Rounds_Update();
    else if (player.state == PS_DEAD) { Game_SetState(ST_GAME_OVER); return; }

    /* the three gameplay states follow the round phase */
    if (rounds.phase == RP_START) G.state = ST_ROUND_START;
    else if (rounds.phase == RP_COMPLETE) G.state = ST_ROUND_COMPLETE;
    else G.state = ST_PLAYING;
    render_play();
}

void Game_SetState(int st)
{
    int old = G.state;
    G.prev_state = (u8)old;
    G.state = (u8)st;
    G.state_frame = 0;
    switch (st) {
    case ST_TITLE: case ST_MENU: case ST_OPTIONS: case ST_CONTROLS: case ST_HIGH_SCORE:
    case ST_PAUSED: case ST_STATUS: case ST_GAME_OVER:
        Menu_Enter(st);
        break;
    case ST_PLAYING: case ST_ROUND_START: case ST_ROUND_COMPLETE:
        break;
    }
}

void Game_Init(void)
{
    memset(&G, 0, sizeof(G));
    G.show_map = save.minimap_on;
    Audio_Enable(save.music_on, save.sfx_on);
    Rounds_Reset();
    Player_Init();
    G.state = ST_TITLE;
    if (!save.seen_controls) {
        Game_SetState(ST_CONTROLS);
    } else {
        Game_SetState(ST_TITLE);
    }
}

void Game_Frame(void)
{
    Input_Update();
    G.frame++;
    G.state_frame++;
    switch (G.state) {
    case ST_PLAYING: case ST_ROUND_START: case ST_ROUND_COMPLETE:
        update_play();
        break;
    default:
        Menu_Update();
        Menu_Draw();
        break;
    }
    Audio_Update();
}
