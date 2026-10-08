#ifndef CAMERA_H
#define CAMERA_H
#include "gba.h"

extern int cam_x, cam_y;       /* top-left of the view in world pixels (includes screen shake) */
void Cam_Init(int px, int py);
void Cam_Update(int px, int py, int aim_x, int aim_y);

#endif
