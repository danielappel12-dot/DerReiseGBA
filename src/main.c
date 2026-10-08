#include "game.h"

int main(void)
{
    Video_Init();
    Save_Load();
    Audio_Init();
    REG_TM0CNT_L = 0;
    REG_TM0CNT_H = TM_ENABLE | TM_FREQ_1024;
    Game_Init();

    u16 last_t = REG_TM0CNT_L;
    u32 acc = 0;
    int n = 0;
    for (;;) {
        Video_VSync();
        Video_PalCycle(G.frame, power_on);
        Game_Frame();
        /* frame rate estimate: 16384 timer ticks per second, 60 frames = 16384 ticks when on target */
        u16 now = REG_TM0CNT_L;
        acc += (u16)(now - last_t);
        last_t = now;
        if (++n >= 30) {
            G.fps = acc ? (u8)((30u * 16384u) / acc) : 60;
            if (G.fps > 60) G.fps = 60;
            acc = 0; n = 0;
        }
    }
}
