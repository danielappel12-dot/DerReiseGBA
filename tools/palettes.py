"""palettes.py - the two 256-colour palettes (BG and OBJ) used by NIGHTFALL.

Every palette is 16 banks x 16 colours.  Slot 0 of each bank is transparent
(on BG layers it shows whatever is behind, ultimately the backdrop colour
which is BG bank 0 / slot 0 = near-black).
"""
from pix import Palette, rgb

# --------------------------------------------------------------------------
# BG palette banks
# --------------------------------------------------------------------------
BG0_STRUCT = [  # concrete / steel / dirty green / brown / blue
    '#06080c', '#10141a', '#1a2028', '#262d37', '#353f4b', '#4d5967', '#6f7d8c', '#1f2d28',
    '#2b4034', '#3f5c49', '#2a211c', '#473627', '#6a5139', '#16213a', '#27406a', '#a3b0bc']
BG1_MACH = [  # machinery & accents (orange / yellow / red / electric blue / radioactive green)
    '#06080c', '#10141a', '#262d37', '#43505e', '#7a8794', '#e8742a', '#a8431a', '#f2c230',
    '#d12a2a', '#721616', '#3ad0ff', '#1c5f9a', '#7aff3a', '#2a8a1a', '#e8f0f4', '#1f6f73']
BG2_WOOD = [  # crates, desks, paper, military green
    '#06080c', '#1b130e', '#2e2118', '#47341f', '#66482a', '#8a6538', '#b08848', '#d9b36a',
    '#3a3f2e', '#566044', '#7a8a60', '#c8c0a8', '#8c8472', '#e8742a', '#f2c230', '#d12a2a']
BG3_LAB = [  # research lab / test chamber: cold teal and white tile
    '#06080c', '#10161b', '#1e2b30', '#2c4048', '#3f5c66', '#5f8590', '#8fb4bb', '#c8e0e4',
    '#2a5a5e', '#3aa59d', '#7affd2', '#3ad0ff', '#c0392b', '#7aff3a', '#e8f0f4', '#243038']
BG4_BLOOD = [  # floor + blood / ooze decals
    '#06080c', '#10141a', '#1a2028', '#262d37', '#353f4b', '#4d5967', '#5a0e0e', '#8c1818',
    '#b52020', '#d63a2a', '#3c1a14', '#2b4034', '#4aa83a', '#7aff3a', '#1c2a24', '#a3b0bc']
BG6_MINI = [  # minimap + UI panel
    '#000000', '#05070a', '#1d2b44', '#5b6b7d', '#e8742a', '#3ad0ff', '#f2c230', '#7aff3a',
    '#d12a2a', '#e8f0f4', '#0e131b', '#2a3a52', '#7a8794', '#3a4a60', '#162033', '#9aa8b4']

# HUD text colours: (main, light, dark)
HUD_COLORS = [
    ('#e8f0f4', '#ffffff', '#8c98a4'),   # 8  white
    ('#f2c230', '#ffe680', '#8a6a10'),   # 9  yellow
    ('#d12a2a', '#ff6a5a', '#5a1010'),   # 10 red
    ('#3fd02a', '#9aff7a', '#145a10'),   # 11 green
    ('#e8742a', '#ffb070', '#6a2a0a'),   # 12 orange
    ('#3ad0ff', '#a0ecff', '#104a70'),   # 13 cyan
    ('#7a8794', '#aab6c2', '#2a323c'),   # 14 gray
    ('#b48aff', '#dcc8ff', '#4a2a7a'),   # 15 violet
]


def hud_bank(main, light, dark):
    return ['#000000', '#05070a', main, light, '#55616e', dark, '#141a22'] + ['#000000'] * 9


def lit(bank, warm):
    """brighten a BG0 style bank to simulate light pools"""
    out = []
    for i, c in enumerate(bank):
        r, g, b = rgb(c)
        if i == 0:
            out.append('#%02x%02x%02x' % (r, g, b))
            continue
        k = 1.55
        if warm:
            r, g, b = r * k + 26, g * k + 16, b * k * 0.9
        else:
            r, g, b = r * k * 0.9, g * k + 14, b * k + 30
        out.append('#%02x%02x%02x' % (min(255, int(r)), min(255, int(g)), min(255, int(b))))
    return out


BG5_LIT_WARM = lit(BG0_STRUCT, True)
BG7_LIT_COOL = lit(BG0_STRUCT, False)


def build_bg_palette():
    p = Palette()
    p.bank(0, BG0_STRUCT)
    p.bank(1, BG1_MACH)
    p.bank(2, BG2_WOOD)
    p.bank(3, BG3_LAB)
    p.bank(4, BG4_BLOOD)
    # banks 5 and 7 start identical to bank 0 (lights off); the lit versions are
    # exported separately and swapped in when the generator is switched on.
    p.bank(5, BG0_STRUCT)
    p.bank(6, BG6_MINI)
    p.bank(7, BG0_STRUCT)
    for i, (m, l, d) in enumerate(HUD_COLORS):
        p.bank(8 + i, hud_bank(m, l, d))
    return p


# --------------------------------------------------------------------------
# OBJ palette banks.  Slot meaning for character banks:
#  1 outline 2 skin 3 skin-shade 4 clothA 5 clothA-shade 6 clothB 7 clothB-shade
#  8 accent 9 gear/blood 10 metal-light 11 metal-dark 12 highlight 13 leather
#  14 leather-shade 15 white
# --------------------------------------------------------------------------
OBJ_PLAYER = ['#000000', '#0a0c10', '#d9a77a', '#a8764e', '#2f4259', '#1f2c3d', '#3a4430', '#272e20',
              '#e8742a', '#55663f', '#aab6c2', '#55616e', '#8a9a6a', '#6a4a2a', '#46301c', '#f2f6f8']
OBJ_SHAMBLER = ['#000000', '#0a0c10', '#8a9e72', '#5e7450', '#5a4a3a', '#3b2f25', '#3a3f4a', '#262a32',
                '#ffe14a', '#a01818', '#aab6c2', '#55616e', '#c8d6a8', '#4a3a2a', '#2e2318', '#f2f6f8']
OBJ_RUSHER = ['#000000', '#0a0c10', '#c8b0a0', '#9a7e72', '#8a2a2a', '#5a1818', '#4a4a52', '#2f2f36',
              '#ff3030', '#a01818', '#aab6c2', '#55616e', '#e8d8cc', '#4a3a2a', '#2e2318', '#f2f6f8']
OBJ_SPITTER = ['#000000', '#0a0c10', '#9ac060', '#688a3a', '#b8c8b0', '#8a9a86', '#3a4a3a', '#26332a',
               '#7aff3a', '#3fd02a', '#aab6c2', '#55616e', '#d8f0a0', '#4a3a2a', '#2e2318', '#f2f6f8']
OBJ_STALKER = ['#000000', '#05060a', '#4a5c82', '#2e3a58', '#1c2236', '#121626', '#161a2a', '#0e101c',
               '#3ad0ff', '#1c5f9a', '#7a8fbf', '#3a4a6a', '#8aa4d8', '#2a2a44', '#1a1a2c', '#d8f0ff']
OBJ_BRUTE = ['#000000', '#0a0c10', '#6a8a5a', '#4a6a3c', '#6a7785', '#3f4955', '#3a3430', '#26211e',
             '#e8742a', '#a01818', '#aab6c2', '#55616e', '#a8c090', '#5a4028', '#38281a', '#f2f6f8']
OBJ_FX = ['#000000', '#0a0c10', '#fff6c0', '#ffd23a', '#ff8a1e', '#d12a2a', '#7a1010', '#3ad0ff',
          '#b8f4ff', '#7aff3a', '#2f8a1c', '#ffffff', '#aab6c2', '#55616e', '#272e38', '#f2c230']
OBJ_MISC = ['#000000', '#0a0c10', '#e8742a', '#a8431a', '#f2c230', '#b8901a', '#3ad0ff', '#1c5f9a',
            '#7aff3a', '#2f8a1c', '#d12a2a', '#721616', '#e8f0f4', '#aab6c2', '#55616e', '#272e38']


def flash_bank(color_main, outline='#0a0c10'):
    return ['#000000', outline] + [color_main] * 14


def tint(bank, fn):
    out = []
    for i, c in enumerate(bank):
        if i < 2:
            out.append(c)
        else:
            out.append(fn(rgb(c)))
    return ['#%02x%02x%02x' % tuple(c) if not isinstance(c, str) else c for c in out]


def build_obj_palette():
    p = Palette()
    p.bank(0, OBJ_PLAYER)
    p.bank(1, OBJ_SHAMBLER)
    p.bank(2, OBJ_RUSHER)
    p.bank(3, OBJ_SPITTER)
    p.bank(4, OBJ_STALKER)
    p.bank(5, OBJ_BRUTE)
    p.bank(6, OBJ_FX)
    p.bank(7, OBJ_MISC)
    p.bank(8, flash_bank('#ffffff'))
    # damage flash for the player: bright red, tones preserved a little
    red = ['#000000', '#0a0c10'] + ['#ff5040', '#c02a20'] * 7
    p.bank(9, red)
    # elite (wave 10+) tints of the common enemies: hue shifted toward red / purple
    p.bank(10, tint(OBJ_SHAMBLER, lambda c: (min(255, c[0] + 60), max(0, c[1] - 20), max(0, c[2] - 20))))
    p.bank(11, tint(OBJ_RUSHER, lambda c: (min(255, c[0] // 2 + 40), c[1] // 2, min(255, c[2] + 70))))
    p.bank(12, tint(OBJ_BRUTE, lambda c: (min(255, c[0] + 50), max(0, c[1] - 30), max(0, c[2] - 30))))
    return p
