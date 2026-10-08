#include "video.h"
#include "utils.h"

extern const u16 bg_palette[256];
extern const u16 obj_palette[256];
extern const u32 env_tiles[];
extern const u32 anim_tiles[];
extern const u32 cb1_tiles[];
extern const u32 obj_tiles[];
extern const u16 logo_map[];
extern const u16 map_entries[MAP_W * MAP_H];
extern const u16 title_bg[32 * 32];
extern const u16 title_gear_tiles[3];
extern const u16 title_conv_tile;
extern const u16 lit_warm_palette[16];
extern const u16 lit_cool_palette[16];
extern const u16 lit_base_palette[16];

#define SB_WORLD 24
#define SB_HUD   28
#define SB_MINI  29

EWRAM_BSS u16 hud_map[32 * 32];
EWRAM_BSS u16 mini_tiles[64 * 16];
u8 mini_dirty;
u8 bg_title_loaded;

static ObjAttr oam_shadow[128] ALIGN4;
static int oam_count;
static int scroll_x, scroll_y;
static int blend_mode, blend_evy;

#define MAP_QUEUE 256
static struct { u16 idx; u16 entry; } map_queue[MAP_QUEUE];
static int map_queue_n;

void Video_Blank(int on)
{
    if (on) REG_DISPCNT = DCNT_BLANK;
}

void Video_Init(void)
{
    REG_DISPCNT = DCNT_BLANK;
    memcpy32((void *)MEM_PAL, bg_palette, 256 / 2);
    memcpy32((void *)(MEM_PAL + 0x200), obj_palette, 256 / 2);
    /* env tiles: CB0, interactive tiles come from the generated header */
    memcpy32((void *)TILE_BASE(0), env_tiles, ENV_TILE_COUNT * 8);
    memcpy32((void *)TILE_BASE(1), cb1_tiles, CB1_TILE_WORDS);
    memcpy32((void *)OBJ_TILES, obj_tiles, OBJ_TILE_COUNT * 8);
    memset32((void *)SCR_BASE(SB_WORLD), 0, 4 * 512);
    memset32((void *)SCR_BASE(SB_HUD), 0, 512);
    memset32((void *)SCR_BASE(SB_MINI), 0, 512);
    Mini_Clear();
    Hud_Clear();
    REG_BG0CNT = BG_PRIO(0) | BG_CBB(1) | BG_SBB(SB_HUD) | BG_4BPP | BG_REG_32x32;
    REG_BG1CNT = BG_PRIO(2) | BG_CBB(0) | BG_SBB(SB_WORLD) | BG_4BPP | BG_REG_64x64;
    REG_BG2CNT = BG_PRIO(1) | BG_CBB(1) | BG_SBB(SB_MINI) | BG_4BPP | BG_REG_32x32;
    REG_BG0HOFS = REG_BG0VOFS = 0;
    REG_BG2HOFS = REG_BG2VOFS = 0;
    for (int i = 0; i < 128; i++) oam_shadow[i].a0 = A0_HIDE;
    oam_count = 0;
    map_queue_n = 0;
    REG_IME = 0;
    REG_DISPSTAT = DSTAT_VBL_IRQ;
    REG_IE = IRQ_VBLANK;
    REG_IME = 1;
    REG_DISPCNT = DCNT_MODE0 | DCNT_OBJ_1D | DCNT_BG0 | DCNT_BG1 | DCNT_OBJ;
}

void Video_Pal_BG(int bank, const u16 *colors)
{
    for (int i = 0; i < 16; i++) PAL_BG[bank * 16 + i] = colors[i];
}

void Video_SetLights(int on)
{
    /* banks 5 (warm light pools) and 7 (cool) mirror bank 0 while the power is off */
    if (on) {
        Video_Pal_BG(5, lit_warm_palette);
        Video_Pal_BG(7, lit_cool_palette);
    } else {
        Video_Pal_BG(5, lit_base_palette);
        Video_Pal_BG(7, lit_base_palette);
    }
}

void Video_LoadWorldMap(void)
{
    bg_title_loaded = 0;
    REG_DISPCNT |= DCNT_BLANK;
    for (int y = 0; y < MAP_H; y++) {
        for (int x = 0; x < MAP_W; x++) {
            int sb = ((y >> 5) << 1) + (x >> 5);
            SCR_BASE(SB_WORLD + sb)[((y & 31) << 5) + (x & 31)] = map_entries[y * MAP_W + x];
        }
    }
    REG_DISPCNT &= ~DCNT_BLANK;
}

void Video_LoadTitleBg(void)
{
    bg_title_loaded = 1;
    REG_DISPCNT |= DCNT_BLANK;
    memset32((void *)SCR_BASE(SB_WORLD), 0, 4 * 512);
    memcpy32((void *)SCR_BASE(SB_WORLD), title_bg, 512);
    /* logo into BG2 (map entries are tile indices relative to CB1_LOGO, bank 1) */
    memset32((void *)SCR_BASE(SB_MINI), 0, 512);
    for (int y = 0; y < LOGO_H; y++)
        for (int x = 0; x < LOGO_W; x++)
            SCR_BASE(SB_MINI)[(y + 4) * 32 + x + 1] = (CB1_LOGO + logo_map[y * LOGO_W + x]) | (1 << 12);
    REG_DISPCNT &= ~DCNT_BLANK;
}

void Video_ModeGame(void)
{
    /* BG2 = minimap: 8x8 tiles (64x64 px) in the top-right corner of the screen */
    memset32((void *)SCR_BASE(SB_MINI), 0, 512);
    for (int ty = 0; ty < 8; ty++)
        for (int tx = 0; tx < 8; tx++)
            SCR_BASE(SB_MINI)[ty * 32 + 22 + tx] = (u16)((CB1_MINI + ty * 8 + tx) | (6 << 12));
    mini_dirty = 1;
    REG_BG2CNT = BG_PRIO(0) | BG_CBB(1) | BG_SBB(SB_MINI) | BG_4BPP | BG_REG_32x32;
    REG_DISPCNT = DCNT_MODE0 | DCNT_OBJ_1D | DCNT_BG0 | DCNT_BG1 | DCNT_BG2 | DCNT_OBJ;
}

void Video_ModeTitle(void)
{
    REG_BG2CNT = BG_PRIO(1) | BG_CBB(1) | BG_SBB(SB_MINI) | BG_4BPP | BG_REG_32x32;
    REG_DISPCNT = DCNT_MODE0 | DCNT_OBJ_1D | DCNT_BG0 | DCNT_BG1 | DCNT_BG2 | DCNT_OBJ;
}

void Video_ModeMenu(void)
{
    REG_DISPCNT = DCNT_MODE0 | DCNT_OBJ_1D | DCNT_BG0 | DCNT_BG1 | DCNT_OBJ;
}

void Video_SetScroll(int x, int y) { scroll_x = x; scroll_y = y; }

void Video_SetBlend(int mode, int evy)
{
    blend_mode = mode;
    blend_evy = evy;
}

void Video_QueueMapEntry(int x, int y, u16 entry)
{
    if (map_queue_n < MAP_QUEUE) {
        map_queue[map_queue_n].idx = (u16)(y * MAP_W + x);
        map_queue[map_queue_n].entry = entry;
        map_queue_n++;
    }
}

void Video_Flush(void)
{
    /* everything that touches VRAM/OAM/palette happens here, in VBlank */
    for (int i = oam_count; i < 128; i++) oam_shadow[i].a0 = A0_HIDE;
    memcpy32((void *)OAM_MEM, oam_shadow, 256);
    memcpy32((void *)SCR_BASE(SB_HUD), hud_map, 512);
    if (mini_dirty) {
        memcpy32((void *)(MEM_VRAM + 0x4000 + CB1_MINI * 32), mini_tiles, 64 * 8);
        mini_dirty = 0;
    }
    for (int i = 0; i < map_queue_n; i++) {
        int idx = map_queue[i].idx;
        int x = idx & 63, y = idx >> 6;
        int sb = ((y >> 5) << 1) + (x >> 5);
        SCR_BASE(SB_WORLD + sb)[((y & 31) << 5) + (x & 31)] = map_queue[i].entry;
    }
    map_queue_n = 0;
    REG_BG1HOFS = scroll_x;
    REG_BG1VOFS = scroll_y;
    if (blend_mode == VID_BLEND_NONE || blend_evy <= 0) {
        REG_BLDCNT = 0;
        REG_BLDY = 0;
    } else {
        REG_BLDCNT = BLD_BG1 | BLD_OBJ | BLD_BD | (blend_mode == VID_BLEND_WHITE ? BLD_WHITE : BLD_BLACK);
        REG_BLDY = blend_evy > 16 ? 16 : blend_evy;
    }
}

void Video_VSync(void)
{
    VBlankIntrWait();
    Video_Flush();
}

/* ------------------------------------------------------------------ sprites */
void Spr_Begin(void) { oam_count = 0; }

IWRAM_CODE void Spr_Add(int x, int y, int size, int tile, int pal, int prio, int flip)
{
    static const u8 w_tab[12] = { 8, 16, 32, 64, 16, 32, 32, 64, 8, 8, 16, 32 };
    static const u8 h_tab[12] = { 8, 16, 32, 64, 8, 8, 16, 32, 16, 32, 32, 64 };
    if (oam_count >= 127) return;
    int w = w_tab[size], h = h_tab[size];
    if (x <= -w || x >= SCREEN_W || y <= -h || y >= SCREEN_H) return;
    ObjAttr *o = &oam_shadow[oam_count++];
    o->a0 = (u16)(A0_Y(y) | (((size >> 2)) << 14));
    o->a1 = (u16)(A1_X(x) | ((size & 3) << 14) | ((flip & SPR_HFLIP) ? A1_HFLIP : 0) | ((flip & SPR_VFLIP) ? A1_VFLIP : 0));
    o->a2 = (u16)(A2_TILE(tile) | A2_PRIO(prio) | A2_PAL(pal));
}

int Spr_Count(void) { return oam_count; }

/* ------------------------------------------------------------------ minimap buffer */
void Mini_Clear(void)
{
    /* every pixel = slot 1 (near-black backdrop) until explored */
    memset32(mini_tiles, 0x11111111u, 64 * 8);
    mini_dirty = 1;
}

void Mini_Pixel(int x, int y, int slot)
{
    if ((u32)x >= 64 || (u32)y >= 64) return;
    int tile = (y >> 3) * 8 + (x >> 3);
    u16 *w = &mini_tiles[tile * 16 + (y & 7) * 2 + ((x & 7) >> 2)];
    int sh = ((x & 3)) * 4;
    *w = (u16)((*w & ~(0xF << sh)) | (slot << sh));
    mini_dirty = 1;
}

int Mini_Get(int x, int y)
{
    if ((u32)x >= 64 || (u32)y >= 64) return 0;
    int tile = (y >> 3) * 8 + (x >> 3);
    u16 w = mini_tiles[tile * 16 + (y & 7) * 2 + ((x & 7) >> 2)];
    return (w >> (((x & 3)) * 4)) & 15;
}

/* ------------------------------------------------------------------ title animation */
void Video_AnimTitle(u32 frame)
{
    /* gears: swap tile data every 6 frames, conveyor every 3 */
    int gf = (frame / 6) & 3;
    for (int g = 0; g < 3; g++) {
        int f = (g == 1) ? (3 - gf) : gf;
        memcpy32((void *)(MEM_VRAM + title_gear_tiles[g] * 32), &anim_tiles[f * 4 * 8], 4 * 8);
    }
    int cf = (frame / 3) & 3;
    memcpy32((void *)(MEM_VRAM + title_conv_tile * 32), &anim_tiles[(16 + cf) * 8], 8);
}

/* palette cycling for blinking LEDs / lamps (BG bank 1 slots 10, 12 and 7) */
void Video_PalCycle(u32 frame, int powered)
{
    static const u16 blue[2] = { RGB15(7, 26, 31), RGB15(2, 10, 14) };
    static const u16 green[2] = { RGB15(15, 31, 7), RGB15(4, 12, 3) };
    int a = (frame >> 4) & 1;
    PAL_BG[16 + 10] = blue[a];
    PAL_BG[16 + 12] = green[a ^ 1];
    (void)powered;
}
