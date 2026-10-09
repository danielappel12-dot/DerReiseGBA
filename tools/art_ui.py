"""art_ui.py - fonts, UI tiles and the title logo (all original pixel art)."""
from pix import Canvas

# ---------------------------------------------------------------------------
# 5x7 glyph definitions (original, hand drawn).  '#' = pixel.
# ---------------------------------------------------------------------------
G = {}


def g(ch, *rows):
    assert len(rows) == 7, ch
    for r in rows:
        assert len(r) == 5, (ch, r)
    G[ch] = rows


g('A', ".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
g('B', "####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")
g('C', ".###.", "#...#", "#....", "#....", "#....", "#...#", ".###.")
g('D', "####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.")
g('E', "#####", "#....", "#....", "####.", "#....", "#....", "#####")
g('F', "#####", "#....", "#....", "####.", "#....", "#....", "#....")
g('G', ".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####")
g('H', "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
g('I', ".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###.")
g('J', "..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..")
g('K', "#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#")
g('L', "#....", "#....", "#....", "#....", "#....", "#....", "#####")
g('M', "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
g('N', "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#")
g('O', ".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
g('P', "####.", "#...#", "#...#", "####.", "#....", "#....", "#....")
g('Q', ".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#")
g('R', "####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#")
g('S', ".####", "#....", "#....", ".###.", "....#", "....#", "####.")
g('T', "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
g('U', "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
g('V', "#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#..")
g('W', "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#")
g('X', "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
g('Y', "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
g('Z', "#####", "....#", "...#.", "..#..", ".#...", "#....", "#####")
g('0', ".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.")
g('1', "..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.")
g('2', ".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####")
g('3', "####.", "....#", "....#", ".###.", "....#", "....#", "####.")
g('4', "...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.")
g('5', "#####", "#....", "####.", "....#", "....#", "#...#", ".###.")
g('6', ".###.", "#....", "#....", "####.", "#...#", "#...#", ".###.")
g('7', "#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#...")
g('8', ".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.")
g('9', ".###.", "#...#", "#...#", ".####", "....#", "....#", ".###.")
g(' ', ".....", ".....", ".....", ".....", ".....", ".....", ".....")
g('!', "..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#..")
g('?', ".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..")
g('.', ".....", ".....", ".....", ".....", ".....", ".##..", ".##..")
g(',', ".....", ".....", ".....", ".....", ".##..", "..#..", ".#...")
g(':', ".....", ".##..", ".##..", ".....", ".##..", ".##..", ".....")
g(';', ".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#...")
g('-', ".....", ".....", ".....", ".###.", ".....", ".....", ".....")
g('+', ".....", "..#..", "..#..", "#####", "..#..", "..#..", ".....")
g('/', "....#", "....#", "...#.", "..#..", ".#...", "#....", "#....")
g('%', "##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##")
g('(', "...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#.")
g(')', ".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#...")
g('<', "...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#.")
g('>', ".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#...")
g('=', ".....", ".....", "#####", ".....", "#####", ".....", ".....")
g('*', ".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", ".....")
g("'", "..#..", "..#..", ".....", ".....", ".....", ".....", ".....")
g('"', ".#.#.", ".#.#.", ".....", ".....", ".....", ".....", ".....")
g('#', ".#.#.", "#####", ".#.#.", ".#.#.", "#####", ".#.#.", ".....")
g('_', ".....", ".....", ".....", ".....", ".....", ".....", "#####")
g('[', ".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###.")
g(']', ".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###.")
g('&', ".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#")
g('$', "..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#..")
g('@', ".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###.")
# private glyphs mapped onto unused ASCII slots
g('^', "..#..", ".###.", "#####", "..#..", "..#..", "..#..", "..#..")   # up arrow
g('~', "..#..", "..#..", "..#..", "#####", ".###.", "..#..", ".....")   # down arrow
g('`', "..#..", "..##.", "#####", "..##.", "..#..", ".....", ".....")   # right arrow
g('\\', "..#..", ".##..", "#####", ".##..", "..#..", ".....", ".....")  # left arrow
g('{', ".#.#.", "#####", "#####", "#####", ".###.", "..#..", ".....")   # heart
g('}', "..#..", ".###.", "#####", ".###.", "#.#.#", ".....", ".....")   # skull-ish star
g('|', "..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")


def glyph(ch):
    return G.get(ch.upper() if ch.upper() in G else ch, G['?'])


def font_sheet():
    """16x6 grid of 8x8 glyphs, ASCII 0x20..0x7F.  Slots: 1 shadow, 2 fill, 3 highlight."""
    cv = Canvas(128, 48)
    for code in range(0x20, 0x80):
        i = code - 0x20
        ox, oy = (i % 16) * 8, (i // 16) * 8
        rows = glyph(chr(code))
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == '#':
                    cv.px(ox + 1 + x, oy + y, 2 if y >= 1 else 3)
        # shadow pass (right+down)
        cp = cv.sub(ox, oy, 8, 8)
        for y in range(8):
            for x in range(8):
                if cp.get(x, y) == 0 and (cp.get(x - 1, y) in (2, 3) or cp.get(x, y - 1) in (2, 3)
                                          or cp.get(x - 1, y - 1) in (2, 3)):
                    cv.px(ox + x, oy + y, 1)
    return cv


BIG_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!:-. "


def bigfont_sheet():
    """each glyph = 16x16 (2x2 tiles).  Sheet is one glyph per 16x16 cell, 16 per row.
    slots: 1 outline, 2 fill, 3 highlight"""
    n = len(BIG_CHARS)
    cols = 16
    rows = (n + cols - 1) // cols
    cv = Canvas(cols * 16, rows * 16)
    for i, ch in enumerate(BIG_CHARS):
        ox, oy = (i % cols) * 16, (i // cols) * 16
        tmp = Canvas(16, 16)
        for y, row in enumerate(glyph(ch)):
            for x, c in enumerate(row):
                if c == '#':
                    # 2x scale, bold by 1px horizontally
                    for dy in range(2):
                        for dx in range(3):
                            tmp.px(2 + x * 2 + dx, 1 + y * 2 + dy, 2 if (y * 2 + dy) >= 4 else 3)
        # outline
        tmp.outline(1, diag=True)
        # shadow: down-right
        cv.blit(tmp, ox, oy, skip0=False)
    return cv


# ---------------------------------------------------------------------------
# UI tiles (8x8, slots in bank 0 of the sheet: 1 dark, 2 main, 3 light, 4 frame, 5 dark main, 6 panel)
# ---------------------------------------------------------------------------
UI_TILE_NAMES = []
_ui = []


def ui_tile(name, canvas):
    UI_TILE_NAMES.append(name)
    _ui.append(canvas)


def _bar_tile(fill, left=False, right=False):
    t = Canvas(8, 8)
    t.hline(0, 1, 8, 4)
    t.hline(0, 6, 8, 4)
    if left:
        t.vline(0, 1, 6, 4)
    if right:
        t.vline(7, 1, 6, 4)
    t.rect(0 if not left else 1, 2, 8 - (1 if left else 0) - (1 if right else 0), 4, 6)
    for x in range(fill):
        t.vline(x, 2, 4, 2)
        t.px(x, 2, 3)
    return t


def build_ui_tiles():
    del UI_TILE_NAMES[:]
    del _ui[:]
    ui_tile('BLANK', Canvas(8, 8))
    for i in range(9):
        ui_tile('BAR_%d' % i, _bar_tile(i))
    # window panel 3x3 (corner / edge tiles)
    def pt(name, edges):
        t = Canvas(8, 8, 6)
        if 'T' in edges:
            t.hline(0, 0, 8, 4)
            t.hline(0, 1, 8, 3)
        if 'B' in edges:
            t.hline(0, 7, 8, 4)
            t.hline(0, 6, 8, 5)
        if 'L' in edges:
            t.vline(0, 0, 8, 4)
            t.vline(1, 0, 8, 3)
        if 'R' in edges:
            t.vline(7, 0, 8, 4)
            t.vline(6, 0, 8, 5)
        ui_tile(name, t)
    pt('PANEL_TL', 'TL'); pt('PANEL_T', 'T'); pt('PANEL_TR', 'TR')
    pt('PANEL_L', 'L');  pt('PANEL_C', '');  pt('PANEL_R', 'R')
    pt('PANEL_BL', 'BL'); pt('PANEL_B', 'B'); pt('PANEL_BR', 'BR')
    # small icons
    ic = Canvas(8, 8)
    for (x, y) in [(1, 1), (2, 1), (5, 1), (6, 1)]:
        ic.px(x, y, 2)
    ic.rect(0, 2, 8, 2, 2); ic.rect(1, 4, 6, 1, 2); ic.rect(2, 5, 4, 1, 2); ic.rect(3, 6, 2, 1, 2)
    ic.px(1, 2, 3); ic.px(2, 2, 3)
    ui_tile('ICON_HEART', ic)
    ic = Canvas(8, 8)
    ic.rect(3, 0, 2, 5, 3); ic.rect(2, 5, 4, 3, 2); ic.px(3, 0, 3)
    ui_tile('ICON_BULLET', ic)
    ic = Canvas(8, 8)
    ic.ellipse(4, 4, 3, 3, 2); ic.vline(4, 2, 4, 5); ic.px(3, 2, 3)
    ui_tile('ICON_COIN', ic)
    # perk logos, drawn 6x6 inside the tile ('#' main, 'o' highlight); order = perk ids
    PERK_ART = [
        ["##..##", "o#####", "######", ".####.", "..##.."],          # IRON HEART: heart
        ["...##.", "..##..", ".####.", "..##..", ".##..."],          # QUICK HANDS: bolt
        ["..##..", ".#..#.", "##oo##", "##oo##", ".#..#.", "..##.."],  # STEADY AIM: crosshair
        ["#..#..", ".#..#.", "..#..#", ".#..#.", "#..#.."],          # SECOND WIND: speed chevrons
        ["..##..", "..#o..", "######", "o#####", "..##..", "..##.."],  # FIELD MEDIC: cross
    ]
    for i, art in enumerate(PERK_ART):
        ic = Canvas(8, 8)
        for y, row in enumerate(art):
            for x, ch in enumerate(row):
                if ch != '.':
                    ic.px(1 + x, 1 + y, 3 if ch == 'o' else 2)
        ic.outline(1)
        ui_tile('PERK_%d' % i, ic)
    return _ui


def ui_sheet():
    tiles = build_ui_tiles()
    cols = 16
    rows = (len(tiles) + cols - 1) // cols
    cv = Canvas(cols * 8, rows * 8)
    for i, t in enumerate(tiles):
        cv.blit(t, (i % cols) * 8, (i // cols) * 8, skip0=False)
    return cv


# ---------------------------------------------------------------------------
# Title logo.  Uses BG bank 1 colours (5 orange, 6 dark orange, 7 yellow,
# 8 red, 9 dark red, 1 outline, 14 white, 3 steel, 4 steel light)
# ---------------------------------------------------------------------------
def _scaled(ch, sx, sy, bold=0):
    rows = glyph(ch)
    w, h = 5 * sx + bold, 7 * sy
    c = Canvas(w, h)
    for y, row in enumerate(rows):
        for x, p in enumerate(row):
            if p == '#':
                for dy in range(sy):
                    for dx in range(sx + bold):
                        c.px(x * sx + dx, y * sy + dy, 1)
    return c


def logo_canvas():
    W, H = 232, 64
    cv = Canvas(W, H)
    # "PROJECT:" - steel, 2x
    word = "PROJECT:"
    pitch = 14
    total = pitch * len(word)
    x0 = (W - total) // 2
    for i, ch in enumerate(word):
        s = _scaled(ch, 2, 2, 0)
        tmp = Canvas(s.w + 4, s.h + 4)
        for y in range(s.h):
            for x in range(s.w):
                if s.p[y][x]:
                    tmp.px(x + 2, y + 2, 4 if y < s.h // 2 else 3)
        sh = tmp.copy()
        tmp.outline(1)
        cv.blit(tmp, x0 + i * pitch, 2)
    # "NIGHTFALL" - hot gradient, 3x, bold
    word = "NIGHTFALL"
    pitch = 25
    total = pitch * len(word)
    x0 = (W - total) // 2 + 1
    for i, ch in enumerate(word):
        s = _scaled(ch, 3, 3, 1)
        tmp = Canvas(s.w + 4, s.h + 4)
        for y in range(s.h):
            for x in range(s.w):
                if s.p[y][x]:
                    t = y / s.h
                    if t < 0.28:
                        col = 7        # yellow
                    elif t < 0.62:
                        col = 5        # orange
                    elif t < 0.86:
                        col = 8        # red
                    else:
                        col = 9        # dark red
                    # bevel: left/top highlight
                    if s.get(x - 1, y) == 0 or s.get(x, y - 1) == 0:
                        col = 14 if t < 0.5 else 7
                    tmp.px(x + 2, y + 2, col)
        # drop shadow + outline
        sh = Canvas(tmp.w + 2, tmp.h + 2)
        for y in range(tmp.h):
            for x in range(tmp.w):
                if tmp.p[y][x]:
                    sh.px(x + 2, y + 2, 1)
        full = sh
        full.blit(tmp, 0, 0)
        out = Canvas(full.w, full.h)
        out.blit(full, 0, 0)
        out.outline(1, diag=True)
        # extra drips on a few letters
        if ch in "GTL":
            for k in range(3):
                out.vline(8 + k * 4, 26 + 2, 3 + (k % 2) * 2, 8)
        cv.blit(out, x0 + i * pitch - 2, 20)
    # steel underline rivets
    cv.hline(8, 57, W - 16, 3)
    cv.hline(8, 58, W - 16, 2)
    for x in range(10, W - 10, 12):
        cv.px(x, 57, 4)
    return cv
