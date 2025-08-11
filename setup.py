#!/usr/bin/env python3

"""
RISC-V Toolchain Setup Script for Ubuntu
Downloads and extracts RISC-V toolchain binaries (as, ld, objcopy)
Installs QEMU for RISC-V emulation
"""

import os
import sys
import subprocess
import urllib.request
import tarfile
import shutil
from pathlib import Path

# Configuration
TOOLCHAIN_URL = "https://github.com/riscv-collab/riscv-gnu-toolchain/releases/download/2025.06.13/riscv64-elf-ubuntu-24.04-gcc-nightly-2025.06.13-nightly.tar.xz"
TOOLCHAIN_ARCHIVE = "riscv64-elf-ubuntu-24.04-gcc-nightly-2025.06.13-nightly.tar.xz"
WORK_DIR = "riscv_setup"
BINARIES = ["as", "ld", "objcopy"]

def run_command(cmd, shell=True, check=True):
    """Run a shell command with error handling."""
    try:
        result = subprocess.run(cmd, shell=shell, check=check, 
                              capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def download_file(url, filename):
    """Download a file with progress indication."""
    print(f"Downloading {filename}...")
    
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
        print(f"Error downloading {filename}: {e}")
        return False

def extract_binary_from_tar(tar_path, binary_name, extract_dir):
    """Extract a specific binary from the tar archive."""
    print(f"Extracting {binary_name}...")
    
    try:
        with tarfile.open(tar_path, 'r:xz') as tar:
            # Find the binary in the archive
            target_path = None
            for member in tar.getmembers():
                if member.name.endswith(f"riscv64-unknown-elf/bin/{binary_name}"):
                    target_path = member.name
                    break
            
            if target_path:
                # Extract the specific file
                tar.extract(target_path, extract_dir)
                print(f"Extracted: {target_path}")
                return os.path.join(extract_dir, target_path)
            else:
                print(f"Warning: {binary_name} not found in archive")
                return None
                
    except Exception as e:
        print(f"Error extracting {binary_name}: {e}")
        return None

def setup_local_binary(extracted_path, binary_name):
    """Copy binary to local directory with executable permissions."""
    if extracted_path and os.path.exists(extracted_path):
        local_path = f"./{binary_name}"
        shutil.copy2(extracted_path, local_path)
        # Make executable
        os.chmod(local_path, 0o755)
        print(f"Set up local {binary_name}")
        return True
    else:
        print(f"Warning: Could not find extracted {binary_name}")
        return False

def install_qemu():
    """Install QEMU for RISC-V using apt."""
    print("Installing QEMU for RISC-V...")
    
    # Update package list
    run_command("sudo apt update")
    
    # Install QEMU packages
    run_command("sudo apt install -y qemu-system-riscv64 qemu-utils")

def create_qemu_wrapper():
    """Create a local wrapper script for qemu-system-riscv64."""
    print("Creating local QEMU wrapper...")
    
    wrapper_content = """#!/bin/bash
# Wrapper script for qemu-system-riscv64
exec /usr/bin/qemu-system-riscv64 "$@"
"""
    
    wrapper_path = "./qemu-system-riscv64"
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    
    # Make executable
    os.chmod(wrapper_path, 0o755)

def get_version(binary_path):
    """Try to get version information from a binary."""
    try:
        result = subprocess.run([binary_path, "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout:
            return result.stdout.split('\n')[0]
    except:
        pass
    return "Version unavailable"

def verify_installation():
    """Verify that all binaries are properly installed."""
    print("Verifying installation...")
    
    all_good = True
    
    # Check toolchain binaries
    for binary in BINARIES:
        binary_path = f"./{binary}"
        if os.path.exists(binary_path) and os.access(binary_path, os.X_OK):
            print(f"✓ {binary} is available locally")
            version = get_version(binary_path)
            if version != "Version unavailable":
                print(f"  Version: {version}")
        else:
            print(f"✗ {binary} is not available")
            all_good = False
    
    # Check QEMU wrapper
    qemu_path = "./qemu-system-riscv64"
    if os.path.exists(qemu_path) and os.access(qemu_path, os.X_OK):
        print("✓ qemu-system-riscv64 is available locally")
        version = get_version(qemu_path)
        if version != "Version unavailable":
            print(f"  Version: {version}")
    else:
        print("✗ qemu-system-riscv64 is not available")
        all_good = False
    
    return all_good

def main():
    """Main function that orchestrates the setup process."""
    print("Starting RISC-V toolchain setup...")
    
    # Create working directory
    work_dir = Path(WORK_DIR)
    work_dir.mkdir(exist_ok=True)
    
    # Change to working directory
    original_dir = os.getcwd()
    os.chdir(work_dir)
    
    try:
        # Download toolchain if not already present
        if not os.path.exists(TOOLCHAIN_ARCHIVE):
            if not download_file(TOOLCHAIN_URL, TOOLCHAIN_ARCHIVE):
                print("Failed to download toolchain archive")
                return 1
        else:
            print("Toolchain archive already exists, skipping download.")
        
        # Extract binaries
        print("Extracting specific binaries from toolchain...")
        extracted_binaries = {}
        
        for binary in BINARIES:
            extracted_path = extract_binary_from_tar(TOOLCHAIN_ARCHIVE, binary, ".")
            if extracted_path:
                extracted_binaries[binary] = extracted_path
        
        # Go back to original directory
        os.chdir(original_dir)
        
        # Set up local binaries
        print("Setting up local binaries...")
        for binary in BINARIES:
            if binary in extracted_binaries:
                full_path = os.path.join(WORK_DIR, extracted_binaries[binary])
                setup_local_binary(full_path, binary)
        
        # Install QEMU
        install_qemu()
        
        # Create QEMU wrapper
        create_qemu_wrapper()
        
        # Clean up working directory
        print("Cleaning up...")
        shutil.rmtree(WORK_DIR)
        
        # Verify installation
        if verify_installation():
            print("\nSetup complete! You can now use:")
            print("  ./as        - RISC-V assembler")
            print("  ./ld        - RISC-V linker")
            print("  ./objcopy   - RISC-V objcopy utility")
            print("  ./qemu-system-riscv64 - QEMU RISC-V emulator")
            print("\nExample usage:")
            print("  ./qemu-system-riscv64 --version")
            print("  ./as --version")
            return 0
        else:
            print("\nSetup completed with some issues. Please check the output above.")
            return 1
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    
    finally:
        # Ensure we're back in the original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    sys.exit(main())
