bash build.sh
qemu-system-riscv64 \
  -machine virt \
  -cpu rv64 \
  -m 2G \
  -nographic \
  -smp cpus=1,maxcpus=1 \
  -bios build/bios.bin \
  -device loader,file=build/stage1_bootloader.bin,addr=0x80000000,force-raw=on \
  -device loader,file=build/stage2_bootloader.bin,addr=0x80100000,force-raw=on \
  -device loader,file=build/kernel.bin,addr=0x80200000,force-raw=on \
  -device virtio-net-device,netdev=net \
  -netdev user,id=net,hostfwd=tcp::2222-:22 \
  -append "console=ttyS0 earlycon=sbi"
