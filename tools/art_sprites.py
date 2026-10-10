"""art_sprites.py - procedural character / fx sprites (all original).

Character sprites are 16x32 (hardware size 16x32) with the figure occupying the
top 26 rows.  The feet contact row is SPR_FEET_Y (25).  Colours are palette
indices: bank*16 + slot (see palettes.py for slot meaning).
"""
import math
import random
from pix import Canvas

FEET_Y = 25


def C(bank, slot):
    return bank * 16 + slot


def finish(c, outline_slot=1, bank=0):
    c.outline(C(bank, outline_slot))
    return c


# characters (player, zombies, brute, corpses) live in art_chars.py
from art_chars import (player, player_dead, shambler, rusher, spitter, stalker,  # noqa: E402,F401
                       zombie_corpse, brute, brute_corpse)


# ---------------------------------------------------------------------------
# FX / pickups / misc small sprites (bank 6 = FX, bank 7 = misc)
# ---------------------------------------------------------------------------
def fx8():
    """returns ordered list of (name, 8x8 canvas)"""
    out = []
    b = 6

    def add(name, c):
        out.append((name, c))

    # bullets
    c = Canvas(8, 8); c.rect(3, 3, 2, 2, C(b, 2)); c.px(3, 3, C(b, 11)); add('BULLET', c)
    c = Canvas(8, 8); c.rect(2, 2, 4, 4, C(b, 3)); c.rect(3, 3, 2, 2, C(b, 2)); c.outline(C(b, 4)); add('BULLET_BIG', c)
    c = Canvas(8, 8); c.rect(3, 3, 2, 2, C(b, 8)); c.px(3, 3, C(b, 11)); c.outline(C(b, 7)); add('BULLET_ARC', c)
    c = Canvas(8, 8); c.ellipse(4, 4, 3, 3, C(b, 9)); c.px(3, 3, C(b, 11)); c.outline(C(b, 10)); add('SPIT_0', c)
    c = Canvas(8, 8); c.ellipse(4, 4, 2.4, 2.4, C(b, 9)); c.px(4, 3, C(b, 11)); c.outline(C(b, 10)); add('SPIT_1', c)
    c = Canvas(8, 8); c.rect(2, 3, 4, 2, C(b, 8)); c.rect(1, 3, 6, 2, C(b, 8)); c.hline(1, 3, 6, C(b, 11)); c.outline(C(b, 7)); add('RAY', c)
    # particles: blood (3 frames)
    for i, r in enumerate([1, 1.5, 1]):
        c = Canvas(8, 8)
        if i == 0:
            c.px(3, 3, C(b, 5)); c.px(4, 4, C(b, 5)); c.px(3, 4, C(b, 6))
        elif i == 1:
            c.px(2, 2, C(b, 5)); c.px(5, 3, C(b, 5)); c.px(3, 5, C(b, 6)); c.px(4, 4, C(b, 5))
        else:
            c.px(1, 1, C(b, 6)); c.px(6, 2, C(b, 5)); c.px(2, 6, C(b, 6)); c.px(5, 6, C(b, 5))
        add('BLOOD_%d' % i, c)
    # impact sparks (3 frames)
    for i in range(3):
        c = Canvas(8, 8)
        if i == 0:
            c.px(4, 4, C(b, 2)); c.px(3, 3, C(b, 3)); c.px(5, 5, C(b, 3)); c.px(3, 5, C(b, 3)); c.px(5, 3, C(b, 3))
        elif i == 1:
            for (x, y) in [(2, 2), (6, 2), (2, 6), (6, 6), (4, 1), (1, 4)]:
                c.px(x, y, C(b, 3))
            c.px(4, 4, C(b, 2))
        else:
            for (x, y) in [(1, 1), (7, 1), (1, 7), (7, 7)]:
                c.px(x, y, C(b, 4))
        add('SPARK_%d' % i, c)
    # smoke puff
    for i in range(3):
        c = Canvas(8, 8)
        r = 1.2 + i * 0.9
        c.ellipse(4, 4, r, r, C(b, 12 if i < 2 else 13))
        add('PUFF_%d' % i, c)
    # arc node / electric
    for i in range(2):
        c = Canvas(8, 8)
        pts = [(1, 4), (3, 2 + i * 3), (5, 5 - i * 3), (7, 3)]
        for p, q in zip(pts, pts[1:]):
            c.line(p[0], p[1], q[0], q[1], C(b, 8))
        c.px(3, 2 + i * 3, C(b, 11))
        add('ARC_%d' % i, c)
    # objective pointer arrows (yellow): right, down-right, down; other directions are flips
    Y, YD = C(b, 15), C(b, 4)
    c = Canvas(8, 8)
    c.rect(0, 3, 4, 2, Y)
    for i in range(3):
        c.vline(4 + i, 1 + i, 6 - 2 * i, Y)
    c.hline(0, 4, 4, YD)
    c.outline(C(b, 1)); add('ARROW_R', c)
    c = Canvas(8, 8)
    for i in range(6):
        c.px(i, i, Y); c.px(i + 1, i, Y); c.px(i, i + 1, YD)
    for y in range(8):
        for x in range(8):
            if x + y >= 10:
                c.px(x, y, Y)
    c.outline(C(b, 1)); add('ARROW_DR', c)
    c = Canvas(8, 8)
    c.rect(3, 0, 2, 4, Y)
    for i in range(3):
        c.hline(1 + i, 4 + i, 6 - 2 * i, Y)
    c.vline(4, 0, 4, YD)
    c.outline(C(b, 1)); add('ARROW_D', c)
    c = Canvas(8, 8); c.rect(1, 1, 6, 6, C(b, 15)); c.rect(2, 2, 4, 4, C(b, 2)); c.outline(C(b, 5)); add('MINIGEN', c)
    # explosive rocket + flame particles
    c = Canvas(8, 8); c.rect(2, 3, 4, 2, C(b, 12)); c.rect(5, 3, 2, 2, C(b, 5)); c.px(1, 3, C(b, 4)); c.px(0, 4, C(b, 3)); c.px(1, 4, C(b, 4)); c.outline(C(b, 1)); add('ROCKET', c)
    c = Canvas(8, 8); c.ellipse(4, 4, 2.4, 2.4, C(b, 4)); c.ellipse(4, 4, 1.4, 1.4, C(b, 3)); c.px(4, 4, C(b, 2)); add('FLAME_0', c)
    c = Canvas(8, 8); c.ellipse(4, 4, 3.2, 3.0, C(b, 5)); c.ellipse(4, 4, 2.2, 2.0, C(b, 4)); c.ellipse(4, 4, 1.2, 1.2, C(b, 3)); add('FLAME_1', c)
    # aim reticle
    c = Canvas(8, 8)
    for (x, y) in [(0, 3), (0, 4), (7, 3), (7, 4), (3, 0), (4, 0), (3, 7), (4, 7)]:
        c.px(x, y, C(b, 3))
    c.px(3, 3, C(b, 5)); c.px(4, 4, C(b, 5))
    add('RETICLE', c)
    # minimap player dot (bank 7)
    c = Canvas(8, 8); c.rect(3, 3, 2, 2, C(7, 12)); c.outline(C(7, 10)); add('MINIDOT', c)
    # damage arrows (4 directions) bank 6 red
    for name in ('DMG_U', 'DMG_D', 'DMG_L', 'DMG_R'):
        c = Canvas(8, 8)
        if name == 'DMG_U':
            c.rect(3, 1, 2, 6, C(b, 5)); c.rect(2, 2, 4, 1, C(b, 5)); c.px(3, 0, C(b, 5)); c.px(4, 0, C(b, 5))
        elif name == 'DMG_D':
            c.rect(3, 1, 2, 6, C(b, 5)); c.rect(2, 5, 4, 1, C(b, 5)); c.px(3, 7, C(b, 5)); c.px(4, 7, C(b, 5))
        elif name == 'DMG_L':
            c.rect(1, 3, 6, 2, C(b, 5)); c.rect(2, 2, 1, 4, C(b, 5)); c.px(0, 3, C(b, 5)); c.px(0, 4, C(b, 5))
        else:
            c.rect(1, 3, 6, 2, C(b, 5)); c.rect(5, 2, 1, 4, C(b, 5)); c.px(7, 3, C(b, 5)); c.px(7, 4, C(b, 5))
        c.outline(C(b, 6))
        add(name, c)
    return out


def fx16():
    out = []
    b = 6

    def add(name, c):
        out.append((name, c))

    # muzzle flashes
    c = Canvas(16, 16)
    c.ellipse(8, 8, 3.2, 3.2, C(b, 3)); c.ellipse(8, 8, 2, 2, C(b, 2)); c.px(8, 8, C(b, 11))
    c.line(8, 2, 8, 14, C(b, 3)); c.line(2, 8, 14, 8, C(b, 3))
    add('MUZZLE_0', c)
    c = Canvas(16, 16)
    c.ellipse(8, 8, 2.2, 2.2, C(b, 3)); c.px(8, 8, C(b, 2)); c.px(8, 8, C(b, 11))
    c.line(5, 5, 11, 11, C(b, 4)); c.line(11, 5, 5, 11, C(b, 4))
    add('MUZZLE_1', c)
    # explosion (4 frames)
    for i, (r, cc) in enumerate([(3, 3), (5, 3), (6.8, 4), (7.5, 12)]):
        c = Canvas(16, 16)
        c.ellipse(8, 8, r, r, C(b, cc))
        if i < 3:
            c.ellipse(8, 8, r * 0.6, r * 0.6, C(b, 2))
            c.ellipse(8, 8, r * 0.3, r * 0.3, C(b, 11))
        else:
            c.ellipse(8, 8, r * 0.7, r * 0.7, C(b, 13))
            c.noise(0, 0, 16, 16, [0], 0.0)
            for (x, y) in [(2, 3), (13, 4), (3, 12), (12, 13), (8, 1), (1, 8), (14, 8)]:
                c.px(x, y, C(b, 4))
        add('EXPLODE_%d' % i, c)
    # melee slash (3)
    for i in range(3):
        c = Canvas(16, 16)
        ang0 = -1.2 + i * 0.7
        for t in range(14):
            a = ang0 + t * 0.12
            x = 8 + math.cos(a) * (6 + i)
            y = 8 + math.sin(a) * (6 + i)
            c.px(int(x), int(y), C(b, 11)); c.px(int(x), int(y) + 1, C(b, 12))
        add('SLASH_%d' % i, c)
    # shadow (bank 6 slot 14 dither) as 16x16? use 16x8 sheet below
    # pickups (bank 7): ammo, overdrive, double, restore, clearout
    bm = 7
    # ammo cache: crate with bullets
    c = Canvas(16, 16)
    c.rect(2, 4, 12, 10, C(bm, 4)); c.frame(2, 4, 12, 10, C(bm, 5)); c.hline(3, 5, 10, C(bm, 4)); c.hline(2, 8, 12, C(bm, 5))
    for x in (4, 7, 10):
        c.rect(x, 2, 2, 5, C(bm, 2)); c.px(x, 2, C(bm, 12))
    c.rect(3, 9, 10, 3, C(bm, 14)); c.hline(4, 10, 8, C(bm, 4))
    add('PU_AMMO', finish(c, 1, bm))
    # overdrive: lightning bolt in orange disc
    c = Canvas(16, 16)
    c.ellipse(8, 8, 6.4, 6.4, C(bm, 3)); c.ellipse(8, 8, 5.2, 5.2, C(bm, 2))
    for (x1, y1, x2, y2) in [(9, 3, 5, 9), (5, 9, 8, 9), (8, 9, 6, 14)]:
        c.line(x1, y1, x2, y2, C(bm, 12)); c.line(x1 + 1, y1, x2 + 1, y2, C(bm, 4))
    add('PU_OVERDRIVE', finish(c, 1, bm))
    # double score: coin 2x
    c = Canvas(16, 16)
    c.ellipse(8, 8, 6.4, 6.4, C(bm, 5)); c.ellipse(8, 8, 5.2, 5.2, C(bm, 4)); c.px(5, 5, C(bm, 12)); c.px(6, 4, C(bm, 12))
    c.hline(5, 6, 3, C(bm, 5)); c.px(7, 7, C(bm, 5)); c.px(6, 8, C(bm, 5)); c.hline(5, 9, 4, C(bm, 5))
    c.px(10, 6, C(bm, 5)); c.px(10, 9, C(bm, 5)); c.hline(10, 7, 1, C(bm, 5)); c.vline(11, 6, 4, C(bm, 5))
    add('PU_DOUBLE', finish(c, 1, bm))
    # full restore: medkit / heart
    c = Canvas(16, 16)
    c.rect(2, 4, 12, 9, C(bm, 12)); c.frame(2, 4, 12, 9, C(bm, 13)); c.rect(6, 5, 4, 7, C(bm, 10)); c.rect(4, 7, 8, 3, C(bm, 10))
    c.rect(6, 2, 4, 2, C(bm, 13))
    add('PU_RESTORE', finish(c, 1, bm))
    # nuke: radiation trefoil on a yellow disc
    c = Canvas(16, 16)
    c.ellipse(8, 8, 6.6, 6.6, C(bm, 4)); c.ellipse(8, 8, 5.6, 5.6, C(bm, 4))
    for y in range(16):
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            d = math.hypot(dx, dy)
            if 2.2 < d < 5.6:
                ang = (math.degrees(math.atan2(dy, dx)) + 90) % 120
                if ang < 60:
                    c.px(x, y, C(bm, 15))
            if d <= 1.6:
                c.px(x, y, C(bm, 15))
    add('PU_NUKE', finish(c, 1, bm))
    # insta kill: red skull
    c = Canvas(16, 16)
    c.ellipse(8, 8, 6.6, 6.6, C(bm, 11)); c.ellipse(8, 8, 5.4, 5.4, C(bm, 10))
    c.ellipse(8, 7, 3.2, 3.0, C(bm, 12)); c.rect(6, 9, 5, 3, C(bm, 12))
    c.rect(6, 6, 2, 2, C(bm, 15)); c.rect(9, 6, 2, 2, C(bm, 15)); c.px(8, 9, C(bm, 15))
    c.px(7, 11, C(bm, 15)); c.px(9, 11, C(bm, 15))
    add('PU_INSTA', finish(c, 1, bm))
    for i, icon in enumerate(weapon_icons()):
        add('WICON_%d' % i, icon)
    # perk gems, one colour per perk (IRON HEART red, QUICK HANDS yellow, STEADY AIM cyan, SECOND WIND green, FIELD MEDIC orange)
    for nm, main, dark in (('IRON', 10, 11), ('QUICK', 4, 5), ('STEADY', 6, 7), ('SECOND', 8, 9), ('FIELD', 2, 3)):
        c = Canvas(16, 16)
        for y in range(16):
            half = 7 - abs(y - 7) if y <= 7 else 7 - abs(y - 8)
            half = max(0, min(6, half))
            for x in range(8 - half, 8 + half):
                c.px(x, y, C(bm, main) if (x + y) % 5 else C(bm, 12))
        for y in range(8, 15):
            half = 14 - y
            for x in range(8 - half, 8 + half):
                if x >= 8:
                    c.px(x, y, C(bm, dark))
        c.px(6, 4, C(bm, 12)); c.px(7, 3, C(bm, 12)); c.px(5, 5, C(bm, 12))
        c = finish(c, 1, bm)
        c.px(2, 1, C(bm, 12)); c.px(1, 2, C(bm, 12)); c.px(2, 2, C(bm, 12)); c.px(3, 2, C(bm, 12)); c.px(2, 3, C(bm, 12))
        add('PERK_ICON_' + nm, c)
    # corpses are produced elsewhere
    return out


def shadow16x8():
    b = 6
    c = Canvas(16, 8)
    for y in range(8):
        for x in range(16):
            dx, dy = (x + 0.5 - 8) / 7.5, (y + 0.5 - 4) / 3.5
            if dx * dx + dy * dy <= 1.0 and ((x + y) & 1) == 0 or (dx * dx + dy * dy <= 0.45):
                c.px(x, y, C(b, 14))
    return c


def shadow_big():
    b = 6
    c = Canvas(32, 8)
    for y in range(8):
        for x in range(32):
            dx, dy = (x + 0.5 - 16) / 15.5, (y + 0.5 - 4) / 3.5
            if dx * dx + dy * dy <= 1.0 and ((x + y) & 1) == 0 or (dx * dx + dy * dy <= 0.45):
                c.px(x, y, C(b, 14))
    return c


def weapon_icons():
    """13 weapon silhouettes, 16x16, bank 7 (misc): 13 light, 14 mid, 15 dark, 4 yellow, 6 cyan, 8 green, 2 orange, 10 red"""
    bm = 7
    L, M, D = C(bm, 13), C(bm, 14), C(bm, 15)
    out = []

    def mk(fn):
        c = Canvas(16, 16)
        fn(c)
        out.append(finish(c, 1, bm))

    def pistol(c):
        c.rect(3, 5, 9, 3, L); c.rect(3, 8, 3, 4, M); c.rect(10, 5, 3, 1, D); c.px(12, 5, C(bm, 12))
    def shotgun(c):
        c.rect(1, 6, 13, 2, L); c.rect(1, 8, 9, 1, M); c.rect(8, 8, 3, 2, M); c.rect(1, 5, 4, 5, D); c.hline(5, 5, 8, M)
    def smg(c):
        c.rect(2, 5, 11, 3, L); c.rect(12, 6, 3, 1, M); c.rect(5, 8, 2, 5, M); c.rect(2, 8, 2, 3, D); c.px(9, 4, M)
    def rifle(c):
        c.rect(0, 6, 15, 2, L); c.rect(4, 4, 6, 2, M); c.rect(0, 8, 4, 3, D); c.rect(6, 8, 2, 3, M); c.px(7, 3, C(bm, 4))
    def arc(c):
        c.rect(2, 6, 11, 4, M); c.rect(12, 7, 3, 2, L)
        for x in (4, 7, 10):
            c.vline(x, 5, 6, C(bm, 6))
        c.px(14, 6, C(bm, 12)); c.px(14, 9, C(bm, 12)); c.rect(2, 10, 3, 3, D)
    def ray(c):
        c.rect(2, 6, 9, 4, L); c.rect(10, 7, 5, 2, C(bm, 8)); c.px(14, 7, C(bm, 12)); c.rect(4, 7, 4, 2, C(bm, 9)); c.rect(3, 10, 3, 3, D)
    def cannon(c):
        c.rect(5, 4, 9, 3, L); c.ellipse(6.5, 8, 3, 3, M); c.ellipse(6.5, 8, 1.2, 1.2, D); c.rect(3, 9, 3, 5, D); c.rect(13, 4, 2, 1, M)
    def twin(c):
        c.rect(1, 2, 9, 3, L); c.rect(1, 5, 3, 3, M); c.rect(6, 8, 9, 3, L); c.rect(6, 11, 3, 3, M); c.px(9, 2, C(bm, 12)); c.px(14, 8, C(bm, 12))
    def buzz(c):
        for y in (4, 7, 10):
            c.rect(6, y, 9, 2, L)
        c.rect(1, 3, 6, 10, M); c.ellipse(4, 8, 2.2, 2.2, D); c.px(4, 8, C(bm, 4))
    def blast(c):
        c.rect(1, 5, 11, 5, M); c.rect(1, 5, 11, 1, L); c.rect(12, 6, 3, 3, C(bm, 10)); c.px(14, 7, C(bm, 4)); c.rect(3, 10, 2, 4, D)
    def flame(c):
        c.rect(1, 6, 9, 3, L); c.rect(9, 7, 3, 1, D); c.rect(2, 9, 5, 4, M)
        c.ellipse(13, 7.5, 2.2, 2.0, C(bm, 2)); c.ellipse(13.5, 7.5, 1.2, 1.2, C(bm, 4))
    def bounce(c):
        c.rect(2, 8, 8, 3, L); c.rect(2, 11, 3, 3, D)
        for (x1, y1, x2, y2) in [(10, 8, 13, 3), (13, 3, 15, 6)]:
            c.line(x1, y1, x2, y2, C(bm, 4))
        c.px(10, 9, C(bm, 4)); c.px(14, 6, C(bm, 12))
    def sniper(c):
        c.rect(0, 7, 15, 2, L); c.rect(4, 4, 6, 2, C(bm, 6)); c.hline(5, 3, 4, M); c.rect(0, 9, 4, 3, D); c.rect(7, 9, 2, 3, M)
    for fn in (pistol, shotgun, smg, rifle, arc, ray, cannon, twin, buzz, blast, flame, bounce, sniper):
        mk(fn)
    return out
