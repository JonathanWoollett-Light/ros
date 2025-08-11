# Create build directory
mkdir -p build

# Build BIOS
as -o build/bios.o src/bios.s
ld -o build/bios.elf build/bios.o
objcopy -O binary build/bios.elf build/bios.bin

# Build 1st Stage Bootloader
as -o build/stage1_bootloader.o src/stage1_bootloader.s
ld -o build/stage1_bootloader.elf build/stage1_bootloader.o
objcopy -O binary build/stage1_bootloader.elf build/stage1_bootloader.bin

# Build 2nd Stage Bootloader
as -o build/stage2_bootloader.o src/stage2_bootloader.s
ld -o build/stage2_bootloader.elf build/stage2_bootloader.o
objcopy -O binary build/stage2_bootloader.elf build/stage2_bootloader.bin

# Build Kernel
as -o build/kernel.o src/kernel.s
ld -o build/kernel.elf build/kernel.o
objcopy -O binary build/kernel.elf build/kernel.bin
