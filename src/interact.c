#include "game.h"

u8 interact_progress;
static u8 locked;
static int hold_frames;

void Interact_Reset(void)
{
    interact_progress = 0;
    locked = 0;
    hold_frames = 0;
}

int Interact_Find(int px, int py)
{
    for (int i = 0; i < NUM_INTERACTS; i++) {
        const Interact *z = &map_interacts[i];
        if (px < z->x || px >= z->x + z->w || py < z->y || py >= z->y + z->h) continue;
        if (z->kind == IK_DOOR && (doors_opened & (1 << z->id))) continue;
        if (z->kind == IK_GEN && power_on) continue;
        return i;
    }
    return -1;
}

static void deny(const char *l1, const char *l2)
{
    Hud_Message(l1, l2, HC_RED, 100);
    Audio_PlaySfx(SFX_DENIED);
}

static void activate(int zone)
{
    const Interact *z = &map_interacts[zone];
    switch (z->kind) {
    case IK_DOOR: {
        const DoorDef *d = &map_doors[z->id];
        if (d->power && !power_on) { deny("POWER REQUIRED", "ACTIVATE THE GENERATOR"); return; }
        if (G.score < d->cost) { deny("NOT ENOUGH POINTS", d->name); return; }
        G.score -= d->cost;
        Map_OpenDoor(z->id);
        Audio_PlaySfx(SFX_DOOR);
        Fx_Shake(4);
        Hud_Message("DOOR OPENED", d->name, HC_GREEN, 110);
        break;
    }
    case IK_GEN:
        Map_SetPower(1);
        Audio_PlaySfx(SFX_GENERATOR);
        Fx_Shake(8);
        Fx_Flash(8);
        Hud_Message("POWER RESTORED", "LIGHTS AND MACHINES ONLINE", HC_CYAN, 180);
        break;
    case IK_PERK: {
        if (!power_on) { deny("POWER REQUIRED", "ACTIVATE THE GENERATOR"); return; }
        if (player.perks & (1 << z->id)) { deny("ALREADY OWNED", perk_defs[z->id].name); return; }
        if (G.score < z->cost) { deny("NOT ENOUGH POINTS", perk_defs[z->id].name); return; }
        G.score -= z->cost;
        Perk_Buy(z->id);
        Audio_PlaySfx(SFX_PERK);
        Hud_Message(perk_defs[z->id].name, perk_defs[z->id].desc, HC_YELLOW, 140);
        break;
    }
    case IK_WEAPON: {
        int owned = (player.wpn[0].id == z->id) || (player.wpn[1].id == z->id);
        int price = owned ? Weapon_AmmoPrice(z->id) : z->cost;
        if (z->id >= W_ARC && !power_on) { deny("POWER REQUIRED", "ACTIVATE THE GENERATOR"); return; }
        if (G.score < (u32)price) { deny("NOT ENOUGH POINTS", weapon_defs[z->id].name); return; }
        G.score -= price;
        Weapon_Give(&player, z->id);
        Audio_PlaySfx(SFX_BUY);
        Hud_Message(weapon_defs[z->id].name, owned ? "AMMO REFILLED" : "ACQUIRED", HC_YELLOW, 120);
        break;
    }
    case IK_NOTE:
        Hud_Message(map_notes[z->id], 0, HC_WHITE, 360);
        Audio_PlaySfx(SFX_NOTE);
        break;
    case IK_BOX:
        Box_Use();
        break;
    case IK_PAP: {
        WeaponSlot *s = &player.wpn[player.cur];
        if (!power_on) { deny("POWER REQUIRED", "ACTIVATE THE GENERATOR"); return; }
        if (s->pap) { deny("ALREADY UPGRADED", weapon_defs[s->id].name); return; }
        if (G.score < z->cost) { deny("NOT ENOUGH POINTS", "PACK-A-PUNCH"); return; }
        G.score -= z->cost;
        Weapon_Punch(&player);
        Audio_PlaySfx(SFX_PAP);
        Fx_Flash(10);
        Fx_Shake(8);
        Hud_Message("PACK-A-PUNCH", weapon_defs[s->id].name, HC_CYAN, 150);
        break;
    }
    }
}

void Interact_Hold(int zone)
{
    if (locked) return;
    const Interact *z = &map_interacts[zone];
    if (z->kind == IK_BOX && Box_State() == BOX_ROLLING) return;
    hold_frames = (z->kind == IK_GEN) ? 90 : (z->kind == IK_NOTE ? 10 : (z->kind == IK_BOX ? 16 : 28));
    int add = (100 + hold_frames - 1) / hold_frames;
    int p = interact_progress + add;
    if (p >= 100) {
        interact_progress = 0;
        locked = 1;
        activate(zone);
    } else {
        interact_progress = (u8)p;
    }
}

void Interact_Release(void)
{
    interact_progress = 0;
    locked = 0;
}

void Interact_Draw(int zone)
{
    if (zone < 0) return;
    const Interact *z = &map_interacts[zone];
    char buf[20];
    const char *l1 = "HOLD B  USE", *l2 = "";
    int c1 = HC_YELLOW, cost = z->cost, c3 = HC_GREEN;
    int need_power = 0;
    switch (z->kind) {
    case IK_DOOR: {
        const DoorDef *d = &map_doors[z->id];
        l1 = "HOLD B  OPEN"; l2 = d->name; cost = d->cost; need_power = d->power && !power_on;
        break;
    }
    case IK_GEN:
        l1 = "HOLD B  ACTIVATE"; l2 = "GENERATOR"; cost = 0;
        break;
    case IK_PERK:
        l1 = (player.perks & (1 << z->id)) ? "OWNED" : "HOLD B  BUY";
        l2 = perk_defs[z->id].name; need_power = !power_on;
        break;
    case IK_WEAPON: {
        int owned = (player.wpn[0].id == z->id) || (player.wpn[1].id == z->id);
        l1 = owned ? "HOLD B  AMMO" : "HOLD B  BUY";
        l2 = weapon_defs[z->id].name;
        cost = owned ? Weapon_AmmoPrice(z->id) : z->cost;
        need_power = (z->id >= W_ARC) && !power_on;
        break;
    }
    case IK_NOTE:
        l1 = "HOLD B  READ"; l2 = "TERMINAL"; cost = 0;
        break;
    case IK_BOX:
        l2 = "MYSTERY BOX";
        if (Box_State() == BOX_ROLLING) { l1 = "GOOD LUCK..."; cost = 0; c1 = HC_CYAN; }
        else if (Box_State() == BOX_READY) { l1 = "HOLD B  TAKE"; l2 = weapon_defs[Box_Shown()].name; cost = 0; c1 = HC_GREEN; }
        else l1 = "HOLD B  OPEN";
        break;
    case IK_PAP:
        l2 = "PACK-A-PUNCH"; need_power = !power_on;
        if (player.wpn[player.cur].pap) { l1 = "ALREADY UPGRADED"; cost = 0; c1 = HC_GRAY; }
        else l1 = "HOLD B  UPGRADE";
        break;
    }
    if (need_power) { l1 = "POWER REQUIRED"; c1 = HC_RED; }
    Hud_TextC(13, l1, c1);
    Hud_TextC(14, l2, HC_WHITE);
    if (cost > 0) {
        char num[12];
        UInt2Str(num, (u32)cost, 1, '0');
        int n = 0;
        const char *pre = "COST $";
        for (int i = 0; pre[i]; i++) buf[n++] = pre[i];
        for (int i = 0; num[i]; i++) buf[n++] = num[i];
        buf[n] = 0;
        if (G.score < (u32)cost) c3 = HC_RED;
        Hud_TextC(15, buf, c3);
    }
    if (interact_progress) Hud_Bar(11, 16, 8, interact_progress, 100, HC_YELLOW);
}

int Objective_Get(int *wx, int *wy, const char **label, int *cost)
{
    if (power_on) return 0;
    if (!Map_AreaOpen(AREA_G)) {
        /* the generator room is still locked: point at its door (door 1 = GENERATOR ACCESS) */
        const DoorDef *d = &map_doors[1];
        *wx = d->x * 8 + d->w * 4;
        *wy = d->y * 8 + d->h * 4;
        *label = "GEN DOOR";
        *cost = (doors_opened & 2) ? 0 : d->cost;
        return 1;
    }
    for (int i = 0; i < NUM_INTERACTS; i++) {
        const Interact *z = &map_interacts[i];
        if (z->kind != IK_GEN) continue;
        *wx = z->x + z->w / 2;
        *wy = z->y + z->h / 2;
        *label = "GENERATOR";
        *cost = 0;
        return 1;
    }
    return 0;
}
