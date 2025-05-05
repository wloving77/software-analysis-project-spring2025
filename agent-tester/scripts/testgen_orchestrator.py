import os
import argparse
import logging
import google.generativeai as genai
from afl.generate_afl_seeds import read_c_programs_with_filenames
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(level=logging.INFO, format="[*] %(message)s")


def init_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Please set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def generate_tests_with_gemini(num_tests=10, additional_prompt=""):
    src_dir = ROOT_DIR / "c_program/src"
    artifact_dir = ROOT_DIR / "artifacts/llm-testgen"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    NUM_SEEDS = num_tests
    SEED_DELIMITER = "----"

    header = (
        "You are helping evaluate a C program using gcov for code coverage. The codebase consists of several C files listed below.\n\n"
        f"Please generate {NUM_SEEDS} diverse inputs that may trigger different execution paths or edge cases in the program.\n"
        "- Inputs should be realistic for the program under test\n"
        "- Return only inputs that will be *accepted* by the program via CLI file input.\n\n"
        f"Return the seeds as plain text only, each separated by a line with only the delimiter: `{SEED_DELIMITER}`.\n"
        "Do not include explanations or formatting. Just the text to be put in files.\n\n"
        "Please make these tests as large and complex as possible so that they function well for the program under test and maximize code coverage, shoot for a minimum of 25-50 line programs.\n\n"
        "Example Format:\n\n"
        f"{SEED_DELIMITER}\n"
        "seed 1\n"
        f"{SEED_DELIMITER}\n"
        "seed 2\n"
        f"{SEED_DELIMITER}\n\n"
        "Please format individual seeds as the program would require via file input.\n\n"
        "C programs:\n"
        "Remember, nothing besides delimiters and input text"
    )

    programs = read_c_programs_with_filenames(src_dir)
    program_text = ""
    for filename, content in programs:
        if filename == "tcc.c":
            program_text = f"{filename}:\n{content}\n"
    if not program_text:
        raise FileNotFoundError("tcc.c not found in source directory.")

    model = init_gemini()
    final_prompt = (
        header
        + "\n\n"
        + program_text
        + "\n\n"
        + "Additional Instructions to Fine Tune Generated Tests:\n"
        + additional_prompt
    )

    response = model.generate_content(final_prompt)
    test_cases = response.text.strip().split(f"\n{SEED_DELIMITER}\n")
    test_cases = [case.strip() for case in test_cases if case.strip()]

    for i, case in enumerate(test_cases):
        logging.info(f"Writing test case {i:03d}")
        test_file = artifact_dir / f"test_{i:03d}.c"
        test_file.write_text(case.strip("```").strip("---") + "\n")
    print(f"[✔] {len(test_cases)} test cases written to {artifact_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate LLM test inputs for a C program"
    )
    parser.add_argument(
        "--num-tests", type=int, default=10, help="Number of test cases to generate"
    )
    parser.add_argument(
        "--additional-prompt",
        type=str,
        default="",
        help="Additional Prompt to Fine Tune Generated Tests",
    )
    args = parser.parse_args()
    generate_tests_with_gemini(
        num_tests=args.num_tests, additional_prompt=args.additional_prompt
    )
