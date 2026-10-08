/* video.h - layers, sprites (OAM shadow), HUD text layer, palette helpers */
#ifndef VIDEO_H
#define VIDEO_H
#include "gba.h"
#include "gfx_ids.h"
#include "map.h"

/* sprite sizes: (shape << 2) | size */
#define SZ_8x8    0
#define SZ_16x16  1
#define SZ_32x32  2
#define SZ_16x8   4
#define SZ_32x8   5
#define SZ_32x16  6
#define SZ_8x16   8
#define SZ_16x32  10

#define SPR_HFLIP 1
#define SPR_VFLIP 2

/* HUD palette banks (BG banks 8..15) */
#define HC_WHITE  8
#define HC_YELLOW 9
#define HC_RED    10
#define HC_GREEN  11
#define HC_ORANGE 12
#define HC_CYAN   13
#define HC_GRAY   14
#define HC_VIOLET 15

/* OBJ palette banks */
#define OP_PLAYER   0
#define OP_SHAMBLER 1
#define OP_RUSHER   2
#define OP_SPITTER  3
#define OP_STALKER  4
#define OP_BRUTE    5
#define OP_FX       6
#define OP_MISC     7
#define OP_FLASH    8
#define OP_HURT     9
#define OP_ELITE_SH 10
#define OP_ELITE_RU 11
#define OP_ELITE_BR 12

#define VID_BLEND_NONE  0
#define VID_BLEND_WHITE 1
#define VID_BLEND_BLACK 2

extern u16 hud_map[32 * 32];   /* 4-byte aligned (memcpy32) */
extern u16 mini_tiles[64 * 16];      /* 64 tiles x 8 words (16 halfwords) */
extern u8  mini_dirty;

void Video_Init(void);
void Video_Flush(void);                  /* call right after VBlankIntrWait() */
void Video_VSync(void);                  /* wait + flush */
void Video_SetScroll(int x, int y);
void Video_SetBlend(int mode, int evy);
void Video_Blank(int on);
void Video_SetLights(int on);
void Video_ModeGame(void);               /* BG setup for gameplay (world + minimap) */
void Video_ModeTitle(void);              /* BG setup for title / menus (title bg + logo) */
void Video_ModeMenu(void);               /* menus drawn over a plain dark background */
void Video_LoadWorldMap(void);
void Video_LoadTitleBg(void);
void Video_QueueMapEntry(int x, int y, u16 entry);
void Video_AnimTitle(u32 frame);
void Video_Pal_BG(int bank, const u16 *colors);
void Video_PalCycle(u32 frame, int powered);

/* sprites */
void Spr_Begin(void);
void Spr_Add(int x, int y, int size, int tile, int pal, int prio, int flip) __attribute__((long_call));
int  Spr_Count(void);

/* HUD / text layer (BG0) */
void Hud_Clear(void);
void Hud_Text(int x, int y, const char *s, int pal) __attribute__((long_call));
void Hud_TextC(int y, const char *s, int pal);          /* centred */
void Hud_Num(int x, int y, u32 v, int width, int pal, char pad) __attribute__((long_call));
void Hud_Big(int x, int y, const char *s, int pal);     /* 16x16 glyphs, x/y in tiles */
void Hud_BigC(int y, const char *s, int pal);
void Hud_Bar(int x, int y, int tiles, int value, int maxv, int pal);
void Hud_Box(int x, int y, int w, int h);
void Hud_Tile(int x, int y, int tile, int pal) __attribute__((long_call));

/* minimap pixel buffer */
void Mini_Clear(void);
void Mini_Pixel(int x, int y, int slot);
int  Mini_Get(int x, int y);

#endif
