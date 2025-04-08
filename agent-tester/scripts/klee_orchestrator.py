import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "c_program/src/proof_of_concept.c"
REWRITE_NAME = "proof_of_concept_klee"
REWRITE_BC_PATH = REPO_ROOT / f"artifacts/klee/llvm/{REWRITE_NAME}.bc"


def run(cmd, cwd=None):
    print(f"[>] Running: {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def rewrite_for_klee():
    print("[1] Rewriting for KLEE with Gemini...")
    run(
        [
            "python3",
            "scripts/klee/generate_klee_rewrite.py",
            str(SRC_PATH),
            "--outname",
            REWRITE_NAME,
        ],
        cwd=REPO_ROOT,
    )


def compile_bitcode():
    print("[2] Compiling LLVM bitcode from rewrite...")
    run(
        ["make", f"../artifacts/klee/llvm/{REWRITE_NAME}.bc"],
        cwd=REPO_ROOT / "c_program",
    )


def run_klee():
    print("[3] Running KLEE...")
    run(
        ["python3", "scripts/klee/run_klee_only.py", str(REWRITE_BC_PATH)],
        cwd=REPO_ROOT,
    )


def full_pipeline():
    rewrite_for_klee()
    compile_bitcode()
    run_klee()
    print("[✓] Done.")


if __name__ == "__main__":
    full_pipeline()
