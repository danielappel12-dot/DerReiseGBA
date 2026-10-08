#!/usr/bin/env python3
"""gen_assets.py - procedural art + level generator for PROJECT: NIGHTFALL.

Writes
    assets/tiles/env.png, anim.png          BG tile sheets (indexed, 256 colour palette)
    assets/ui/font.png, bigfont.png, ui.png, logo.png
    assets/sprites/*.png                    OBJ sheets
    assets/manifest.json                    what is where (read by png2gba.py)
    data/map_data.c, data/map_ids.h         BLACKSITE 13 level tables
    data/title_data.c                       title-screen background tables
    data/tables.c                           sine / atan lookup tables
then runs png2gba.py to turn everything into data/gfx_data.c + data/gfx_ids.h.

Run from the repository root:  python3 tools/gen_assets.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from pix import Canvas, save_indexed, sheet_from_frames, Palette, rgb   # noqa: E402
import palettes                                                           # noqa: E402
import art_tiles as A                                                     # noqa: E402
import art_sprites as S                                                   # noqa: E402
import art_ui as U                                                        # noqa: E402
import mapgen                                                             # noqa: E402


def path(*p):
    full = os.path.join(ROOT, *p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    return full


def ui_palette():
    """palette used to *view* font/ui sheets (slot 1 shadow, 2 fill, 3 light)"""
    p = Palette()
    p.bank(0, ['#000000', '#05070a', '#e8f0f4', '#ffffff', '#55616e', '#8c98a4', '#141a22'] + ['#000000'] * 9)
    return p


def write_sheet(cv, pal, rel, scale=1):
    save_indexed(cv.p, cv.w, cv.h, pal, path(rel))
    # preview (upscaled) goes to docs/preview
    if scale > 1:
        from PIL import Image
        im = Image.open(path(rel))
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        big.save(path('docs', 'preview', os.path.basename(rel).replace('.png', '_x%d.png' % scale)))


# ---------------------------------------------------------------------------
def build_title(ts):
    """30x20 (+padding to 32x32) title-screen background tilemap using env tiles"""
    ent = [[0] * 32 for _ in range(32)]
    rng = __import__('random').Random(5)
    # wall background (front faces) rows 0..13
    for y in range(0, 14):
        for x in range(32):
            if y in (2, 3):
                kind = 'pipe' if y == 2 else 'pipe2'
            elif y == 0:
                kind = 'panel'
            else:
                r = rng.random()
                kind = 'plain' if r < 0.6 else ('panel' if r < 0.8 else rng.choice(['vent', 'cable', 'sign2']))
            open_ = set()
            tid, bank = ts.add(A.wall_front(kind, open_, 2 + (x * 3 + y) % 5))
            ent[y][x] = tid | (bank << 12)
    # lamps
    for x in (4, 14, 25):
        tid, bank = ts.add(A.wall_front('lamp', set()))
        ent[1][x] = tid | (bank << 12)
    # windows
    for x in (8, 20, 28):
        tid, bank = ts.add(A.wall_front('window', set()))
        ent[10][x] = tid | (bank << 12)
    # hazard stripe row
    for x in range(32):
        tid, bank = ts.add(A.floor_hazard((x // 1) % 2))
        ent[14][x] = tid | (bank << 12)
    # floor rows 15..19 : plates + conveyor belt on row 17
    for y in range(15, 20):
        for x in range(32):
            if y == 17:
                continue
            cv = A.floor_plate() if (x + y) % 3 else A.floor_grate()
            tid, bank = ts.add(cv)
            ent[y][x] = tid | (bank << 12)
    conv_ids = ts.add(A.anim_conveyor(0), force_new=True)
    for x in range(32):
        ent[17][x] = conv_ids[0] | (conv_ids[1] << 12)
    # gears: two 2x2 gear blocks (distinct tiles so they can be animated separately)
    gearA = ts.add_block(A.anim_gear(0), force_new=True)
    gearB = ts.add_block(A.anim_gear(0), force_new=True)
    gearC = ts.add_block(A.anim_gear(0), force_new=True)
    def put_block(blk, bx, by):
        for j, row in enumerate(blk):
            for i, (tid, bank) in enumerate(row):
                ent[by + j][bx + i] = tid | (bank << 12)
    put_block(gearA, 2, 5); put_block(gearB, 26, 6); put_block(gearC, 23, 10)
    info = dict(gearA=gearA[0][0][0], gearB=gearB[0][0][0], gearC=gearC[0][0][0], conv=conv_ids[0])
    return ent, info


def main():
    os.makedirs(path('docs', 'preview', 'x'), exist_ok=True)
    bg_pal = palettes.build_bg_palette()
    obj_pal = palettes.build_obj_palette()
    uipal = ui_palette()
    manifest = {'bg_palette': None, 'obj_palette': None}

    # ------------------------------------------------------------------ tiles + map
    ts = A.TileSet()
    ts.add(Canvas(8, 8))                         # id 0: blank
    L = mapgen.build(ts)
    unreachable, bad, nfloor = mapgen.validate(L)
    entries = mapgen.render(L)
    print("map: %d floor cells, %d unreachable, %d bad spawns" % (nfloor, len(unreachable), len(bad)))
    if unreachable:
        print("  unreachable sample:", unreachable[:12])
    if bad:
        print("  bad spawns:", bad)
    if os.environ.get('DUMP_MAP'):
        print(mapgen.ascii_dump(L))

    title_ent, tinfo = build_title(ts)

    # animated tiles (gear frames, conveyor frames) stored in their own sheet
    anim = []
    for f in range(4):
        blk = A.anim_gear(f).copy()
        anim += [blk.sub(0, 0, 8, 8), blk.sub(8, 0, 8, 8), blk.sub(0, 8, 8, 8), blk.sub(8, 8, 8, 8)]
    for f in range(4):
        anim.append(A.anim_conveyor(f))
    anim_sheet = sheet_from_frames(anim, 16, 8, 8)

    print("BG tiles used: %d (limit 512 incl. nothing else in charblock 0)" % len(ts.canvases))
    assert len(ts.canvases) <= 512, "too many env tiles"
    env = sheet_from_frames(ts.canvases, 16, 8, 8)
    write_sheet(env, bg_pal, 'assets/tiles/env.png', 4)
    write_sheet(anim_sheet, bg_pal, 'assets/tiles/anim.png', 4)

    # full-map preview (lit palette banks shown as if powered)
    big = Canvas(512, 512)
    for y in range(64):
        for x in range(64):
            e = entries[y][x]
            tid, bank = e & 0x3FF, e >> 12
            t = ts.canvases[tid]
            for yy in range(8):
                for xx in range(8):
                    v = t.p[yy][xx]
                    if v:
                        big.px(x * 8 + xx, y * 8 + yy, (bank << 4) | (v & 15))
    pv = palettes.build_bg_palette()
    pv.bank(5, palettes.BG5_LIT_WARM)
    pv.bank(7, palettes.BG7_LIT_COOL)
    save_indexed(big.p, 512, 512, pv, path('docs', 'preview', 'blacksite13_map.png'))
    mapgen.emit_c(L, entries, path('data', 'map_data.c'), path('data', 'map_ids.h'))

    # title data
    with open(path('data', 'title_data.c'), 'w') as f:
        f.write('/* GENERATED by tools/gen_assets.py - title screen background */\n#include "gba.h"\n')
        f.write('const u16 title_bg[32 * 32] ALIGN4 = {\n')
        for y in range(32):
            f.write('    ' + ','.join('0x%04X' % title_ent[y][x] for x in range(32)) + ',\n')
        f.write('};\n')
        f.write('const u16 title_gear_tiles[3] = { %d, %d, %d };\n' % (tinfo['gearA'], tinfo['gearB'], tinfo['gearC']))
        f.write('const u16 title_conv_tile = %d;\n' % tinfo['conv'])

    # ------------------------------------------------------------------ UI sheets
    font = U.font_sheet()
    big = U.bigfont_sheet()
    uis = U.ui_sheet()
    logo = U.logo_canvas()
    write_sheet(font, uipal, 'assets/ui/font.png', 4)
    write_sheet(big, uipal, 'assets/ui/bigfont.png', 3)
    write_sheet(uis, uipal, 'assets/ui/ui.png', 4)
    write_sheet(logo, bg_pal, 'assets/ui/logo.png', 3)

    # ------------------------------------------------------------------ sprites
    sheets = []

    def add_sheet(name, frames, fw, fh, cols=None):
        names = [n for n, _ in frames]
        cvs = [c for _, c in frames]
        cols = cols or min(len(cvs), 16 * 8 // fw if fw else 8)
        cols = min(cols, len(cvs))
        sh = sheet_from_frames(cvs, cols, fw, fh)
        rel = 'assets/sprites/%s.png' % name
        write_sheet(sh, obj_pal, rel, 4)
        sheets.append(dict(name=name, png=rel, fw=fw, fh=fh, cols=cols, count=len(cvs), names=names))

    views = ('down', 'up', 'side')
    pl = []
    for v in views:
        for f in range(4):
            pl.append(('P_WALK_%s_%d' % (v.upper(), f), S.player(v, f)))
    for v in views:
        pl.append(('P_SHOOT_%s' % v.upper(), S.player(v, 0, 'shoot')))
    for v in views:
        pl.append(('P_RELOAD_%s' % v.upper(), S.player(v, 0, 'reload')))
    for f in range(3):
        pl.append(('P_DEAD_%d' % f, S.player_dead(f)))
    add_sheet('player', pl, 16, 32, 8)
    for nm, fn in (('shambler', S.shambler), ('rusher', S.rusher), ('spitter', S.spitter), ('stalker', S.stalker)):
        fr = []
        for v in views:
            for f in range(3):
                fr.append(('E_%s_%s_%d' % (nm.upper(), v.upper(), f), fn(v, f)))
        add_sheet(nm, fr, 16, 32, 9)
    fr = []
    for v in views:
        for f in range(3):
            fr.append(('E_BRUTE_%s_%d' % (v.upper(), f), S.brute(v, f)))
    add_sheet('brute', fr, 32, 32, 9)
    corp = []
    for bank, nm in ((1, 'SHAMBLER'), (2, 'RUSHER'), (3, 'SPITTER'), (4, 'STALKER')):
        for f in range(2):
            corp.append(('C_%s_%d' % (nm, f), S.zombie_corpse(bank, f)))
    add_sheet('corpses', corp, 16, 16, 8)
    add_sheet('brute_corpse', [('C_BRUTE_0', S.brute_corpse(0)), ('C_BRUTE_1', S.brute_corpse(1))], 32, 16, 2)
    add_sheet('fx8', [(('FX_' + n), c) for n, c in S.fx8()], 8, 8, 16)
    add_sheet('fx16', [(('FX_' + n), c) for n, c in S.fx16()], 16, 16, 8)
    add_sheet('shadow', [('SHADOW_S', S.shadow16x8())], 16, 8, 1)
    add_sheet('shadow_big', [('SHADOW_B', S.shadow_big())], 32, 8, 1)

    manifest['sheets'] = sheets
    manifest['bg'] = dict(
        env=dict(png='assets/tiles/env.png', count=len(ts.canvases), cols=16),
        anim=dict(png='assets/tiles/anim.png', count=len(anim), cols=16),
        font=dict(png='assets/ui/font.png', count=96, cols=16),
        bigfont=dict(png='assets/ui/bigfont.png', count=len(U.BIG_CHARS), cols=16, chars=U.BIG_CHARS),
        ui=dict(png='assets/ui/ui.png', count=len(U.UI_TILE_NAMES), cols=16, names=U.UI_TILE_NAMES),
        logo=dict(png='assets/ui/logo.png', w=logo.w, h=logo.h),
    )
    manifest['lit_warm'] = palettes.BG5_LIT_WARM
    manifest['lit_cool'] = palettes.BG7_LIT_COOL
    manifest['lit_base_warm'] = palettes.BG0_STRUCT
    manifest['lit_base_cool'] = palettes.BG0_STRUCT
    with open(path('assets', 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=1)

    # ------------------------------------------------------------------ tables
    sin = [int(round(math.sin(i * 2 * math.pi / 256) * 256)) for i in range(256)]
    atan = [int(round(math.atan(i / 64.0) * 256 / (2 * math.pi))) for i in range(65)]
    with open(path('data', 'tables.c'), 'w') as f:
        f.write('/* GENERATED by tools/gen_assets.py */\n#include "gba.h"\n')
        f.write('const s16 sin_tab[256] = {\n')
        for i in range(0, 256, 16):
            f.write('    ' + ','.join(str(v) for v in sin[i:i + 16]) + ',\n')
        f.write('};\nconst u8 atan_tab[65] = {\n')
        for i in range(0, 65, 16):
            f.write('    ' + ','.join(str(v) for v in atan[i:i + 16]) + ',\n')
        f.write('};\n')

    import png2gba
    png2gba.convert(ROOT)
    print("assets generated OK")


if __name__ == '__main__':
    main()
