"""art_tiles.py - procedural 8x8 tile art for BLACKSITE 13 (all original).

Every tile is drawn with palette *indices* (bank*16 + slot, see palettes.py).
The TileSet registry de-duplicates tiles (by slot data) and hands out ids.
"""
import random
from pix import Canvas


def col(bank, slot):
    return bank * 16 + slot


class TileSet:
    def __init__(self):
        self.canvases = []          # first-seen canvas of each unique tile
        self.banks = []
        self.index = {}
        self.names = {}

    def _bank_of(self, cv):
        """tile palette bank = majority bank; minority-bank pixels are snapped to the nearest
        colour (by RGB distance) of the majority bank, since a tile can use only one bank"""
        from collections import Counter
        cnt = Counter(c >> 4 for row in cv.p for c in row if c)
        if not cnt:
            return 0
        bank = cnt.most_common(1)[0][0]
        if len(cnt) > 1:
            import palettes
            pal = palettes.build_bg_palette().c
            for y in range(cv.h):
                for x in range(cv.w):
                    c = cv.p[y][x]
                    if c and (c >> 4) != bank:
                        r, g, b = pal[c]
                        best = min(range(1, 16), key=lambda s: (pal[bank * 16 + s][0] - r) ** 2 +
                                   (pal[bank * 16 + s][1] - g) ** 2 + (pal[bank * 16 + s][2] - b) ** 2)
                        cv.p[y][x] = bank * 16 + best
        return bank

    @staticmethod
    def _slots(cv):
        return tuple(tuple(c & 15 for c in row) for row in cv.p)

    def add(self, cv, name=None, force_new=False):
        """returns (tile id, natural bank)"""
        assert cv.w == 8 and cv.h == 8
        bank = self._bank_of(cv)
        key = self._slots(cv)
        if not force_new and key in self.index:
            tid = self.index[key]
        else:
            tid = len(self.canvases)
            self.canvases.append(cv.copy())
            self.banks.append(bank)
            self.index[key] = tid
        if name:
            self.names[name] = (tid, bank)
        return tid, bank

    def add_block(self, cv, name=None, force_new=False):
        """split a (8k x 8m) canvas into tiles; returns 2D list [row][col] of (id, bank)"""
        out = []
        for ty in range(cv.h // 8):
            row = []
            for tx in range(cv.w // 8):
                row.append(self.add(cv.sub(tx * 8, ty * 8, 8, 8), force_new=force_new))
            out.append(row)
        if name:
            self.names[name] = out
        return out


def T(fill=0):
    return Canvas(8, 8, fill)


# ---------------------------------------------------------------------------
# floors
# ---------------------------------------------------------------------------
def floor_concrete(seed=1, bank=0):
    c = T(col(bank, 3))
    c.noise(0, 0, 8, 8, [col(bank, 2)], 0.14, seed)
    c.noise(0, 0, 8, 8, [col(bank, 4)], 0.07, seed + 50)
    return c


def floor_seam(seed=1, bank=0):
    c = floor_concrete(seed, bank)
    c.hline(0, 0, 8, col(bank, 2))
    c.vline(0, 0, 8, col(bank, 2))
    c.px(2, 2, col(bank, 5))
    c.px(5, 5, col(bank, 2))
    return c


def floor_grate(bank=0):
    c = T(col(bank, 2))
    for y in (0, 2, 4, 6):
        c.hline(0, y, 8, col(bank, 4))
        c.hline(0, y + 1, 8, col(bank, 1))
    c.vline(0, 0, 8, col(bank, 5))
    return c


def floor_plate(bank=0):
    c = T(col(bank, 4))
    c.hline(0, 0, 8, col(bank, 3))
    c.hline(0, 7, 8, col(bank, 3))
    for (x, y) in [(1, 1), (2, 2), (5, 1), (6, 2), (1, 5), (2, 6), (5, 5), (6, 6)]:
        c.px(x, y, col(bank, 5))
    for (x, y) in [(3, 1), (4, 2), (3, 5), (4, 6)]:
        c.px(x, y, col(bank, 3))
    return c


def floor_green(seed=1, bank=0):
    c = T(col(bank, 7))
    c.rect(0, 0, 4, 4, col(bank, 8))
    c.rect(4, 4, 4, 4, col(bank, 8))
    c.noise(0, 0, 8, 8, [col(bank, 2), col(bank, 9)], 0.10, seed)
    c.hline(0, 0, 8, col(bank, 2))
    c.vline(0, 0, 8, col(bank, 2))
    return c


def floor_crack(seed=3, bank=0):
    c = floor_concrete(seed, bank)
    pts = [(1, 0), (2, 2), (3, 3), (4, 5), (6, 6), (7, 7)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], col(bank, 1))
    c.px(3, 4, col(bank, 1))
    return c


def floor_lab(variant=0):
    b = 3
    c = T(col(b, 4))
    c.rect(1, 1, 6, 6, col(b, 5))
    c.hline(1, 1, 6, col(b, 6))
    c.vline(1, 1, 6, col(b, 6))
    c.hline(0, 7, 8, col(b, 3))
    c.vline(7, 0, 8, col(b, 3))
    if variant:
        c.px(3, 3, col(b, 7))
        c.px(4, 4, col(b, 6))
    return c


def floor_test(variant=0):
    b = 3
    c = T(col(b, 2))
    c.noise(0, 0, 8, 8, [col(b, 3)], 0.12, 7 + variant)
    c.hline(0, 0, 8, col(b, 15))
    c.vline(0, 0, 8, col(b, 15))
    if variant == 1:
        c.px(3, 3, col(b, 8)); c.px(4, 3, col(b, 9)); c.px(3, 4, col(b, 9))
    elif variant == 2:
        c.hline(2, 5, 4, col(b, 8)); c.px(2, 4, col(b, 8)); c.px(5, 6, col(b, 9))
    return c


def floor_hazard(phase=0):
    b = 1
    c = T(col(b, 2))
    for y in range(8):
        for x in range(8):
            if ((x + y + phase) // 2) % 2 == 0:
                c.px(x, y, col(b, 7))
    c.hline(0, 0, 8, col(b, 1))
    c.hline(0, 7, 8, col(b, 1))
    return c


# decals: floor tile + stain
def decal_blood(kind, base_seed=1):
    b = 4
    c = floor_concrete(base_seed, 0)
    # rebuild on bank 4 slots (slots 2-5 identical to bank 0)
    c = floor_concrete(base_seed, b)
    r = random.Random(100 + kind)
    if kind == 0:      # splat
        c.ellipse(4, 4, 3, 2.5, col(b, 6))
        c.ellipse(4, 3.5, 2, 1.5, col(b, 7))
        for _ in range(5):
            c.px(r.randrange(8), r.randrange(8), col(b, 7))
        c.px(3, 3, col(b, 9))
    elif kind == 1:    # trail
        c.hline(0, 3, 6, col(b, 6)); c.hline(2, 4, 6, col(b, 6)); c.hline(1, 4, 3, col(b, 7))
        c.px(6, 2, col(b, 7)); c.px(1, 2, col(b, 10))
    elif kind == 2:    # spatter
        for _ in range(9):
            c.px(r.randrange(8), r.randrange(8), col(b, r.choice([6, 7, 10])))
        c.ellipse(5, 5, 1.5, 1.5, col(b, 7))
    elif kind == 3:    # pool
        c.ellipse(4, 4, 3.6, 3.2, col(b, 10))
        c.ellipse(4, 4, 2.6, 2.2, col(b, 6))
        c.px(3, 3, col(b, 8)); c.px(4, 3, col(b, 9))
    elif kind == 4:    # ooze puddle
        c.ellipse(4, 4, 3.4, 2.8, col(b, 11))
        c.ellipse(4, 4, 2.4, 1.8, col(b, 12))
        c.px(3, 3, col(b, 13)); c.px(5, 4, col(b, 13))
    elif kind == 5:    # scorch
        c.ellipse(4, 4, 3.5, 3, col(b, 1))
        c.noise(1, 1, 6, 6, [col(b, 2)], 0.3, 4)
    return c


def decal_debris(kind):
    b = 0
    c = floor_concrete(11 + kind, b)
    r = random.Random(200 + kind)
    if kind == 0:   # rubble
        for _ in range(7):
            x, y = r.randrange(1, 7), r.randrange(1, 7)
            c.px(x, y, col(b, 5)); c.px(x + 1, y, col(b, 6)); c.px(x, y + 1, col(b, 1))
    elif kind == 1:  # papers
        pb = 2
        c = floor_concrete(14, 0)
        c.rect(1, 2, 3, 4, col(pb, 11)); c.hline(1, 3, 3, col(pb, 12)); c.hline(1, 5, 3, col(pb, 12))
        c.rect(4, 1, 3, 3, col(pb, 12)); c.px(5, 2, col(pb, 11))
        return c
    elif kind == 2:  # glass / shards
        for _ in range(6):
            x, y = r.randrange(0, 7), r.randrange(0, 7)
            c.px(x, y, col(b, 15)); c.px(x + 1, y + 1, col(b, 6))
    elif kind == 3:  # bones
        c.line(1, 6, 5, 2, col(b, 15)); c.line(2, 6, 6, 2, col(b, 6))
        c.px(6, 1, col(b, 15)); c.px(1, 5, col(b, 15))
    return c


def pipe_floor(horizontal=True):
    b = 1
    c = floor_concrete(5, 0)
    # recolour floor slots to bank 1 equivalents is not needed: mixed banks not allowed -> redraw on bank 1
    c = T(col(b, 2))
    c.noise(0, 0, 8, 8, [col(b, 1)], 0.1, 9)
    if horizontal:
        c.rect(0, 2, 8, 4, col(b, 3)); c.hline(0, 2, 8, col(b, 4)); c.hline(0, 5, 8, col(b, 1))
        c.vline(3, 2, 4, col(b, 1)); c.px(1, 3, col(b, 4)); c.px(6, 3, col(b, 4))
    else:
        c.rect(2, 0, 4, 8, col(b, 3)); c.vline(2, 0, 8, col(b, 4)); c.vline(5, 0, 8, col(b, 1))
        c.hline(2, 3, 4, col(b, 1)); c.px(3, 1, col(b, 4)); c.px(3, 6, col(b, 4))
    return c


# ---------------------------------------------------------------------------
# walls: top face (viewed from above) and front face (south facing)
# open = set of 'N','E','W' sides adjacent to non-wall floor
# ---------------------------------------------------------------------------
def wall_top(open_sides, seed=2):
    b = 0
    c = T(col(b, 3))
    c.noise(0, 0, 8, 8, [col(b, 2), col(b, 4)], 0.18, seed)
    if 'N' in open_sides:
        c.hline(0, 0, 8, col(b, 6)); c.hline(0, 1, 8, col(b, 5))
    if 'W' in open_sides:
        c.vline(0, 0, 8, col(b, 6)); c.vline(1, 0, 8, col(b, 5))
    if 'E' in open_sides:
        c.vline(7, 0, 8, col(b, 1)); c.vline(6, 0, 8, col(b, 2))
    if 'N' in open_sides and 'W' in open_sides:
        c.px(0, 0, col(b, 15))
    return c


def wall_front(kind, open_sides, seed=2):
    """8x8 south-facing wall face.  kind: plain, pipe, window, lamp, vent, sign, cable, stain,
    stencil, panel"""
    b = 0
    c = T(col(b, 4))
    # cap and base
    c.hline(0, 0, 8, col(b, 6))
    c.hline(0, 1, 8, col(b, 5))
    c.hline(0, 7, 8, col(b, 1))
    c.hline(0, 6, 8, col(b, 2))
    c.noise(0, 2, 8, 4, [col(b, 3)], 0.2, seed)
    if 'W' in open_sides:
        c.vline(0, 0, 8, col(b, 6))
    if 'E' in open_sides:
        c.vline(7, 1, 7, col(b, 1))
    if kind == 'plain':
        c.vline(3, 2, 4, col(b, 3)); c.px(2, 3, col(b, 5)); c.px(5, 4, col(b, 5))
    elif kind == 'panel':
        c.frame(1, 2, 6, 4, col(b, 3)); c.px(2, 3, col(b, 5)); c.px(5, 4, col(b, 2))
    elif kind == 'pipe':
        bb = 1
        c = T(col(bb, 3))
        c.hline(0, 0, 8, col(bb, 4)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 2))
        c.rect(0, 2, 8, 3, col(bb, 6)); c.hline(0, 2, 8, col(bb, 5)); c.hline(0, 4, 8, col(bb, 1))
        c.px(3, 3, col(bb, 7)); c.vline(6, 1, 5, col(bb, 2))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 4))
        if 'E' in open_sides:
            c.vline(7, 1, 7, col(bb, 1))
    elif kind == 'pipe2':
        bb = 1
        c = T(col(bb, 3))
        c.hline(0, 0, 8, col(bb, 4)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 2))
        c.rect(0, 1, 8, 2, col(bb, 4))
        c.hline(0, 2, 8, col(bb, 2))
        c.rect(0, 4, 8, 2, col(bb, 11)); c.hline(0, 4, 8, col(bb, 10)); c.hline(0, 5, 8, col(bb, 2))
        c.vline(2, 1, 5, col(bb, 1)); c.vline(5, 1, 5, col(bb, 1))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 4))
        if 'E' in open_sides:
            c.vline(7, 1, 7, col(bb, 1))
    elif kind == 'window':
        bb = 1
        c = T(col(bb, 2))
        c.hline(0, 0, 8, col(bb, 4)); c.hline(0, 7, 8, col(bb, 1))
        c.rect(1, 2, 6, 4, col(bb, 1))
        c.rect(2, 3, 4, 2, col(bb, 11))
        c.px(2, 3, col(bb, 10)); c.px(3, 3, col(bb, 10)); c.px(5, 4, col(bb, 15))
        c.hline(1, 6, 6, col(bb, 3))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 4))
    elif kind == 'lamp':
        bb = 1
        c = T(col(bb, 2))
        c.hline(0, 0, 8, col(bb, 4)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 1))
        c.noise(0, 1, 8, 5, [col(bb, 3)], 0.2, seed)
        c.rect(2, 2, 4, 3, col(bb, 7)); c.rect(3, 3, 2, 1, col(bb, 14))
        c.hline(2, 1, 4, col(bb, 1)); c.hline(2, 5, 4, col(bb, 6))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 4))
    elif kind == 'vent':
        c.rect(1, 2, 6, 4, col(b, 1))
        for y in (2, 4):
            c.hline(1, y, 6, col(b, 3))
        c.hline(1, 3, 6, col(b, 1)); c.hline(1, 5, 6, col(b, 2))
        c.px(0, 2, col(b, 5)); c.px(7, 2, col(b, 5))
    elif kind == 'sign':
        bb = 1
        c = T(col(bb, 3))
        c.hline(0, 0, 8, col(bb, 4)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 2))
        c.rect(1, 1, 6, 5, col(bb, 7)); c.frame(1, 1, 6, 5, col(bb, 1))
        c.vline(4, 2, 2, col(bb, 1)); c.px(4, 4, col(bb, 1))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 4))
    elif kind == 'sign2':
        bb = 1
        c = T(col(bb, 3))
        c.hline(0, 0, 8, col(bb, 4)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 2))
        c.rect(1, 1, 6, 5, col(bb, 8)); c.frame(1, 1, 6, 5, col(bb, 1))
        c.hline(2, 3, 4, col(bb, 14)); c.hline(2, 4, 3, col(bb, 14))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 4))
    elif kind == 'cable':
        c.line(0, 2, 3, 5, col(b, 1)); c.line(3, 5, 7, 2, col(b, 1))
        c.line(0, 3, 3, 6, col(b, 2)); c.line(3, 6, 7, 3, col(b, 2))
        c.px(3, 5, col(b, 15))
    elif kind == 'stain':
        bb = 4
        c = T(col(bb, 4))
        c.hline(0, 0, 8, col(bb, 5)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 2))
        c.noise(0, 2, 8, 4, [col(bb, 3)], 0.2, seed)
        c.vline(2, 1, 5, col(bb, 6)); c.vline(2, 1, 3, col(bb, 7)); c.vline(5, 1, 3, col(bb, 6))
        c.px(2, 6, col(bb, 6)); c.px(5, 4, col(bb, 7))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 5))
    elif kind == 'stencil':
        bb = 2
        c = T(col(bb, 8))
        c.hline(0, 0, 8, col(bb, 10)); c.hline(0, 7, 8, col(bb, 1)); c.hline(0, 6, 8, col(bb, 2))
        c.rect(2, 2, 4, 3, col(bb, 9)); c.px(3, 3, col(bb, 13)); c.px(4, 3, col(bb, 13)); c.px(3, 4, col(bb, 13))
        if 'W' in open_sides:
            c.vline(0, 0, 8, col(bb, 10))
    return c


# ---------------------------------------------------------------------------
# multi-tile objects
# ---------------------------------------------------------------------------
def obj_crate(variant=0):
    b = 2
    c = Canvas(16, 16)
    if variant == 0:  # wooden
        c.rect(0, 1, 16, 15, col(b, 4))
        c.frame(0, 1, 16, 15, col(b, 1))
        c.rect(1, 2, 14, 13, col(b, 5))
        c.frame(1, 2, 14, 13, col(b, 3))
        c.line(2, 3, 13, 13, col(b, 3)); c.line(13, 3, 2, 13, col(b, 3))
        c.hline(1, 2, 14, col(b, 7))
        c.rect(0, 15, 16, 1, col(b, 1))
    elif variant == 1:  # military green with stencil
        c.rect(0, 1, 16, 15, col(b, 9))
        c.frame(0, 1, 16, 15, col(b, 1))
        c.hline(1, 2, 14, col(b, 10))
        c.rect(1, 3, 14, 11, col(b, 9))
        c.hline(1, 13, 14, col(b, 8))
        c.rect(3, 6, 10, 4, col(b, 8)); c.hline(4, 7, 4, col(b, 14)); c.hline(4, 8, 6, col(b, 14))
        c.vline(2, 2, 12, col(b, 8)); c.vline(13, 2, 12, col(b, 8))
        c.rect(0, 15, 16, 1, col(b, 1))
    else:  # small boxes stack
        c.rect(0, 8, 9, 8, col(b, 5)); c.frame(0, 8, 9, 8, col(b, 1)); c.hline(1, 9, 7, col(b, 7)); c.vline(4, 9, 6, col(b, 3))
        c.rect(7, 1, 9, 8, col(b, 6)); c.frame(7, 1, 9, 8, col(b, 1)); c.hline(8, 2, 7, col(b, 7)); c.vline(11, 2, 6, col(b, 4))
        c.rect(9, 9, 7, 7, col(b, 4)); c.frame(9, 9, 7, 7, col(b, 1)); c.hline(10, 10, 5, col(b, 5))
    return c


def obj_barrel(variant=0):
    b = 1
    c = Canvas(8, 8)
    body, band = (3, 7) if variant == 0 else (13, 12)
    if variant == 2:
        body, band = (11, 10)
    c.rect(1, 0, 6, 8, col(b, body))
    c.vline(1, 0, 8, col(b, 1)); c.vline(6, 0, 8, col(b, 1))
    c.hline(1, 0, 6, col(b, 4)); c.hline(1, 7, 6, col(b, 1))
    c.hline(1, 2, 6, col(b, band)); c.hline(1, 5, 6, col(b, band))
    c.px(2, 3, col(b, 4)); c.px(2, 4, col(b, 4))
    return c


def obj_desk(variant=0):
    """desk 16x16: wood top with items"""
    b = 2
    c = Canvas(16, 16)
    c.rect(0, 5, 16, 11, col(b, 4))
    c.frame(0, 5, 16, 11, col(b, 1))
    c.rect(1, 6, 14, 6, col(b, 5)); c.hline(1, 6, 14, col(b, 6))
    c.hline(1, 12, 14, col(b, 3)); c.rect(1, 13, 14, 2, col(b, 3))
    c.vline(8, 13, 2, col(b, 1))
    if variant == 0:     # papers + mug
        c.rect(2, 7, 5, 4, col(b, 11)); c.hline(2, 8, 4, col(b, 12)); c.hline(2, 10, 4, col(b, 12))
        c.rect(10, 8, 2, 2, col(b, 13)); c.px(12, 8, col(b, 12))
    elif variant == 1:   # monitor
        mb = 1
        c.rect(5, 0, 7, 6, col(mb, 3)); c.frame(5, 0, 7, 6, col(mb, 1))
        c.rect(6, 1, 5, 3, col(mb, 11)); c.px(6, 1, col(mb, 10)); c.px(7, 2, col(mb, 10)); c.hline(7, 3, 3, col(mb, 10))
        c.rect(7, 5, 3, 1, col(mb, 4)); c.rect(3, 8, 3, 2, col(b, 11))
    else:                # broken desk with blood
        mb = 4
        c.rect(0, 5, 8, 11, col(b, 4)); c.rect(8, 7, 8, 9, col(b, 3))
        c.frame(0, 5, 8, 11, col(b, 1)); c.frame(8, 7, 8, 9, col(b, 1))
        c.ellipse(9, 9, 3, 2, col(mb, 6)); c.px(8, 8, col(mb, 8))
        c.rect(2, 7, 4, 3, col(b, 11))
    return c


def obj_server(variant=0):
    """server rack / lab cabinet 16x16"""
    b = 1
    c = Canvas(16, 16)
    c.rect(0, 1, 16, 15, col(b, 2))
    c.frame(0, 1, 16, 15, col(b, 1))
    c.hline(1, 2, 14, col(b, 4))
    for y in (4, 7, 10):
        c.rect(2, y, 12, 2, col(b, 1))
        c.hline(2, y, 12, col(b, 3))
    ledcols = [10, 12, 7] if variant == 0 else [12, 10, 8]
    for i, y in enumerate((4, 7, 10)):
        for x in range(3, 13, 3):
            c.px(x, y + 1, col(b, ledcols[(i + x) % 3]))
    c.hline(2, 13, 12, col(b, 3)); c.px(4, 14, col(b, 5)); c.px(11, 14, col(b, 5))
    return c


def obj_lathe(variant=0):
    """machine shop: heavy press/lathe 16x16"""
    b = 1
    c = Canvas(16, 16)
    c.rect(0, 6, 16, 10, col(b, 3)); c.frame(0, 6, 16, 10, col(b, 1))
    c.hline(1, 7, 14, col(b, 4))
    c.rect(2, 0, 5, 7, col(b, 4)); c.frame(2, 0, 5, 7, col(b, 1))
    c.rect(3, 1, 3, 4, col(b, 3))
    c.rect(9, 9, 5, 4, col(b, 5)); c.frame(9, 9, 5, 4, col(b, 1)); c.px(10, 10, col(b, 7))
    c.rect(8, 7, 7, 1, col(b, 7))
    c.hline(1, 14, 14, col(b, 2))
    if variant:
        c.rect(4, 3, 2, 2, col(b, 8))
    # hazard foot
    for x in range(1, 15):
        if (x // 2) % 2 == 0:
            c.px(x, 15, col(b, 7))
    return c


def obj_tank(broken=False):
    """containment tube 16x24 (2x3 tiles)"""
    b = 3 if not broken else 3
    c = Canvas(16, 24)
    c.rect(2, 0, 12, 24, col(b, 3)); c.frame(2, 0, 12, 24, col(b, 1))
    c.rect(4, 3, 8, 16, col(b, 1))
    liquid = col(b, 9) if not broken else col(b, 3)
    if not broken:
        c.rect(5, 4, 6, 14, col(b, 8))
        c.rect(5, 4, 2, 14, col(b, 9)); c.vline(10, 4, 14, col(b, 3))
        for (x, y) in [(7, 6), (8, 10), (6, 14), (9, 16)]:
            c.px(x, y, col(b, 10))
        c.hline(4, 2, 8, col(b, 6))
    else:
        c.rect(5, 12, 6, 6, col(b, 8)); c.rect(5, 12, 2, 6, col(b, 9))
        c.line(5, 4, 10, 11, col(b, 7)); c.line(10, 4, 6, 12, col(b, 7)); c.line(8, 3, 8, 12, col(b, 6))
        c.px(6, 8, col(b, 14))
    c.rect(1, 19, 14, 3, col(b, 4)); c.frame(1, 19, 14, 3, col(b, 1))
    c.hline(2, 20, 12, col(b, 5)); c.px(4, 21, col(b, 9)); c.px(11, 21, col(b, 12))
    c.rect(3, 22, 10, 2, col(b, 2))
    if broken:
        bb = 4
        c.rect(4, 22, 8, 2, col(bb, 6)); c.px(6, 23, col(bb, 8))
    return c


def obj_generator(on=False):
    """24x16 (3x2 tiles)"""
    b = 1
    c = Canvas(24, 16)
    c.rect(0, 2, 24, 14, col(b, 3)); c.frame(0, 2, 24, 14, col(b, 1))
    c.hline(1, 3, 22, col(b, 4))
    # engine block + fan
    c.rect(2, 5, 9, 8, col(b, 2)); c.frame(2, 5, 9, 8, col(b, 1))
    c.ellipse(6.5, 9, 3, 3, col(b, 1)); c.ellipse(6.5, 9, 2, 2, col(b, 3))
    c.line(4, 9, 9, 9, col(b, 4)); c.line(6, 7, 6, 11, col(b, 4))
    # panel
    c.rect(13, 5, 9, 8, col(b, 2)); c.frame(13, 5, 9, 8, col(b, 1))
    if on:
        c.rect(14, 6, 7, 3, col(b, 10)); c.px(15, 7, col(b, 14)); c.hline(16, 7, 3, col(b, 14))
        c.px(15, 11, col(b, 12)); c.px(17, 11, col(b, 12)); c.px(19, 11, col(b, 7))
        c.rect(9, 0, 6, 2, col(b, 5)); c.px(11, 0, col(b, 7))
    else:
        c.rect(14, 6, 7, 3, col(b, 1))
        c.px(15, 11, col(b, 8)); c.px(17, 11, col(b, 9)); c.px(19, 11, col(b, 9))
        c.rect(9, 0, 6, 2, col(b, 3))
    c.rect(0, 14, 24, 2, col(b, 1))
    for x in range(1, 23):
        if (x // 2) % 2 == 0:
            c.px(x, 15, col(b, 7))
    return c


PERK_COLORS = {  # name: (main slot, light slot)
    'IRON HEART': (8, 10),      # red
    'QUICK HANDS': (7, 14),     # yellow
    'STEADY AIM': (10, 14),     # blue
    'SECOND WIND': (12, 14),    # green
    'FIELD MEDIC': (5, 7),      # orange
}


def obj_perk(main, light, on=True):
    """vending machine 16x24 (2x3 tiles)"""
    b = 1
    c = Canvas(16, 24)
    c.rect(1, 0, 14, 24, col(b, 2)); c.frame(1, 0, 14, 24, col(b, 1))
    c.hline(2, 1, 12, col(b, 4))
    # sign
    c.rect(3, 2, 10, 4, col(b, main) if on else col(b, 3)); c.frame(3, 2, 10, 4, col(b, 1))
    if on:
        c.hline(4, 3, 8, col(b, light))
        c.px(5, 4, col(b, 1)); c.px(7, 4, col(b, 1)); c.px(9, 4, col(b, 1))
    # window with bottles
    c.rect(3, 8, 10, 8, col(b, 1))
    for i, x in enumerate((4, 7, 10)):
        c.rect(x, 10, 2, 5, col(b, main) if on else col(b, 3))
        c.px(x, 10, col(b, light) if on else col(b, 4))
        c.px(x, 9, col(b, 4))
    c.hline(3, 15, 10, col(b, 3))
    # keypad / slot
    c.rect(4, 18, 4, 3, col(b, 3)); c.px(5, 19, col(b, light) if on else col(b, 1))
    c.rect(9, 18, 4, 3, col(b, 1)); c.hline(10, 19, 2, col(b, 4))
    c.hline(2, 22, 12, col(b, 1)); c.rect(2, 23, 12, 1, col(b, 1))
    return c


def obj_terminal(on=True):
    """standing console 16x16"""
    b = 1
    c = Canvas(16, 16)
    c.rect(1, 3, 14, 13, col(b, 3)); c.frame(1, 3, 14, 13, col(b, 1))
    c.rect(3, 0, 10, 8, col(b, 2)); c.frame(3, 0, 10, 8, col(b, 1))
    c.rect(4, 1, 8, 5, col(b, 1))
    if on:
        c.hline(5, 2, 5, col(b, 12)); c.hline(5, 3, 3, col(b, 12)); c.hline(5, 4, 6, col(b, 13))
    c.rect(2, 9, 12, 3, col(b, 2)); c.hline(3, 10, 10, col(b, 4))
    for x in range(3, 13, 2):
        c.px(x, 11, col(b, 3))
    c.rect(2, 14, 12, 2, col(b, 1))
    return c


def obj_weapon_rack(weapon):
    """16x8 wall-mounted weapon station (2x1 tiles).  weapon: 0..5"""
    b = 1
    c = Canvas(16, 8)
    c.rect(0, 0, 16, 8, col(b, 2))
    c.hline(0, 0, 16, col(b, 4)); c.hline(0, 7, 16, col(b, 1)); c.hline(0, 6, 16, col(b, 1))
    c.rect(1, 1, 14, 5, col(b, 1)); c.frame(1, 1, 14, 5, col(b, 5))
    g = col(b, 14)
    d = col(b, 4)
    if weapon == 0:      # pistol
        c.rect(5, 2, 6, 2, d); c.rect(5, 4, 2, 1, d); c.px(11, 2, col(b, 3))
    elif weapon == 1:    # shotgun
        c.rect(3, 3, 11, 1, d); c.rect(3, 2, 8, 1, col(b, 3)); c.rect(3, 4, 3, 1, col(b, 5)); c.px(5, 4, col(b, 6))
    elif weapon == 2:    # smg
        c.rect(4, 2, 8, 2, d); c.rect(6, 4, 2, 2, col(b, 3)); c.rect(11, 3, 3, 1, d)
    elif weapon == 3:    # rifle
        c.rect(2, 3, 12, 1, d); c.rect(5, 2, 4, 1, col(b, 3)); c.rect(3, 4, 3, 1, col(b, 5)); c.px(11, 2, col(b, 12))
    elif weapon == 4:    # arc launcher
        c.rect(3, 2, 9, 3, col(b, 3)); c.rect(11, 3, 3, 1, col(b, 10)); c.px(5, 3, col(b, 10)); c.px(8, 3, col(b, 10))
        c.px(13, 2, col(b, 14)); c.px(13, 4, col(b, 14))
    else:                # ray weapon
        c.rect(3, 2, 8, 3, col(b, 3)); c.rect(10, 3, 4, 1, col(b, 12)); c.px(5, 3, col(b, 12)); c.px(7, 3, col(b, 12))
        c.px(14, 3, col(b, 14))
    # little amber light
    return c


def obj_door(w_tiles, h_tiles, vertical, open_=False):
    """closed bulkhead door.  w_tiles x h_tiles tiles."""
    b = 1
    W, H = w_tiles * 8, h_tiles * 8
    c = Canvas(W, H)
    c.rect(0, 0, W, H, col(b, 3))
    c.frame(0, 0, W, H, col(b, 1))
    if not vertical:
        # sliding panels with hazard band in the middle
        c.rect(1, 1, W - 2, 2, col(b, 4))
        c.vline(W // 2, 1, H - 2, col(b, 1)); c.vline(W // 2 - 1, 1, H - 2, col(b, 2))
        for x in range(2, W - 2):
            if ((x // 3) % 2) == 0:
                c.px(x, H // 2 - 1, col(b, 7)); c.px(x, H // 2, col(b, 7))
        c.rect(W // 2 - 2, H // 2 - 2, 4, 4, col(b, 1)); c.px(W // 2 - 1, H // 2 - 1, col(b, 8)); c.px(W // 2, H // 2 - 1, col(b, 8))
        c.hline(1, H - 2, W - 2, col(b, 2))
    else:
        c.rect(1, 1, 2, H - 2, col(b, 4))
        c.hline(1, H // 2, W - 2, col(b, 1)); c.hline(1, H // 2 - 1, W - 2, col(b, 2))
        for y in range(2, H - 2):
            if ((y // 3) % 2) == 0:
                c.px(W // 2 - 1, y, col(b, 7)); c.px(W // 2, y, col(b, 7))
        c.rect(W // 2 - 2, H // 2 - 2, 4, 4, col(b, 1)); c.px(W // 2 - 1, H // 2 - 1, col(b, 8)); c.px(W // 2, H // 2 - 1, col(b, 8))
        c.vline(W - 2, 1, H - 2, col(b, 2))
    return c


def anim_gear(frame, size=16):
    """rotating gear for the title screen (bank 1), 16x16"""
    import math
    b = 1
    c = Canvas(size, size)
    r = size / 2
    teeth = 8
    ang0 = frame * (math.pi / teeth / 2)
    for y in range(size):
        for x in range(size):
            dx, dy = x + 0.5 - r, y + 0.5 - r
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx) + ang0
            tooth = (math.cos(a * teeth) > -0.2)
            outer = r - 0.6 if tooth else r - 2.6
            if d <= outer:
                c.px(x, y, col(b, 5) if d > r - 3.2 else col(b, 4))
            if d <= 2.4:
                c.px(x, y, col(b, 7))
            elif 4.2 < d < 5.2 and abs(math.cos(a * 4)) > 0.75:
                c.px(x, y, col(b, 1))
            elif d <= 4.2 and d > 2.4:
                c.px(x, y, col(b, 3))
    c.outline(col(b, 1))
    return c


def anim_conveyor(frame):
    """hazard stripe belt tile (bank 1)"""
    b = 1
    c = T(col(b, 2))
    for y in range(1, 7):
        for x in range(8):
            if ((x + frame * 2) // 2) % 2 == 0:
                c.px(x, y, col(b, 7))
            else:
                c.px(x, y, col(b, 1))
    c.hline(0, 0, 8, col(b, 4)); c.hline(0, 7, 8, col(b, 4))
    return c


def obj_mystery_box(open_=False):
    """MYSTERY BOX: steel chest with a glowing question mark; open = lid up + light beam (16x16)"""
    b = 1
    c = Canvas(16, 16)
    # body
    c.rect(1, 7, 14, 9, col(b, 3)); c.frame(1, 7, 14, 9, col(b, 1))
    c.hline(2, 8, 12, col(b, 4)); c.hline(2, 14, 12, col(b, 2))
    c.rect(1, 10, 14, 2, col(b, 6)); c.hline(1, 10, 14, col(b, 5)); c.hline(1, 11, 14, col(b, 6))
    c.rect(7, 9, 2, 5, col(b, 7)); c.px(7, 11, col(b, 1)); c.px(8, 11, col(b, 1))     # latch
    if not open_:
        c.rect(1, 3, 14, 5, col(b, 4)); c.frame(1, 3, 14, 5, col(b, 1))
        c.hline(2, 4, 12, col(b, 14)); c.hline(2, 7, 12, col(b, 2))
        # glowing question mark on the lid
        for (x, y) in [(6, 4), (7, 4), (8, 4), (9, 5), (9, 6), (8, 6), (7, 6)]:
            pass
        c.px(6, 5, col(b, 10)); c.px(7, 4, col(b, 10)); c.px(8, 4, col(b, 10)); c.px(9, 5, col(b, 10))
        c.px(8, 6, col(b, 10)); c.px(7, 6, col(b, 10)); c.px(7, 7, col(b, 10))
    else:
        # lid tilted up behind the box, light pouring out
        c.rect(2, 0, 12, 3, col(b, 4)); c.frame(2, 0, 12, 3, col(b, 1))
        c.rect(3, 3, 10, 4, col(b, 7)); c.rect(5, 3, 6, 4, col(b, 14))
        c.hline(4, 3, 8, col(b, 14))
    return c


def obj_pap(on=True):
    """PACK-A-PUNCH machine 16x24: blue energy press with a hazard base"""
    b = 1
    c = Canvas(16, 24)
    c.rect(1, 0, 14, 24, col(b, 2)); c.frame(1, 0, 14, 24, col(b, 1))
    c.hline(2, 1, 12, col(b, 4))
    # header sign
    c.rect(3, 2, 10, 4, col(b, 10) if on else col(b, 3)); c.frame(3, 2, 10, 4, col(b, 1))
    if on:
        c.hline(4, 3, 8, col(b, 14)); c.px(5, 4, col(b, 11)); c.px(8, 4, col(b, 11)); c.px(10, 4, col(b, 11))
    # press piston
    c.rect(6, 7, 4, 5, col(b, 4)); c.frame(6, 7, 4, 5, col(b, 1)); c.hline(7, 8, 2, col(b, 14) if on else col(b, 3))
    # forging chamber
    c.rect(3, 12, 10, 6, col(b, 1))
    if on:
        c.rect(4, 13, 8, 4, col(b, 11)); c.rect(5, 14, 6, 2, col(b, 10)); c.px(7, 14, col(b, 14)); c.px(8, 15, col(b, 14))
    else:
        c.rect(4, 13, 8, 4, col(b, 2))
    # controls
    c.rect(3, 19, 4, 3, col(b, 3)); c.px(4, 20, col(b, 7) if on else col(b, 1)); c.px(5, 20, col(b, 12) if on else col(b, 1))
    c.rect(9, 19, 4, 3, col(b, 1)); c.hline(10, 20, 2, col(b, 10) if on else col(b, 3))
    # hazard base
    for x in range(2, 14):
        if (x // 2) % 2 == 0:
            c.px(x, 23, col(b, 7))
    return c
