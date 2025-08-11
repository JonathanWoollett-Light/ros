as -o app.o app.s
ld -o app.elf app.o
objcopy -O binary app.elf app.bin