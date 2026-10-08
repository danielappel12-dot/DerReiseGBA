#include "game.h"

const PerkDef perk_defs[5] = {
    { "IRON HEART",  "MORE HEALTH",       "IH" },
    { "QUICK HANDS", "FASTER RELOAD",     "QH" },
    { "STEADY AIM",  "LESS SPREAD",       "SA" },
    { "SECOND WIND", "MOVE FASTER",       "SW" },
    { "FIELD MEDIC", "HEAL SOONER",       "FM" },
};

int Perk_Buy(int perk)
{
    if (player.perks & (1 << perk)) return 0;
    Player_ApplyPerk(perk);
    return 1;
}
