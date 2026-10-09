/* audio.h - PSG (square/wave/noise) sound effects + sequenced music */
#ifndef AUDIO_H
#define AUDIO_H
#include "gba.h"

typedef enum {
    SFX_NONE = 0,
    SFX_SHOT_PISTOL, SFX_SHOT_SHOTGUN, SFX_SHOT_SMG, SFX_SHOT_RIFLE, SFX_SHOT_ARC, SFX_SHOT_RAY,
    SFX_RELOAD, SFX_RELOAD_DONE, SFX_EMPTY, SFX_MELEE,
    SFX_ENEMY_ATTACK, SFX_ENEMY_HIT, SFX_ENEMY_DEATH, SFX_SPIT, SFX_TELEPORT, SFX_BRUTE_DEATH,
    SFX_PLAYER_HURT, SFX_PLAYER_DOWN, SFX_POINTS, SFX_DOOR, SFX_DENIED, SFX_POWERUP, SFX_PICKUP,
    SFX_WAVE_START, SFX_WAVE_CLEAR, SFX_GENERATOR, SFX_PERK, SFX_BUY, SFX_EXPLOSION, SFX_HEARTBEAT,
    SFX_MENU_MOVE, SFX_MENU_SELECT, SFX_NOTE,
    SFX_SHOT_FLAME, SFX_SHOT_BLAST, SFX_PAP, SFX_BOX_TICK, SFX_BOX_OPEN,
    SFX_COUNT
} SfxId;

typedef enum { MUS_NONE = 0, MUS_MENU, MUS_GAME, MUS_INTENSE, MUS_GAMEOVER, MUS_COUNT } MusicId;

void Audio_Init(void);
void Audio_Update(void);                 /* once per frame */
void Audio_PlaySfx(int id);
void Audio_SetMusic(int id);
void Audio_SetTension(int on);           /* low-health layer */
void Audio_Enable(int music_on, int sfx_on);
void Audio_StopAll(void);

#endif
