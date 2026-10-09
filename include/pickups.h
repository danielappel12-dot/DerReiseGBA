#ifndef PICKUPS_H
#define PICKUPS_H
#include "gba.h"

#define MAX_PICKUPS 12
enum { PU_AMMO, PU_OVERDRIVE, PU_DOUBLE, PU_RESTORE, PU_NUKE, PU_INSTA, PU_COUNT };

typedef struct {
    u8 active, type;
    s16 x, y;
    s16 timer;          /* frames left */
    u8 phase;
    s16 bounce_v;       /* initial pop */
    s16 z;              /* height above ground (1/16 px) */
} Pickup;

extern Pickup pickups[MAX_PICKUPS];
extern const char *const pickup_names[PU_COUNT];

void Pickups_Init(void);
void Pickups_Spawn(int type, int px, int py);
void Pickups_MaybeDrop(int px, int py);
void Pickups_Update(void);
void Pickups_Apply(int type);

#endif
