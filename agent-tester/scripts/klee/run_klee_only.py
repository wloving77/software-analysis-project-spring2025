# scripts/python/klee/run_klee_only.py
import os
import argparse
import subprocess
from datetime import datetime


def run_klee(bitcode_path, output_dir):
    # KLEE must create this directory itself — so we can't pre-create it
    if os.path.exists(output_dir):
        raise FileExistsError(f"KLEE output directory already exists: {output_dir}")

    print(f"[+] Running KLEE on: {bitcode_path}")
    cmd = ["klee", "--output-dir=" + output_dir, bitcode_path]
    print(f"[>] Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run KLEE on LLVM bitcode")
    parser.add_argument("bitcode_path", help="Path to .bc file (LLVM bitcode)")
    parser.add_argument(
        "--outdir",
        help="Optional name for output directory under artifacts/klee/klee_output",
    )

    args = parser.parse_args()

    # Compute absolute repo root relative to this script
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    base_outdir = os.path.join(repo_root, "artifacts/klee/klee_output")
    os.makedirs(base_outdir, exist_ok=True)  # Ensure base klee_output dir exists

    # Final output path (timestamped or named)
    if args.outdir:
        output_dir = os.path.join(base_outdir, args.outdir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_outdir, f"run_{timestamp}")

    run_klee(args.bitcode_path, output_dir)
