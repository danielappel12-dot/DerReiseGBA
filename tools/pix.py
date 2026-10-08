"""pix.py - tiny pixel-art toolkit used by the NIGHTFALL asset generators.

Colour values on a Canvas are *palette indices* 0..255 where
    index = bank * 16 + slot        (slot 0 of every bank is "transparent")
which maps 1:1 to GBA 4bpp tiles + 16 palette banks.
"""
import random
from PIL import Image


class Canvas:
    def __init__(self, w, h, fill=0):
        self.w, self.h = w, h
        self.p = [[fill] * w for _ in range(h)]

    # -- basics ---------------------------------------------------------
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.p[y][x]
        return 0

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)

    def frame(self, x, y, w, h, c):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.px(xx, y, c)

    def vline(self, x, y, h, c):
        for yy in range(y, y + h):
            self.px(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, c):
        """filled ellipse, integer maths, centre (cx,cy) in pixel coords (x.5 allowed via *2)"""
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.px(x, y, c)

    def noise(self, x, y, w, h, colors, density, seed=1):
        r = random.Random(seed)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if r.random() < density:
                    self.px(xx, yy, r.choice(colors))

    def dither(self, x, y, w, h, c1, c2, phase=0):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c1 if ((xx + yy + phase) & 1) == 0 else c2)

    def blit(self, other, x, y, skip0=True):
        for yy in range(other.h):
            for xx in range(other.w):
                c = other.p[yy][xx]
                if c or not skip0:
                    self.px(x + xx, y + yy, c)

    def sub(self, x, y, w, h):
        c = Canvas(w, h)
        for yy in range(h):
            for xx in range(w):
                c.p[yy][xx] = self.get(x + xx, y + yy)
        return c

    def copy(self):
        c = Canvas(self.w, self.h)
        c.p = [row[:] for row in self.p]
        return c

    def hflip(self):
        c = Canvas(self.w, self.h)
        c.p = [row[::-1] for row in self.p]
        return c

    def outline(self, col, diag=False):
        """add a 1px outline of colour `col` around every opaque pixel"""
        src = self.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src.p[y][x] == 0:
                    n = [src.get(x - 1, y), src.get(x + 1, y), src.get(x, y - 1), src.get(x, y + 1)]
                    if diag:
                        n += [src.get(x - 1, y - 1), src.get(x + 1, y - 1),
                              src.get(x - 1, y + 1), src.get(x + 1, y + 1)]
                    if any(n):
                        self.p[y][x] = col
        return self

    def remap(self, mapping):
        for y in range(self.h):
            for x in range(self.w):
                self.p[y][x] = mapping.get(self.p[y][x], self.p[y][x])
        return self

    def shift(self, dx, dy):
        c = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                c.px(x + dx, y + dy, self.p[y][x])
        return c

    def key(self):
        return tuple(tuple(r) for r in self.p)


def rgb(hexstr):
    hexstr = hexstr.lstrip('#')
    return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))


def to15(c):
    """quantise an 8-bit RGB triple to what the GBA can show (and back)"""
    return tuple(((v >> 3) << 3) | (v >> 5) for v in c)


class Palette:
    """256 entry palette = 16 banks of 16."""

    def __init__(self):
        self.c = [(0, 0, 0)] * 256

    def bank(self, b, colors):
        assert len(colors) <= 16
        for i, col in enumerate(colors):
            self.c[b * 16 + i] = to15(rgb(col)) if isinstance(col, str) else to15(col)

    def flat(self):
        out = []
        for r, g, b in self.c:
            out += [r, g, b]
        return out


def save_indexed(canvas_rows, w, h, pal, path, scale=1):
    """write a list-of-rows of palette indices as an indexed PNG"""
    im = Image.new('P', (w, h))
    im.putpalette(pal.flat())
    data = []
    for row in canvas_rows:
        data += row
    im.putdata(data)
    im.save(path)
    if scale > 1:
        big = im.resize((w * scale, h * scale), Image.NEAREST)
        big.save(path.replace('.png', '_x%d.png' % scale))
    return im


def sheet_from_frames(frames, cols, fw, fh):
    """pack equally-sized canvases in a grid, return (rows, w, h)"""
    n = len(frames)
    rows_n = (n + cols - 1) // cols
    W, H = cols * fw, rows_n * fh
    big = Canvas(W, H)
    for i, f in enumerate(frames):
        big.blit(f, (i % cols) * fw, (i // cols) * fh, skip0=False)
    return big
