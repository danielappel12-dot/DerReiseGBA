#ifndef SAVE_H
#define SAVE_H
#include "gba.h"

typedef struct {
    u32 magic;
    u16 version;
    u8  music_on, sfx_on, minimap_on, aim_range;
    u8  seen_controls, vibrate_dummy;
    u32 best_score;
    u16 best_wave;
    u16 pad;
    u32 best_kills;
    u32 best_time;          /* frames */
    u32 total_kills;
    u32 games_played;
    u16 checksum;
} SaveData;

extern SaveData save;

void Save_Load(void);
void Save_Save(void);
void Save_Clear(void);
void Save_Defaults(void);

#endif
