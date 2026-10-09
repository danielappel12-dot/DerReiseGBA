/* audio.c - PSG sound effects + step-sequenced music
 *
 * Channel plan:  CH1 square  -> tonal sound effects
 *                CH2 square  -> music lead
 *                CH3 wave    -> music bass
 *                CH4 noise   -> noise sound effects, music drums when no sfx is playing
 */
#include "audio.h"
#include "audio_data.h"
#include "utils.h"

#define SQ(hz) (2048 - 131072 / (hz))
#define NZ(shift, width, div) (((shift) << 4) | ((width) << 3) | (div))

typedef struct {
    u8  delay;        /* frames after the effect starts */
    u8  ch;           /* 1 = square 1, 4 = noise */
    u16 x0, x1;       /* ch1: frequency register start/end; ch4: NZ() start/end */
    u8  len;          /* frames */
    u8  duty;
    u8  vol;          /* 0-15 */
    u8  env;          /* hardware envelope step time 0-7 (0 = constant volume) */
} SfxVoice;

typedef struct { u8 n, prio; const SfxVoice *v; } SfxDef;

#define V1(d, a, b, len, duty, vol, env) { d, 1, SQ(a), SQ(b), len, duty, vol, env }
#define V4(d, a, b, len, vol, env)       { d, 4, a, b, len, 0, vol, env }

static const SfxVoice s_pistol[]   = { V1(0, 1400, 260, 7, 2, 13, 1), V4(0, NZ(5, 0, 1), NZ(7, 0, 1), 7, 11, 1) };
static const SfxVoice s_shotgun[]  = { V1(0, 180, 70, 14, 1, 14, 2), V4(0, NZ(8, 0, 2), NZ(11, 0, 3), 20, 15, 2) };
static const SfxVoice s_smg[]      = { V1(0, 1800, 500, 4, 2, 10, 1), V4(0, NZ(4, 0, 1), NZ(5, 0, 1), 4, 9, 1) };
static const SfxVoice s_rifle[]    = { V1(0, 1000, 120, 10, 2, 14, 2), V4(0, NZ(7, 0, 2), NZ(10, 0, 3), 16, 15, 2) };
static const SfxVoice s_arc[]      = { V1(0, 2400, 600, 12, 0, 12, 2), V1(2, 1800, 400, 10, 0, 10, 2), V4(0, NZ(2, 1, 1), NZ(3, 1, 1), 8, 8, 1) };
static const SfxVoice s_ray[]      = { V1(0, 500, 2200, 12, 1, 11, 3), V1(12, 2200, 1800, 4, 1, 8, 1) };
static const SfxVoice s_reload[]   = { V1(0, 1100, 1100, 2, 2, 9, 0), V1(14, 700, 700, 3, 2, 9, 0), V1(30, 1300, 1300, 2, 2, 9, 0) };
static const SfxVoice s_reload_d[] = { V1(0, 600, 600, 3, 2, 11, 0), V1(3, 900, 900, 5, 2, 11, 1) };
static const SfxVoice s_empty[]    = { V1(0, 300, 300, 2, 3, 9, 0) };
static const SfxVoice s_melee[]    = { V4(0, NZ(4, 0, 0), NZ(8, 0, 2), 10, 11, 2), V1(0, 150, 80, 6, 2, 12, 1) };
static const SfxVoice s_eatk[]     = { V1(0, 380, 250, 8, 3, 9, 2) };
static const SfxVoice s_ehit[]     = { V4(0, NZ(3, 0, 1), NZ(3, 0, 1), 3, 9, 1), V1(0, 500, 200, 4, 2, 8, 1) };
static const SfxVoice s_edeath[]   = { V1(0, 420, 90, 20, 3, 11, 3), V4(0, NZ(6, 0, 2), NZ(9, 0, 3), 14, 10, 2) };
static const SfxVoice s_bdeath[]   = { V1(0, 200, 65, 30, 3, 14, 4), V4(0, NZ(9, 0, 3), NZ(12, 0, 3), 26, 15, 3) };
static const SfxVoice s_spit[]     = { V1(0, 300, 900, 10, 1, 9, 2), V4(0, NZ(3, 1, 0), NZ(5, 1, 0), 8, 7, 1) };
static const SfxVoice s_tele[]     = { V1(0, 2000, 300, 10, 0, 10, 2), V1(5, 300, 2000, 8, 0, 9, 2) };
static const SfxVoice s_hurt[]     = { V4(0, NZ(5, 0, 2), NZ(7, 0, 2), 8, 13, 1), V1(0, 260, 110, 10, 3, 12, 2) };
static const SfxVoice s_down[]     = { V1(0, 500, 70, 50, 2, 13, 5), V4(0, NZ(10, 0, 3), NZ(13, 0, 3), 40, 12, 4) };
static const SfxVoice s_points[]   = { V1(0, 1318, 1318, 2, 2, 8, 1) };
static const SfxVoice s_door[]     = { V4(0, NZ(9, 0, 3), NZ(11, 0, 3), 24, 13, 3), V1(0, 110, 70, 24, 3, 11, 3), V1(24, 200, 200, 4, 2, 13, 1) };
static const SfxVoice s_denied[]   = { V1(0, 220, 220, 6, 3, 11, 0), V1(8, 160, 160, 8, 3, 11, 1) };
static const SfxVoice s_powerup[]  = { V1(0, 523, 523, 3, 2, 11, 0), V1(3, 659, 659, 3, 2, 11, 0), V1(6, 784, 784, 3, 2, 11, 0), V1(9, 1047, 1047, 10, 2, 11, 2) };
static const SfxVoice s_pickup[]   = { V1(0, 880, 880, 3, 2, 10, 0), V1(3, 1320, 1320, 6, 2, 10, 2) };
static const SfxVoice s_wstart[]   = { V1(0, 110, 165, 30, 1, 13, 4), V4(0, NZ(11, 0, 3), NZ(11, 0, 3), 30, 8, 3) };
static const SfxVoice s_wclear[]   = { V1(0, 392, 392, 6, 2, 12, 0), V1(6, 494, 494, 6, 2, 12, 0), V1(12, 587, 587, 6, 2, 12, 0), V1(18, 784, 784, 18, 2, 12, 3) };
static const SfxVoice s_gen[]      = { V1(0, 80, 250, 50, 1, 12, 0), V4(0, NZ(11, 0, 3), NZ(8, 0, 2), 50, 12, 0), V1(50, 1500, 700, 8, 0, 12, 2), V4(50, NZ(4, 0, 1), NZ(4, 0, 1), 8, 12, 2) };
static const SfxVoice s_perk[]     = { V1(0, 660, 660, 4, 2, 11, 0), V1(4, 880, 880, 4, 2, 11, 0), V1(8, 1100, 1100, 4, 2, 11, 0), V1(12, 1320, 1320, 14, 2, 11, 3), V4(0, NZ(2, 0, 1), NZ(2, 0, 1), 3, 9, 1) };
static const SfxVoice s_buy[]      = { V1(0, 900, 900, 3, 2, 11, 0), V1(3, 1200, 1200, 7, 2, 11, 2) };
static const SfxVoice s_explode[]  = { V4(0, NZ(11, 0, 3), NZ(13, 0, 3), 36, 15, 3), V1(0, 150, 65, 20, 3, 14, 3) };
static const SfxVoice s_heart[]    = { V4(0, NZ(11, 0, 3), NZ(12, 0, 3), 6, 12, 2), V4(9, NZ(11, 0, 3), NZ(12, 0, 3), 6, 10, 2) };
static const SfxVoice s_mmove[]    = { V1(0, 1200, 1200, 2, 2, 7, 0) };
static const SfxVoice s_msel[]     = { V1(0, 800, 800, 2, 2, 8, 0), V1(2, 1200, 1200, 5, 2, 8, 1) };
static const SfxVoice s_note[]     = { V1(0, 1500, 1500, 3, 2, 7, 0), V1(3, 1000, 1000, 3, 2, 7, 0), V1(6, 1500, 1500, 6, 2, 7, 1) };

static const SfxVoice s_flame[]    = { V4(0, NZ(4, 1, 0), NZ(5, 1, 0), 4, 7, 1) };
static const SfxVoice s_blast[]    = { V1(0, 220, 90, 12, 1, 13, 2), V4(0, NZ(8, 0, 1), NZ(10, 0, 2), 14, 12, 2) };
static const SfxVoice s_pap[]      = { V1(0, 300, 1800, 40, 1, 12, 0), V4(0, NZ(9, 0, 3), NZ(6, 0, 2), 40, 10, 0), V1(40, 1568, 1568, 4, 2, 13, 0), V1(44, 2093, 2093, 16, 2, 13, 3) };
static const SfxVoice s_boxtick[]  = { V1(0, 1800, 1800, 1, 2, 7, 0) };
static const SfxVoice s_boxopen[]  = { V1(0, 400, 900, 20, 2, 11, 2), V1(20, 1200, 1200, 5, 2, 11, 1) };

#define SFX(arr, prio) { sizeof(arr) / sizeof(arr[0]), prio, arr }
static const SfxDef sfx_defs[SFX_COUNT] = {
    [SFX_NONE] = { 0, 0, 0 },
    [SFX_SHOT_PISTOL] = SFX(s_pistol, 3),  [SFX_SHOT_SHOTGUN] = SFX(s_shotgun, 3), [SFX_SHOT_SMG] = SFX(s_smg, 2),
    [SFX_SHOT_RIFLE] = SFX(s_rifle, 3),    [SFX_SHOT_ARC] = SFX(s_arc, 3),         [SFX_SHOT_RAY] = SFX(s_ray, 3),
    [SFX_RELOAD] = SFX(s_reload, 1),       [SFX_RELOAD_DONE] = SFX(s_reload_d, 2), [SFX_EMPTY] = SFX(s_empty, 2),
    [SFX_MELEE] = SFX(s_melee, 3),
    [SFX_ENEMY_ATTACK] = SFX(s_eatk, 2),   [SFX_ENEMY_HIT] = SFX(s_ehit, 1),       [SFX_ENEMY_DEATH] = SFX(s_edeath, 2),
    [SFX_SPIT] = SFX(s_spit, 2),           [SFX_TELEPORT] = SFX(s_tele, 2),        [SFX_BRUTE_DEATH] = SFX(s_bdeath, 3),
    [SFX_PLAYER_HURT] = SFX(s_hurt, 5),    [SFX_PLAYER_DOWN] = SFX(s_down, 7),     [SFX_POINTS] = SFX(s_points, 1),
    [SFX_DOOR] = SFX(s_door, 5),           [SFX_DENIED] = SFX(s_denied, 4),        [SFX_POWERUP] = SFX(s_powerup, 5),
    [SFX_PICKUP] = SFX(s_pickup, 4),       [SFX_WAVE_START] = SFX(s_wstart, 6),    [SFX_WAVE_CLEAR] = SFX(s_wclear, 6),
    [SFX_GENERATOR] = SFX(s_gen, 7),       [SFX_PERK] = SFX(s_perk, 5),            [SFX_BUY] = SFX(s_buy, 5),
    [SFX_EXPLOSION] = SFX(s_explode, 6),   [SFX_HEARTBEAT] = SFX(s_heart, 2),      [SFX_MENU_MOVE] = SFX(s_mmove, 4),
    [SFX_MENU_SELECT] = SFX(s_msel, 4),    [SFX_NOTE] = SFX(s_note, 4),
    [SFX_SHOT_FLAME] = SFX(s_flame, 2),    [SFX_SHOT_BLAST] = SFX(s_blast, 3),     [SFX_PAP] = SFX(s_pap, 6),
    [SFX_BOX_TICK] = SFX(s_boxtick, 1),    [SFX_BOX_OPEN] = SFX(s_boxopen, 5),
};

/* ------------------------------------------------------------------ effect engine */
#define MAX_PENDING 10
typedef struct { const SfxVoice *v; s16 t; u8 prio; } Pending;
typedef struct { const SfxVoice *v; u8 t; u8 prio; } Active;

static Pending pending[MAX_PENDING];
static Active act1, act4;
static u8 music_on = 1, sfx_on = 1;

static void ch1_off(void) { REG_SND1CNT_H = 0; }
static void ch4_off(void) { REG_SND4CNT_L = 0; }

static void start_voice(const SfxVoice *v, int prio)
{
    int vol = v->vol;
    if (v->ch == 1) {
        REG_SND1CNT_L = 0;
        REG_SND1CNT_H = (u16)((vol << 12) | (v->env << 8) | (v->duty << 6));
        REG_SND1CNT_X = (u16)(v->x0 | 0x8000);
        act1.v = v; act1.t = 0; act1.prio = (u8)prio;
    } else {
        REG_SND4CNT_L = (u16)((vol << 12) | (v->env << 8));
        REG_SND4CNT_H = (u16)(0x8000 | v->x0);
        act4.v = v; act4.t = 0; act4.prio = (u8)prio;
    }
}

static void update_active(Active *a, int ch)
{
    const SfxVoice *v = a->v;
    if (!v) return;
    a->t++;
    if (a->t >= v->len) {
        if (ch == 1) ch1_off(); else ch4_off();
        a->v = 0;
        return;
    }
    /* linear slide between start and end values (no re-trigger) */
    if (ch == 1) {
        if (v->x0 != v->x1) {
            int x = v->x0 + ((int)(v->x1 - v->x0) * a->t) / v->len;
            REG_SND1CNT_X = (u16)x;
        }
    } else {
        int s0 = v->x0 >> 4, s1 = v->x1 >> 4;
        if (s0 != s1) {
            int s = s0 + ((s1 - s0) * a->t) / v->len;
            REG_SND4CNT_H = (u16)((v->x0 & 15) | (s << 4));   /* bit 15 clear: no restart */
        }
    }
}

void Audio_PlaySfx(int id)
{
    if (!sfx_on || id <= 0 || id >= SFX_COUNT) return;
    const SfxDef *d = &sfx_defs[id];
    for (int i = 0; i < d->n; i++) {
        for (int s = 0; s < MAX_PENDING; s++) {
            if (!pending[s].v) {
                pending[s].v = &d->v[i];
                pending[s].t = (s16)-(d->v[i].delay);
                pending[s].prio = d->prio;
                break;
            }
        }
    }
}

/* ------------------------------------------------------------------ music engine */
static s8 mus_track = -1;
static u8 mus_step;
static u32 mus_acc;
static u8 mus_running;
static u8 tension, tension_t;
static u8 want_music;

static void lead_off(void) { REG_SND2CNT_L = 0; }
static void bass_off(void) { REG_SND3CNT_H = 0; }

static void play_drum(int d)
{
    if (!d || act4.v) return;       /* effects own the noise channel while they play */
    switch (d) {
    case 1: REG_SND4CNT_L = (12 << 12) | (2 << 8); REG_SND4CNT_H = 0x8000 | NZ(11, 0, 3); break;   /* kick */
    case 2: REG_SND4CNT_L = (10 << 12) | (2 << 8); REG_SND4CNT_H = 0x8000 | NZ(6, 0, 2); break;    /* snare */
    case 3: REG_SND4CNT_L = (6 << 12) | (1 << 8);  REG_SND4CNT_H = 0x8000 | NZ(3, 1, 1); break;    /* hat */
    case 4: REG_SND4CNT_L = (6 << 12) | (3 << 8);  REG_SND4CNT_H = 0x8000 | NZ(3, 1, 1); break;    /* open hat */
    case 5: REG_SND4CNT_L = (10 << 12) | (3 << 8); REG_SND4CNT_H = 0x8000 | NZ(9, 0, 3); break;    /* tom */
    }
}

static void music_step(void)
{
    int t = mus_track;
    int n = track_lead[t][mus_step];
    if (n == 0) lead_off();
    else if (n != 255) {
        int vol = (t == TRACK_INTENSE) ? 9 : (t == TRACK_MENU ? 6 : 8);
        int env = (t == TRACK_INTENSE) ? 2 : (t == TRACK_MENU ? 5 : 4);
        REG_SND2CNT_L = (u16)((vol << 12) | (env << 8) | (2 << 6));
        REG_SND2CNT_H = (u16)(note_square[n] | 0x8000);
    }
    n = track_bass[t][mus_step];
    if (n == 0) bass_off();
    else if (n != 255) {
        REG_SND3CNT_H = 0x4000;                      /* 50 % volume */
        REG_SND3CNT_X = (u16)(note_wave[n] | 0x8000);
    }
    play_drum(track_drums[t][mus_step]);
}

static void load_wave(void)
{
    REG_SND3CNT_L = 0x40;                            /* play bank 1, write bank 0 */
    for (int i = 0; i < 4; i++) REG_WAVE_RAM[i] = wave_table[i];
    REG_SND3CNT_L = 0x00;                            /* play bank 0 */
    REG_SND3CNT_L = 0x80;                            /* channel 3 DAC on */
}

void Audio_Init(void)
{
    REG_SNDCNT_X = 0x80;            /* master enable */
    REG_SNDCNT_L = 0xFF77;          /* all four PSG channels left+right, full master volume */
    REG_SNDCNT_H = 0x0002;          /* PSG 100 % */
    load_wave();
    memset(pending, 0, sizeof(pending));
    act1.v = act4.v = 0;
    ch1_off(); ch4_off(); lead_off(); bass_off();
    mus_track = -1;
}

void Audio_Enable(int m, int s)
{
    music_on = (u8)m; sfx_on = (u8)s;
    if (!m) { lead_off(); bass_off(); mus_running = 0; mus_track = -1; }
    if (!s) { ch1_off(); ch4_off(); act1.v = act4.v = 0; for (int i = 0; i < MAX_PENDING; i++) pending[i].v = 0; }
}

void Audio_StopAll(void)
{
    ch1_off(); ch4_off(); lead_off(); bass_off();
    act1.v = act4.v = 0;
    mus_running = 0; mus_track = -1; want_music = MUS_NONE;
}

void Audio_SetMusic(int id)
{
    want_music = (u8)id;
    if (!music_on) return;
    int tr = -1;
    switch (id) {
    case MUS_MENU: tr = TRACK_MENU; break;
    case MUS_GAME: tr = TRACK_GAME; break;
    case MUS_INTENSE: tr = TRACK_INTENSE; break;
    case MUS_GAMEOVER: tr = TRACK_GAMEOVER; break;
    default: break;
    }
    if (tr == mus_track) return;
    if (tr < 0) { lead_off(); bass_off(); mus_running = 0; mus_track = -1; return; }
    int keep = (mus_track == TRACK_GAME && tr == TRACK_INTENSE) || (mus_track == TRACK_INTENSE && tr == TRACK_GAME);
    mus_track = (s8)tr;
    if (!keep) { mus_step = 0; mus_acc = track_step_x256[tr]; }   /* start on the next frame */
    mus_running = 1;
}

void Audio_SetTension(int on)
{
    if (on && !tension) tension_t = 0;
    tension = (u8)on;
}

void Audio_Update(void)
{
    /* ---- effects: start pending voices whose delay has elapsed */
    for (int i = 0; i < MAX_PENDING; i++) {
        Pending *p = &pending[i];
        if (!p->v) continue;
        if (p->t < 0) { p->t++; continue; }
        const SfxVoice *v = p->v;
        Active *a = (v->ch == 1) ? &act1 : &act4;
        if (!a->v || p->prio >= a->prio) start_voice(v, p->prio);
        p->v = 0;
    }
    update_active(&act1, 1);
    update_active(&act4, 4);

    /* ---- low health heartbeat */
    if (tension && sfx_on) {
        if (++tension_t >= 52) { tension_t = 0; Audio_PlaySfx(SFX_HEARTBEAT); }
    }

    /* ---- music */
    if (music_on && mus_running && mus_track >= 0) {
        mus_acc += 256;
        while (mus_acc >= track_step_x256[mus_track]) {
            mus_acc -= track_step_x256[mus_track];
            music_step();
            if (++mus_step >= 64) {
                mus_step = 0;
                if (!track_loop[mus_track]) { mus_running = 0; lead_off(); bass_off(); break; }
            }
        }
    }
}
