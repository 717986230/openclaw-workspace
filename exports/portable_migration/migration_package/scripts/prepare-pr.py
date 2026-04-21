#!/usr/bin/env python3
"""
Prepare PR for system-design-primer Issue #1193
Translation: Add Georgian language
"""

import subprocess
import os
from pathlib import Path

# Create work directory
work_dir = Path(r"D:\CODE\sd-pr-1193")
if work_dir.exists():
    import shutil
    shutil.rmtree(work_dir)
work_dir.mkdir(parents=True, exist_ok=True)

os.chdir(work_dir)

print("=== Preparing PR for Issue #1193 ===")
print(f"Work directory: {work_dir}")

# Initialize git
subprocess.run(["git", "init"], check=True)

# Add remote
subprocess.run([
    "git", "remote", "add", "origin",
    "https://github.com/donnemartin/system-design-primer.git"
], check=True)

# Sparse checkout
subprocess.run(["git", "config", "core.sparseCheckout", "true"], check=True)

# Only checkout README files
sparse_info = work_dir / ".git" / "info" / "sparse-checkout"
sparse_info.write_text("README.md\nREADME-*.md\n")

# Fetch and checkout
print("Fetching minimal files...")
subprocess.run(["git", "fetch", "--depth=1", "origin", "main"], check=True)
subprocess.run(["git", "checkout", "main"], check=True)

print("\n=== Files ready ===")
print("Creating PR branch...")

# Create branch
subprocess.run(["git", "checkout", "-b", "add-georgian-translation"], check=True)

print("\nBranch: add-georgian-translation")
print("Ready to create Georgian translation!")

# Fork repo for PR
print("\nTo create PR:")
print("1. Fork the repo on GitHub")
print("2. Push changes to fork")
print("3. Create PR via gh CLI")
