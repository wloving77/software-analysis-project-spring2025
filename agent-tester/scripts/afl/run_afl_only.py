# scripts/run_afl_only.py
import os
import argparse
import subprocess
from datetime import datetime


def run_afl(binary_path, input_dir, output_dir, timeout=60):
    os.makedirs(output_dir, exist_ok=True)

    # If no seed input, add an empty one to satisfy AFL
    if not os.listdir(input_dir):
        os.makedirs(input_dir, exist_ok=True)
        with open(os.path.join(input_dir, "empty.txt"), "w") as f:
            f.write("")

    print(f"[+] Running AFL on: {binary_path}")
    cmd = [
        "afl-fuzz",
        "-i",
        input_dir,
        "-o",
        output_dir,
        "-t",
        str(timeout * 1000),  # timeout in ms
        "--",
        binary_path,
    ]
    print(f"[>] Executing: {' '.join(cmd)}")
    subprocess.run(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AFL++ fuzzer on compiled binary")
    parser.add_argument("binary_path", help="Path to AFL-instrumented binary")
    parser.add_argument(
        "--seeds", default="../data/fuzz_seeds", help="Directory of initial seed files"
    )
    parser.add_argument(
        "--out",
        default="../artifacts/afl_output",
        help="Output directory for fuzzing results",
    )
    parser.add_argument(
        "--timeout", type=int, default=60, help="Per-input timeout in seconds"
    )

    args = parser.parse_args()

    # Timestamped run directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.out, f"run_{timestamp}")

    run_afl(args.binary_path, args.seeds, output_dir, timeout=args.timeout)
