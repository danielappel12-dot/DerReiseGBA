#include "save.h"
#include "utils.h"

/* mGBA / flash carts look for this tag to pick the save type */
const char save_type_tag[] __attribute__((used)) = "SRAM_V113";

#define SAVE_MAGIC 0x4E465353u   /* 'NFSS' */
#define SAVE_VERSION 2

SaveData save;

#define SRAM ((volatile u8 *)MEM_SRAM)

/* SRAM is on the cartridge bus: access it from IWRAM code, byte wide */
IWRAM_CODE static void sram_read(void *dst, int n)
{
    REG_WAITCNT = (REG_WAITCNT & ~3) | 3;     /* SRAM: 8 wait states */
    u8 *d = dst;
    for (int i = 0; i < n; i++) d[i] = SRAM[i];
}

IWRAM_CODE static void sram_write(const void *src, int n)
{
    REG_WAITCNT = (REG_WAITCNT & ~3) | 3;
    const u8 *s = src;
    for (int i = 0; i < n; i++) SRAM[i] = s[i];
}

static u16 checksum(const SaveData *s)
{
    const u8 *b = (const u8 *)s;
    u32 sum = 0x1234;
    for (u32 i = 0; i < sizeof(SaveData) - 2; i++) sum = (sum * 31 + b[i]) & 0xFFFF;
    return (u16)sum;
}

void Save_Defaults(void)
{
    memset(&save, 0, sizeof(save));
    save.magic = SAVE_MAGIC;
    save.version = SAVE_VERSION;
    save.music_on = 1;
    save.sfx_on = 1;
    save.minimap_on = 1;
    save.aim_range = 1;
}

void Save_Load(void)
{
    SaveData tmp;
    sram_read(&tmp, sizeof(tmp));
    if (tmp.magic == SAVE_MAGIC && tmp.version == SAVE_VERSION && tmp.checksum == checksum(&tmp)) {
        save = tmp;
    } else {
        Save_Defaults();
        Save_Save();
    }
}

void Save_Save(void)
{
    save.magic = SAVE_MAGIC;
    save.version = SAVE_VERSION;
    save.checksum = checksum(&save);
    sram_write(&save, sizeof(save));
}

void Save_Clear(void)
{
    Save_Defaults();
    Save_Save();
}
