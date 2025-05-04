import os
import sys
import argparse
import subprocess
from datetime import datetime

# Dynamically resolve project root (assumes script is 2 levels deep under root)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT_DIR)  # Ensure internal packages can be imported


def rel_path(path):
    return os.path.join(ROOT_DIR, path)


def find_latest_binary(directory):
    """
    Find the most recently modified executable file in a given directory.
    """
    candidates = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
        and os.access(os.path.join(directory, f), os.X_OK)
    ]
    if not candidates:
        raise FileNotFoundError(f"No executable binary found in {directory}")
    return max(candidates, key=os.path.getmtime)


def run_afl(binary_path, input_dir, output_dir, timeout=60, max_runtime=300):
    """
    timeout: per-input timeout in seconds (AFL -t)
    max_runtime: total fuzzing time in seconds (Python subprocess timeout)
    """
    os.makedirs(output_dir, exist_ok=True)

    if not os.listdir(input_dir):
        print(
            f"[!] No seed inputs found in {input_dir}. Creating a default empty input."
        )
        os.makedirs(input_dir, exist_ok=True)
        with open(os.path.join(input_dir, "empty.txt"), "w") as f:
            f.write("")

    print(f"[+] Running AFL++ on binary: {binary_path}")
    cmd = [
        "afl-fuzz",
        "-i",
        input_dir,
        "-o",
        output_dir,
        "-t",
        str(timeout * 1000),  # ms
        "--",
        binary_path,
        "@@",
    ]

    print(f"[>] Executing command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, timeout=max_runtime, check=True)
    except subprocess.TimeoutExpired:
        print(f"[!] AFL run exceeded {max_runtime} seconds. Terminating...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AFL++ on an instrumented binary.")
    parser.add_argument(
        "--binary",
        default=None,
        help="Path to AFL-instrumented binary. If not provided, the most recently modified executable in artifacts/afl/ will be used.",
    )
    parser.add_argument(
        "--seeds",
        default="artifacts/afl/generated_seeds",
        help="Directory containing seed inputs",
    )
    parser.add_argument(
        "--out",
        default="artifacts/afl/output",
        help="Base output directory for AFL results",
    )
    parser.add_argument(
        "--timeout", type=int, default=60, help="Per-input timeout in seconds"
    )
    parser.add_argument(
        "--max-runtime",
        type=int,
        default=300,
        help="Max duration to run AFL (in seconds) before killing the process",
    )

    args = parser.parse_args()

    # Resolve full paths
    afl_dir = rel_path("artifacts/afl/compiled_afl")
    binary_path = rel_path(args.binary) if args.binary else find_latest_binary(afl_dir)
    seeds_path = rel_path(args.seeds)
    base_output_path = rel_path(args.out)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(base_output_path, f"run_{timestamp}")

    run_afl(
        binary_path,
        seeds_path,
        run_dir,
        timeout=args.timeout,
        max_runtime=args.max_runtime,
    )
