#include "collision.h"
#include "map.h"

IWRAM_CODE int Col_BoxSolid(int px, int py, int hw, int hu)
{
    int tx0 = (px - hw) >> 3, tx1 = (px + hw - 1) >> 3;
    int ty0 = (py - hu) >> 3, ty1 = (py - 1) >> 3;
    for (int ty = ty0; ty <= ty1; ty++)
        for (int tx = tx0; tx <= tx1; tx++)
            if (Map_SolidT(tx, ty)) return 1;
    return 0;
}

IWRAM_CODE int Col_Move(s32 *x, s32 *y, s32 dx, s32 dy, int hw, int hu)
{
    int hit = 0;
    if (dx) {
        s32 nx = *x + dx;
        int py = *y >> 8;
        if (Col_BoxSolid(nx >> 8, py, hw, hu)) {
            int npx = nx >> 8;
            if (dx > 0) {
                int tcx = (npx + hw - 1) >> 3;
                nx = (s32)((tcx << 3) - hw) << 8;
            } else {
                int tcx = (npx - hw) >> 3;
                nx = (s32)(((tcx + 1) << 3) + hw) << 8;
            }
            /* snapping may still collide when squeezed; then stay */
            if (Col_BoxSolid(nx >> 8, py, hw, hu)) nx = *x;
            hit |= COL_HIT_X;
        }
        *x = nx;
    }
    if (dy) {
        s32 ny = *y + dy;
        int px = *x >> 8;
        if (Col_BoxSolid(px, ny >> 8, hw, hu)) {
            int npy = ny >> 8;
            if (dy > 0) {
                int tcy = (npy - 1) >> 3;
                ny = (s32)(tcy << 3) << 8;
            } else {
                int tcy = (npy - hu) >> 3;
                ny = (s32)(((tcy + 1) << 3) + hu) << 8;
            }
            if (Col_BoxSolid(px, ny >> 8, hw, hu)) ny = *y;
            hit |= COL_HIT_Y;
        }
        *y = ny;
    }
    return hit;
}

IWRAM_CODE int Col_LineClear(int x0, int y0, int x1, int y1)
{
    int dx = x1 - x0, dy = y1 - y0;
    int adx = dx < 0 ? -dx : dx, ady = dy < 0 ? -dy : dy;
    int n = (adx > ady ? adx : ady) >> 2;       /* sample every 4 px */
    if (n < 1) return 1;
    if (n > 48) n = 48;
    s32 sx = (dx << 8) / n, sy = (dy << 8) / n;
    s32 cx = x0 << 8, cy = y0 << 8;
    for (int i = 1; i < n; i++) {
        cx += sx; cy += sy;
        if (Map_SolidPx(cx >> 8, cy >> 8)) return 0;
    }
    return 1;
}
