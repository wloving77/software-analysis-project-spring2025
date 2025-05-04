import os
import argparse
import logging
import google.generativeai as genai
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

    c_files = list(src_dir.glob("*.c"))
    if not c_files:
        raise FileNotFoundError(f"No .c file found in {src_dir}")
    logging.info(f"Found {len(c_files)} C files. Generating {num_tests} test cases...")
    program_text = "\n\n----\n\n".join(file.read_text() for file in c_files)

    NUM_SEEDS = num_tests
    SEED_DELIMITER = "----"

    header = f"""
    You are helping evaluate a C program using gcov for code coverage. The codebase consists of several C files listed below.

    Please generate {NUM_SEEDS} diverse input strings that exercise different branches or edge cases in the code.
    - Inputs should be realistic: valid user inputs or values the program is likely to encounter.
    - Avoid empty strings, raw binary, or inputs clearly outside the program’s expected behavior.
    - Prefer inputs that lead to meaningful execution paths, rather than crashing or exiting early.

    Return the inputs as plain text only, each separated by a line with only the delimiter: `{SEED_DELIMITER}`.
    Do not include explanations, comments, or formatting. Just the program inputs.

    Example Format:

    {SEED_DELIMITER}
    test 1
    {SEED_DELIMITER}
    test 2
    {SEED_DELIMITER}

    Do not label the inputs or describe them in any way. We will be using your output programmatically.

    C programs:
    """

    model = init_gemini()
    prompt = header + "\n\n" + program_text + "\n\n" + additional_prompt

    response = model.generate_content(prompt)
    test_cases = response.text.strip().split(f"\n{SEED_DELIMITER}\n")
    test_cases = [case.strip() for case in test_cases if case.strip()]

    for i, case in enumerate(test_cases):
        logging.info(f"Writing test case {i:03d}")
        test_file = artifact_dir / f"test_{i:03d}.txt"
        test_file.write_text(case + "\n")
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
