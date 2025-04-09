import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "c_program/src"
REWRITE_DIR = REPO_ROOT / "artifacts/klee/rewrite"
LLVM_DIR = REPO_ROOT / "artifacts/klee/llvm"


def run(cmd, cwd=None):
    print(f"[>] Running: {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def rewrite_for_klee(src_path: Path, outname: str):
    print(f"[1] Rewriting {src_path.name} for KLEE with Gemini...")
    run(
        [
            "python3",
            "scripts/klee/generate_klee_rewrite.py",
            str(src_path),
            "--outname",
            outname,
        ],
        cwd=REPO_ROOT,
    )


def compile_bitcode(rewrite_name: str):
    print(f"[2] Compiling {rewrite_name}.c to LLVM bitcode...")
    target = f"../artifacts/klee/llvm/{rewrite_name}.bc"
    run(["make", target], cwd=REPO_ROOT / "c_program")


def run_klee_on_bc(rewrite_name: str):
    bc_path = LLVM_DIR / f"{rewrite_name}.bc"
    print(f"[3] Running KLEE on {bc_path.name}...")
    run(
        ["python3", "scripts/klee/run_klee_only.py", str(bc_path)],
        cwd=REPO_ROOT,
    )


def full_pipeline_for_all():
    src_files = list(SRC_DIR.glob("*.c"))
    if not src_files:
        print("❌ No .c files found in c_program/src/")
        return

    for src_path in src_files:
        base_name = src_path.stem
        rewrite_name = f"{base_name}_klee"

        print(f"\n🚀 Processing {src_path.name}")
        try:
            rewrite_for_klee(src_path, rewrite_name)
            compile_bitcode(rewrite_name)
            run_klee_on_bc(rewrite_name)
            print(f"[✓] {base_name} complete.\n")
        except subprocess.CalledProcessError as e:
            print(f"[!] Error processing {base_name}: {e}\n")


if __name__ == "__main__":
    full_pipeline_for_all()
