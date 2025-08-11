/*
 * Stage-1 Bootloader
 * Minimal first-stage loader in M-mode
 */
        .option norelax
        .section .text
        .globl _start

_start:
        /* Set up stack */
        li      sp, 0x81000000

        /* Clear machine interrupt enable */
        csrci   mstatus, (1<<3)

        /* Prepare arguments for next stage */
        csrr    a0, mhartid     /* Hart ID */
        mv      a1, zero        /* Device tree pointer (none) */

        /* Jump to Stage-2 bootloader */
        li      t0, 0x80100000
        jr      t0
