import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import argparse

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "c_program/src"
BIN_DIR = REPO_ROOT / "artifacts/afl/compiled_afl"
SEED_DIR = REPO_ROOT / "artifacts/afl/generated_seeds"

parser = argparse.ArgumentParser(description="Run AFL fuzzing pipeline")
parser.add_argument(
    "--num-seeds", type=int, default=10, help="Number of AFL seed inputs to generate"
)
parser.add_argument(
    "--afl-runtime", type=int, default=60, help="Maximum runtime for AFL in seconds"
)
args = parser.parse_args()
NUM_SEEDS = args.num_seeds
AFL_RUNTIME = args.afl_runtime

load_dotenv(".env")


def run(cmd, cwd=None):
    print(f"[>] Running: {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def generate_afl_seeds():
    print("[1] Generating AFL seed inputs using Gemini...")
    run(
        [
            "python3",
            "scripts/afl/generate_afl_seeds.py",
            "--num-seeds",
            str(NUM_SEEDS),
        ],
        cwd=REPO_ROOT,
    )


def compile_afl_binary():
    print(f"[2] Compiling AFL-instrumented binary...")
    # target = "../artifacts/afl/compiled_afl"
    run(["make", "afl_bin"], cwd=REPO_ROOT / "c_program")


def find_latest_binary(directory: Path) -> Path:
    """
    Find the most recently modified executable binary in a directory.
    """
    candidates = [
        entry
        for entry in directory.iterdir()
        if entry.is_file() and os.access(entry, os.X_OK)
    ]
    if not candidates:
        raise FileNotFoundError(f"No executable binary found in {directory}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def run_afl_fuzzer(binary_path: Path):
    print(f"[3] Running AFL fuzzer on {binary_path.name}...")
    run(
        [
            "python3",
            "scripts/afl/run_afl_only.py",
            "--binary",
            str(binary_path),
            "--seeds",
            str(SEED_DIR),
            "--max-runtime",
            str(AFL_RUNTIME),
        ],
        cwd=REPO_ROOT,
    )


def full_afl_pipeline():
    src_files = list(SRC_DIR.glob("*.c"))
    if not src_files:
        print("❌ No .c files found in c_program/src/")
        return

    print("🚀 Starting full AFL pipeline...\n")

    try:
        generate_afl_seeds()
        compile_afl_binary()

        binary_path = find_latest_binary(BIN_DIR)

        if not binary_path.exists():
            print(f"❌ Compiled binary not found.")
            return

        if not os.access(binary_path, os.X_OK):
            print(f"[!] Binary not executable. Attempting to chmod +x...")
            os.chmod(binary_path, 0o755)

        run_afl_fuzzer(binary_path)
        print(f"[✓] AFL fuzzing complete.\n")
    except subprocess.CalledProcessError as e:
        print(f"[!] AFL pipeline failed: {e}")
    except FileNotFoundError as e:
        print(f"[!] {e}")


if __name__ == "__main__":
    full_afl_pipeline()
