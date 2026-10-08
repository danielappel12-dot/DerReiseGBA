@ ---------------------------------------------------------------------------
@ crt0.s - GBA ROM header, start-up code, interrupt dispatcher and a few
@ hand-written ARM helpers.  Part of PROJECT: NIGHTFALL.
@ ---------------------------------------------------------------------------
    .section .crt0, "ax", %progbits
    .arm
    .global _start
    .global VBlankIntrWait
    .global SoftReset

_start:
    b       rom_start
    @ 0x04 - 0x9F : Nintendo logo.  Filled in by gbafix (tools/gbafix.py or the
    @ devkitPro gbafix) after linking.
    .space  156
    @ 0xA0 : header proper
    .ascii  "NIGHTFALL\0\0\0"       @ game title (12 bytes)
    .ascii  "ANFE"                  @ game code
    .ascii  "01"                    @ maker code
    .byte   0x96                    @ fixed value
    .byte   0x00                    @ main unit code
    .byte   0x00                    @ device type
    .space  7                       @ reserved
    .byte   0x00                    @ software version
    .byte   0x00                    @ header checksum (gbafix)
    .space  2                       @ reserved

rom_start:
    @ stacks (BIOS has already set these up, but be explicit)
    msr     cpsr_c, #0xD2           @ IRQ mode, IRQ+FIQ off
    ldr     sp, =0x03007FA0
    msr     cpsr_c, #0xD3           @ SVC mode
    ldr     sp, =0x03007FE0
    msr     cpsr_c, #0x1F           @ System mode, IRQs on (IME still 0)
    ldr     sp, =0x03007F00

    @ copy initialised IWRAM (.iwram + .data)
    ldr     r0, =__iwram_lma
    ldr     r1, =__iwram_start
    ldr     r2, =__iwram_end
1:  cmp     r1, r2
    ldrlo   r3, [r0], #4
    strlo   r3, [r1], #4
    blo     1b

    @ copy initialised EWRAM
    ldr     r0, =__ewram_lma
    ldr     r1, =__ewram_start
    ldr     r2, =__ewram_end
2:  cmp     r1, r2
    ldrlo   r3, [r0], #4
    strlo   r3, [r1], #4
    blo     2b

    @ zero IWRAM bss
    mov     r0, #0
    ldr     r1, =__bss_start
    ldr     r2, =__bss_end
3:  cmp     r1, r2
    strlo   r0, [r1], #4
    blo     3b

    @ zero EWRAM bss
    ldr     r1, =__ewram_bss_start
    ldr     r2, =__ewram_bss_end
4:  cmp     r1, r2
    strlo   r0, [r1], #4
    blo     4b

    @ install the interrupt dispatcher
    ldr     r0, =irq_dispatch
    ldr     r1, =0x03007FFC
    str     r0, [r1]

    ldr     r0, =main
    bx      r0
5:  b       5b

@ void VBlankIntrWait(void)  - BIOS call 5
    .type   VBlankIntrWait, %function
VBlankIntrWait:
    swi     0x050000
    bx      lr

@ void SoftReset(void) - BIOS call 0
    .type   SoftReset, %function
SoftReset:
    swi     0x000000
    bx      lr

    .pool

@ ---------------------------------------------------------------------------
@ Everything below lives in IWRAM (fast 32-bit bus)
@ ---------------------------------------------------------------------------
    .section .iwram, "ax", %progbits
    .arm
    .align  2
    .global memcpy32
    .global memset32

@ BIOS jumps here with r0-r3,r12,lr already saved.
    .type   irq_dispatch, %function
irq_dispatch:
    mov     r3, #0x04000000
    add     r3, r3, #0x200
    ldr     r2, [r3]                @ low: IE, high: IF
    and     r1, r2, r2, lsr #16     @ r1 = IE & IF
    strh    r1, [r3, #2]            @ acknowledge
    ldr     r0, =0x03007FF8         @ BIOS "IntrWait" flags
    ldrh    r2, [r0]
    orr     r2, r2, r1
    strh    r2, [r0]
    bx      lr
    .pool

@ void memcpy32(void *dst, const void *src, u32 words)
    .type   memcpy32, %function
memcpy32:
    stmfd   sp!, {r4-r10}
    movs    r12, r2, lsr #3
    beq     2f
1:  ldmia   r1!, {r3-r10}
    stmia   r0!, {r3-r10}
    subs    r12, r12, #1
    bne     1b
2:  ands    r2, r2, #7
    beq     4f
3:  ldr     r3, [r1], #4
    str     r3, [r0], #4
    subs    r2, r2, #1
    bne     3b
4:  ldmfd   sp!, {r4-r10}
    bx      lr

@ void memset32(void *dst, u32 value, u32 words)
    .type   memset32, %function
memset32:
    stmfd   sp!, {r4-r9}
    mov     r3, r1
    mov     r4, r1
    mov     r5, r1
    mov     r6, r1
    mov     r7, r1
    mov     r8, r1
    mov     r9, r1
    movs    r12, r2, lsr #3
    beq     2f
1:  stmia   r0!, {r1, r3-r9}
    subs    r12, r12, #1
    bne     1b
2:  ands    r2, r2, #7
    beq     4f
3:  str     r1, [r0], #4
    subs    r2, r2, #1
    bne     3b
4:  ldmfd   sp!, {r4-r9}
    bx      lr
    .pool
