/*
 * Minimal RISC-V Kernel
 * Simple kernel that prints identification and enters WFI loop
 */
        .option norelax
        .section .text
        .globl _start

_start:
        /* Set up kernel stack */
        li      sp, 0x81000000

        /* Print kernel identifier */
        li      a0, 'K'         /* Kernel identifier */
        li      a7, 0x00        /* SBI extension */
        li      a6, 0x01        /* SBI console putchar */
        ecall

        /* Enable interrupts */
        li      t0, (1<<7)|(1<<11)  /* MEIE | MTIE */
        csrs    mie, t0
        csrsi   mstatus, 0x8        /* Set MIE bit */

        /* Main kernel loop */
kernel_loop:
        wfi                     /* Wait for interrupt */
        j       kernel_loop     /* Continue waiting */
