#ifndef PERKS_H
#define PERKS_H
#include "gba.h"

typedef struct { const char *name; const char *desc; const char *tag; } PerkDef;
extern const PerkDef perk_defs[5];
int Perk_Buy(int perk);        /* applies; returns 0 if already owned */

#endif
