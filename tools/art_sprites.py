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


# ---------------------------------------------------------------------------
# limb helpers
# ---------------------------------------------------------------------------
def leg(c, x, ytop, w, ybot, cloth, shade, boot, sole, boot_h=2, toe=0, lift=0):
    """leg from ytop down to ybot (inclusive).  lift raises the foot."""
    yb = ybot - lift
    c.rect(x, ytop, w, max(1, yb - ytop - boot_h + 1), cloth)
    c.vline(x + w - 1, ytop, max(1, yb - ytop - boot_h + 1), shade)
    c.rect(x - (1 if toe < 0 else 0), yb - boot_h + 1, w + abs(toe) + (1 if toe == 0 else 0), boot_h, boot)
    c.hline(x - (1 if toe < 0 else 0), yb, w + abs(toe) + (1 if toe == 0 else 0), sole)


def arm(c, x, y, w, h, cloth, shade, hand=None, hand_h=2):
    c.rect(x, y, w, h, cloth)
    c.vline(x + w - 1, y, h, shade)
    if hand is not None:
        c.rect(x, y + h, w, hand_h, hand)


def finish(c, outline_slot=1, bank=0):
    c.outline(C(bank, outline_slot))
    return c


# ---------------------------------------------------------------------------
# PLAYER "Rook"
# ---------------------------------------------------------------------------
def player(view, frame, pose='walk'):
    b = 0
    c = Canvas(16, 32)
    ph = frame if pose == 'walk' else 0
    bob = [0, 1, 0, 1][ph]
    lift = [(0, 0), (2, 0), (0, 0), (0, 2)][ph]
    jac, jacs = C(b, 4), C(b, 5)
    pan, pans = C(b, 6), C(b, 7)
    skin, skins = C(b, 2), C(b, 3)
    hel, helh = C(b, 9), C(b, 12)
    boot, sole = C(b, 13), C(b, 14)
    gold = C(b, 8)
    metal, metald = C(b, 10), C(b, 11)
    if pose == 'dead':
        return player_dead(frame)
    if view == 'down':
        yb = 24
        leg(c, 4, 16 + bob, 4, yb, pan, pans, boot, sole, lift=lift[0], toe=-1)
        leg(c, 8, 16 + bob, 4, yb, pan, pans, boot, sole, lift=lift[1], toe=1)
        # torso
        c.rect(3, 9 + bob, 10, 7, jac)
        c.vline(12, 9 + bob, 7, jacs); c.hline(3, 15 + bob, 10, jacs)
        c.rect(5, 10 + bob, 6, 4, jacs)
        c.hline(5, 11 + bob, 6, gold)
        c.hline(3, 15 + bob, 10, boot); c.px(7, 15 + bob, metal); c.px(8, 15 + bob, metal)
        # arms
        if pose == 'reload':
            arm(c, 2, 10 + bob, 2, 4, jac, jacs)
            arm(c, 12, 10 + bob, 2, 4, jac, jacs)
            c.rect(4, 13 + bob, 8, 2, skin)
            c.rect(6, 12 + bob, 4, 3, metald); c.px(7, 12 + bob, metal)
        elif pose == 'shoot':
            arm(c, 2, 10 + bob, 2, 6, jac, jacs, skin)
            arm(c, 12, 10 + bob, 2, 7, jac, jacs, skin)
            c.rect(12, 19 + bob, 3, 4, metald); c.px(13, 19 + bob, metal)
        else:
            arm(c, 1, 10 + bob, 2, 6, jac, jacs, skin)
            arm(c, 13, 10 + bob, 2, 6, jac, jacs, skin)
            c.rect(13, 18 + bob, 2, 3, metald); c.px(13, 18 + bob, metal)
        # head
        hb = bob
        c.rect(4, 1 + hb, 8, 4, hel)
        c.rect(5, 1 + hb, 3, 1, helh)
        c.hline(3, 5 + hb, 10, hel)
        c.hline(3, 5 + hb, 1, C(b, 7)); c.hline(12, 5 + hb, 1, C(b, 7))
        c.rect(5, 6 + hb, 6, 3, skin)
        c.hline(5, 6 + hb, 6, gold)             # goggles
        c.px(6, 6 + hb, C(b, 15)); c.px(9, 6 + hb, C(b, 15))
        c.hline(6, 8 + hb, 4, skins)
        c.px(5, 7 + hb, skins)
    elif view == 'up':
        yb = 24
        leg(c, 4, 16 + bob, 4, yb, pan, pans, boot, sole, lift=lift[0], toe=-1)
        leg(c, 8, 16 + bob, 4, yb, pan, pans, boot, sole, lift=lift[1], toe=1)
        c.rect(3, 9 + bob, 10, 7, jac); c.vline(12, 9 + bob, 7, jacs)
        # backpack
        c.rect(4, 9 + bob, 8, 7, C(b, 13)); c.vline(11, 9 + bob, 7, C(b, 14)); c.hline(4, 15 + bob, 8, C(b, 14))
        c.rect(5, 10 + bob, 6, 2, C(b, 14)); c.hline(5, 9 + bob, 6, gold)
        c.vline(7, 12 + bob, 3, C(b, 14)); c.vline(9, 12 + bob, 3, C(b, 14))
        arm(c, 1, 10 + bob, 2, 6, jac, jacs, skin)
        arm(c, 13, 10 + bob, 2, 6, jac, jacs, skin)
        if pose == 'shoot':
            c.rect(11, 6 + bob, 4, 3, skin); c.rect(13, 3 + bob, 2, 4, metald); c.px(13, 3 + bob, metal)
        if pose == 'reload':
            c.rect(4, 13 + bob, 8, 2, skin)
        c.rect(4, 1 + bob, 8, 7, hel)
        c.rect(5, 1 + bob, 3, 2, helh)
        c.hline(4, 5 + bob, 8, C(b, 7)); c.hline(3, 6 + bob, 10, hel)
        c.rect(6, 8 + bob, 4, 1, skins)
    else:  # side, facing right
        yb = 24
        offs = [(0, 0), (2, -2), (0, 0), (-2, 2)][ph]
        # back leg first
        leg(c, 6 + offs[1], 16 + bob, 4, yb, pans, pans, C(b, 14), C(b, 1), lift=(1 if offs[1] > 0 and ph else 0), toe=1)
        leg(c, 7 + offs[0], 16 + bob, 4, yb, pan, pans, boot, sole, lift=(1 if offs[0] > 0 and ph else 0), toe=1)
        rec = 1 if pose == 'shoot' else 0
        # torso (shifted back on recoil)
        c.rect(5 - rec, 9 + bob, 7, 7, jac); c.vline(5 - rec, 9 + bob, 7, jacs)
        c.rect(7 - rec, 10 + bob, 4, 4, jacs); c.hline(7 - rec, 11 + bob, 4, gold)
        c.hline(5 - rec, 15 + bob, 7, boot); c.px(10 - rec, 15 + bob, metal)
        # backpack
        c.rect(2 - rec, 9 + bob, 4, 8, C(b, 13)); c.vline(2 - rec, 9 + bob, 8, C(b, 14)); c.hline(2 - rec, 16 + bob, 4, C(b, 14))
        c.hline(2 - rec, 9 + bob, 4, gold)
        # arm + pistol
        if pose == 'reload':
            c.rect(8, 11 + bob, 4, 3, jac); c.rect(11, 12 + bob, 2, 2, skin)
            c.rect(10, 9 + bob, 2, 3, metald); c.px(10, 9 + bob, metal)
        elif pose == 'shoot':
            c.rect(9 - rec, 11 + bob, 4, 2, jac); c.rect(13 - rec, 11 + bob, 2, 2, skin)
            c.rect(14 - rec, 10 + bob, 2, 2, metald); c.px(15 - rec, 10 + bob, metal)
        else:
            c.rect(9, 10 + bob, 2, 3, jac); c.rect(10, 12 + bob, 3, 2, jac)
            c.rect(12, 12 + bob, 2, 2, skin); c.rect(13, 11 + bob, 2, 2, metald); c.px(14, 11 + bob, metal)
        # head
        hb = bob
        c.rect(4 - rec, 1 + hb, 8, 5, hel); c.rect(5 - rec, 1 + hb, 4, 1, helh)
        c.hline(4 - rec, 5 + hb, 9, C(b, 7))
        c.rect(8 - rec, 6 + hb, 4, 3, skin)
        c.hline(9 - rec, 6 + hb, 3, gold); c.px(10 - rec, 6 + hb, C(b, 15))
        c.hline(8 - rec, 8 + hb, 3, skins)
        c.rect(5 - rec, 6 + hb, 3, 2, hel)
    return finish(c)


def player_dead(frame):
    """0: staggering back / kneeling, 1: falling, 2: lying flat"""
    b = 0
    c = Canvas(16, 32)
    jac, jacs = C(b, 4), C(b, 5)
    pan, pans = C(b, 6), C(b, 7)
    skin = C(b, 2)
    hel = C(b, 9)
    boot = C(b, 13)
    if frame == 0:
        c.rect(5, 12, 7, 7, jac); c.vline(5, 12, 7, jacs)
        c.rect(3, 12, 3, 8, C(b, 13))
        c.rect(6, 5, 8, 4, hel); c.rect(8, 9, 4, 3, skin); c.px(10, 10, C(b, 8))
        c.rect(5, 19, 5, 5, pan); c.rect(9, 20, 5, 4, pan); c.rect(5, 23, 3, 2, boot); c.rect(11, 23, 4, 2, boot)
        c.rect(11, 13, 3, 2, jac); c.px(14, 14, C(b, 9))
        c.rect(12, 14, 1, 1, C(b, 8))
    elif frame == 1:
        c.rect(2, 16, 9, 6, jac); c.rect(2, 16, 9, 2, C(b, 13))
        c.rect(10, 14, 5, 5, hel); c.rect(12, 18, 3, 2, skin)
        c.rect(5, 21, 8, 3, pan); c.rect(11, 22, 4, 3, boot)
        c.rect(0, 20, 3, 2, skin)
    else:
        c.rect(0, 18, 4, 6, hel); c.rect(0, 20, 3, 3, skin)
        c.rect(3, 18, 8, 6, jac); c.vline(3, 18, 6, C(b, 13)); c.hline(3, 23, 8, jacs)
        c.rect(10, 19, 6, 4, pan); c.rect(14, 19, 2, 4, boot)
        c.rect(5, 16, 5, 2, C(b, 13))
        c.rect(2, 19, 2, 2, skin)
    c = finish(c)
    # blood
    bl = C(0, 9)
    if frame == 2:
        c.rect(5, 24, 8, 2, bl) ; c.px(3, 24, bl); c.px(9, 25, bl)
    if frame == 1:
        c.rect(3, 22, 3, 1, bl)
    return c


# ---------------------------------------------------------------------------
# ZOMBIES (shared humanoid skeleton, per type parameters)
# ---------------------------------------------------------------------------
def zombie_common(bank, view, frame, P):
    """frame: 0/1 walk, 2 attack.  P holds per-type look."""
    b = bank
    c = Canvas(16, 32)
    skin, skins = C(b, 2), C(b, 3)
    ca, cas = C(b, 4), C(b, 5)
    cb, cbs = C(b, 6), C(b, 7)
    eye = C(b, 8)
    blood = C(b, 9)
    boot, sole = C(b, 13), C(b, 14)
    ph = frame if frame < 2 else 0
    atk = frame == 2
    hunch = P.get('hunch', 2)
    stride = P.get('stride', 2)
    bob = [0, 1][ph] if not atk else 1
    top = P.get('top', 1) + hunch
    lw = P.get('leg_w', 4)
    torso_w = P.get('torso_w', 10)
    tx = 8 - torso_w // 2
    head_w = P.get('head_w', 8)
    hx = 8 - head_w // 2
    ytorso = top + 7 + bob
    legtop = ytorso + 7
    yb = 24
    if view in ('down', 'up'):
        lf = [(0, 2), (2, 0)][ph] if not atk else (0, 0)
        leg(c, 8 - lw - 0, legtop, lw, yb, cb, cbs, boot, sole, lift=lf[0], toe=-1, boot_h=P.get('boot_h', 2))
        leg(c, 8, legtop, lw, yb, cb, cbs, boot, sole, lift=lf[1], toe=1, boot_h=P.get('boot_h', 2))
        # torso
        c.rect(tx, ytorso, torso_w, 7, ca)
        c.vline(tx + torso_w - 1, ytorso, 7, cas); c.hline(tx, ytorso + 6, torso_w, cas)
        if view == 'down':
            P['torso_decor'](c, tx, ytorso, torso_w, b) if 'torso_decor' in P else None
        else:
            P['back_decor'](c, tx, ytorso, torso_w, b) if 'back_decor' in P else None
        # arms
        al = P.get('arm_len', 6)
        if view == 'down':
            if atk:
                arm(c, tx - 2, ytorso - 1, 2, al - 1, skin, skins, skin)
                arm(c, tx + torso_w, ytorso - 1, 2, al - 1, skin, skins, skin)
                c.rect(tx - 2, ytorso - 3, 2, 2, skin); c.rect(tx + torso_w, ytorso - 3, 2, 2, skin)
            else:
                arm(c, tx - 2, ytorso + 1, 2, al, ca, cas, skin)
                arm(c, tx + torso_w, ytorso + 1, 2, al, ca, cas, skin)
                # reaching forward: hands in front of body
                c.rect(tx - 1 + (1 if ph else 0), ytorso + al + 1, 2, 1, skin)
        else:
            arm(c, tx - 2, ytorso + 1, 2, al, ca, cas, skin)
            arm(c, tx + torso_w, ytorso + 1, 2, al, ca, cas, skin)
        # head
        hy = top + bob
        c.rect(hx, hy, head_w, 7, skin)
        c.vline(hx + head_w - 1, hy, 7, skins)
        if view == 'down':
            P['head_decor'](c, hx, hy, head_w, b, atk) if 'head_decor' in P else None
        else:
            P['head_back'](c, hx, hy, head_w, b) if 'head_back' in P else None
    else:  # side facing right
        offs = [(0, 0), (stride, -stride)][ph] if not atk else (1, -1)
        leg(c, 6 + offs[1], legtop, lw, yb, cbs, cbs, C(b, 14), C(b, 1), toe=1, boot_h=P.get('boot_h', 2))
        leg(c, 7 + offs[0], legtop, lw, yb, cb, cbs, boot, sole, toe=1, boot_h=P.get('boot_h', 2))
        sw = max(6, torso_w - 3)
        c.rect(8 - sw // 2, ytorso, sw, 7, ca); c.vline(8 - sw // 2, ytorso, 7, cas); c.hline(8 - sw // 2, ytorso + 6, sw, cas)
        P['side_decor'](c, 8 - sw // 2, ytorso, sw, b) if 'side_decor' in P else None
        # arms reaching forward
        ay = ytorso + (0 if atk else 2)
        c.rect(9, ay, 4, 2, ca if not atk else skin)
        c.rect(12, ay - (1 if atk else 0), 3, 2, skin)
        if atk:
            c.rect(12, ay - 2, 3, 1, skin)
        else:
            c.rect(13, ay + 2, 2, 1, skin)
        # head, leaning forward
        hy = top + bob
        hx2 = 8 - head_w // 2 + 1
        c.rect(hx2, hy, head_w - 1, 7, skin)
        c.vline(hx2, hy, 7, skins)
        P['head_side'](c, hx2, hy, head_w - 1, b, atk) if 'head_side' in P else None
    return c


def _eyes_down(c, hx, hy, hw, b, atk, glow=True):
    c.px(hx + 2, hy + 3, C(b, 8)); c.px(hx + hw - 3, hy + 3, C(b, 8))
    if glow:
        c.px(hx + 2, hy + 2, C(b, 1)); c.px(hx + hw - 3, hy + 2, C(b, 1))
    # mouth
    mh = 2 if atk else 1
    c.rect(hx + 2, hy + 5, hw - 4, mh, C(b, 1))
    c.px(hx + 3, hy + 5, C(b, 15)) if atk else None


def shambler(view, frame):
    b = 1

    def torso_decor(c, tx, ty, tw, bk):
        c.rect(tx + 1, ty + 1, 3, 4, C(bk, 5)); c.px(tx + 6, ty + 3, C(bk, 9)); c.px(tx + 7, ty + 4, C(bk, 9))
        c.hline(tx, ty + 6, tw, C(bk, 7)); c.px(tx + tw - 2, ty + 5, C(bk, 3))

    def back_decor(c, tx, ty, tw, bk):
        c.line(tx + 2, ty + 1, tx + 5, ty + 5, C(bk, 5)); c.px(tx + 6, ty + 2, C(bk, 3)); c.px(tx + 3, ty + 5, C(bk, 9))

    def head_decor(c, hx, hy, hw, bk, atk):
        _eyes_down(c, hx, hy, hw, bk, atk)
        c.hline(hx, hy, hw, C(bk, 13)); c.px(hx + 1, hy + 1, C(bk, 13)); c.px(hx + hw - 2, hy + 1, C(bk, 13))
        c.px(hx + hw - 2, hy + 4, C(bk, 9))

    def head_back(c, hx, hy, hw, bk):
        c.rect(hx, hy, hw, 3, C(bk, 13)); c.px(hx + 2, hy + 3, C(bk, 13)); c.px(hx + 5, hy + 4, C(bk, 3))

    def head_side(c, hx, hy, hw, bk, atk):
        c.px(hx + hw - 2, hy + 3, C(bk, 8)); c.px(hx + hw - 2, hy + 2, C(bk, 1))
        c.rect(hx + hw - 3, hy + 5, 3, 2 if atk else 1, C(bk, 1))
        c.rect(hx, hy, hw, 2, C(bk, 13))

    P = dict(hunch=2, stride=2, torso_decor=torso_decor, back_decor=back_decor, head_decor=head_decor,
             head_back=head_back, head_side=head_side, side_decor=lambda c, x, y, w, bk: c.px(x + 2, y + 3, C(bk, 9)))
    return finish(zombie_common(b, view, frame, P), bank=b)


def rusher(view, frame):
    b = 2

    def torso_decor(c, tx, ty, tw, bk):
        c.rect(tx + 2, ty + 0, tw - 4, 6, C(bk, 4)); c.px(tx + 3, ty + 2, C(bk, 3)); c.hline(tx + 2, ty + 5, tw - 4, C(bk, 5))
        for i in range(3):
            c.px(tx + 2 + i * 2, ty + 3, C(bk, 3))

    def back_decor(c, tx, ty, tw, bk):
        c.vline(tx + 4, ty, 6, C(bk, 3)); c.px(tx + 2, ty + 3, C(bk, 9))

    def head_decor(c, hx, hy, hw, bk, atk):
        c.px(hx + 1, hy + 3, C(bk, 8)); c.px(hx + 2, hy + 3, C(bk, 8))
        c.px(hx + hw - 3, hy + 3, C(bk, 8)); c.px(hx + hw - 2, hy + 3, C(bk, 8))
        c.rect(hx + 1, hy + 5, hw - 2, 2, C(bk, 1)); c.px(hx + 2, hy + 5, C(bk, 15)); c.px(hx + 5, hy + 5, C(bk, 15))
        c.rect(hx, hy, hw, 1, C(bk, 3))

    def head_back(c, hx, hy, hw, bk):
        c.rect(hx, hy, hw, 2, C(bk, 3)); c.px(hx + 3, hy + 4, C(bk, 9))

    def head_side(c, hx, hy, hw, bk, atk):
        c.px(hx + hw - 2, hy + 3, C(bk, 8)); c.px(hx + hw - 3, hy + 3, C(bk, 8))
        c.rect(hx + hw - 3, hy + 5, 3, 2, C(bk, 1)); c.px(hx + hw - 2, hy + 5, C(bk, 15))

    P = dict(hunch=3, stride=3, torso_w=8, head_w=8, top=1, arm_len=5, torso_decor=torso_decor,
             back_decor=back_decor, head_decor=head_decor, head_back=head_back, head_side=head_side,
             side_decor=lambda c, x, y, w, bk: c.hline(x + 1, y + 3, 3, C(bk, 3)))
    return finish(zombie_common(b, view, frame, P), bank=b)


def spitter(view, frame):
    b = 3

    def torso_decor(c, tx, ty, tw, bk):
        c.ellipse(8, ty + 3.5, 4.2, 3.4, C(bk, 9)); c.ellipse(8, ty + 3.5, 3, 2.4, C(bk, 8))
        c.px(7, ty + 2, C(bk, 12)); c.px(10, ty + 4, C(bk, 3)); c.px(6, ty + 4, C(bk, 3))

    def back_decor(c, tx, ty, tw, bk):
        c.ellipse(8, ty + 3.5, 3.6, 3, C(bk, 5)); c.px(6, ty + 2, C(bk, 9)); c.px(10, ty + 4, C(bk, 9))
        c.vline(8, ty, 6, C(bk, 3))

    def head_decor(c, hx, hy, hw, bk, atk):
        c.px(hx + 2, hy + 3, C(bk, 8)); c.px(hx + hw - 3, hy + 3, C(bk, 8))
        mh = 3 if atk else 1
        c.rect(hx + 2, hy + 5, hw - 4, mh, C(bk, 9) if atk else C(bk, 1))
        c.px(hx + 3, hy + 5, C(bk, 8)) if atk else None
        c.rect(hx + 1, hy, hw - 2, 1, C(bk, 12))

    def head_back(c, hx, hy, hw, bk):
        c.rect(hx + 1, hy, hw - 2, 2, C(bk, 12)); c.px(hx + 3, hy + 4, C(bk, 3))

    def head_side(c, hx, hy, hw, bk, atk):
        c.px(hx + hw - 2, hy + 3, C(bk, 8))
        c.rect(hx + hw - 3, hy + 5, 3, 3 if atk else 1, C(bk, 9) if atk else C(bk, 1))

    P = dict(hunch=1, stride=2, torso_w=12, head_w=6, top=2, arm_len=6, leg_w=3, torso_decor=torso_decor,
             back_decor=back_decor, head_decor=head_decor, head_back=head_back, head_side=head_side,
             side_decor=lambda c, x, y, w, bk: (c.ellipse(x + w - 1, y + 3.5, 3.4, 3.2, C(bk, 9)),
                                                 c.ellipse(x + w - 1, y + 3.5, 2.2, 2.0, C(bk, 8))))
    return finish(zombie_common(b, view, frame, P), bank=b)


def stalker(view, frame):
    b = 4

    def torso_decor(c, tx, ty, tw, bk):
        c.line(tx + 1, ty, tx + 3, ty + 6, C(bk, 5)); c.line(tx + 8, ty, tx + 6, ty + 6, C(bk, 5))
        c.px(tx + 4, ty + 3, C(bk, 3)); c.px(tx + 5, ty + 3, C(bk, 3))

    def back_decor(c, tx, ty, tw, bk):
        c.vline(tx + 4, ty, 7, C(bk, 5)); c.vline(tx + 5, ty, 7, C(bk, 3))

    def head_decor(c, hx, hy, hw, bk, atk):
        c.rect(hx, hy, hw, 2, C(bk, 5)); c.hline(hx, hy + 2, hw, C(bk, 4))
        c.px(hx + 2, hy + 3, C(bk, 8)); c.px(hx + 3, hy + 3, C(bk, 8))
        c.px(hx + hw - 4, hy + 3, C(bk, 8)); c.px(hx + hw - 3, hy + 3, C(bk, 8))
        if atk:
            c.rect(hx + 2, hy + 5, hw - 4, 2, C(bk, 1)); c.px(hx + 3, hy + 5, C(bk, 15)); c.px(hx + 5, hy + 5, C(bk, 15))

    def head_back(c, hx, hy, hw, bk):
        c.rect(hx, hy, hw, 4, C(bk, 5))

    def head_side(c, hx, hy, hw, bk, atk):
        c.rect(hx, hy, hw, 2, C(bk, 5))
        c.px(hx + hw - 2, hy + 3, C(bk, 8)); c.px(hx + hw - 3, hy + 3, C(bk, 8))

    P = dict(hunch=0, stride=2, torso_w=8, head_w=8, top=1, arm_len=8, leg_w=3, torso_decor=torso_decor,
             back_decor=back_decor, head_decor=head_decor, head_back=head_back, head_side=head_side)
    c = zombie_common(b, view, frame, P)
    # claws: long pale spikes at the ends of the arms
    cl = C(b, 12)
    if view in ('down', 'up'):
        yb = 18 if frame != 2 else 12
        c.vline(2, yb, 3, cl); c.vline(13, yb, 3, cl)
    else:
        c.hline(14, 12 if frame != 2 else 10, 2, cl)
    return finish(c, bank=b)


def zombie_corpse(bank, frame, base_w=14):
    """16x16 corpse (frame 0 = collapsing, 1 = flat)"""
    b = bank
    c = Canvas(16, 16)
    skin, skins = C(b, 2), C(b, 3)
    ca, cb = C(b, 4), C(b, 6)
    bl = C(1, 9)
    if frame == 0:
        c.rect(3, 4, 9, 7, ca); c.rect(9, 2, 6, 5, skin); c.rect(2, 10, 8, 4, cb); c.rect(11, 9, 4, 3, cb)
        c.px(12, 4, C(b, 8)); c.px(10, 6, skins)
        c.rect(0, 6, 3, 2, skin)
    else:
        c.rect(1, 6, 10, 6, ca); c.vline(1, 6, 6, skins); c.hline(1, 11, 10, C(b, 5))
        c.rect(11, 6, 5, 5, skin); c.vline(15, 6, 5, skins); c.px(13, 8, C(b, 1)); c.px(14, 8, C(b, 1))
        c.rect(3, 12, 8, 2, cb); c.rect(10, 12, 4, 2, C(b, 13))
        c.rect(2, 3, 4, 3, skin)
    return finish(c, bank=b)


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
    ph = frame if frame < 2 else 0
    atk = frame == 2
    bob = [0, 1][ph] if not atk else 0
    yb = 29
    if view in ('down', 'up'):
        lf = [(0, 3), (3, 0)][ph] if not atk else (0, 0)
        leg(c, 7, 19 + bob, 8, yb, cb, cbs, boot, sole, boot_h=3, lift=lf[0], toe=-1)
        leg(c, 17, 19 + bob, 8, yb, cb, cbs, boot, sole, boot_h=3, lift=lf[1], toe=1)
        # torso
        c.rect(7, 9 + bob, 18, 11, ar); c.vline(24, 9 + bob, 11, ars); c.hline(7, 19 + bob, 18, ars)
        if view == 'down':
            c.rect(11, 11 + bob, 10, 6, ars); c.hline(11, 13 + bob, 10, ar)
            for x in (12, 19):
                c.px(x, 12 + bob, org)
            c.rect(14, 16 + bob, 4, 3, C(b, 10)); c.px(15, 16 + bob, C(b, 15))
        else:
            c.vline(15, 9 + bob, 11, ars); c.vline(16, 9 + bob, 11, ar)
            c.rect(9, 11 + bob, 4, 3, ars); c.rect(19, 12 + bob, 4, 3, ars)
        # shoulder plates
        c.rect(2, 8 + bob, 8, 6, ar); c.frame(2, 8 + bob, 8, 6, ars); c.px(4, 10 + bob, org); c.px(7, 10 + bob, org)
        c.rect(22, 8 + bob, 8, 6, ar); c.frame(22, 8 + bob, 8, 6, ars); c.px(24, 10 + bob, org); c.px(27, 10 + bob, org)
        # arms + fists
        if atk:
            c.rect(2, 2, 6, 7, skin); c.rect(1, 0, 8, 4, skin); c.vline(8, 1, 3, skins)
            c.rect(24, 2, 6, 7, skin); c.rect(23, 0, 8, 4, skin); c.vline(30, 1, 3, skins)
            c.rect(3, 7, 4, 2, ars); c.rect(25, 7, 4, 2, ars)
        else:
            c.rect(2, 14 + bob, 6, 9, skin); c.vline(7, 14 + bob, 9, skins)
            c.rect(1, 22 + bob, 8, 5, skin); c.vline(8, 22 + bob, 5, skins); c.hline(2, 26 + bob, 6, skins)
            c.rect(24, 14 + bob, 6, 9, skin); c.vline(29, 14 + bob, 9, skins)
            c.rect(23, 22 + bob, 8, 5, skin); c.vline(30, 22 + bob, 5, skins); c.hline(24, 26 + bob, 6, skins)
        # head
        hy = 1 + bob + (2 if atk else 0)
        c.rect(11, hy, 10, 8, skin); c.vline(20, hy, 8, skins)
        if view == 'down':
            c.rect(11, hy, 10, 2, C(b, 12))
            c.hline(12, hy + 3, 3, C(b, 1)); c.hline(17, hy + 3, 3, C(b, 1))
            c.px(13, hy + 4, org); c.px(18, hy + 4, org)
            c.rect(12, hy + 6, 8, 2, C(b, 1)); c.px(13, hy + 6, C(b, 15)); c.px(15, hy + 6, C(b, 15)); c.px(18, hy + 6, C(b, 15))
        else:
            c.rect(11, hy, 10, 4, C(b, 5)); c.px(15, hy + 5, C(b, 9))
        c.rect(10, hy + 7, 12, 2, ars)
    else:
        offs = [(0, 0), (4, -4)][ph] if not atk else (2, -2)
        leg(c, 10 + offs[1], 19 + bob, 8, yb, cbs, cbs, C(b, 14), C(b, 1), boot_h=3, toe=1)
        leg(c, 12 + offs[0], 19 + bob, 8, yb, cb, cbs, boot, sole, boot_h=3, toe=1)
        c.rect(8, 9 + bob, 14, 11, ar); c.vline(8, 9 + bob, 11, ars); c.hline(8, 19 + bob, 14, ars)
        c.rect(11, 11 + bob, 8, 6, ars); c.px(13, 12 + bob, org)
        c.rect(4, 8 + bob, 9, 6, ar); c.frame(4, 8 + bob, 9, 6, ars); c.px(6, 10 + bob, org)
        # arms forward
        ay = 12 + bob - (6 if atk else 0)
        c.rect(14, ay, 8, 5, skin); c.hline(14, ay + 4, 8, skins)
        c.rect(21, ay - 1, 8, 8, skin); c.vline(28, ay - 1, 8, skins); c.hline(22, ay + 6, 6, skins)
        hy = 2 + bob + (1 if atk else 0)
        c.rect(14, hy, 10, 8, skin); c.vline(14, hy, 8, skins)
        c.rect(14, hy, 10, 2, C(b, 12))
        c.px(21, hy + 3, org); c.px(22, hy + 3, org)
        c.rect(19, hy + 5, 5, 2, C(b, 1)); c.px(20, hy + 5, C(b, 15)); c.px(22, hy + 5, C(b, 15))
        c.rect(12, hy + 7, 10, 2, ars)
    return finish(c, bank=b)


def brute_corpse(frame):
    b = 5
    c = Canvas(32, 16)
    skin, skins = C(b, 2), C(b, 3)
    ar, ars = C(b, 4), C(b, 5)
    cb = C(b, 6)
    if frame == 0:
        c.rect(5, 4, 18, 9, ar); c.rect(22, 3, 8, 7, skin); c.rect(0, 8, 10, 6, cb); c.rect(24, 10, 6, 4, cb)
        c.rect(2, 3, 8, 4, ar); c.px(26, 5, C(b, 8))
    else:
        c.rect(2, 6, 20, 8, ar); c.hline(2, 13, 20, ars); c.rect(21, 4, 10, 9, skin); c.vline(30, 4, 9, skins)
        c.px(26, 7, C(b, 1)); c.px(28, 7, C(b, 1)); c.hline(25, 10, 5, C(b, 1))
        c.rect(0, 9, 6, 5, cb); c.rect(8, 2, 8, 5, ar); c.frame(8, 2, 8, 5, ars)
    return finish(c, bank=b)


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
