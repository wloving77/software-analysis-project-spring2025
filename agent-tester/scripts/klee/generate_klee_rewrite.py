# scripts/python/klee/generate_klee_rewrite.py
import os
import argparse
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


def init_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Please set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def read_c_source(file_path):
    with open(file_path, "r") as f:
        return f.read()


def write_transformed_code(output_path, code):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(code)


def build_prompt(source_code):
    system_instruction = (
        "You are modifying C code to prepare it for symbolic execution using the KLEE tool.\n"
        "Rewrite the following C program so that all user inputs (via stdin, argv, fgets, etc.) "
        "are made symbolic using `klee_make_symbolic`. Add `#include <klee/klee.h>` if needed.\n"
        "Replace any concrete input statements with symbolic declarations. Do not change the logic.\n"
        "Return ONLY the full modified C code.\n"
        "Thank you!"
    )
    return f"{system_instruction}\n\n{source_code}"


def extract_clean_c_code(raw_text):
    lines = raw_text.strip().splitlines()

    # Remove Markdown code fencing if present
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(
        description="Rewrite a C file to use symbolic inputs for KLEE."
    )
    parser.add_argument("input_file", help="Path to the C source file")
    parser.add_argument(
        "--outname",
        help="Optional basename for output (default is input name + '_klee')",
    )

    args = parser.parse_args()

    model = init_gemini()
    source_code = read_c_source(args.input_file)
    prompt = build_prompt(source_code)

    print("[+] Querying Gemini to rewrite for symbolic execution...")
    response = model.generate_content(prompt)
    rewritten_code = extract_clean_c_code(response.text)

    basename = (
        args.outname or os.path.splitext(os.path.basename(args.input_file))[0] + "_klee"
    )

    # Use repo-root-relative path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    output_path = os.path.join(repo_root, "artifacts/klee/rewrite", f"{basename}.c")

    write_transformed_code(output_path, rewritten_code)
    print(f"[✓] Rewritten C source saved to: {output_path}")


if __name__ == "__main__":
    main()
