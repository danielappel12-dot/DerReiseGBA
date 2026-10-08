#include "camera.h"
#include "effects.h"
#include "utils.h"

int cam_x, cam_y;
static s32 fx, fy;       /* smoothed centre (8.8) */

void Cam_Init(int px, int py)
{
    fx = (s32)px << 8; fy = (s32)py << 8;
    cam_x = px - SCREEN_W / 2;
    cam_y = py - SCREEN_H / 2;
}

void Cam_Update(int px, int py, int aim_x, int aim_y)
{
    /* look slightly toward where the player aims, smooth follow */
    s32 tx = ((s32)(px + aim_x) << 8);
    s32 ty = ((s32)(py + aim_y) << 8);
    fx += (tx - fx) >> 3;
    fy += (ty - fy) >> 3;
    int cx = (fx >> 8) - SCREEN_W / 2;
    int cy = (fy >> 8) - SCREEN_H / 2 - 8;
    cx = CLAMP(cx, 0, 512 - SCREEN_W);
    cy = CLAMP(cy, 0, 512 - SCREEN_H);
    if (fx_shake) {
        int a = fx_shake > 6 ? 3 : (fx_shake > 2 ? 2 : 1);
        cx += RandSigned(a);
        cy += RandSigned(a);
    }
    cam_x = cx;
    cam_y = cy;
}
