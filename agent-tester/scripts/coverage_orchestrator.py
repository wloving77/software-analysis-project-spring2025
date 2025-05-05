import os
import sys
import subprocess
import argparse
import re
from pathlib import Path
from klee.ktest import KTest

from afl.generate_afl_seeds import read_c_programs_with_filenames


""" This is more or less the ground truth, this is where the model gets feedback on how fuzzing, symbolic, and raw test generation are performing """

REPO_ROOT = Path(__file__).resolve().parents[1]
C_SRC_DIR = REPO_ROOT / "c_program/src"
KLEE_OUTPUT_DIR = REPO_ROOT / "artifacts/klee/klee_output"
AFL_OUTPUT_DIR = REPO_ROOT / "artifacts/afl/output"
BINARY_PATH = REPO_ROOT / "artifacts/standard_binary/tcc"
LLM_OUTPUT_DIR = REPO_ROOT / "artifacts/llm-testgen"
GCDA_DIR = REPO_ROOT / "artifacts/coverage/coverage_data"
GCOV_REPORT_DIR = REPO_ROOT / "artifacts/coverage/coverage_report"
TEST_CASES_DIR = REPO_ROOT / "artifacts/coverage/test_cases"

# Ensure report directories exist
GCDA_DIR.mkdir(parents=True, exist_ok=True)
GCOV_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def extract_afl_generated_tests(seed_dir):
    inputs = []
    for testcase in Path(seed_dir).glob("*"):
        try:
            inputs.append(testcase.read_text(errors="ignore"))
        except Exception as e:
            print(f"[!] Could not read {testcase}: {e}")
    return inputs


def extract_llm_generated_tests(test_case_dir):
    inputs = []
    for testcase in test_case_dir.iterdir():
        if testcase.is_file():
            try:
                inputs.append(testcase.read_text(errors="ignore"))
            except Exception as e:
                print(f"[!] Could not read {testcase}: {e}")
    return inputs


def extract_all_klee_inputs(root_dir):
    inputs = []
    for subdir in Path(root_dir).resolve().glob("run_*"):
        for ktest in subdir.rglob("*.ktest"):
            print(f"[KLEE] Found KTest file: {ktest}")
            try:
                kt = KTest.fromfile(str(ktest))
                input_objects = {}

                for name, data in kt.objects:
                    match = re.fullmatch(r"input_(\d+)", name)
                    if match:
                        index = int(match.group(1))
                        input_objects[index] = data

                if not input_objects:
                    continue

                input_strs = []
                for index in sorted(input_objects):
                    data = input_objects[index]
                    for i in range(0, len(data), 4):
                        val = int.from_bytes(
                            data[i : i + 4], byteorder="little", signed=True
                        )
                        input_strs.append(str(val))

                inputs.append(" ".join(input_strs))
            except Exception as e:
                print(f"[!] Failed to parse {ktest}: {e}")
    return inputs


def extract_all_afl_inputs(root_dir):
    inputs = []
    for subdir in Path(root_dir).resolve().glob("run_*"):
        queue_dir = subdir / "default/queue"
        if not queue_dir.exists():
            continue
        for testcase in queue_dir.iterdir():
            if testcase.is_file():
                try:
                    inputs.append(testcase.read_text(errors="ignore"))
                except Exception as e:
                    print(f"[!] Could not read {testcase}: {e}")
    return inputs


def compile_gcov_binary():
    print("[*] Compiling gcov-instrumented binary...")
    subprocess.run(["make", "gcov_bin"], cwd=REPO_ROOT / "c_program", check=True)


def reset_coverage_data():
    for f in REPO_ROOT.rglob("*.gcda"):
        f.unlink()


def run_with_input(input_str):
    input_file = REPO_ROOT / "temp_input.c"  # Use .c to match expectations
    input_file.write_text(input_str)

    try:
        result = subprocess.run(
            [
                str(BINARY_PATH),
                "-c",
                str(input_file),
                "-I",
                str(REPO_ROOT / "c_program" / "include"),
                "-I",
                str("/usr/include"),
                "-I",
                str("/usr/lib/gcc/x86_64-linux-gnu/11/include"),
            ],
            check=True,
            timeout=3,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        # if result.stderr:
        #     print("[stderr]", result.stderr)
    except subprocess.CalledProcessError as e:
        # print(f"[!] Binary exited non-zero: {e}")
        pass
    except subprocess.TimeoutExpired:
        # print("[!] Execution timed out")
        pass
    finally:
        input_file.unlink(missing_ok=True)


def generate_gcov_report():
    # Use hardcoded reference to tcc.c
    c_files = read_c_programs_with_filenames(C_SRC_DIR)
    base_name = "tcc"

    # Ensure .gcno is present in coverage_data
    original_gcno = BINARY_PATH.parent / f"{base_name}.gcno"
    if original_gcno.exists():
        dest_gcno = GCDA_DIR / f"{base_name}.gcno"
        dest_gcno.write_bytes(original_gcno.read_bytes())

    # Ensure .gcda is present in coverage_data
    original_gcda = BINARY_PATH.parent / f"{base_name}.gcda"
    if original_gcda.exists():
        dest_gcda = GCDA_DIR / f"{base_name}.gcda"
        dest_gcda.write_bytes(original_gcda.read_bytes())

    # Copy source file into report directory so gcov can annotate it
    for filename, content in c_files:
        copied_src = GCOV_REPORT_DIR / "src" / filename
        copied_src.parent.mkdir(parents=True, exist_ok=True)
        copied_src.write_text(content)

    result = subprocess.run(
        ["gcov", "-o", str(GCDA_DIR), str(base_name)],
        cwd=GCOV_REPORT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )

    results_dir = REPO_ROOT / "artifacts/final-results"
    results_dir.mkdir(parents=True, exist_ok=True)
    existing_files = list(results_dir.glob("results*.txt"))
    indices = [
        int(f.stem.replace("results", ""))
        for f in existing_files
        if f.stem.replace("results", "").isdigit()
    ]
    new_index = max(indices) + 1 if indices else 0
    new_results_file = results_dir / f"results{new_index}.txt"
    new_results_file.write_text(result.stdout)
    print(result.stdout)

    # Print contents of the generated .gcov file
    # for gcov_file in GCOV_REPORT_DIR.glob("*.gcov"):
    #     pass
    #     print(f"\n[GCOV] Contents of {gcov_file.name}:\n")
    #     print(gcov_file.read_text())


def save_test_cases(klee_inputs, afl_inputs, llm_inputs):
    TEST_CASES_DIR.mkdir(parents=True, exist_ok=True)

    # Determine the starting index by counting existing test_case_*.txt files
    existing_cases = list(TEST_CASES_DIR.glob("test_case_*.c"))
    if existing_cases:
        existing_indices = [
            int(f.stem.split("_")[-1])
            for f in existing_cases
            if f.stem.split("_")[-1].isdigit()
        ]
        start_idx = max(existing_indices) + 1 if existing_indices else 0
    else:
        start_idx = 0

    all_inputs = klee_inputs + afl_inputs + llm_inputs

    for i, input_str in enumerate(all_inputs):
        idx = start_idx + i
        test_case_path = TEST_CASES_DIR / f"test_case_{idx}.c"
        try:
            test_case_path.write_text(input_str)
        except Exception as e:
            print(f"[!] Failed to write {test_case_path}: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Orchestrate coverage evaluation")

    compile_gcov_binary()
    print("[*] Resetting coverage data...")
    reset_coverage_data()

    print("[*] Extracting KLEE inputs...")
    klee_inputs = extract_all_klee_inputs(KLEE_OUTPUT_DIR)
    print(f"[+] Got {len(klee_inputs)} inputs from KLEE")

    print("[*] Extracting AFL inputs...")
    afl_inputs = extract_all_afl_inputs(AFL_OUTPUT_DIR)
    print(f"[+] Got {len(afl_inputs)} inputs from AFL")

    print("[*] Extracting LLM Generated inputs...")
    llm_inputs = extract_llm_generated_tests(LLM_OUTPUT_DIR)
    print(f"[+] Got {len(llm_inputs)} inputs from LLM")

    print("[*] Extracting AFL generated seeds...")
    afl_generated_inputs = extract_afl_generated_tests(
        REPO_ROOT / "artifacts/afl/generated_seeds"
    )
    print(f"[+] Got {len(afl_generated_inputs)} generated AFL inputs")

    print("[*] Saving test cases...")
    save_test_cases(klee_inputs, afl_inputs + afl_generated_inputs, llm_inputs)

    print("[*] Replaying saved test cases...")
    for test_case_path in sorted(TEST_CASES_DIR.glob("test_case_*.c")):
        try:
            input_str = test_case_path.read_text()
            run_with_input(input_str)
        except Exception as e:
            print(f"[!] Failed to replay {test_case_path}: {e}")

    print("[*] Generating gcov report...")
    generate_gcov_report()

    print(
        f"[✔] Done! See coverage report in {GCOV_REPORT_DIR} and all saved test cases in {TEST_CASES_DIR}"
    )
