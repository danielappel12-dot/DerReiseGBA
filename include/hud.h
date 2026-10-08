#ifndef HUD_H
#define HUD_H
#include "gba.h"
#include "video.h"

void Hud_Game(void);                          /* draw the in-game HUD into the text layer */
void Hud_Message(const char *l1, const char *l2, int color, int frames);
void Hud_Banner(const char *text, int color);  /* big centred banner (one frame) */
void Hud_Debug(void);
void Hud_Update(void);

#endif
