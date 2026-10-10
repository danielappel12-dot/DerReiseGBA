"""art_chars.py - cartoony character sprites (player, zombies, corpses, brute).

Style: chibi proportions (huge head, tiny body), thick near-black outline,
flat cel shading, big white eyes with pupils and a little shine, chunky boots.
All frames are 16x32 (brute 32x32); the feet contact row stays at y=25.
Colours are palette indices bank*16+slot (see palettes.py for slot meaning).
"""
from pix import Canvas

OUT = 1
WHITE = 15
FEET = 24


def C(bank, slot):
    return bank * 16 + slot


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def ball(c, x, y, w, h, col):
    """rounded blob: a rectangle with its four corner pixels cut"""
    c.rect(x, y + 1, w, h - 2, col)
    c.rect(x + 1, y, w - 2, h, col)


def cel(c, x, y, w, h, col, sh):
    """rounded blob with a one pixel cel-shade on the right and bottom"""
    ball(c, x, y, w, h, col)
    for yy in range(y + 1, y + h - 1):
        c.px(x + w - 1, yy, sh)
    for xx in range(x + 1, x + w - 1):
        c.px(xx, y + h - 1, sh)


def eye(c, x, y, b, px=1, py=1, w=3, h=4, pupil=OUT):
    """big cartoon eye: white blob, 2x2 pupil, the left-over white is the shine"""
    ball(c, x, y, w, h, C(b, WHITE))
    c.rect(x + px, y + py, 2, 2, pupil)


def brow(c, x, y, left, col=OUT):
    """angry eyebrow above a 3 wide eye; the inner end dips toward the nose"""
    if left:
        c.hline(x, y - 1, 2, col); c.px(x + 2, y, col)
    else:
        c.hline(x + 1, y - 1, 2, col); c.px(x, y, col)


def mouth(c, x, y, w, b, atk, tongue=9):
    """toothy cartoon mouth"""
    h = 3 if atk else 2
    c.rect(x, y, w, h, OUT)
    for i in range(1, w - 1, 2):
        c.px(x + i, y, C(b, WHITE))
    if atk:
        c.px(x + w // 2, y + 2, C(b, tongue)); c.px(x + w // 2 - 1, y + 2, C(b, tongue))


def boots(c, x, ytop, w, ybot, cloth, shade, boot, sole, toe, lift=0):
    """one stubby leg with a big round shoe (toe: -1 left, +1 right)"""
    yb = ybot - lift
    c.rect(x, ytop, w, max(1, yb - 3 - ytop + 1), cloth)
    c.vline(x + w - 1, ytop, max(1, yb - 3 - ytop + 1), shade)
    sx = x - (1 if toe < 0 else 0)
    c.rect(sx, yb - 2, w + 1, 3, boot)
    c.hline(sx, yb, w + 1, sole)


def finish(c, bank=0):
    c.outline(C(bank, OUT))
    return c


# ---------------------------------------------------------------------------
# PLAYER "Rook"
# ---------------------------------------------------------------------------
def _player_head_down(c, hy, b, ko=False):
    skin, skins = C(b, 2), C(b, 3)
    hel, helh, helh2 = C(b, 9), C(b, 12), C(b, 7)
    gold = C(b, 8)
    cel(c, 2, hy, 12, 10, skin, skins)
    # helmet
    c.rect(3, hy, 10, 1, hel); c.rect(2, hy + 1, 12, 3, hel)
    c.hline(2, hy + 3, 12, helh2)
    c.hline(4, hy + 1, 3, helh)
    c.px(2, hy + 3, helh2)
    # goggle strap with two lenses pushed up on the forehead
    c.hline(2, hy + 4, 12, gold)
    c.px(5, hy + 4, C(b, 14)); c.px(10, hy + 4, C(b, 14))
    if ko:
        for ex in (4, 9):
            c.px(ex, hy + 5, OUT); c.px(ex + 2, hy + 5, OUT); c.px(ex + 1, hy + 6, OUT)
            c.px(ex, hy + 7, OUT); c.px(ex + 2, hy + 7, OUT)
        c.rect(6, hy + 8, 4, 1, OUT)
    else:
        eye(c, 4, hy + 5, b, px=1, py=1, h=3)
        eye(c, 9, hy + 5, b, px=0, py=1, h=3)
        c.hline(6, hy + 8, 4, skins)
        c.px(5, hy + 8, C(b, 8)); c.px(10, hy + 8, C(b, 8))      # rosy cheeks


def player(view, frame, pose='walk'):
    b = 0
    if pose == 'dead':
        return player_dead(frame)
    c = Canvas(16, 32)
    ph = frame if pose == 'walk' else 0
    bob = [0, 1, 0, 1][ph]
    lift = [(0, 0), (2, 0), (0, 0), (0, 2)][ph]
    swing = [0, -1, 0, 1][ph]
    jac, jacs = C(b, 4), C(b, 5)
    pan, pans = C(b, 6), C(b, 7)
    skin, skins = C(b, 2), C(b, 3)
    hel, helh = C(b, 9), C(b, 12)
    boot, sole = C(b, 13), C(b, 14)
    gold = C(b, 8)
    metal, metald = C(b, 10), C(b, 11)
    hy = 3 + bob
    ty = hy + 9
    if view == 'down':
        boots(c, 4, ty + 6, 3, FEET, pan, pans, boot, sole, -1, lift[0])
        boots(c, 9, ty + 6, 3, FEET, pan, pans, boot, sole, 1, lift[1])
        cel(c, 4, ty, 8, 6, jac, jacs)
        c.hline(4, ty + 4, 8, boot); c.px(7, ty + 4, gold); c.px(8, ty + 4, gold)
        c.rect(9, ty + 1, 2, 2, gold)                              # chest badge
        c.px(9, ty + 1, C(b, WHITE))
        if pose == 'reload':
            c.rect(2, ty + 1, 2, 3, jac); c.rect(12, ty + 1, 2, 3, jac)
            c.rect(3, ty + 3, 3, 2, skin); c.rect(10, ty + 3, 3, 2, skin)
            c.rect(6, ty + 2, 4, 4, metald); c.rect(6, ty + 2, 4, 1, metal)
        elif pose == 'shoot':
            c.rect(2, ty + 1, 2, 4, jac); c.rect(2, ty + 4, 2, 2, skin)
            c.rect(12, ty + 1, 2, 5, jac); c.rect(12, ty + 5, 2, 2, skin)
            c.rect(12, ty + 7, 3, 4, metald); c.rect(12, ty + 7, 3, 1, metal)
        else:
            c.rect(2, ty + 1 + swing, 2, 3, jac); c.rect(2, ty + 4 + swing, 2, 2, skin)
            c.rect(12, ty + 1 - swing, 2, 3, jac); c.rect(12, ty + 4 - swing, 2, 2, skin)
            c.rect(12, ty + 6 - swing, 3, 3, metald); c.rect(12, ty + 6 - swing, 3, 1, metal)
        _player_head_down(c, hy, b)
    elif view == 'up':
        boots(c, 4, ty + 6, 3, FEET, pan, pans, boot, sole, -1, lift[0])
        boots(c, 9, ty + 6, 3, FEET, pan, pans, boot, sole, 1, lift[1])
        cel(c, 4, ty, 8, 6, boot, C(b, 14))                        # backpack
        c.hline(4, ty, 8, gold); c.rect(5, ty + 2, 6, 2, C(b, 14))
        c.vline(7, ty + 4, 2, C(b, 14)); c.vline(9, ty + 4, 2, C(b, 14))
        c.rect(2, ty + 1 + swing, 2, 3, jac); c.rect(2, ty + 4 + swing, 2, 2, skin)
        c.rect(12, ty + 1 - swing, 2, 3, jac); c.rect(12, ty + 4 - swing, 2, 2, skin)
        # back of the helmet
        cel(c, 2, hy, 12, 9, hel, C(b, 7))
        c.rect(4, hy + 8, 8, 2, skin); c.hline(4, hy + 9, 8, skins)
        c.hline(4, hy + 1, 3, helh)
        c.hline(2, hy + 5, 12, C(b, 7)); c.px(7, hy + 5, gold); c.px(8, hy + 5, gold)
        if pose == 'shoot':
            c.rect(12, ty - 3, 2, 6, jac); c.rect(12, ty - 5, 2, 2, skin)
            c.rect(12, ty - 9, 3, 4, metald); c.rect(13, ty - 9, 1, 1, metal)
        if pose == 'reload':
            c.rect(3, ty + 1, 10, 3, jac); c.rect(6, ty + 1, 4, 2, metald)
    else:  # side, facing right
        offs = [(0, 0), (2, -2), (0, 0), (-2, 2)][ph]
        rec = 1 if pose == 'shoot' else 0
        boots(c, 5 + offs[1], ty + 6, 3, FEET, pans, pans, C(b, 14), C(b, 1), 1,
              1 if (offs[1] > 0 and ph) else 0)
        boots(c, 7 + offs[0], ty + 6, 3, FEET, pan, pans, boot, sole, 1,
              1 if (offs[0] > 0 and ph) else 0)
        # backpack then torso
        cel(c, 2 - rec, ty - 1, 4, 7, boot, C(b, 14)); c.hline(2 - rec, ty - 1, 4, gold)
        cel(c, 5 - rec, ty, 7, 6, jac, jacs)
        c.hline(5 - rec, ty + 4, 7, boot); c.px(10 - rec, ty + 4, gold)
        c.rect(9 - rec, ty + 1, 2, 2, gold)
        if pose == 'reload':
            c.rect(8, ty + 2, 3, 3, jac); c.rect(10, ty + 3, 2, 2, skin)
            c.rect(9, ty + 1, 3, 3, metald); c.rect(9, ty + 1, 3, 1, metal)
        elif pose == 'shoot':
            c.rect(9 - rec, ty + 1, 4, 2, jac); c.rect(13 - rec, ty + 1, 2, 2, skin)
            c.rect(13 - rec, ty - 1, 3, 3, metald); c.rect(13 - rec, ty - 1, 3, 1, metal)
        else:
            c.rect(9, ty + 1, 2, 3, jac); c.rect(9, ty + 3, 3, 2, jac)
            c.rect(11, ty + 3, 2, 2, skin)
            c.rect(12, ty + 1, 3, 3, metald); c.rect(12, ty + 1, 3, 1, metal)
        # head (profile)
        hx = 3 - rec
        cel(c, hx, hy, 11, 10, skin, skins)
        c.rect(hx + 1, hy, 9, 1, hel); c.rect(hx, hy + 1, 11, 3, hel)
        c.hline(hx, hy + 3, 11, C(b, 7)); c.hline(hx + 8, hy + 3, 4, hel)     # brim sticks out front
        c.hline(hx + 2, hy + 1, 3, helh)
        c.rect(hx, hy + 4, 3, 4, hel); c.rect(hx, hy + 7, 3, 1, C(b, 7))      # back flap
        c.hline(hx + 3, hy + 4, 8, gold)
        eye(c, hx + 6, hy + 5, b, px=1, py=1, h=3)
        c.px(hx + 11, hy + 6, skin)                                           # nose
        c.hline(hx + 8, hy + 8, 3, skins)
        c.px(hx + 6, hy + 8, C(b, 8))
    return finish(c)


def player_dead(frame):
    """0: dazed and wobbling, 1: toppling over, 2: flat on the floor"""
    b = 0
    c = Canvas(16, 32)
    jac, jacs = C(b, 4), C(b, 5)
    pan, pans = C(b, 6), C(b, 7)
    skin, skins = C(b, 2), C(b, 3)
    hel = C(b, 9)
    boot, sole = C(b, 13), C(b, 14)
    gold = C(b, 8)
    star = C(b, 8)
    if frame == 0:
        hy = 6
        boots(c, 4, hy + 15, 3, FEET, pan, pans, boot, sole, -1, 0)
        boots(c, 9, hy + 15, 3, FEET, pan, pans, boot, sole, 1, 1)
        cel(c, 4, hy + 9, 8, 6, jac, jacs)
        c.rect(1, hy + 8, 3, 3, jac); c.rect(0, hy + 10, 3, 2, skin)
        c.rect(12, hy + 8, 3, 3, jac); c.rect(13, hy + 10, 3, 2, skin)
        _player_head_down(c, hy, b, ko=True)
        c.px(3, 2, star); c.px(4, 1, star); c.px(4, 3, star); c.px(5, 2, star)       # dizzy stars
        c.px(11, 1, star); c.px(12, 0, star); c.px(12, 2, star); c.px(13, 1, star)
    elif frame == 1:
        # slumping sideways
        boots(c, 1, 19, 3, FEET, pan, pans, boot, sole, -1, 0)
        c.rect(4, 17, 6, 4, pan); c.rect(6, 21, 5, 3, pan); c.rect(9, 22, 4, 3, boot)
        cel(c, 3, 11, 8, 8, jac, jacs)
        c.hline(3, 17, 8, boot); c.px(6, 17, gold)
        c.rect(0, 14, 3, 3, jac); c.rect(0, 16, 2, 2, skin)
        cel(c, 6, 5, 10, 9, skin, skins)
        c.rect(7, 5, 8, 1, hel); c.rect(6, 6, 10, 3, hel); c.hline(6, 8, 10, C(b, 7))
        c.hline(6, 9, 10, gold)
        for ex in (8, 12):
            c.px(ex, 10, OUT); c.px(ex + 2, 10, OUT); c.px(ex + 1, 11, OUT)
            c.px(ex, 12, OUT); c.px(ex + 2, 12, OUT)
    else:
        # flat on the back, seen from above
        boots(c, 0, 16, 4, FEET - 4, pan, pans, boot, sole, 1, 0)
        c.rect(0, 15, 5, 3, boot); c.rect(0, 20, 5, 3, boot)
        c.rect(3, 15, 5, 3, pan); c.rect(3, 20, 5, 3, pan)
        cel(c, 6, 13, 6, 12, jac, jacs)
        c.rect(7, 17, 4, 2, gold)
        c.rect(7, 11, 3, 3, jac); c.rect(7, 25, 3, 3, jac)
        cel(c, 10, 13, 6, 12, skin, skins)
        c.rect(10, 13, 6, 3, hel); c.rect(10, 22, 6, 3, hel)
        c.px(13, 17, OUT); c.px(15, 17, OUT); c.px(14, 18, OUT)
        c.px(13, 20, OUT); c.px(15, 20, OUT); c.px(14, 19, OUT)
    c = finish(c)
    bl = C(1, 9)
    if frame == 2:
        c.rect(1, 25, 6, 1, bl); c.px(4, 26, bl)
    return c


# ---------------------------------------------------------------------------
# ZOMBIES
# ---------------------------------------------------------------------------
def zombie(b, view, frame, P):
    """frame: 0/1 shamble, 2 attack.  P describes the type (sizes + decoration callbacks)"""
    c = Canvas(16, 32)
    skin, skins = C(b, 2), C(b, 3)
    ca, cas = C(b, 4), C(b, 5)
    cb, cbs = C(b, 6), C(b, 7)
    boot, sole = C(b, 13), C(b, 14)
    ph = frame if frame < 2 else 0
    atk = frame == 2
    bob = 1 if atk else ph
    hw, hh, tw = P.get('hw', 12), P.get('hh', 10), P.get('tw', 8)
    hx = 8 - hw // 2
    hy = P.get('top', 3) + bob
    ty = hy + hh - 1
    legtop = ty + 6
    tx = 8 - tw // 2
    lf = [(0, 2), (2, 0)][ph] if not atk else (0, 0)
    stride = P.get('stride', 2)
    if view in ('down', 'up'):
        lx = tx
        rx = tx + tw - 3
        boots(c, lx, legtop, 3, FEET, cb, cbs, boot, sole, -1, lf[0])
        boots(c, rx, legtop, 3, FEET, cb, cbs, boot, sole, 1, lf[1])
        cel(c, tx, ty, tw, 6, ca, cas)
        if view == 'down' and 'torso' in P:
            P['torso'](c, tx, ty, tw, b)
        if view == 'up' and 'back' in P:
            P['back'](c, tx, ty, tw, b)
        # arms: shuffling arms hang, hands up when attacking
        if atk:
            c.rect(tx - 2, ty - 2, 2, 5, ca); c.rect(tx + tw, ty - 2, 2, 5, ca)
            ball(c, tx - 3, ty - 5, 3, 3, skin); ball(c, tx + tw, ty - 5, 3, 3, skin)
        else:
            sw = 1 if ph else 0
            c.rect(tx - 2, ty + 1, 2, 3, ca); c.rect(tx + tw, ty + 1, 2, 3, ca)
            ball(c, tx - 3, ty + 3 - sw, 3, 3, skin); ball(c, tx + tw, ty + 3 - (1 - sw), 3, 3, skin)
        if view == 'down':
            cel(c, hx, hy, hw, hh, skin, skins)
            P['face'](c, hx, hy, hw, b, atk)
        else:
            cel(c, hx, hy, hw, hh, skin, skins)
            P['hair_back'](c, hx, hy, hw, b)
    else:
        offs = [(0, 0), (stride, -stride)][ph] if not atk else (1, -1)
        boots(c, 5 + offs[1], legtop, 3, FEET, cbs, cbs, C(b, 14), OUT, 1)
        boots(c, 7 + offs[0], legtop, 3, FEET, cb, cbs, boot, sole, 1)
        sw = max(6, tw - 2)
        cel(c, 8 - sw // 2, ty, sw, 6, ca, cas)
        if 'side' in P:
            P['side'](c, 8 - sw // 2, ty, sw, b)
        # arms stretched out in front
        ay = ty + (0 if atk else 1)
        c.rect(9, ay, 4, 2, ca if not atk else skin)
        ball(c, 12, ay - 1 - (1 if atk else 0), 3, 4, skin)
        hx2 = hx + 1
        cel(c, hx2, hy, hw - 1, hh, skin, skins)
        P['face_side'](c, hx2, hy, hw - 1, b, atk)
    return finish(c, b)


def _zeyes(c, hx, hy, hw, b, atk, mad=True, pupil=OUT, px=(1, 0), size=(3, 4)):
    w, h = size
    el, er = hx + 2, hx + hw - 2 - w
    eye(c, el, hy + 3, b, px=px[0], py=1, w=w, h=h, pupil=pupil)
    eye(c, er, hy + 3, b, px=px[1], py=1, w=w, h=h, pupil=pupil)
    if mad:
        brow(c, el, hy + 3, True); brow(c, er, hy + 3, False)


def shambler(view, frame):
    b = 1

    def face(c, hx, hy, hw, bk, atk):
        _zeyes(c, hx, hy, hw, bk, atk, mad=atk, px=(1, 0))
        mouth(c, hx + 3, hy + 7, hw - 6, bk, atk)
        c.px(hx + hw - 3, hy + 8, C(bk, 9))                       # drool / blood
        # messy hair tufts
        for x in (hx + 1, hx + 4, hx + 8):
            c.rect(x, hy - 1, 2, 2, C(bk, 13))
        c.hline(hx + 1, hy, hw - 2, C(bk, 13)); c.px(hx + 6, hy - 2, C(bk, 13))

    def hair_back(c, hx, hy, hw, bk):
        ball(c, hx, hy, hw, 8, C(bk, 13)); c.hline(hx + 1, hy + 7, hw - 2, C(bk, 14))
        for x in (hx + 1, hx + 4, hx + 8):
            c.rect(x, hy - 1, 2, 2, C(bk, 13))
        c.px(hx + 4, hy + 4, C(bk, 3))

    def face_side(c, hx, hy, hw, bk, atk):
        eye(c, hx + hw - 5, hy + 3, bk, px=1, py=1)
        if atk:
            brow(c, hx + hw - 5, hy + 3, False)
        mouth(c, hx + hw - 5, hy + 7, 4, bk, atk)
        c.px(hx + hw, hy + 5, C(bk, 2))
        c.rect(hx, hy, 6, 3, C(bk, 13)); c.rect(hx + 1, hy - 1, 2, 2, C(bk, 13)); c.rect(hx + 4, hy - 1, 2, 2, C(bk, 13))
        c.hline(hx, hy + 3, 3, C(bk, 13))

    def torso(c, tx, ty, tw, bk):
        c.rect(tx + 1, ty + 1, 3, 3, C(bk, 3))                   # torn hole showing skin
        c.px(tx + 2, ty + 2, C(bk, 9))
        c.hline(tx, ty + 5, tw, C(bk, 7))
        c.px(tx + 6, ty + 3, C(bk, 5)); c.px(tx + 5, ty + 5, C(bk, 3))
        c.px(tx + tw - 2, ty, C(bk, 9))

    def back(c, tx, ty, tw, bk):
        c.line(tx + 2, ty + 1, tx + 5, ty + 4, C(bk, 5)); c.px(tx + 5, ty + 1, C(bk, 3)); c.px(tx + 2, ty + 4, C(bk, 9))

    P = dict(hw=12, hh=10, tw=8, top=3, face=face, hair_back=hair_back, face_side=face_side, torso=torso, back=back,
             side=lambda c, x, y, w, bk: (c.px(x + 2, y + 2, C(bk, 3)), c.hline(x, y + 5, w, C(bk, 7))))
    return zombie(b, view, frame, P)


def rusher(view, frame):
    b = 2

    def face(c, hx, hy, hw, bk, atk):
        _zeyes(c, hx, hy, hw, bk, atk, mad=True, pupil=C(bk, 8), px=(1, 0), size=(3, 3))
        c.rect(hx + 2, hy + 6, hw - 4, 3 + (1 if atk else 0), OUT)
        for x in range(hx + 3, hx + hw - 3, 2):
            c.px(x, hy + 6, C(bk, WHITE)); c.px(x + 1, hy + 8 + (1 if atk else 0), C(bk, WHITE))
        for x in (hx + 2, hx + 5, hx + 8):                          # spiky mohawk-ish hair
            c.px(x, hy - 1, C(bk, 14)); c.px(x + 1, hy - 2, C(bk, 14)); c.px(x + 1, hy - 1, C(bk, 14))
        c.hline(hx + 1, hy, hw - 2, C(bk, 14))

    def hair_back(c, hx, hy, hw, bk):
        ball(c, hx, hy, hw, 7, C(bk, 14)); c.hline(hx + 1, hy + 6, hw - 2, C(bk, 5))
        for x in (hx + 2, hx + 5, hx + 8):
            c.px(x + 1, hy - 1, C(bk, 14)); c.px(x + 1, hy - 2, C(bk, 14))

    def face_side(c, hx, hy, hw, bk, atk):
        eye(c, hx + hw - 5, hy + 3, bk, px=1, py=0, h=3, pupil=C(bk, 8))
        brow(c, hx + hw - 5, hy + 3, False)
        c.rect(hx + hw - 6, hy + 6, 6, 3, OUT)
        for x in (hx + hw - 5, hx + hw - 3):
            c.px(x, hy + 6, C(bk, WHITE))
        c.px(hx + hw, hy + 4, C(bk, 2))
        c.rect(hx, hy, hw - 3, 2, C(bk, 14)); c.px(hx + 2, hy - 1, C(bk, 14)); c.px(hx + 5, hy - 1, C(bk, 14))

    def torso(c, tx, ty, tw, bk):                                   # torn red shirt with a skull-ish mark
        c.rect(tx + 2, ty + 1, 4, 3, C(bk, 12)); c.px(tx + 3, ty + 2, OUT); c.px(tx + 5, ty + 2, OUT)
        c.hline(tx, ty + 5, tw, C(bk, 5))

    def back(c, tx, ty, tw, bk):
        c.vline(tx + 3, ty, 6, C(bk, 5)); c.px(tx + 5, ty + 2, C(bk, 9))

    P = dict(hw=10, hh=10, tw=8, top=3, stride=3, face=face, hair_back=hair_back, face_side=face_side,
             torso=torso, back=back, side=lambda c, x, y, w, bk: c.hline(x + 1, y + 3, 3, C(bk, 5)))
    return zombie(b, view, frame, P)


def spitter(view, frame):
    b = 3

    def face(c, hx, hy, hw, bk, atk):
        _zeyes(c, hx, hy, hw, bk, atk, mad=False, px=(0, 1), size=(3, 3))
        # big open mouth full of slime
        h = 4 if atk else 2
        c.rect(hx + 2, hy + 7 - (1 if atk else 0), hw - 4, h, OUT)
        c.rect(hx + 3, hy + 8 - (1 if atk else 0), hw - 6, max(1, h - 1), C(bk, 8) if atk else OUT)
        c.px(hx + 2, hy + 9 + (1 if atk else 0), C(bk, 8))
        c.px(hx + 4, hy - 1, C(bk, 8)); c.px(hx + 5, hy - 2, C(bk, 8))   # one slimy hair sprout
        c.px(hx + 5, hy - 1, C(bk, 8))

    def hair_back(c, hx, hy, hw, bk):
        ball(c, hx, hy, hw, 6, C(bk, 12)); c.hline(hx + 1, hy + 5, hw - 2, C(bk, 3))
        c.px(hx + 4, hy - 1, C(bk, 8)); c.px(hx + 5, hy - 2, C(bk, 8)); c.px(hx + 5, hy - 1, C(bk, 8))

    def face_side(c, hx, hy, hw, bk, atk):
        eye(c, hx + hw - 5, hy + 3, bk, px=1, py=1, h=3)
        h = 4 if atk else 2
        c.rect(hx + hw - 5, hy + 7 - (1 if atk else 0), 5, h, OUT)
        if atk:
            c.rect(hx + hw - 4, hy + 7, 4, 2, C(bk, 8))
        c.px(hx + 4, hy - 1, C(bk, 8)); c.px(hx + 5, hy - 2, C(bk, 8))

    def torso(c, tx, ty, tw, bk):                                   # glowing toxic belly
        ball(c, tx + 1, ty + 1, tw - 2, 5, C(bk, 9)); c.rect(tx + 3, ty + 2, tw - 6, 3, C(bk, 8))
        c.px(tx + 3, ty + 2, C(bk, WHITE)); c.px(tx + tw - 4, ty + 4, C(bk, 12))

    def back(c, tx, ty, tw, bk):
        ball(c, tx + 1, ty + 1, tw - 2, 5, C(bk, 5)); c.px(tx + 3, ty + 2, C(bk, 9)); c.px(tx + tw - 4, ty + 3, C(bk, 9))

    P = dict(hw=10, hh=9, tw=10, top=4, face=face, hair_back=hair_back, face_side=face_side, torso=torso, back=back,
             side=lambda c, x, y, w, bk: (ball(c, x + w - 4, y + 1, 5, 5, C(bk, 9)), c.rect(x + w - 3, y + 2, 3, 3, C(bk, 8))))
    return zombie(b, view, frame, P)


def stalker(view, frame):
    b = 4

    def face(c, hx, hy, hw, bk, atk):
        hood = C(bk, 5)
        c.rect(hx, hy, hw, 3, hood); c.hline(hx, hy + 3, hw, C(bk, 4)); c.px(hx, hy + 3, hood); c.px(hx + hw - 1, hy + 3, hood)
        c.px(hx + 1, hy - 1, hood); c.px(hx + hw - 2, hy - 1, hood)
        # glowing slit eyes
        for ex in (hx + 2, hx + hw - 5):
            c.rect(ex, hy + 4, 3, 2, C(bk, 8)); c.px(ex + 1, hy + 4, C(bk, 15))
        brow(c, hx + 2, hy + 5, True); brow(c, hx + hw - 5, hy + 5, False)
        mouth(c, hx + 3, hy + 7, hw - 6, bk, atk)

    def hair_back(c, hx, hy, hw, bk):
        ball(c, hx, hy, hw, 9, C(bk, 5)); c.vline(hx + hw // 2, hy + 1, 8, C(bk, 4))
        c.px(hx + 1, hy - 1, C(bk, 5)); c.px(hx + hw - 2, hy - 1, C(bk, 5))

    def face_side(c, hx, hy, hw, bk, atk):
        c.rect(hx, hy, hw, 4, C(bk, 5)); c.px(hx + 1, hy - 1, C(bk, 5)); c.rect(hx, hy + 4, 3, 4, C(bk, 5))
        ex = hx + hw - 4
        c.rect(ex, hy + 4, 3, 2, C(bk, 8)); c.px(ex + 1, hy + 4, C(bk, 15))
        brow(c, ex, hy + 5, False)
        mouth(c, hx + hw - 5, hy + 7, 4, bk, atk)

    def torso(c, tx, ty, tw, bk):
        c.line(tx + 1, ty, tx + 3, ty + 5, C(bk, 3)); c.line(tx + tw - 2, ty, tx + tw - 4, ty + 5, C(bk, 3))
        c.px(tx + 3, ty + 3, C(bk, 8)); c.px(tx + 4, ty + 3, C(bk, 8))

    def back(c, tx, ty, tw, bk):
        c.vline(tx + tw // 2, ty, 6, C(bk, 3))

    P = dict(hw=10, hh=10, tw=6, top=1, face=face, hair_back=hair_back, face_side=face_side, torso=torso, back=back,
             side=lambda c, x, y, w, bk: c.px(x + 2, y + 2, C(bk, 3)))
    c = zombie(b, view, frame, P)
    # long pale claws on the fingertips
    cl = C(b, 12)
    c.p = [row[:] for row in c.p]
    ty = 1 + (1 if frame == 2 else (frame if frame < 2 else 0)) + 9
    if view in ('down', 'up'):
        yy = ty + 6 if frame != 2 else ty - 6
        c.vline(2, yy, 3, cl); c.vline(13, yy, 3, cl)
        c.px(1, yy + 1, OUT); c.px(14, yy + 1, OUT)
    else:
        yy = ty + (0 if frame == 2 else 1) - 1
        c.hline(15, yy, 1, cl)
    return c


def zombie_corpse(bank, frame, base_w=14):
    """16x16 corpse (frame 0 = collapsing, 1 = flat)"""
    b = bank
    c = Canvas(16, 16)
    skin, skins = C(b, 2), C(b, 3)
    ca, cas = C(b, 4), C(b, 5)
    cb = C(b, 6)
    if frame == 0:
        cel(c, 2, 5, 8, 6, ca, cas)
        c.rect(1, 9, 5, 4, cb); c.rect(8, 10, 5, 3, cb); c.rect(12, 10, 3, 3, C(b, 13))
        cel(c, 8, 1, 7, 7, skin, skins)
        c.px(10, 3, OUT); c.px(12, 3, OUT); c.px(11, 4, OUT); c.px(10, 5, OUT); c.px(12, 5, OUT)
        c.rect(0, 5, 3, 2, skin)
    else:
        cel(c, 1, 5, 9, 6, ca, cas)
        c.rect(2, 11, 4, 3, cb); c.rect(6, 11, 4, 3, cb); c.rect(0, 12, 3, 3, C(b, 13))
        cel(c, 9, 3, 7, 8, skin, skins)
        c.px(11, 5, OUT); c.px(13, 5, OUT); c.px(12, 6, OUT); c.px(11, 7, OUT); c.px(13, 7, OUT)
        c.hline(11, 9, 3, OUT)
        c.rect(5, 2, 3, 3, skin)
    return finish(c, b)


# ---------------------------------------------------------------------------
# BRUTE 32x32
# ---------------------------------------------------------------------------
def brute(view, frame):
    b = 5
    c = Canvas(32, 32)
    skin, skins = C(b, 2), C(b, 3)
    ar, ars = C(b, 4), C(b, 5)
    cb, cbs = C(b, 6), C(b, 7)
    org = C(b, 8)
    boot, sole = C(b, 13), C(b, 14)
    wh = C(b, WHITE)
    ph = frame if frame < 2 else 0
    atk = frame == 2
    bob = 0 if atk else ph
    yb = 29
    hy = 1 + bob + (2 if atk else 0)
    if view in ('down', 'up'):
        lf = [(0, 3), (3, 0)][ph] if not atk else (0, 0)
        for x, tf, l in ((7, -1, lf[0]), (17, 1, lf[1])):
            yy = yb - l
            c.rect(x, 21 + bob, 8, yy - 3 - 21 - bob + 1, cb); c.vline(x + 7, 21 + bob, yy - 3 - 21 - bob + 1, cbs)
            sx = x - (1 if tf < 0 else 0)
            c.rect(sx, yy - 3, 9, 4, boot); c.hline(sx, yy, 9, sole)
        # big round belly
        cel(c, 6, 10 + bob, 20, 13, ar, ars)
        if view == 'down':
            ball(c, 10, 13 + bob, 12, 8, ars); c.rect(11, 14 + bob, 10, 6, ar)
            c.rect(14, 17 + bob, 4, 3, C(b, 10)); c.px(15, 17 + bob, wh)      # buckle
            c.px(12, 15 + bob, org); c.px(19, 15 + bob, org)
        else:
            c.vline(15, 11 + bob, 11, ars); c.vline(16, 11 + bob, 11, ar)
            c.rect(9, 13 + bob, 4, 3, ars); c.rect(19, 14 + bob, 4, 3, ars)
        # shoulders
        ball(c, 1, 9 + bob, 9, 7, ar); c.px(4, 11 + bob, org); c.px(6, 11 + bob, org)
        ball(c, 22, 9 + bob, 9, 7, ar); c.px(25, 11 + bob, org); c.px(27, 11 + bob, org)
        # arms and big round fists
        if atk:
            c.rect(2, 3, 5, 8, skin); ball(c, 0, 0, 9, 7, skin); c.vline(8, 1, 5, skins)
            c.rect(25, 3, 5, 8, skin); ball(c, 23, 0, 9, 7, skin); c.vline(31, 1, 5, skins)
        else:
            c.rect(2, 15 + bob, 5, 6, skin); c.vline(6, 15 + bob, 6, skins)
            cel(c, 0, 20 + bob, 9, 8, skin, skins)
            c.rect(25, 15 + bob, 5, 6, skin); c.vline(29, 15 + bob, 6, skins)
            cel(c, 23, 20 + bob, 9, 8, skin, skins)
        # small head (huge body, tiny head is the joke) with underbite
        cel(c, 9, hy, 14, 11, skin, skins)
        if view == 'down':
            c.rect(10, hy, 12, 3, C(b, 13)); c.hline(10, hy + 2, 12, C(b, 14))
            eye(c, 11, hy + 3, b, px=1, py=1, w=4, h=4); eye(c, 17, hy + 3, b, px=1, py=1, w=4, h=4)
            c.hline(11, hy + 2, 3, OUT); c.px(14, hy + 3, OUT); c.hline(18, hy + 2, 3, OUT); c.px(17, hy + 3, OUT)
            c.rect(11, hy + 8, 10, 3 if atk else 2, OUT)
            c.px(12, hy + 7, wh); c.px(13, hy + 7, wh); c.px(19, hy + 7, wh); c.px(18, hy + 7, wh)  # tusks
            c.px(14, hy + 8, wh); c.px(17, hy + 8, wh)
        else:
            ball(c, 9, hy, 14, 9, C(b, 13)); c.hline(10, hy + 8, 12, C(b, 14))
            c.px(15, hy + 3, C(b, 14)); c.px(16, hy + 3, C(b, 14))
    else:
        offs = [(0, 0), (4, -4)][ph] if not atk else (2, -2)
        for x, l, col, shd, bt, sl in ((9 + offs[1], 0, cbs, cbs, C(b, 14), OUT), (12 + offs[0], 0, cb, cbs, boot, sole)):
            c.rect(x, 21 + bob, 8, yb - 3 - 21 - bob + 1, col); c.vline(x + 7, 21 + bob, yb - 3 - 21 - bob + 1, shd)
            c.rect(x, yb - 3, 10, 4, bt); c.hline(x, yb, 10, sl)
        cel(c, 6, 10 + bob, 16, 13, ar, ars)
        ball(c, 10, 13 + bob, 9, 7, ars); c.px(13, 14 + bob, org)
        ball(c, 2, 9 + bob, 10, 7, ar); c.px(5, 11 + bob, org)
        ay = 13 + bob - (6 if atk else 0)
        c.rect(13, ay, 8, 5, skin); c.hline(13, ay + 4, 8, skins)
        cel(c, 20, ay - 2, 10, 10, skin, skins)
        cel(c, 12, hy + 1, 13, 11, skin, skins)
        c.rect(12, hy + 1, 13, 3, C(b, 13)); c.rect(13, hy, 11, 1, C(b, 13)); c.hline(12, hy + 3, 13, C(b, 14))
        c.rect(12, hy + 4, 3, 5, C(b, 13))
        eye(c, 19, hy + 4, b, px=2, py=1, w=4, h=4); c.hline(19, hy + 3, 3, OUT); c.px(22, hy + 4, OUT)
        c.rect(18, hy + 9, 7, 3 if atk else 2, OUT); c.px(19, hy + 8, wh); c.px(23, hy + 8, wh)
    return finish(c, b)


def brute_corpse(frame):
    b = 5
    c = Canvas(32, 16)
    skin, skins = C(b, 2), C(b, 3)
    ar, ars = C(b, 4), C(b, 5)
    cb = C(b, 6)
    if frame == 0:
        cel(c, 4, 3, 18, 10, ar, ars)
        c.rect(0, 8, 8, 6, cb); c.rect(22, 10, 8, 4, cb)
        cel(c, 21, 1, 10, 9, skin, skins)
        c.px(24, 4, OUT); c.px(26, 4, OUT); c.px(25, 5, OUT); c.px(24, 6, OUT); c.px(26, 6, OUT)
        ball(c, 3, 1, 9, 5, ar)
    else:
        cel(c, 2, 5, 20, 9, ar, ars)
        cel(c, 20, 3, 11, 10, skin, skins)
        c.px(23, 6, OUT); c.px(25, 6, OUT); c.px(24, 7, OUT); c.px(23, 8, OUT); c.px(25, 8, OUT)
        c.hline(23, 10, 5, OUT)
        c.rect(0, 9, 6, 5, cb); ball(c, 8, 1, 9, 5, skin)
    return finish(c, b)
