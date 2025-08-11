/*
 * RISC-V BIOS - First stage boot code
 * Runs in M-mode at reset vector 0x1000
 */
        .option norelax
        .section .text
        .globl _start

_start:
        /* Install minimal trap handler */
        la      t0, trap_vector
        csrw    mtvec, t0

        /* Disable paging */
        csrw    satp, zero

        /* Set up stack */
        li      sp, 0x81000000

        /* Jump to Stage-1 bootloader */
        li      t0, 0x80000000
        jr      t0

trap_vector:
        /* Simple trap handler - infinite loop */
        j       trap_vector
