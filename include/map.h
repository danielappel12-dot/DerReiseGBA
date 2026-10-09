/* map.h - BLACKSITE 13: tile flags, doors, power, interaction zones, minimap */
#ifndef MAP_HEADER_H
#define MAP_HEADER_H
#include "gba.h"
#include "map_ids.h"

#ifndef MAP_W
#define MAP_W 64
#define MAP_H 64
#endif

#define MF_SOLID 1
#define MF_DOOR  2

typedef struct { u8 x, y, w, h; u16 cost; u8 power; u8 opens; const char *name; } DoorDef;
typedef struct { u8 door; u8 x; u8 y; u16 closed; u16 open; } DoorCell;
typedef struct { u8 kind; u8 id; u16 cost; s16 x, y, w, h; } Interact;
typedef struct { u16 idx; u16 off; u16 on; } PowerSwap;
typedef struct { u8 x, y, area; } SpawnPoint;

enum { IK_DOOR, IK_GEN, IK_PERK, IK_WEAPON, IK_NOTE, IK_BOX, IK_PAP };

extern const u16 map_entries[MAP_W * MAP_H];
extern const u8 map_flags_rom[MAP_W * MAP_H];
extern const u8 map_area[MAP_W * MAP_H];
extern const u8 map_mini[MAP_W * MAP_H];
extern const DoorDef map_doors[NUM_DOORS];
extern const DoorCell map_door_cells[NUM_DOOR_CELLS];
extern const Interact map_interacts[NUM_INTERACTS];
extern const PowerSwap map_swaps[NUM_SWAPS];
extern const PowerSwap map_box_cells[NUM_BOX_CELLS];   /* off = closed, on = open */
extern const SpawnPoint map_spawns[NUM_SPAWNS];
extern const char *const map_area_names[NUM_AREAS];
extern const char *const map_notes[NUM_NOTES];
extern const u8 map_player_start[2];

extern u8 map_flags[MAP_W * MAP_H];
extern u16 areas_open;       /* bit per area id */
extern u16 doors_opened;     /* bit per door */
extern u8 power_on;

void Map_Init(void);
void Map_OpenDoor(int id);
void Map_SetPower(int on);
int  Map_AreaOpen(int area);
void Map_Reveal(int tx, int ty, int radius);
void Map_RevealAll(void);

static inline int Map_SolidT(int tx, int ty)
{
    if ((u32)tx >= MAP_W || (u32)ty >= MAP_H) return 1;
    return map_flags[ty * MAP_W + tx] & MF_SOLID;
}
static inline int Map_SolidPx(int px, int py) { return Map_SolidT(px >> 3, py >> 3); }

#endif
