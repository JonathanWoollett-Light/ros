# ROS: RISC-V Operating System

## Compilation

on windows use `wsl` to compile assembly.

1. download `riscv64-elf-ubuntu-24.04-gcc` for the latest release from https://github.com/riscv-collab/riscv-gnu-toolchain/releases
   e.g. `wget https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2025.06.13/riscv64-elf-ubuntu-24.04-gcc-nightly-2025.06.13-nightly.tar.xz`
2. within the downloaded tarball at `riscv/riscv64-unknown-elf/bin` extract `as`, `ld` and `objcopy`
3. assemble source to ELF object file `as -o app.o app.s`
4. link object file to ELF executable `ld -o app.elf app.o`
5. convert ELF to raw binary `objcopy -O binary app.elf app.bin`

when running in QEMU you will probably use the ELF executable.

## Execution

1. Install QEMU: https://www.qemu.org/download/
2. `qemu-system-riscv64`
