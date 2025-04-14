import os
import sys
from pathlib import Path
import subprocess
from analyzer import extract_all_klee_inputs, extract_all_afl_inputs


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "c_program/src"
KLEE_OUTPUT_DIR = REPO_ROOT / "artifacts/klee/klee_output"
AFL_OUTPUT_DIR = REPO_ROOT / "artifacts/afl/output"
BINARY_PATH = REPO_ROOT / "artifacts/standard_binary/mini_qsort"

GCDA_DIR = REPO_ROOT / "artifacts/coverage/coverage_data"
GCOV_REPORT_DIR = REPO_ROOT / "artifacts/coverage/coverage_report"

# Ensure report directories exist
GCDA_DIR.mkdir(parents=True, exist_ok=True)
GCOV_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def reset_coverage_data():
    for f in REPO_ROOT.rglob("*.gcda"):
        f.unlink()


def run_with_input(input_str):
    input_file = REPO_ROOT / "temp_input.txt"
    input_file.write_text(input_str)

    try:
        subprocess.run(
            [str(BINARY_PATH), str(input_file)],
            check=True,
            timeout=3,
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] Binary exited non-zero: {e}")
    except subprocess.TimeoutExpired:
        print("[!] Execution timed out")
    finally:
        input_file.unlink(missing_ok=True)


def generate_gcov_report():
    # Ensure .gcno is present in coverage_data
    original_gcno = BINARY_PATH.parent / "mini_qsort.gcno"
    if original_gcno.exists():
        dest_gcno = GCDA_DIR / "mini_qsort.gcno"
        dest_gcno.write_bytes(original_gcno.read_bytes())

    # Ensure .gcda is present in coverage_data
    original_gcda = BINARY_PATH.parent / "mini_qsort.gcda"
    if original_gcda.exists():
        dest_gcda = GCDA_DIR / "mini_qsort.gcda"
        dest_gcda.write_bytes(original_gcda.read_bytes())

    c_file = SRC_DIR / "mini_qsort.c"

    # Copy source file into report directory so gcov can annotate it
    copied_src = GCOV_REPORT_DIR / "src" / "mini_qsort.c"
    copied_src.parent.mkdir(parents=True, exist_ok=True)
    if not copied_src.exists():
        copied_src.write_bytes(c_file.read_bytes())

    subprocess.run(["gcov", "-o", str(GCDA_DIR), str(c_file)], cwd=GCOV_REPORT_DIR)


if __name__ == "__main__":
    print("[*] Resetting coverage data...")
    reset_coverage_data()

    print("[*] Extracting KLEE inputs...")
    klee_inputs = extract_all_klee_inputs(KLEE_OUTPUT_DIR)
    print(f"[+] Got {len(klee_inputs)} inputs from KLEE")

    print("[*] Extracting AFL inputs...")
    afl_inputs = extract_all_afl_inputs(AFL_OUTPUT_DIR)
    print(f"[+] Got {len(afl_inputs)} inputs from AFL")

    print("[*] Replaying inputs...")
    for input_str in klee_inputs + afl_inputs:
        run_with_input(input_str)

    print("[*] Generating gcov report...")
    generate_gcov_report()

    print("[✔] Done! See coverage report in artifacts/coverage_report/")
