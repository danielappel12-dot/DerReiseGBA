#include "map.h"
#include "video.h"
#include "utils.h"

u8 map_flags[MAP_W * MAP_H] ALIGN4;
u16 areas_open;
u16 doors_opened;
u8 power_on;

void Map_Init(void)
{
    memcpy32(map_flags, map_flags_rom, (MAP_W * MAP_H) / 4);
    areas_open = (1 << AREA_E) | (1 << AREA_C);
    doors_opened = 0;
    power_on = 0;
    Video_LoadWorldMap();
    Video_SetLights(0);
    Mini_Clear();
}

int Map_AreaOpen(int area) { return (areas_open >> area) & 1; }

static void mini_cell(int x, int y)
{
    Mini_Pixel(x, y, map_mini[y * MAP_W + x]);
}

void Map_OpenDoor(int id)
{
    if (doors_opened & (1 << id)) return;
    doors_opened |= 1 << id;
    areas_open |= 1 << map_doors[id].opens;
    for (int i = 0; i < NUM_DOOR_CELLS; i++) {
        const DoorCell *c = &map_door_cells[i];
        if (c->door != id) continue;
        map_flags[c->y * MAP_W + c->x] &= ~(MF_SOLID | MF_DOOR);
        Video_QueueMapEntry(c->x, c->y, c->open);
        if (Mini_Get(c->x, c->y) == 4) Mini_Pixel(c->x, c->y, 2);
    }
}

void Map_SetPower(int on)
{
    power_on = (u8)on;
    for (int i = 0; i < NUM_SWAPS; i++) {
        const PowerSwap *s = &map_swaps[i];
        Video_QueueMapEntry(s->idx & 63, s->idx >> 6, on ? s->on : s->off);
    }
    Video_SetLights(on);
}

void Map_Reveal(int tx, int ty, int r)
{
    for (int y = ty - r; y <= ty + r; y++) {
        if ((u32)y >= MAP_H) continue;
        for (int x = tx - r; x <= tx + r; x++) {
            if ((u32)x >= MAP_W) continue;
            int dx = x - tx, dy = y - ty;
            if (dx * dx + dy * dy > r * r + 1) continue;
            u8 code = map_mini[y * MAP_W + x];
            if (!code) continue;
            if (Mini_Get(x, y) == 1) {
                /* an opened door shows as floor */
                if (code == 4 && !(map_flags[y * MAP_W + x] & MF_DOOR)) code = 2;
                Mini_Pixel(x, y, code);
            }
        }
    }
}

void Map_RevealAll(void)
{
    for (int y = 0; y < MAP_H; y++)
        for (int x = 0; x < MAP_W; x++)
            if (map_mini[y * MAP_W + x]) mini_cell(x, y);
}
