#include "nav.h"
#include "map.h"
#include "utils.h"

#define N_CELLS (MAP_W * MAP_H)

static u8 field_a[N_CELLS] EWRAM_BSS ALIGN4;
static u8 field_b[N_CELLS] EWRAM_BSS ALIGN4;
static u16 queue[N_CELLS] EWRAM_BSS ALIGN4;
static u8 *cur = field_a;       /* completed field read by enemies */
static u8 *work = field_b;      /* field being built */
static int q_head, q_tail;
static int building;
static int last_tx = -1, last_ty = -1;
static int ready;

void Nav_Reset(void)
{
    memset(field_a, 255, N_CELLS);
    memset(field_b, 255, N_CELLS);
    cur = field_a; work = field_b;
    building = 0; ready = 0;
    last_tx = last_ty = -1;
}

int Nav_Ready(void) { return ready; }

static void begin(int tx, int ty)
{
    memset(work, 255, N_CELLS);
    q_head = q_tail = 0;
    work[ty * MAP_W + tx] = 0;
    queue[q_tail++] = (u16)(ty * MAP_W + tx);
    building = 1;
    last_tx = tx; last_ty = ty;
}

IWRAM_CODE void Nav_Update(int tx, int ty, int budget)
{
    if (!building) {
        if (tx == last_tx && ty == last_ty) return;
        begin(tx, ty);
    }
    while (budget-- > 0 && q_head < q_tail) {
        int c = queue[q_head++];
        u8 d = work[c] + 1;
        int x = c & 63, y = c >> 6;
        if (d == 255) continue;
        if (x > 0 && work[c - 1] == 255 && !(map_flags[c - 1] & MF_SOLID)) { work[c - 1] = d; queue[q_tail++] = (u16)(c - 1); }
        if (x < MAP_W - 1 && work[c + 1] == 255 && !(map_flags[c + 1] & MF_SOLID)) { work[c + 1] = d; queue[q_tail++] = (u16)(c + 1); }
        if (y > 0 && work[c - MAP_W] == 255 && !(map_flags[c - MAP_W] & MF_SOLID)) { work[c - MAP_W] = d; queue[q_tail++] = (u16)(c - MAP_W); }
        if (y < MAP_H - 1 && work[c + MAP_W] == 255 && !(map_flags[c + MAP_W] & MF_SOLID)) { work[c + MAP_W] = d; queue[q_tail++] = (u16)(c + MAP_W); }
    }
    if (building && q_head >= q_tail) {
        u8 *t = cur; cur = work; work = t;
        building = 0;
        ready = 1;
    }
}

int Nav_Dist(int tx, int ty)
{
    if ((u32)tx >= MAP_W || (u32)ty >= MAP_H) return 255;
    return cur[ty * MAP_W + tx];
}

IWRAM_CODE int Nav_Step(int tx, int ty, int *dirx, int *diry)
{
    static const s8 ox[8] = { 1, -1, 0, 0, 1, 1, -1, -1 };
    static const s8 oy[8] = { 0, 0, 1, -1, 1, -1, 1, -1 };
    if ((u32)tx >= MAP_W || (u32)ty >= MAP_H) return 0;
    int best = cur[ty * MAP_W + tx];
    int bi = -1;
    /* solid tiles are 255 in the field unless they were the seed; a start tile that is
       itself unreachable (e.g. an enemy squeezed against a wall) still looks at its neighbours */
    for (int i = 0; i < 8; i++) {
        int nx = tx + ox[i], ny = ty + oy[i];
        if ((u32)nx >= MAP_W || (u32)ny >= MAP_H) continue;
        int d = cur[ny * MAP_W + nx];
        if (d >= best) continue;
        if (i >= 4) {   /* diagonal: both orthogonal neighbours must be open */
            if (map_flags[ty * MAP_W + nx] & MF_SOLID) continue;
            if (map_flags[ny * MAP_W + tx] & MF_SOLID) continue;
        }
        best = d; bi = i;
    }
    if (bi < 0) return 0;
    *dirx = ox[bi]; *diry = oy[bi];
    return 1;
}
