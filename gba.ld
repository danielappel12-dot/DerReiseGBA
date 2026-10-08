/* Linker script for PROJECT: NIGHTFALL (Game Boy Advance, plain arm-none-eabi toolchain) */
OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)

MEMORY
{
    rom   (rx)  : ORIGIN = 0x08000000, LENGTH = 32M
    ewram (rwx) : ORIGIN = 0x02000000, LENGTH = 256K
    iwram (rwx) : ORIGIN = 0x03000000, LENGTH = 32K - 0x800   /* top 2 KB: stacks + BIOS area */
}

SECTIONS
{
    .text : ALIGN(4)
    {
        KEEP(*(.crt0))
        *(EXCLUDE_FILE(*enemy.o *nav.o *bullets.o *utils.o *render.o) .text EXCLUDE_FILE(*enemy.o *nav.o *bullets.o *utils.o *render.o) .text.*)
        *(.rodata .rodata.* .gnu.linkonce.r.*)
        *(.glue_7 .glue_7t .vfp11_veneer .v4_bx .iplt .igot.plt)
        . = ALIGN(4);
    } > rom

    .ARM.exidx : { *(.ARM.exidx*) } > rom

    /* Initialised IWRAM: hot code + data, copied from ROM at boot */
    .iwram : ALIGN(4)
    {
        __iwram_start = .;
        *(.iwram .iwram.*)
        /* hot per-frame code runs from fast IWRAM (Thumb, no ROM wait states) */
        *enemy.o(.text .text.*)
        *nav.o(.text .text.*)
        *bullets.o(.text .text.*)
        *utils.o(.text .text.*)
        *render.o(.text .text.*)
        *(.data .data.*)
        . = ALIGN(4);
        __iwram_end = .;
    } > iwram AT> rom
    __iwram_lma = LOADADDR(.iwram);

    /* Initialised EWRAM */
    .ewram : ALIGN(4)
    {
        __ewram_start = .;
        *(.ewram .ewram.*)
        . = ALIGN(4);
        __ewram_end = .;
    } > ewram AT> rom
    __ewram_lma = LOADADDR(.ewram);

    .bss (NOLOAD) : ALIGN(4)
    {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > iwram

    .ewram_bss (NOLOAD) : ALIGN(4)
    {
        __ewram_bss_start = .;
        *(.ewram_bss .ewram_bss.*)
        . = ALIGN(4);
        __ewram_bss_end = .;
    } > ewram

    /DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) *(.eh_frame*) }
}
