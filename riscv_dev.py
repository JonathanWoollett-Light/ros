#!/usr/bin/env python3
"""
RISC-V Boot Chain Development Tool
Handles installation, building, and execution of a custom RISC-V boot chain.
Only creates build artifacts - no source files or user configurations.

Usage:
    python3 riscv_dev.py install
    python3 riscv_dev.py build [--debug]
    python3 riscv_dev.py run [--debug]
"""

import argparse
import os
import sys
import subprocess
import urllib.request
import tarfile
import shutil
import threading
import time
import json
from pathlib import Path

class RISCVDevelopment:
    def __init__(self):
        self.toolchain_url = "https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2025.06.13/riscv64-elf-ubuntu-24.04-gcc-nightly-2025.06.13-nightly.tar.xz"
        self.toolchain_archive = "riscv64-elf-ubuntu-24.04-gcc-nightly-2025.06.13-nightly.tar.xz"
        self.toolchain_prefix = "riscv64-unknown-elf-"
        self.components = ["bios", "stage1_bootloader", "stage2_bootloader", "kernel"]
        self.load_addresses = {
            "bios": "0x1000",
            "stage1_bootloader": "0x80000000", 
            "stage2_bootloader": "0x80100000",
            "kernel": "0x80200000"
        }
        self.qemu_process = None
        
        # All generated content goes in build/
        self.build_dir = Path("build")
        self.toolchain_dir = self.build_dir / "toolchain"
        self.debug_dir = self.build_dir / "debug"
        self.bin_dir = self.build_dir / "bin"
        self.obj_dir = self.build_dir / "obj"
        self.logs_dir = self.build_dir / "logs"
        
    def log(self, message, color="green"):
        colors = {
            "red": "\033[0;31m",
            "green": "\033[0;32m", 
            "yellow": "\033[1;33m",
            "blue": "\033[0;34m",
            "reset": "\033[0m"
        }
        print(f"{colors.get(color, '')}{message}{colors['reset']}")
    
    def run_command(self, cmd, shell=True, check=True, capture_output=False):
        """Run a command with error handling"""
        try:
            if not shell and isinstance(cmd, str):
                cmd = cmd.split()
            result = subprocess.run(cmd, shell=shell, check=check, 
                                  capture_output=capture_output, text=True)
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Error running command: {cmd}", "red")
            if e.stderr:
                self.log(f"Error output: {e.stderr}", "red")
            sys.exit(1)
    
    def check_required_files(self):
        """Check that required source files exist"""
        required_files = [
            "src/bios.s",
            "src/stage1_bootloader.s", 
            "src/stage2_bootloader.s",
            "src/kernel.s"
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log("Error: Required source files not found:", "red")
            for file in missing_files:
                self.log(f"  {file}", "red")
            self.log("\nPlease create these files in the src/ directory.", "yellow")
            self.log("See README.md for example content.", "yellow")
            return False
        
        return True
    
    def setup_directories(self):
        """Create all necessary directories within build/"""
        dirs = [
            self.build_dir,
            self.toolchain_dir,
            self.debug_dir,
            self.bin_dir,
            self.obj_dir,
            self.logs_dir
        ]
        
        for d in dirs:
            d.mkdir(exist_ok=True, parents=True)
    
    def download_with_progress(self, url, filename):
        """Download file with progress bar"""
        self.log(f"Downloading {filename}...")
        
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                print(f"\rProgress: {percent}%", end="", flush=True)
        
        try:
            urllib.request.urlretrieve(url, filename, progress_hook)
            print()  # New line after progress
            return True
        except Exception as e:
            self.log(f"Error downloading {filename}: {e}", "red")
            return False
    
    def install_qemu(self):
        """Install QEMU for RISC-V"""
        self.log("Installing QEMU for RISC-V...")
        self.run_command("sudo apt update")
        self.run_command("sudo apt install -y qemu-system-riscv64 qemu-utils")
        self.log("✓ QEMU installed successfully")
    
    def extract_toolchain_binaries(self):
        """Extract specific binaries from toolchain archive"""
        self.log("Extracting RISC-V toolchain binaries...")
        
        archive_path = self.toolchain_dir / self.toolchain_archive
        extract_path = self.toolchain_dir / "extracted"
        
        binaries = ["as", "ld", "objcopy", "gdb", "objdump", "nm", "readelf"]
        
        with tarfile.open(archive_path, 'r:xz') as tar:
            members = tar.getnames()
            
            for binary in binaries:
                # Find the binary in the archive
                binary_path = None
                for member in members:
                    if member.endswith(f"riscv/riscv64-unknown-elf/bin/{binary}"):
                        binary_path = member
                        break
                
                if binary_path:
                    tar.extract(binary_path, extract_path)
                    # Copy to bin directory with proper name
                    extracted_binary = extract_path / binary_path
                    local_binary = self.bin_dir / f"{self.toolchain_prefix}{binary}"
                    shutil.copy2(extracted_binary, local_binary)
                    local_binary.chmod(0o755)
                    self.log(f"✓ Extracted {binary}")
                else:
                    self.log(f"Warning: {binary} not found in archive", "yellow")
        
        # Cleanup extraction directory
        if extract_path.exists():
            shutil.rmtree(extract_path)
    
    def install(self):
        """Install all required tools and dependencies"""
        self.log("=== Installing RISC-V Development Environment ===", "blue")
        
        # Setup directory structure
        self.setup_directories()
        
        # Download toolchain if not present
        archive_path = self.toolchain_dir / self.toolchain_archive
        if not archive_path.exists():
            if not self.download_with_progress(self.toolchain_url, archive_path):
                return False
        
        # Extract toolchain binaries
        self.extract_toolchain_binaries()
        
        # Install QEMU
        self.install_qemu()
        
        self.log("✓ Installation complete!", "green")
        self.log("", "")
        self.log("Next steps:", "blue")
        self.log("1. Create source files in src/ directory", "blue")
        self.log("2. Configure VS Code settings in .vscode/", "blue") 
        self.log("3. Run: python3 riscv_dev.py build --debug", "blue")
        self.log("4. Run: python3 riscv_dev.py run --debug", "blue")
        return True
    
    def build_component(self, name, debug=False):
        """Build a single component"""
        source_file = f"src/{name}.s"
        load_addr = self.load_addresses[name]
        
        if not Path(source_file).exists():
            self.log(f"Error: {source_file} not found", "red")
            return False
        
        arch_flags = "-march=rv64gc -mabi=lp64"
        debug_flags = "-g -O0" if debug else "-O2"
        
        # All tools are in build/bin/
        as_tool = self.bin_dir / f"{self.toolchain_prefix}as"
        ld_tool = self.bin_dir / f"{self.toolchain_prefix}ld"
        objcopy_tool = self.bin_dir / f"{self.toolchain_prefix}objcopy"
        
        # Object file goes in build/obj/
        obj_file = self.obj_dir / f"{name}.o"
        # Final outputs go in build/bin/
        elf_file = self.bin_dir / f"{name}.elf"
        bin_file = self.bin_dir / f"{name}.bin"
        
        # Assemble
        as_cmd = f"{as_tool} {arch_flags} {debug_flags} {source_file} -o {obj_file}"
        self.run_command(as_cmd)
        
        # Link
        ld_cmd = f"{ld_tool} -Ttext={load_addr} --oformat=elf64-littleriscv {obj_file} -o {elf_file}"
        self.run_command(ld_cmd)
        
        # Create binary
        objcopy_cmd = f"{objcopy_tool} -O binary {elf_file} {bin_file}"
        self.run_command(objcopy_cmd)
        
        if debug:
            # Generate debug files in build/debug/
            objdump_tool = self.bin_dir / f"{self.toolchain_prefix}objdump"
            nm_tool = self.bin_dir / f"{self.toolchain_prefix}nm"
            
            disasm_file = self.debug_dir / f"{name}_disasm.txt"
            symbols_file = self.debug_dir / f"{name}_symbols.txt"
            
            self.run_command(f"{objdump_tool} -D {elf_file} > {disasm_file}")
            self.run_command(f"{nm_tool} {elf_file} > {symbols_file}")
        
        self.log(f"✓ Built {name}")
        return True
    
    def create_gdb_script(self):
        """Create GDB initialization script in build/debug/"""
        gdb_script = f"""
# GDB script for RISC-V boot chain debugging
target remote localhost:1234

# Load symbols from build/bin/
symbol-file {self.bin_dir}/bios.elf
add-symbol-file {self.bin_dir}/stage1_bootloader.elf 0x80000000
add-symbol-file {self.bin_dir}/stage2_bootloader.elf 0x80100000
add-symbol-file {self.bin_dir}/kernel.elf 0x80200000

# Set breakpoints at key locations
break *0x1000        # BIOS entry
break *0x80000000    # Stage-1 bootloader entry
break *0x80100000    # Stage-2 bootloader entry
break *0x80200000    # Kernel entry

# Set breakpoints at symbolic locations (if debug symbols exist)
break stage2_entry
break stage2_sbi_call
break stage2_kernel_jump

# Custom debugging commands
define show-boot-state
    printf "=== Boot State Debug ===\\n"
    printf "PC: 0x%016lx\\n", $pc
    printf "SP: 0x%016lx\\n", $sp
    printf "mstatus: 0x%016lx\\n", $mstatus
    if ($pc >= 0x1000) && ($pc < 0x80000000)
        printf "Current stage: BIOS\\n"
    end
    if ($pc >= 0x80000000) && ($pc < 0x80100000)
        printf "Current stage: Stage-1 Bootloader\\n"
    end
    if ($pc >= 0x80100000) && ($pc < 0x80200000)
        printf "Current stage: Stage-2 Bootloader\\n"
    end
    if ($pc >= 0x80200000)
        printf "Current stage: Kernel\\n"
    end
    printf "========================\\n"
end

define step-boot
    stepi
    show-boot-state
end

# Enable useful debugging features
set disassemble-next-line on
set print pretty on
set confirm off

# Print startup message
echo \\n=== RISC-V Boot Chain Debugger ===\\n
echo Available commands:\\n
echo   show-boot-state : Show current boot state\\n
echo   step-boot      : Step one instruction and show state\\n
echo   continue       : Continue execution\\n
echo ===================================\\n\\n
"""
        gdb_script_path = self.debug_dir / "gdb_init.gdb"
        with open(gdb_script_path, "w") as f:
            f.write(gdb_script)
    
    def create_trace_script(self):
        """Create trace analysis script in build/debug/"""
        trace_script = '''#!/usr/bin/env python3
"""
QEMU Trace Analysis Script for RISC-V Boot Chain
Analyzes QEMU execution logs to provide boot sequence insights
"""

import sys
import re
from pathlib import Path

def analyze_boot_sequence(logfile):
    print("=== RISC-V Boot Sequence Analysis ===\\n")
    
    stages = {
        0x1000: "BIOS",
        0x80000000: "Stage-1 Bootloader", 
        0x80100000: "Stage-2 Bootloader",
        0x80200000: "Kernel"
    }
    
    current_stage = None
    instruction_count = 0
    memory_accesses = 0
    exceptions = []
    
    try:
        with open(logfile, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Track stage transitions
                for addr, stage_name in stages.items():
                    if f"IN: 0x{addr:016x}" in line:
                        if current_stage != stage_name:
                            if current_stage:
                                print(f"  Instructions executed: {instruction_count}")
                                print(f"  Memory accesses: {memory_accesses}")
                                if exceptions:
                                    print(f"  Exceptions: {len(exceptions)}")
                                print()
                            print(f"→ Entering {stage_name} (0x{addr:x})")
                            current_stage = stage_name
                            instruction_count = 0
                            memory_accesses = 0
                            exceptions = []
                        break
                
                # Count instructions and memory accesses
                if current_stage and "IN:" in line:
                    instruction_count += 1
                elif current_stage and ("load" in line.lower() or "store" in line.lower()):
                    memory_accesses += 1
                
                # Track important events
                if "exception" in line.lower():
                    exception_info = f"Line {line_num}: {line.strip()}"
                    exceptions.append(exception_info)
                    print(f"  ⚠️  Exception in {current_stage}: {line.strip()}")
                elif "interrupt" in line.lower():
                    print(f"  📶 Interrupt in {current_stage}: {line.strip()}")
                    
    except FileNotFoundError:
        print(f"Error: Log file '{logfile}' not found")
        print("Make sure to run QEMU with debug logging enabled")
        print("Usage: python3 riscv_dev.py run --debug")
        return 1
    
    # Final stage summary
    if current_stage:
        print(f"  Instructions executed: {instruction_count}")
        print(f"  Memory accesses: {memory_accesses}")
        if exceptions:
            print(f"  Exceptions: {len(exceptions)}")
        print()
    
    print("Analysis complete!")
    return 0

if __name__ == "__main__":
    logfile = sys.argv[1] if len(sys.argv) > 1 else 'build/logs/qemu.log'
    sys.exit(analyze_boot_sequence(logfile))
'''
        
        trace_script_path = self.debug_dir / "trace_memory.py"
        with open(trace_script_path, "w") as f:
            f.write(trace_script)
        trace_script_path.chmod(0o755)
    
    def build(self, debug=False):
        """Build all components"""
        self.log(f"=== Building RISC-V Boot Chain {'(Debug Mode)' if debug else ''} ===", "blue")
        
        # Check that source files exist
        if not self.check_required_files():
            return False
        
        self.setup_directories()
        
        success = True
        for component in self.components:
            if not self.build_component(component, debug):
                success = False
        
        if debug:
            self.create_gdb_script()
            self.create_trace_script()
            self.log("✓ Created debug scripts")
        
        if success:
            self.log("✓ Build complete!", "green")
            self.log(f"Binaries: {self.bin_dir}/", "blue")
            if debug:
                self.log(f"Debug files: {self.debug_dir}/", "blue")
        else:
            self.log("✗ Build failed!", "red")
        
        return success
    
    def start_qemu(self, debug=False):
        """Start QEMU with the boot chain"""
        cmd = [
            "qemu-system-riscv64",
            "-machine", "virt",
            "-cpu", "rv64",
            "-m", "2G", 
            "-nographic",
            "-bios", str(self.bin_dir / "bios.bin"),
            "-device", f"loader,file={self.bin_dir}/stage1_bootloader.bin,addr=0x80000000,force-raw=on",
            "-device", f"loader,file={self.bin_dir}/stage2_bootloader.bin,addr=0x80100000,force-raw=on",
            "-device", f"loader,file={self.bin_dir}/kernel.bin,addr=0x80200000,force-raw=on"
        ]
        
        if debug:
            log_file = self.logs_dir / "qemu.log"
            cmd.extend([
                "-s", "-S",  # GDB server, halt at startup
                "-d", "in_asm,int,exec,cpu,guest_errors",
                "-D", str(log_file)
            ])
            self.log("Starting QEMU in debug mode (waiting for GDB)...", "blue")
            self.log(f"Connect with: {self.bin_dir}/riscv64-unknown-elf-gdb -x {self.debug_dir}/gdb_init.gdb", "yellow")
        else:
            self.log("Starting QEMU...", "blue")
        
        return subprocess.Popen(cmd)
    
    def run(self, debug=False):
        """Run the boot chain in QEMU"""
        self.log(f"=== Running RISC-V Boot Chain {'(Debug Mode)' if debug else ''} ===", "blue")
        
        # Check if binaries exist
        for component in self.components:
            bin_file = self.bin_dir / f"{component}.bin"
            if not bin_file.exists():
                self.log(f"Error: {bin_file} not found. Run 'build' first.", "red")
                return False
        
        try:
            self.qemu_process = self.start_qemu(debug)
            
            if debug:
                self.log("QEMU started and waiting for debugger connection.", "green")
                self.log("", "")
                self.log("Debug options:", "yellow")
                self.log(f"  GDB: {self.bin_dir}/riscv64-unknown-elf-gdb -x {self.debug_dir}/gdb_init.gdb", "yellow")
                self.log("  VS Code: Press F5 to start debugging", "yellow")
                self.log("", "")
                self.log("After debugging session:", "blue")
                self.log(f"  Analyze trace: python3 {self.debug_dir}/trace_memory.py", "blue")
            
            # Wait for QEMU process
            self.qemu_process.wait()
            
        except KeyboardInterrupt:
            self.log("Interrupted by user", "yellow")
            if self.qemu_process:
                self.qemu_process.terminate()
        except Exception as e:
            self.log(f"Error running QEMU: {e}", "red")
            return False
        
        return True

def main():
    parser = argparse.ArgumentParser(description="RISC-V Boot Chain Development Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install toolchain and dependencies")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build boot chain components")
    build_parser.add_argument("--debug", action="store_true", help="Build with debug information")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run boot chain in QEMU")
    run_parser.add_argument("--debug", action="store_true", help="Run with debug support")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    dev = RISCVDevelopment()
    
    if args.command == "install":
        return 0 if dev.install() else 1
    elif args.command == "build":
        return 0 if dev.build(debug=args.debug) else 1
    elif args.command == "run":
        return 0 if dev.run(debug=args.debug) else 1
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
