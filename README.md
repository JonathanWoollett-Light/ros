# RISC-V Boot Chain Project

A complete RISC-V boot chain implementation with BIOS, two-stage bootloader, and minimal kernel. This project demonstrates the full boot sequence from firmware initialization through kernel startup, with comprehensive debugging support.

## Project Overview

The boot chain consists of four stages:

1. **BIOS** (0x1000) - Minimal firmware that sets up the basic execution environment
2. **Stage-1 Bootloader** (0x80000000) - First bootloader stage with minimal functionality
3. **Stage-2 Bootloader** (0x80100000) - Second bootloader stage with enhanced capabilities
4. **Kernel** (0x80200000) - Minimal kernel implementation

Expected console output: `S2K` (Stage-2 identifier, then Kernel identifier)

## Prerequisites

- Ubuntu 20.04+ or compatible Linux distribution
- Python 3.6+
- Internet connection for downloading toolchain
- Sudo access for installing QEMU


## Installation

### 1. Clone or Create Project Directory

```bash
mkdir riscv-boot-project && cd riscv-boot-project
```


### 2. Set Up Required Files

Create the development script (`riscv_dev.py`) and source files as described in the project structure below.

### 3. Install Toolchain and Dependencies

```bash
python3 riscv_dev.py install
```

This command will:

- Download the RISC-V GCC toolchain
- Extract required binaries (`as`, `ld`, `objcopy`, `gdb`, etc.)
- Install QEMU for RISC-V emulation
- Set up the build directory structure


### 4. Install VS Code Extensions (Recommended)

For optimal debugging experience, install the recommended VS Code extensions:

```bash
# Install required extensions
code --install-extension webfreak.debug
code --install-extension ms-vscode.cpptools

# Install recommended extensions
code --install-extension dan-c-underwood.arm
code --install-extension zhwu95.riscv
```

Or open the workspace in VS Code and accept the extension recommendations when prompted.

## Building

### Basic Build

```bash
python3 riscv_dev.py build
```


### Debug Build (Recommended)

```bash
python3 riscv_dev.py build --debug
```

The debug build includes:

- Debug symbols in ELF files
- Disassembly listings in `build/debug/`
- Symbol tables for each component
- GDB initialization scripts


## Running

### Normal Execution

```bash
python3 riscv_dev.py run
```

This runs the complete boot sequence in QEMU and should output `S2K` to indicate successful boot progression.

### Debug Mode

```bash
python3 riscv_dev.py run --debug
```

This starts QEMU with GDB server enabled, waiting for debugger connection.

## Debugging

### Terminal-Based Debugging with GDB

#### Step 1: Start QEMU in Debug Mode

```bash
python3 riscv_dev.py run --debug
```

You should see output similar to:

```
=== Running RISC-V Boot Chain (Debug Mode) ===
Starting QEMU in debug mode (waiting for GDB)...
Connect with: build/bin/riscv64-unknown-elf-gdb -x build/debug/gdb_init.gdb
QEMU started and waiting for debugger connection.
```


#### Step 2: Connect with GDB (New Terminal)

```bash
build/bin/riscv64-unknown-elf-gdb -x build/debug/gdb_init.gdb
```


#### Step 3: Debug Commands

Once connected, you'll see:

```
=== RISC-V Boot Chain Debugger ===
Available commands:
  show-boot-state : Show current boot state
  step-boot      : Step one instruction and show state
  continue       : Continue execution
===================================
```

**Common debugging workflow:**

```gdb
# View current state
(gdb) show-boot-state

# Continue to first breakpoint (BIOS)
(gdb) continue

# Step through instructions
(gdb) stepi

# Continue to next stage (Stage-1 Bootloader)
(gdb) continue

# Set additional breakpoints
(gdb) break stage2_sbi_call

# Examine memory and registers
(gdb) info registers
(gdb) x/10i $pc
(gdb) x/16x $sp

# Continue execution
(gdb) continue
```

**Advanced debugging:**

```gdb
# Examine specific memory regions
(gdb) x/32i 0x80100000    # Disassemble Stage-2 code
(gdb) x/16gx 0x81000000   # Check stack area

# Watch memory locations
(gdb) watch *(int*)0x80001000

# Display register values continuously
(gdb) display $pc
(gdb) display $sp
```


### VS Code Debugging

#### Step 1: Open Project in VS Code

```bash
code .
```


#### Step 2: Build with Debug Information

- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "build-debug"

Or use the keyboard shortcut: `Ctrl+Shift+B`

#### Step 3: Start Debugging Session

**Method 1: Using Debug Panel**

- Open the "Run and Debug" panel (`Ctrl+Shift+D`)
- Select "Debug RISC-V Boot Chain" configuration
- Click the green play button or press `F5`

**Method 2: Using Keyboard Shortcut**

- Press `F5` directly


#### Step 4: Debugging Features

VS Code will automatically:

- Start QEMU in debug mode
- Connect GDB to the remote target
- Load all symbol files
- Set breakpoints at boot stage entry points

**Available debugging features:**

- **Set breakpoints**: Click in the gutter next to line numbers
- **Step execution**:
    - `F10` - Step over
    - `F11` - Step into
    - `Shift+F11` - Step out
    - `F5` - Continue
- **View variables**: Check the "Variables" panel
- **Examine memory**: Use the debug console
- **Call stack**: View in the "Call Stack" panel

**Debug Console Commands:**

```
-exec info registers
-exec x/10i $pc
-exec show-boot-state
-exec break stage2_kernel_jump
-exec continue
```


#### Step 5: Advanced VS Code Debugging

**Memory Inspection:**

- Install "Memory Viewer" extension for graphical memory inspection
- Use debug console: `-exec x/64x 0x80000000`

**Assembly View:**

- Right-click in editor → "Go to Disassembly"
- Or use debug console: `-exec disas`


## Post-Debug Analysis

After a debugging session, analyze the execution trace:

```bash
python3 build/debug/trace_memory.py
```

This will show:

- Instructions executed per boot stage
- Memory access patterns
- Exception/interrupt occurrences
- Boot sequence timing


## Project Structure

```
riscv-boot-project/
├── src/                          # Assembly source files (edit these)
│   ├── bios.s
│   ├── stage1_bootloader.s
│   ├── stage2_bootloader.s
│   └── kernel.s
├── .vscode/                      # VS Code configuration
│   ├── launch.json              # Debug configuration
│   ├── tasks.json               # Build tasks
│   ├── extensions.json          # Extension recommendations
│   └── settings.json            # Workspace settings
├── build/                        # Generated files (git ignored)
│   ├── bin/                     # Compiled binaries and toolchain
│   ├── obj/                     # Object files
│   ├── debug/                   # Debug scripts and analysis
│   └── logs/                    # QEMU execution logs
├── riscv_dev.py                 # Main development script
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```


## Troubleshooting

### Common Issues

**"Command not found" errors:**

```bash
# Ensure toolchain is installed
python3 riscv_dev.py install

# Check if tools are available
ls build/bin/riscv64-unknown-elf-*
```

**VS Code debugging not working:**

- Ensure required extensions are installed
- Check that `.vscode/launch.json` exists
- Verify build was successful: `python3 riscv_dev.py build --debug`

**QEMU fails to start:**

```bash
# Check if QEMU is installed
qemu-system-riscv64 --version

# Reinstall if needed
sudo apt install qemu-system-riscv64
```

**GDB connection fails:**

- Ensure QEMU is running in debug mode: `python3 riscv_dev.py run --debug`
- Check that port 1234 is not in use: `netstat -ln | grep 1234`
- Try restarting both QEMU and GDB


### Clean Build

To start fresh:

```bash
rm -rf build/
python3 riscv_dev.py install
python3 riscv_dev.py build --debug
```


## Development Workflow

### Typical Development Cycle

1. **Edit source files** in `src/`
2. **Build with debug info**: `python3 riscv_dev.py build --debug`
3. **Test basic functionality**: `python3 riscv_dev.py run`
4. **Debug if needed**: `python3 riscv_dev.py run --debug`
5. **Analyze execution**: `python3 build/debug/trace_memory.py`

### Adding New Components

1. Create new `.s` file in `src/`
2. Add component to `riscv_dev.py` components list
3. Define load address in `load_addresses` dictionary
4. Update QEMU command to load the new component

### Customizing Boot Sequence

Each assembly file in `src/` represents a boot stage. Modify these files to:

- Add hardware initialization
- Implement device drivers
- Add bootloader features
- Extend kernel functionality

The modular design allows you to focus on individual components while maintaining the overall boot chain structure.

## Advanced Usage

### Custom Linker Scripts

For more complex projects, you can create custom linker scripts:

```bash
# Create linker script
cat > custom.ld << 'EOF'
SECTIONS {
    . = 0x80000000;
    .text : { *(.text) }
    .data : { *(.data) }
    .bss : { *(.bss) }
}
EOF

# Use in build process
build/bin/riscv64-unknown-elf-ld -T custom.ld -o output.elf input.o
```


### Adding C Code

You can mix C and assembly:

```c
// hello.c
void print_char(char c) {
    // SBI console putchar
    asm volatile (
        "mv a0, %0\n"
        "li a7, 0\n" 
        "li a6, 1\n"
        "ecall"
        : : "r"(c) : "a0", "a6", "a7"
    );
}
```

Compile and link:

```bash
build/bin/riscv64-unknown-elf-gcc -c -march=rv64gc hello.c -o hello.o
build/bin/riscv64-unknown-elf-ld hello.o main.o -o program.elf
```

This README provides comprehensive guidance for setting up, building, and debugging your RISC-V boot chain project using both terminal-based GDB and VS Code debugging environments.

