/*
 * Stage-2 Bootloader
 * More capable second-stage loader
 */
        .option norelax
        .section .text
        .globl _start

        /* Debug symbols for breakpoints */
        .globl stage2_entry
        .globl stage2_sbi_call
        .globl stage2_kernel_jump

_start:
stage2_entry:
        /* Set up stack */
        li      sp, 0x81000000

        /* Debug breakpoint marker */
        nop

stage2_sbi_call:
        /* Print stage identifier via SBI */
        li      a0, 'S'         /* Character to print */
        li      a7, 0x00        /* SBI extension ID */
        li      a6, 0x01        /* SBI function ID (console putchar) */
        ecall

        li      a0, '2'         /* Stage 2 identifier */
        ecall

        /* Small delay for debugging visibility */
        li      t0, 1000000
delay_loop:
        addi    t0, t0, -1
        bnez    t0, delay_loop

stage2_kernel_jump:
        /* Set up kernel arguments */
        mv      a0, zero        /* Hart ID */
        mv      a1, zero        /* Device tree pointer */

        /* Debug breakpoint marker */
        nop

        /* Jump to kernel */
        li      t0, 0x80200000
        jr      t0

        /* Error handler (should never reach here) */
error_halt:
        li      a0, 'E'
        li      a7, 0x00
        li      a6, 0x01
        ecall
        j       error_halt
