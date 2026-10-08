#include "game.h"
#include "prof.h"

int main(void)
{
    /* ROM wait states 3/1 (WS0), SRAM 8 cycles, game-pak prefetch on */
    REG_WAITCNT = 0x4317;
    Video_Init();
    Save_Load();
    Audio_Init();
    REG_TM0CNT_L = 0;
    REG_TM0CNT_H = TM_ENABLE | TM_FREQ_1024;
#ifdef DEBUG
    Prof_Init();
#endif
    Game_Init();

    u16 last_t = REG_TM0CNT_L;
    u32 acc = 0;
    int n = 0;
    u32 worst = 0;
    int wn = 0;
    for (;;) {
        Video_VSync();
        /* frame rate estimate, sampled at the same point of every frame (right after VBlank):
           16384 timer ticks per second, a perfect 60 Hz frame is ~273 ticks */
        u16 now = REG_TM0CNT_L;
        u32 dt = (u16)(now - last_t);
        last_t = now;
        if (dt > worst) worst = dt;
        if (++wn >= 300) {
            G.fps_low = worst ? (u8)(16384u / worst) : 60;
            if (G.fps_low > 60) G.fps_low = 60;
            worst = 0; wn = 0;
        }
        acc += dt;
        if (++n >= 30) {
            G.fps = acc ? (u8)((30u * 16384u) / acc) : 60;
            if (G.fps > 60) G.fps = 60;
            acc = 0; n = 0;
        }
        Video_PalCycle(G.frame, power_on);
        Game_Frame();
    }
}
