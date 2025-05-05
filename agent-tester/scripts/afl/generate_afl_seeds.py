import os
import argparse
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

SEED_DELIMITER = "---"


def init_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Please set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def read_c_programs_with_filenames(src_dir: str) -> list[tuple[str, str]]:
    """
    Returns a list of tuples: (filename, file_contents)
    """
    program_files = []
    for path in sorted(Path(src_dir).rglob("*.c")):
        with open(path, "r") as f:
            program_files.append((path.name, f.read()))
    return program_files


def format_prompt(
    programs: list[tuple[str, str]], num_seeds: int, additional_prompt: str = ""
) -> str:
    header = f"""
    You are helping fuzz a C program. The codebase consists of several C files listed below.

    Please generate {num_seeds} diverse inputs that may trigger different execution paths or edge cases in the program.
    - Inputs should be realistic for the program under test
    - Return only inputs that will be *accepted* by the program via CLI file input.

    Return the seeds as plain text only, each separated by a line with only the delimiter: `{SEED_DELIMITER}`.
    Do not include explanations or formatting. Just the text to be put in files.
    
    Example Format: 
    
    {SEED_DELIMITER}
    seed 1
    {SEED_DELIMITER}
    seed 2
    {SEED_DELIMITER}

    Please format individual seeds as the program would require via file input.

    C programs:
    """

    program_sections = []
    for filename, content in programs:
        if filename == "tcc.c":
            program_sections.append(f"""{filename}:\n\"\"\"\n{content}\n\"\"\"""")

    final_prompt = header.strip() + "\n\n" + "\n\n".join(program_sections)

    final_prompt += f"\n\n{additional_prompt}"

    return final_prompt


def prompt_for_seeds(
    model, programs: list[tuple[str, str]], num_seeds: int, additional_prompt: str
) -> list:
    prompt = format_prompt(programs, num_seeds, additional_prompt)
    try:
        response = model.generate_content(prompt)
        return parse_seeds(response.text)
    except Exception as e:
        print(f"[!] Error during LLM generation: {e}")
        return []


def parse_seeds(text: str) -> list:
    seeds = [
        s.strip().strip('"').strip("'")
        for s in text.strip().split(SEED_DELIMITER)
        if s.strip()
    ]
    return [s for s in seeds if s]


def save_seeds(seeds: list, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for i, seed in enumerate(seeds, start=1):
        with open(output_path / f"seed{i}.c", "w") as f:
            f.write(seed.strip("```"))


def main():
    parser = argparse.ArgumentParser(
        description="Generate seed inputs for a combined C program using Gemini."
    )
    parser.add_argument(
        "--src-dir", default="c_program/src", help="Relative path to C source files"
    )
    parser.add_argument(
        "--out-dir",
        default="artifacts/afl/generated_seeds",
        help="Relative output directory for seed files",
    )
    parser.add_argument(
        "--num-seeds", type=int, default=3, help="Number of seeds to generate"
    )

    parser.add_argument(
        "--additional-prompt",
        type=str,
        default="",
        help="Additional Prompt to Fine Tune Generated Seeds",
    )

    args = parser.parse_args()
    src_dir = (ROOT_DIR / args.src_dir).resolve()
    out_dir = (ROOT_DIR / args.out_dir).resolve()

    print(f"[+] Initializing Gemini model...")
    model = init_gemini()

    print(f"[+] Reading C files from: {src_dir}")
    programs = read_c_programs_with_filenames(src_dir)

    print(f"[+] Requesting {args.num_seeds} seed inputs...")
    seeds = prompt_for_seeds(model, programs, args.num_seeds, args.additional_prompt)

    if not seeds:
        print("[!] No seeds generated. Exiting.")
        return

    print(f"[+] Saving {len(seeds)} seeds to {out_dir}")
    save_seeds(seeds, out_dir)
    print("[✓] Done.")


if __name__ == "__main__":
    main()
