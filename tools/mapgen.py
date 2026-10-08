"""mapgen.py - builds BLACKSITE 13 (64x64 tiles of 8x8) and the tile sheet it needs.

Layout: a 3x3 grid of rooms separated by 2-tile-thick walls.

     col0 x2..19      col1 x22..41     col2 x44..61
 r0  RESEARCH LAB     TEST CHAMBER     SECURITY OFFICE      y 2..19
 r1  MACHINE SHOP     GENERATOR ROOM   STORAGE ROOM         y 22..41
 r2  LOWER MAINT.     ENTRANCE HALL    CARGO BAY            y 44..61

Outputs (see emit_c): entries/flags/areas/minimap per cell plus door, interact,
spawn and note tables.
"""
import random
import art_tiles as A
from pix import Canvas

W = H = 64

COLS = [(2, 18), (22, 20), (44, 18)]
ROWS = [(2, 18), (22, 20), (44, 18)]

MF_SOLID = 1
MF_DOOR = 2
MF_LOW = 4       # blocks movement but not bullets (reserved)

# area ids
AREA = {'RL': 0, 'T': 1, 'SO': 2, 'MS': 3, 'G': 4, 'S': 5, 'M': 6, 'E': 7, 'C': 8}
AREA_NAMES = ['RESEARCH LAB', 'TEST CHAMBER', 'SECURITY OFFICE', 'MACHINE SHOP', 'GENERATOR ROOM',
              'STORAGE ROOM', 'LOWER MAINTENANCE', 'ENTRANCE HALL', 'CARGO BAY']
ROOM_POS = {'RL': (0, 0), 'T': (1, 0), 'SO': (2, 0), 'MS': (0, 1), 'G': (1, 1), 'S': (2, 1),
            'M': (0, 2), 'E': (1, 2), 'C': (2, 2)}

# weapon ids (must match weapons.h)
WPN = {'SERVICE-9': 0, 'TRENCH SHOTGUN': 1, 'RANGER SMG': 2, 'HEAVY RIFLE': 3, 'ARC LAUNCHER': 4, 'RAY GUN': 5}
PERKS = ['IRON HEART', 'QUICK HANDS', 'STEADY AIM', 'SECOND WIND', 'FIELD MEDIC']

IK_DOOR, IK_GEN, IK_PERK, IK_WEAPON, IK_NOTE = 0, 1, 2, 3, 4

NOTES = [
    "LAB LOG 114: THE NIGHTFALL CORE HUMS BELOW. NIGHT SHIFT SAYS IT SINGS.",
    "DR. ASH: DEAD TISSUE REACTS TO THE CORE. WE FED IT. IT FED BACK.",
    "SECURITY: CONTAINMENT BREACH. SEAL ALL BULKHEADS. DO NOT USE ELEVATORS.",
    "MAINT NOTE: GENERATOR OFFLINE. NO POWER = NO LOCKS = NO MERCY.",
    "EVAC TEAM LOG: ROOK, YOU WERE THE LAST ONE IN. HOLD THE LINE UNTIL DAWN.",
    "SIGN: TEST CHAMBER 7. SUBJECTS MUST NOT BE LEFT UNATTENDED AFTER DARK.",
    "SCRAWLED ON WALL: IT WANTS THE LIGHT. IT WANTS US. IT NEVER STOPS.",
]


class Level:
    def __init__(self, ts):
        self.ts = ts
        self.kind = [['wall'] * W for _ in range(H)]    # wall, floor, door, prop
        self.solid = [[1] * W for _ in range(H)]
        self.area = [[255] * W for _ in range(H)]
        self.obj = {}                                   # (x,y) -> (tid,bank) override gfx
        self.floor_gfx = {}
        self.mini = [[0] * W for _ in range(H)]
        self.doors = []
        self.interacts = []
        self.spawns = []
        self.swaps = []                                 # (x,y, off_entry, on_entry)
        self.lamps = []                                 # (x,y_front, warm)
        self.keepout = set()
        self.rng = random.Random(1313)
        self.wall_decor = {}
        self.player_start = (0, 0)
        self.notes_used = 0
        self.reserved = set()

    # -- helpers -------------------------------------------------------
    def room_rect(self, rid):
        c, r = ROOM_POS[rid]
        x, w = COLS[c]
        y, h = ROWS[r]
        return x, y, w, h

    def carve_room(self, rid):
        x, y, w, h = self.room_rect(rid)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.kind[yy][xx] = 'floor'
                self.solid[yy][xx] = 0
                self.area[yy][xx] = AREA[rid]
                self.mini[yy][xx] = 2

    def passage(self, x, y, w, h, area_a, area_b):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.kind[yy][xx] = 'floor'
                self.solid[yy][xx] = 0
                self.area[yy][xx] = AREA[area_a]
                self.mini[yy][xx] = 2
                self.floor_gfx[(xx, yy)] = 'passage'

    def door(self, x, y, w, h, cost, name, needs_power, opens_area, vertical, side_a, side_b):
        self.passage(x, y, w, h, side_a, side_b)
        did = len(self.doors)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.kind[yy][xx] = 'door'
                self.solid[yy][xx] = 1
                self.mini[yy][xx] = 4
        self.doors.append(dict(x=x, y=y, w=w, h=h, cost=cost, name=name, power=needs_power,
                               opens=AREA[opens_area], vertical=vertical, id=did))
        return did

    def place(self, name, lx_or_gx, ly_or_gy, room=None, check=True):
        """place a prop; coordinates local to `room` when room given"""
        if room:
            rx, ry, _, _ = self.room_rect(room)
            gx, gy = rx + lx_or_gx, ry + ly_or_gy
        else:
            gx, gy = lx_or_gx, ly_or_gy
        sizes = {'crate0': (2, 2), 'crate1': (2, 2), 'crate2': (2, 2), 'barrel0': (1, 1), 'barrel1': (1, 1),
                 'barrel2': (1, 1), 'desk0': (2, 2), 'desk1': (2, 2), 'desk2': (2, 2), 'server0': (2, 2),
                 'server1': (2, 2), 'lathe0': (2, 2), 'lathe1': (2, 2), 'tank': (2, 3), 'tankb': (2, 3),
                 'gen': (3, 2), 'term': (2, 2), 'pipeh': (1, 1), 'pipev': (1, 1)}
        if name.startswith('perk:'):
            sw, sh = 2, 3
        else:
            sw, sh = sizes[name]
        solid = not name.startswith('pipe')
        for yy in range(gy, gy + sh):
            for xx in range(gx, gx + sw):
                if check:
                    assert self.kind[yy][xx] == 'floor' and not self.solid[yy][xx], \
                        "place %s at %d,%d blocked at %d,%d (%s)" % (name, gx, gy, xx, yy, self.kind[yy][xx])
                    assert (xx, yy) not in self.keepout, "place %s at %d,%d in keepout %d,%d" % (name, gx, gy, xx, yy)
                    assert (xx, yy) not in self.reserved, "place %s overlaps reserved %d,%d" % (name, xx, yy)
        cv = self.draw_prop(name)
        blk = self.ts.add_block(cv)
        for j in range(sh):
            for i in range(sw):
                xx, yy = gx + i, gy + j
                self.obj[(xx, yy)] = blk[j][i]
                if solid:
                    self.solid[yy][xx] = 1
                    self.kind[yy][xx] = 'prop'
                    self.mini[yy][xx] = 5
                self.reserved.add((xx, yy))
        return gx, gy, sw, sh, cv

    def draw_prop(self, name):
        if name.startswith('crate'):
            return A.obj_crate(int(name[5]))
        if name.startswith('barrel'):
            cv = Canvas(8, 8)
            cv.blit(A.obj_barrel(int(name[6])), 0, 0)
            return cv
        if name.startswith('desk'):
            return A.obj_desk(int(name[4]))
        if name.startswith('server'):
            return A.obj_server(int(name[6]))
        if name.startswith('lathe'):
            return A.obj_lathe(int(name[5]))
        if name == 'tank':
            return A.obj_tank(False)
        if name == 'tankb':
            return A.obj_tank(True)
        if name == 'gen':
            return A.obj_generator(False)
        if name == 'term':
            return A.obj_terminal(True)
        if name == 'pipeh':
            return A.pipe_floor(True)
        if name == 'pipev':
            return A.pipe_floor(False)
        if name.startswith('perk:'):
            main, light = A.PERK_COLORS[name[5:]]
            return A.obj_perk(main, light, on=False)
        raise KeyError(name)


def build(ts):
    L = Level(ts)
    rng = L.rng
    for rid in ROOM_POS:
        L.carve_room(rid)

    # ------------------------------------------------------------------ passages
    # open doorways: E<->C (two), G<->S, MS<->M, RL<->MS, T<->SO
    L.passage(42, 46, 2, 3, 'E', 'C'); L.passage(42, 56, 2, 3, 'E', 'C')
    L.passage(42, 30, 2, 3, 'G', 'S')
    L.passage(10, 42, 3, 2, 'MS', 'M')
    L.passage(10, 20, 3, 2, 'RL', 'MS')
    L.passage(42, 10, 2, 3, 'T', 'SO')
    # keep-out zones in front of every opening (computed after doors are added)
    # locked doors  (x, y, w, h, cost, name, power, opens, vertical, a, b)
    L.door(20, 51, 2, 3, 500, "MAINTENANCE ACCESS", 0, 'M', True, 'E', 'M')
    L.door(30, 42, 3, 2, 750, "GENERATOR ACCESS", 0, 'G', False, 'E', 'G')
    L.door(52, 42, 3, 2, 600, "STORAGE ACCESS", 0, 'S', False, 'C', 'S')
    L.door(20, 30, 2, 3, 1000, "MACHINE SHOP", 1, 'MS', True, 'G', 'MS')
    L.door(30, 20, 3, 2, 1500, "TEST CHAMBER", 1, 'T', False, 'G', 'T')
    L.door(52, 20, 3, 2, 800, "SECURITY OFFICE", 0, 'SO', False, 'S', 'SO')
    L.door(20, 10, 2, 3, 1200, "RESEARCH LAB", 1, 'RL', True, 'T', 'RL')

    # keepout: 4 tiles in front of each opening on both sides
    def ko_rect(x, y, w, h, vertical):
        if vertical:
            for yy in range(y, y + h):
                for k in range(-4, 6):
                    L.keepout.add((x + k, yy))
        else:
            for xx in range(x, x + w):
                for k in range(-4, 6):
                    L.keepout.add((xx, y + k))
    for (x, y, w, h, v) in [(42, 46, 2, 3, True), (42, 56, 2, 3, True), (42, 30, 2, 3, True), (10, 42, 3, 2, False),
                            (10, 20, 3, 2, False), (42, 10, 2, 3, True)]:
        ko_rect(x, y, w, h, v)
    for d in L.doors:
        ko_rect(d['x'], d['y'], d['w'], d['h'], d['vertical'])

    P = L.place
    # ------------------------------------------------------------------ ENTRANCE HALL  (x22..41,y44..61)
    for (px, py) in [(5, 5), (13, 5), (5, 11), (13, 11)]:
        P('crate1' if (px + py) % 2 else 'crate0', px, py, 'E')
    P('desk0', 8, 8, 'E'); P('desk1', 10, 8, 'E')
    P('barrel0', 1, 15, 'E'); P('barrel1', 2, 15, 'E'); P('barrel0', 18, 16, 'E')
    P('perk:QUICK HANDS', 12, 0, 'E')
    P('term', 1, 0, 'E')
    P('crate2', 17, 8, 'E')
    # ------------------------------------------------------------------ CARGO BAY  (x44..61,y44..61)
    for (px, py) in [(5, 6), (7, 6), (12, 6), (14, 6), (5, 10), (12, 10), (14, 10)]:
        P('crate0' if (px // 2) % 2 else 'crate1', px, py, 'C')
    P('crate2', 8, 15, 'C')
    P('barrel0', 1, 1, 'C'); P('barrel2', 17, 4, 'C'); P('barrel0', 1, 16, 'C'); P('barrel1', 16, 16, 'C'); P('barrel0', 2, 1, 'C')
    # ------------------------------------------------------------------ STORAGE ROOM (x44..61,y22..41)
    for (px, py) in [(2, 3), (4, 3), (12, 3), (14, 3), (4, 8), (6, 8), (12, 8), (14, 8), (2, 13), (4, 13), (13, 13), (15, 13),
                     (3, 17), (13, 17)]:
        P('crate0' if (px + py) % 3 else 'crate1', px, py, 'S')
    P('barrel0', 16, 6, 'S'); P('barrel1', 1, 17, 'S'); P('barrel2', 16, 18, 'S')
    # ------------------------------------------------------------------ GENERATOR ROOM (x22..41,y22..41)
    for (px, py) in [(4, 4), (14, 4), (4, 13), (14, 13)]:
        P('lathe1' if py > 8 else 'lathe0', px, py, 'G')
    P('gen', 8, 8, 'G')
    P('barrel2', 1, 1, 'G'); P('barrel2', 18, 1, 'G'); P('barrel0', 1, 18, 'G'); P('barrel0', 18, 18, 'G')
    for x in range(2, 18):
        if x % 8 not in (0, 1) and (x < 8 or x > 12):
            pass
    # ------------------------------------------------------------------ MACHINE SHOP (x2..19,y22..41)
    for (px, py) in [(2, 2), (5, 2), (13, 2), (16, 2), (2, 16), (5, 16), (13, 16), (16, 16)]:
        P('lathe0' if (px // 3) % 2 else 'lathe1', px, py, 'MS')
    for (px, py) in [(2, 13), (15, 13)]:
        P('crate1', px, py, 'MS')
    P('desk0', 4, 11, 'MS'); P('desk1', 13, 11, 'MS')
    P('barrel1', 1, 11, 'MS'); P('barrel2', 17, 12, 'MS')
    # ------------------------------------------------------------------ RESEARCH LAB (x2..19,y2..19)
    for (px, py) in [(2, 4), (5, 4), (12, 4), (15, 4)]:
        P('desk1' if px % 2 else 'desk0', px, py, 'RL')
    P('tank', 1, 9, 'RL'); P('tankb', 15, 11, 'RL'); P('tank', 15, 14, 'RL')
    P('desk0', 4, 13, 'RL'); P('desk2', 11, 14, 'RL')
    # ------------------------------------------------------------------ TEST CHAMBER (x22..41,y2..19)
    P('tank', 4, 3, 'T'); P('tankb', 14, 3, 'T'); P('tank', 4, 12, 'T'); P('tank', 14, 12, 'T')
    P('server1', 8, 6, 'T')
    # ------------------------------------------------------------------ SECURITY OFFICE (x44..61,y2..19)
    for (px, py) in [(3, 5), (6, 5), (11, 5), (14, 5), (3, 11), (6, 11), (12, 11)]:
        P('desk1' if (px + py) % 2 else 'desk0', px, py, 'SO')
    P('barrel0', 16, 17, 'SO')
    # ------------------------------------------------------------------ LOWER MAINTENANCE (x2..19,y44..61)
    for (px, py) in [(3, 4), (7, 4), (12, 4), (4, 10), (13, 10), (8, 14), (3, 14), (15, 14)]:
        P('barrel1' if px % 2 else 'barrel2', px, py, 'M')
    P('crate0', 8, 8, 'M'); P('crate1', 10, 8, 'M')
    for x in range(1, 17):
        P('pipeh', x, 7, 'M', check=False) if x not in (8, 9, 10, 11) else None
    for y in range(8, 16):
        P('pipev', 6, y, 'M', check=False) if (y not in (8, 9)) and L.kind[44 + y][2 + 6] == 'floor' else None

    # ------------------------------------------------------------------ interactables placed after props
    def add_interact(kind, id_, cost, gx, gy, gw, gh, margin_px=10, pw=0):
        L.interacts.append(dict(kind=kind, id=id_, cost=cost,
                                x=gx * 8 - margin_px, y=gy * 8 - margin_px,
                                w=gw * 8 + margin_px * 2, h=gh * 8 + margin_px * 2))

    # doors
    for d in L.doors:
        add_interact(IK_DOOR, d['id'], d['cost'], d['x'], d['y'], d['w'], d['h'], margin_px=12)

    # generator (tile rect at room G local 8,8 size 3x2)
    gx, gy = L.room_rect('G')[0] + 8, L.room_rect('G')[1] + 8
    add_interact(IK_GEN, 0, 0, gx, gy, 3, 2, margin_px=10)
    # swap on/off for generator tiles
    on = ts.add_block(A.obj_generator(True))
    off = ts.add_block(A.obj_generator(False))
    for j in range(2):
        for i in range(3):
            L.swaps.append((gx + i, gy + j, off[j][i], on[j][i]))

    # perks
    perk_defs = [('QUICK HANDS', 'E', 12, 1000), ('SECOND WIND', 'C', 15, 1500), ('STEADY AIM', 'S', 14, 1500),
                 ('FIELD MEDIC', 'SO', 1, 1250), ('IRON HEART', 'MS', 0, 2000)]
    # perks need to be placed (they are 2x3 on the north wall) - some rooms already had props: place now
    for (pname, rid, lx, cost) in perk_defs:
        rx, ry, _, _ = L.room_rect(rid)
        if pname == 'QUICK HANDS':
            gx2, gy2 = rx + lx, ry + 0   # already placed above
        else:
            try:
                P('perk:' + pname, lx, 0, rid)
            except AssertionError:
                raise
            gx2, gy2 = rx + lx, ry
        L.mini[gy2][gx2] = 7; L.mini[gy2][gx2 + 1] = 7
        pid = PERKS.index(pname)
        add_interact(IK_PERK, pid, cost, gx2, gy2, 2, 3, margin_px=10)
        main, light = A.PERK_COLORS[pname]
        onb = ts.add_block(A.obj_perk(main, light, True))
        offb = ts.add_block(A.obj_perk(main, light, False))
        for j in range(3):
            for i in range(2):
                L.swaps.append((gx2 + i, gy2 + j, offb[j][i], onb[j][i]))

    # weapon racks: wall front row (y = room_y-1), 2 tiles wide
    wpn_defs = [('TRENCH SHOTGUN', 'C', 5, 500, 1), ('RANGER SMG', 'SO', 8, 1000, 2),
                ('HEAVY RIFLE', 'S', 3, 1250, 3), ('ARC LAUNCHER', 'RL', 3, 2250, 4), ('RAY GUN', 'T', 8, 3000, 5)]
    L.weapon_racks = []
    for (wname, rid, lx, cost, wid) in wpn_defs:
        rx, ry, _, _ = L.room_rect(rid)
        gx2, gy2 = rx + lx, ry - 1
        L.wall_decor[(gx2, gy2)] = ('rack', wid, 0)
        L.wall_decor[(gx2 + 1, gy2)] = ('rack', wid, 1)
        add_interact(IK_WEAPON, wid, cost, gx2, gy2, 2, 1, margin_px=12)
        L.mini[gy2][gx2] = 8; L.mini[gy2][gx2 + 1] = 8

    # notes (terminals): 'term' props already placed in E (1,0) -> note 0 ; add more
    note_sites = [('E', 1, 0, 0)]
    for (rid, lx, ly, nid) in note_sites:
        rx, ry, _, _ = L.room_rect(rid)
        add_interact(IK_NOTE, nid, 0, rx + lx, ry + ly, 2, 2, margin_px=8)
        L.mini[ry + ly][rx + lx] = 9
    # extra terminals in other rooms
    extra = [('S', 11, 1, 1), ('SO', 15, 1, 2), ('G', 1, 14, 3), ('RL', 8, 1, 4), ('T', 1, 1, 5), ('M', 14, 1, 6)]
    for (rid, lx, ly, nid) in extra:
        rx, ry, _, _ = L.room_rect(rid)
        try:
            P('term', lx, ly, rid)
        except AssertionError as e:
            # try a few offsets
            ok = False
            for (dx, dy) in [(1, 0), (-1, 0), (0, 1), (2, 0), (-2, 0)]:
                try:
                    P('term', lx + dx, ly + dy, rid); lx, ly = lx + dx, ly + dy; ok = True; break
                except AssertionError:
                    continue
            assert ok, e
        add_interact(IK_NOTE, nid, 0, rx + lx, ry + ly, 2, 2, margin_px=8)
        L.mini[ry + ly][rx + lx] = 9

    # ------------------------------------------------------------------ spawn points
    spawn_defs = {
        'E': [(2, 16), (17, 16), (9, 16), (3, 1)],
        'C': [(2, 3), (15, 3), (2, 15), (15, 15), (8, 9)],
        'S': [(1, 1), (16, 1), (9, 11), (17, 15), (1, 18)],
        'G': [(2, 2), (17, 2), (2, 17), (17, 17), (9, 5)],
        'M': [(1, 1), (16, 1), (1, 16), (16, 16), (9, 12)],
        'MS': [(1, 1), (16, 1), (9, 8), (1, 18), (16, 18)],
        'RL': [(1, 1), (16, 1), (9, 10), (1, 16), (16, 16)],
        'T': [(2, 2), (17, 2), (9, 9), (2, 15), (17, 15)],
        'SO': [(1, 1), (16, 1), (9, 8), (1, 16), (16, 16)],
    }
    for rid, pts in spawn_defs.items():
        rx, ry, _, _ = L.room_rect(rid)
        for (lx, ly) in pts:
            gx2, gy2 = rx + lx, ry + ly
            # nudge to a free cell
            found = None
            for r_ in range(0, 4):
                for dy in range(-r_, r_ + 1):
                    for dx in range(-r_, r_ + 1):
                        x2, y2 = gx2 + dx, gy2 + dy
                        if 0 <= x2 < W and 0 <= y2 < H and L.kind[y2][x2] == 'floor' and not L.solid[y2][x2] \
                                and L.area[y2][x2] == AREA[rid] and (x2, y2) not in L.keepout:
                            found = (x2, y2); break
                    if found:
                        break
                if found:
                    break
            assert found, ("no spawn", rid, lx, ly)
            L.spawns.append((found[0], found[1], AREA[rid]))
            L.floor_gfx[found] = 'spawn'

    # player start: Entrance Hall bottom centre
    rx, ry, _, _ = L.room_rect('E')
    L.player_start = (rx + 9, ry + 13)
    assert L.kind[L.player_start[1]][L.player_start[0]] == 'floor'

    # ------------------------------------------------------------------ lamps / wall decor
    def lamps(rid, xs, warm=True):
        rx, ry, _, _ = L.room_rect(rid)
        for lx in xs:
            L.wall_decor[(rx + lx, ry - 1)] = ('lamp', warm)
            L.lamps.append((rx + lx, ry - 1, warm))
    lamps('E', [4, 15, 18]); lamps('C', [3, 14]); lamps('S', [5, 12]); lamps('G', [3, 6, 13, 16])
    lamps('MS', [3, 14]); lamps('RL', [6, 12]); lamps('T', [6, 14]); lamps('SO', [4, 14]); lamps('M', [4, 14])
    # windows / signs / stains by room style
    style = {'E': ['window', 'plain', 'panel', 'sign'], 'C': ['stencil', 'plain', 'vent', 'sign2'],
             'S': ['stencil', 'plain', 'panel', 'sign'], 'G': ['pipe', 'pipe2', 'plain', 'sign2'],
             'MS': ['pipe', 'plain', 'vent', 'sign'], 'RL': ['window', 'panel', 'plain', 'stain'],
             'T': ['window', 'panel', 'stain', 'sign2'], 'SO': ['window', 'plain', 'panel', 'sign'],
             'M': ['pipe', 'pipe2', 'cable', 'stain']}
    for rid in ROOM_POS:
        rx, ry, w, _ = L.room_rect(rid)
        for lx in range(-0, w):
            key = (rx + lx, ry - 1)
            if key in L.wall_decor:
                continue
            # skip door/passage cells (they are non-wall)
            if L.kind[ry - 1][rx + lx] != 'wall':
                continue
            r = rng.random()
            if r < 0.55:
                kind = 'plain' if rng.random() < 0.6 else 'panel'
            else:
                kind = rng.choice(style[rid])
            L.wall_decor[key] = (kind,)
    # light pools
    L.lit = {}
    for (lx, ly, warm) in L.lamps:
        for dy in range(1, 5):
            for dx in range(-3, 4):
                if (dx * dx) / 12.0 + ((dy - 2.2) ** 2) / 7.0 <= 1.0:
                    x2, y2 = lx + dx, ly + dy
                    if 0 <= x2 < W and 0 <= y2 < H and L.kind[y2][x2] == 'floor':
                        L.lit[(x2, y2)] = 5 if warm else 7
    return L


# ---------------------------------------------------------------------------
# rendering the cell grid into tile entries
# ---------------------------------------------------------------------------
ROOM_FLOOR = {
    'E': ('concrete', 'seam'), 'C': ('plate', 'concrete', 'seam'), 'S': ('concrete', 'seam', 'crack'),
    'G': ('plate', 'grate', 'concrete'), 'MS': ('plate', 'grate', 'hazard_lane'), 'RL': ('lab0', 'lab1'),
    'T': ('test0', 'test1', 'test2'), 'SO': ('green', 'concrete'), 'M': ('green', 'grate', 'concrete'),
}
ROOM_DECALS = {
    'E': [('blood', 0, 5), ('blood', 1, 3), ('debris', 0, 4), ('blood', 2, 5), ('debris', 1, 2), ('bones', 3, 1)],
    'C': [('blood', 2, 4), ('debris', 0, 5), ('scorch', 5, 2), ('blood', 0, 3)],
    'S': [('debris', 1, 6), ('blood', 1, 3), ('blood', 3, 2), ('bones', 3, 2)],
    'G': [('scorch', 5, 4), ('blood', 0, 4), ('debris', 0, 4), ('blood', 2, 3)],
    'MS': [('scorch', 5, 3), ('blood', 2, 4), ('debris', 0, 5), ('blood', 1, 3)],
    'RL': [('blood', 0, 6), ('blood', 3, 3), ('debris', 2, 5), ('debris', 1, 5), ('ooze', 4, 3)],
    'T': [('blood', 3, 4), ('ooze', 4, 5), ('scorch', 5, 4), ('blood', 2, 5)],
    'SO': [('blood', 0, 4), ('debris', 1, 6), ('blood', 1, 3), ('debris', 2, 2)],
    'M': [('ooze', 4, 7), ('blood', 2, 4), ('debris', 0, 4), ('blood', 1, 2)],
}


def floor_tile(L, rid, x, y, rng):
    ts = L.ts
    pick = rng.choice(ROOM_FLOOR[rid])
    seed = rng.randrange(1, 9)
    if pick == 'concrete':
        cv = A.floor_concrete(seed)
    elif pick == 'seam':
        cv = A.floor_seam(seed)
    elif pick == 'plate':
        cv = A.floor_plate()
    elif pick == 'grate':
        cv = A.floor_grate()
    elif pick == 'crack':
        cv = A.floor_crack(seed)
    elif pick == 'green':
        cv = A.floor_green(seed)
    elif pick == 'lab0':
        cv = A.floor_lab(0)
    elif pick == 'lab1':
        cv = A.floor_lab(1)
    elif pick.startswith('test'):
        cv = A.floor_test(int(pick[4]))
    elif pick == 'hazard_lane':
        cv = A.floor_hazard((x // 1) % 2) if (y % 8 == 0) else A.floor_plate()
    else:
        cv = A.floor_concrete(seed)
    return ts.add(cv)


def render(L):
    ts = L.ts
    rng = random.Random(77)
    entries = [[0] * W for _ in range(H)]
    # floor base
    for y in range(H):
        for x in range(W):
            if L.kind[y][x] in ('floor', 'prop', 'door'):
                rid = None
                for r_, a_ in AREA.items():
                    if a_ == L.area[y][x]:
                        rid = r_
                if (x, y) in L.floor_gfx and L.floor_gfx[(x, y)] == 'passage':
                    tid, bank = ts.add(A.floor_plate())
                elif (x, y) in L.floor_gfx and L.floor_gfx[(x, y)] == 'spawn':
                    tid, bank = ts.add(A.floor_crack(5))
                else:
                    tid, bank = floor_tile(L, rid, x, y, rng)
                entries[y][x] = tid | (bank << 12)
    # decals
    for rid in ROOM_POS:
        rx, ry, w, h = L.room_rect(rid)
        for (kind, var, count) in ROOM_DECALS[rid]:
            for _ in range(count):
                for tries in range(30):
                    x, y = rx + rng.randrange(w), ry + rng.randrange(h)
                    if L.kind[y][x] == 'floor' and (x, y) not in L.obj and (x, y) not in L.floor_gfx \
                            and (x, y) not in L.keepout:
                        if kind == 'blood':
                            cv = A.decal_blood(var)
                        elif kind == 'ooze':
                            cv = A.decal_blood(4)
                        elif kind == 'scorch':
                            cv = A.decal_blood(5)
                        elif kind == 'bones':
                            cv = A.decal_debris(3)
                        else:
                            cv = A.decal_debris(var)
                        tid, bank = ts.add(cv)
                        entries[y][x] = tid | (bank << 12)
                        L.floor_gfx[(x, y)] = 'decal'
                        break
    # light pools: re-bank floors (only when tile natural bank is 0)
    for (x, y), pb in L.lit.items():
        e = entries[y][x]
        if (e >> 12) == 0 and L.floor_gfx.get((x, y)) not in ('decal', 'spawn'):
            entries[y][x] = (e & 0x0FFF) | (pb << 12)
    # props
    for (x, y), (tid, bank) in L.obj.items():
        entries[y][x] = tid | (bank << 12)
    # doors (closed + open entries)
    L.door_cells = []
    for d in L.doors:
        w_t, h_t = d['w'], d['h']
        cv = A.obj_door(w_t, h_t, d['vertical'])
        blk = ts.add_block(cv)
        for j in range(h_t):
            for i in range(w_t):
                x, y = d['x'] + i, d['y'] + j
                closed = blk[j][i][0] | (blk[j][i][1] << 12)
                # open version = passage floor
                tid, bank = ts.add(A.floor_plate())
                opened = tid | (bank << 12)
                entries[y][x] = closed
                L.door_cells.append((d['id'], x, y, closed, opened))
    # walls
    def is_wall(x, y):
        if not (0 <= x < W and 0 <= y < H):
            return True
        return L.kind[y][x] == 'wall'
    for y in range(H):
        for x in range(W):
            if L.kind[y][x] != 'wall':
                continue
            south_open = not is_wall(x, y + 1) if y + 1 < H else False
            if south_open:
                dec = L.wall_decor.get((x, y), ('plain',))
                openset = set()
                if not is_wall(x - 1, y):
                    openset.add('W')
                if not is_wall(x + 1, y):
                    openset.add('E')
                kind = dec[0]
                if kind == 'rack':
                    cv = A.obj_weapon_rack(dec[1]).sub(dec[2] * 8, 0, 8, 8)
                    tid, bank = ts.add(cv)
                elif kind == 'lamp':
                    tid, bank = ts.add(A.wall_front('lamp', openset))
                    offcv = A.wall_front('lamp', openset).copy()
                    # dark (unpowered) lamp: recolour yellow/white core to dark steel
                    offcv.remap({1 * 16 + 7: 1 * 16 + 2, 1 * 16 + 14: 1 * 16 + 3, 1 * 16 + 6: 1 * 16 + 1})
                    otid, obank = ts.add(offcv)
                    L.swaps.append((x, y, otid | (obank << 12), tid | (bank << 12)))
                    tid, bank = otid, obank
                else:
                    tid, bank = ts.add(A.wall_front(kind, openset, 2 + (x * 7 + y * 3) % 5))
                entries[y][x] = tid | (bank << 12)
                L.mini[y][x] = 3 if L.mini[y][x] == 0 else L.mini[y][x]
            else:
                openset = set()
                if not is_wall(x, y - 1):
                    openset.add('N')
                if not is_wall(x - 1, y):
                    openset.add('W')
                if not is_wall(x + 1, y):
                    openset.add('E')
                tid, bank = ts.add(A.wall_top(openset, 2 + (x * 5 + y * 11) % 7))
                entries[y][x] = tid | (bank << 12)
                L.mini[y][x] = 3
    # lamp pool swap: floors under lamps get lit palette only once powered -> handled at runtime by palette
    # (banks 5 and 7 start as copies of bank 0).
    # mini: weapon racks etc. keep their codes; any wall cell is 3.
    for y in range(H):
        for x in range(W):
            if L.kind[y][x] == 'wall':
                if L.mini[y][x] == 0:
                    L.mini[y][x] = 3
    return entries


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def validate(L):
    from collections import deque
    sx, sy = L.player_start
    seen = {(sx, sy)}
    dq = deque([(sx, sy)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen:
                # doors are treated as passable for global connectivity
                if L.kind[ny][nx] in ('floor', 'door'):
                    seen.add((nx, ny))
                    dq.append((nx, ny))
    floor_cells = [(x, y) for y in range(H) for x in range(W) if L.kind[y][x] in ('floor', 'door')]
    unreachable = [c for c in floor_cells if c not in seen]
    # check each spawn is reachable w/ doors passable
    bad = [s for s in L.spawns if (s[0], s[1]) not in seen]
    return unreachable, bad, len(floor_cells)


def ascii_dump(L):
    rows = []
    for y in range(H):
        s = ''
        for x in range(W):
            k = L.kind[y][x]
            ch = {'wall': '#', 'floor': '.', 'door': 'D', 'prop': 'o'}[k]
            if (x, y) in [(sp[0], sp[1]) for sp in L.spawns]:
                ch = 's'
            if (x, y) == L.player_start:
                ch = '@'
            s += ch
        rows.append(s)
    return '\n'.join(rows)


def emit_c(L, entries, path, ids_path):
    lines = []
    lines.append('/* GENERATED by tools/gen_assets.py (mapgen.py) - do not edit. BLACKSITE 13. */')
    lines.append('#include "map.h"')
    lines.append('')
    lines.append('const u16 map_entries[MAP_W * MAP_H] = {')
    for y in range(H):
        lines.append('    ' + ','.join('0x%04X' % entries[y][x] for x in range(W)) + ',')
    lines.append('};')
    lines.append('')
    lines.append('const u8 map_flags_rom[MAP_W * MAP_H] = {')
    for y in range(H):
        row = []
        for x in range(W):
            f = 0
            if L.solid[y][x]:
                f |= MF_SOLID
            if L.kind[y][x] == 'door':
                f |= MF_DOOR
            row.append('%d' % f)
        lines.append('    ' + ','.join(row) + ',')
    lines.append('};')
    lines.append('')
    lines.append('const u8 map_area[MAP_W * MAP_H] = {')
    for y in range(H):
        lines.append('    ' + ','.join('%d' % L.area[y][x] for x in range(W)) + ',')
    lines.append('};')
    lines.append('')
    lines.append('const u8 map_mini[MAP_W * MAP_H] = {')
    for y in range(H):
        lines.append('    ' + ','.join('%d' % L.mini[y][x] for x in range(W)) + ',')
    lines.append('};')
    lines.append('')
    # doors
    lines.append('const DoorDef map_doors[NUM_DOORS] = {')
    for d in L.doors:
        lines.append('    { %d, %d, %d, %d, %d, %d, %d, "%s" },' % (d['x'], d['y'], d['w'], d['h'], d['cost'],
                                                                 d['power'], d['opens'], d['name']))
    lines.append('};')
    lines.append('')
    lines.append('const DoorCell map_door_cells[NUM_DOOR_CELLS] = {')
    for (did, x, y, closed, opened) in L.door_cells:
        lines.append('    { %d, %d, %d, 0x%04X, 0x%04X },' % (did, x, y, closed, opened))
    lines.append('};')
    lines.append('')
    lines.append('const Interact map_interacts[NUM_INTERACTS] = {')
    for it in L.interacts:
        lines.append('    { %d, %d, %d, %d, %d, %d, %d },' % (it['kind'], it['id'], it['cost'], it['x'], it['y'], it['w'], it['h']))
    lines.append('};')
    lines.append('')
    lines.append('const PowerSwap map_swaps[NUM_SWAPS] = {')
    for (x, y, off, on) in L.swaps:
        lines.append('    { %d, 0x%04X, 0x%04X },' % (y * W + x, off[0] | (off[1] << 12) if isinstance(off, tuple) else off,
                                                     on[0] | (on[1] << 12) if isinstance(on, tuple) else on))
    lines.append('};')
    lines.append('')
    lines.append('const SpawnPoint map_spawns[NUM_SPAWNS] = {')
    for (x, y, a) in L.spawns:
        lines.append('    { %d, %d, %d },' % (x, y, a))
    lines.append('};')
    lines.append('')
    lines.append('const char *const map_area_names[NUM_AREAS] = {')
    for n in AREA_NAMES:
        lines.append('    "%s",' % n)
    lines.append('};')
    lines.append('')
    lines.append('const char *const map_notes[NUM_NOTES] = {')
    for n in NOTES:
        lines.append('    "%s",' % n)
    lines.append('};')
    lines.append('')
    lines.append('const u8 map_player_start[2] = { %d, %d };' % L.player_start)
    open(path, 'w').write('\n'.join(lines) + '\n')

    with open(ids_path, 'w') as f:
        f.write('/* GENERATED - map constants */\n#ifndef MAP_IDS_H\n#define MAP_IDS_H\n')
        f.write('#define NUM_DOORS %d\n#define NUM_DOOR_CELLS %d\n#define NUM_INTERACTS %d\n' %
                (len(L.doors), len(L.door_cells), len(L.interacts)))
        f.write('#define NUM_SWAPS %d\n#define NUM_SPAWNS %d\n#define NUM_AREAS %d\n#define NUM_NOTES %d\n' %
                (len(L.swaps), len(L.spawns), len(AREA_NAMES), len(NOTES)))
        for k, v in AREA.items():
            f.write('#define AREA_%s %d\n' % (k, v))
        f.write('#endif\n')
