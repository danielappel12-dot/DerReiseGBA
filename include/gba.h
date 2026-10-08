/* gba.h - minimal Game Boy Advance hardware definitions (no libgba needed). */
#ifndef GBA_H
#define GBA_H

#include <stdint.h>
#include <stddef.h>

typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int8_t   s8;
typedef int16_t  s16;
typedef int32_t  s32;
typedef volatile u8  vu8;
typedef volatile u16 vu16;
typedef volatile u32 vu32;

#define SCREEN_W 240
#define SCREEN_H 160

/* ---- placement attributes ---------------------------------------------- */
#define IWRAM_CODE   __attribute__((section(".iwram.text"), target("arm"), long_call, noinline))
#define IWRAM_DATA   __attribute__((section(".iwram.data")))
#define EWRAM_DATA   __attribute__((section(".ewram")))
#define EWRAM_BSS    __attribute__((section(".ewram_bss")))
#define ALIGN4       __attribute__((aligned(4)))
#define UNUSED       __attribute__((unused))

/* ---- memory map --------------------------------------------------------- */
#define MEM_EWRAM   0x02000000
#define MEM_IWRAM   0x03000000
#define MEM_IO      0x04000000
#define MEM_PAL     0x05000000
#define MEM_VRAM    0x06000000
#define MEM_OAM     0x07000000
#define MEM_ROM     0x08000000
#define MEM_SRAM    0x0E000000

#define REG16(off)  (*(vu16 *)(MEM_IO + (off)))
#define REG32(off)  (*(vu32 *)(MEM_IO + (off)))

/* ---- display ------------------------------------------------------------ */
#define REG_DISPCNT   REG16(0x000)
#define REG_DISPSTAT  REG16(0x004)
#define REG_VCOUNT    REG16(0x006)
#define REG_BG0CNT    REG16(0x008)
#define REG_BG1CNT    REG16(0x00A)
#define REG_BG2CNT    REG16(0x00C)
#define REG_BG3CNT    REG16(0x00E)
#define REG_BG0HOFS   REG16(0x010)
#define REG_BG0VOFS   REG16(0x012)
#define REG_BG1HOFS   REG16(0x014)
#define REG_BG1VOFS   REG16(0x016)
#define REG_BG2HOFS   REG16(0x018)
#define REG_BG2VOFS   REG16(0x01A)
#define REG_BG3HOFS   REG16(0x01C)
#define REG_BG3VOFS   REG16(0x01E)
#define REG_MOSAIC    REG16(0x04C)
#define REG_BLDCNT    REG16(0x050)
#define REG_BLDALPHA  REG16(0x052)
#define REG_BLDY      REG16(0x054)

#define DCNT_MODE0    0x0000
#define DCNT_OBJ_1D   0x0040
#define DCNT_BG0      0x0100
#define DCNT_BG1      0x0200
#define DCNT_BG2      0x0400
#define DCNT_BG3      0x0800
#define DCNT_OBJ      0x1000
#define DCNT_BLANK    0x0080

#define DSTAT_VBL_IRQ 0x0008

#define BG_CBB(n)     ((n) << 2)
#define BG_SBB(n)     ((n) << 8)
#define BG_PRIO(n)    (n)
#define BG_4BPP       0x0000
#define BG_REG_32x32  0x0000
#define BG_REG_64x64  0xC000

#define BLD_BG0   0x0001
#define BLD_BG1   0x0002
#define BLD_BG2   0x0004
#define BLD_BG3   0x0008
#define BLD_OBJ   0x0010
#define BLD_BD    0x0020
#define BLD_ALPHA 0x0040
#define BLD_WHITE 0x0080
#define BLD_BLACK 0x00C0

/* ---- memory areas ------------------------------------------------------- */
#define PAL_BG        ((vu16 *)(MEM_PAL))
#define PAL_OBJ       ((vu16 *)(MEM_PAL + 0x200))
#define TILE_BASE(n)  ((vu16 *)(MEM_VRAM + (n) * 0x4000))
#define SCR_BASE(n)   ((vu16 *)(MEM_VRAM + (n) * 0x800))
#define OBJ_TILES     ((vu16 *)(MEM_VRAM + 0x10000))

#define RGB15(r, g, b) ((u16)((r) | ((g) << 5) | ((b) << 10)))

/* ---- sprites ------------------------------------------------------------ */
typedef struct ObjAttr {
    u16 a0, a1, a2, pad;
} ObjAttr;

#define OAM_MEM ((vu32 *)MEM_OAM)

#define A0_Y(y)        ((y) & 0xFF)
#define A0_HIDE        0x0200
#define A0_ALPHA       0x0400
#define A0_4BPP        0x0000
#define A0_SQUARE      0x0000
#define A0_WIDE        0x4000
#define A0_TALL        0x8000
#define A1_X(x)        ((x) & 0x1FF)
#define A1_HFLIP       0x1000
#define A1_VFLIP       0x2000
#define A1_SIZE(n)     ((n) << 14)
#define A2_TILE(t)     ((t) & 0x3FF)
#define A2_PRIO(p)     ((p) << 10)
#define A2_PAL(p)      ((p) << 12)

/* ---- input -------------------------------------------------------------- */
#define REG_KEYINPUT  REG16(0x130)
#define REG_KEYCNT    REG16(0x132)
#define KEY_A      0x0001
#define KEY_B      0x0002
#define KEY_SELECT 0x0004
#define KEY_START  0x0008
#define KEY_RIGHT  0x0010
#define KEY_LEFT   0x0020
#define KEY_UP     0x0040
#define KEY_DOWN   0x0080
#define KEY_R      0x0100
#define KEY_L      0x0200
#define KEY_DPAD   (KEY_RIGHT | KEY_LEFT | KEY_UP | KEY_DOWN)
#define KEY_ANY    0x03FF

/* ---- interrupts / system ------------------------------------------------- */
#define REG_IE        REG16(0x200)
#define REG_IF        REG16(0x202)
#define REG_WAITCNT   REG16(0x204)
#define REG_IME       REG16(0x208)
#define IRQ_VBLANK    0x0001
#define IRQ_HBLANK    0x0002
#define IRQ_VCOUNT    0x0004

/* ---- timers --------------------------------------------------------------- */
#define REG_TM0CNT_L  REG16(0x100)
#define REG_TM0CNT_H  REG16(0x102)
#define REG_TM1CNT_L  REG16(0x104)
#define REG_TM1CNT_H  REG16(0x106)
#define REG_TM2CNT_L  REG16(0x108)
#define REG_TM2CNT_H  REG16(0x10A)
#define REG_TM3CNT_L  REG16(0x10C)
#define REG_TM3CNT_H  REG16(0x10E)
#define TM_ENABLE     0x0080
#define TM_CASCADE    0x0004
#define TM_FREQ_1024  0x0003

/* ---- DMA ------------------------------------------------------------------ */
#define REG_DMA3SAD   REG32(0x0D4)
#define REG_DMA3DAD   REG32(0x0D8)
#define REG_DMA3CNT   REG32(0x0DC)
#define DMA_ENABLE    0x80000000u
#define DMA_32        0x04000000u
#define DMA_SRC_FIXED 0x01000000u

/* ---- sound (PSG only) ------------------------------------------------------ */
#define REG_SND1CNT_L REG16(0x060)
#define REG_SND1CNT_H REG16(0x062)
#define REG_SND1CNT_X REG16(0x064)
#define REG_SND2CNT_L REG16(0x068)
#define REG_SND2CNT_H REG16(0x06C)
#define REG_SND3CNT_L REG16(0x070)
#define REG_SND3CNT_H REG16(0x072)
#define REG_SND3CNT_X REG16(0x074)
#define REG_SND4CNT_L REG16(0x078)
#define REG_SND4CNT_H REG16(0x07C)
#define REG_SNDCNT_L  REG16(0x080)
#define REG_SNDCNT_H  REG16(0x082)
#define REG_SNDCNT_X  REG16(0x084)
#define REG_WAVE_RAM  ((vu32 *)(MEM_IO + 0x090))

/* ---- helpers -------------------------------------------------------------- */
void VBlankIntrWait(void);
void SoftReset(void);
void memcpy32(void *dst, const void *src, u32 words);
void memset32(void *dst, u32 value, u32 words);

#define VRAM_COPY(dst, src, bytes)  memcpy32((void *)(dst), (const void *)(src), ((bytes) + 3) >> 2)

#endif /* GBA_H */
