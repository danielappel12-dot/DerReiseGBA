/* game.h - global game state and state manager */
#ifndef GAME_H
#define GAME_H
#include "gba.h"
#include "utils.h"
#include "video.h"
#include "input.h"
#include "map.h"
#include "collision.h"
#include "nav.h"
#include "camera.h"
#include "player.h"
#include "weapons.h"
#include "bullets.h"
#include "enemy.h"
#include "pickups.h"
#include "effects.h"
#include "rounds.h"
#include "audio.h"
#include "save.h"
#include "hud.h"
#include "perks.h"
#include "interact.h"

typedef enum {
    ST_TITLE, ST_MENU, ST_PLAYING, ST_ROUND_START, ST_ROUND_COMPLETE, ST_PAUSED,
    ST_GAME_OVER, ST_OPTIONS, ST_CONTROLS, ST_HIGH_SCORE, ST_STATUS, ST_COUNT
} GameState;

typedef struct {
    u8  state, prev_state, state_t_dummy;
    u32 frame;               /* free running frame counter */
    u32 state_frame;         /* frames since entering the state */
    u32 score, kills, play_frames;
    u16 score_gain, score_gain_t;
    u8  new_best;
    u8  god;                 /* debug invincibility */
    u8  debug;               /* overlay on */
    u8  show_map;            /* minimap visible */
    u8  menu_sel, menu_sel2;
    u8  intensity;
    u8  lag;                 /* last frame overran the vblank */
    u8  fps;
    u8  fps_low;
    u8  from_pause;
} Game;

extern Game G;

void Game_Init(void);
void Game_Frame(void);                 /* one full update + render pass */
void Game_SetState(int st);
void Game_NewRun(void);
void Game_AddScore(int pts);

/* gameplay world helpers shared by states */
void World_Update(int spawn_enabled);
void World_Render(void);
void World_Reset(void);

/* menu screens (menu.c) */
void Menu_Enter(int st);
void Menu_Update(void);
void Menu_Draw(void);

#endif
