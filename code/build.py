#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import shutil
import subprocess
from pathlib import Path

def main():
    # Determine project root and paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    code_dir = project_root / "code"
    released_dir = project_root / "released"
    tools_dir = project_root / "tools" / "compiler"

    # Rust toolchain paths
    cargo_bin = tools_dir / "cargo" / "bin" / "cargo.exe"
    mingw_bin = project_root / "tools" / "mingw64" / "bin"

    if not cargo_bin.exists():
        print(f"Error: Rust compiler not found at {cargo_bin}")
        return 1

    if not mingw_bin.exists():
        print(f"Error: MinGW not found at {mingw_bin}")
        return 1

    print("Building sqlite2json...")

    # Set CARGO_HOME and RUSTUP_HOME to use portable toolchain
    env = os.environ.copy()
    env['CARGO_HOME'] = str(tools_dir / "cargo")
    env['RUSTUP_HOME'] = str(tools_dir / "rustup")

    # Add MinGW to PATH for GNU linker
    env['PATH'] = str(mingw_bin) + os.pathsep + env.get('PATH', '')

    # Build with release profile (GNU toolchain is default, avoids MSVC dependency)
    result = subprocess.run(
        [str(cargo_bin), "build", "--release"],
        cwd=str(code_dir),
        env=env,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print("Build failed")
        return 1

    print("Build successful")

    # Clear and recreate released directory
    if released_dir.exists():
        shutil.rmtree(released_dir)
    released_dir.mkdir(parents=True, exist_ok=True)

    print("Copying artifacts to ./released/...")

    # Copy the built executable
    exe_name = "sqlite2json.exe" if os.name == 'nt' else "sqlite2json"
    source_exe = code_dir / "target" / "release" / exe_name
    dest_exe = released_dir / exe_name

    if not source_exe.exists():
        print(f"Error: Built executable not found at {source_exe}")
        return 1

    shutil.copy2(source_exe, dest_exe)
    print(f"Copied {exe_name} to ./released/")

    print("Build complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
