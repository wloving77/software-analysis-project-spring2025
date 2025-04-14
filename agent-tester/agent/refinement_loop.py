from agent.tools.analyzer import (
    extract_interesting_afl_inputs,
    extract_klee_inputs,
    get_afl_coverage
)
from agent.tools.prompt_templates import refine_seed_prompt
from agent.tools.coverage_plotter import log_coverage, plot_coverage
from agent.tools.memory_store import is_novel_seed, store_seed
from scripts.afl.generate_afl_seeds import save_seeds
from scripts.afl_orchestrator import full_afl_pipeline, find_latest_binary
from scripts.klee_orchestrator import full_pipeline_for_all
from pathlib import Path
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
import subprocess

def generate_non_crashing_seeds(model, programs, num_seeds, binary_path, out_dir, max_attempts=10):
    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        print(f"[🧪] Attempting seed generation (try #{attempt})...")
        seeds = prompt_for_seeds(model, programs, num_seeds)
        save_seeds(seeds, out_dir)

        remove_crashing_seeds(binary_path, out_dir)
        remaining = list(Path(out_dir).glob("*.txt"))

        if remaining:
            print(f"[✓] {len(remaining)} valid seed(s) remain after filtering.")
            return seeds

        print("[!] All seeds crashed — retrying...")

    print("[🛑] Max retries reached. Injecting fallback seed.")
    fallback_seed = Path(out_dir) / "fallback.txt"
    fallback_seed.write_text("noop")
    return ["noop"]


def remove_crashing_seeds(binary_path: str, seed_dir: str):
    seed_dir_path = Path(seed_dir)
    for seed in seed_dir_path.glob("*.txt"):
        try:
            subprocess.run(
                [binary_path, str(seed)],
                timeout=1,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f"[!] Removing crashing seed: {seed.name}")
            seed.unlink()

from scripts.afl.generate_afl_seeds import (
                init_gemini,
                read_c_programs_with_filenames,
                prompt_for_seeds,
                save_seeds
            )  

load_dotenv()

SEED_DIR = Path("artifacts/afl/generated_seeds")
print(f"[+] Seed directory: {SEED_DIR}")
AFL_OUTPUT_DIR = Path("artifacts/afl/output")
KLEE_OUT_BASE = Path("artifacts/klee/klee_output")
BIN_DIR = Path("artifacts/afl/compiled_afl")

def init_gemini():
    key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.0-flash")


def prompt_for_refined_seeds(model, original_seeds, crash_seeds, klee_seeds, num=5):
    prompt = refine_seed_prompt(original_seeds, crash_seeds + klee_seeds, max_out=num)
    response = model.generate_content(prompt)
    return [
        s.strip().strip('"').strip("'")
        for s in response.text.split("---") if s.strip()
    ]


def read_previous_seeds(seed_dir):
    return [f.read_text().strip() for f in sorted(seed_dir.glob("*.txt"))]


def get_latest_klee_output_dir():
    dirs = list(KLEE_OUT_BASE.glob("run_*"))
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)

def save_iteration_logs(iteration: int, seeds, crashes, klee_seeds):
    log_dir = Path("artifacts/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    def save_list(path, items):
        with open(path, "w") as f:
            f.write("\n".join(items) + "\n")

    save_list(log_dir / f"seeds_iter_{iteration}.txt", seeds)
    save_list(log_dir / f"crashes_iter_{iteration}.txt", crashes)
    save_list(log_dir / f"klee_iter_{iteration}.txt", klee_seeds)


def get_latest_afl_output_dir():
    """
    Return the most recent AFL output run's `default` directory.
    """
    runs = sorted(AFL_OUTPUT_DIR.glob("run_*"), key=os.path.getmtime, reverse=True)
    if not runs:
        return None
    return runs[0] / "default"  # ✅ Only one 'default'

def main_loop(iterations=5, seeds_per_round=5):
    model = init_gemini()
    previous_coverage = 0

    for i in range(iterations):
        print(f"\n🌀 Iteration {i+1} / {iterations}")
        crashes, klee_seeds = [], []

        if i == 0:
            print("[+] Generating initial seeds...")
            programs = read_c_programs_with_filenames("c_program/src")
            binary_path = str(find_latest_binary(BIN_DIR))
            initial = generate_non_crashing_seeds(model, programs, seeds_per_round, binary_path, str(SEED_DIR))
            current_seeds = initial
        else:
            crashes = extract_interesting_afl_inputs(str(AFL_OUTPUT_DIR))
            klee_dir = get_latest_klee_output_dir()
            klee_seeds = extract_klee_inputs(klee_dir) if klee_dir else []
            originals = read_previous_seeds(SEED_DIR)

            # Filter novel seeds
            all_prev = set(originals + crashes + klee_seeds)
            filtered = [s for s in all_prev if is_novel_seed(s)]
            for s in filtered:
                store_seed(s)

            refined = prompt_for_refined_seeds(
                model,
                original_seeds=originals,
                crash_seeds=crashes,
                klee_seeds=klee_seeds,
                num=seeds_per_round
            )

            print(f"[+] Saving {len(refined)} refined seeds...")
            save_seeds(refined, SEED_DIR)
            current_seeds = refined

        # Save seed/crash/klee logs
        save_iteration_logs(i + 1, current_seeds, crashes, klee_seeds)

        # Run fuzzing + symbolic execution
        print("[⚙️] Running AFL pipeline...")
        full_afl_pipeline()

        print("[🔍] Running KLEE symbolic execution...")
        full_pipeline_for_all()

        # 🔍 Get latest AFL stats
        output_dir = get_latest_afl_output_dir()
        if output_dir and (output_dir / "fuzzer_stats").exists():
            coverage = get_afl_coverage(str(output_dir))
        else:
            print(f"[⚠️] Missing fuzzer_stats at {output_dir}")
            coverage = -1

        # 🧠 Track coverage
        if coverage >= 0:
            gain = coverage - previous_coverage
            print(f"[📊] Total AFL paths: {coverage} (Δ {gain})")
            log_coverage(i + 1, coverage)
            previous_coverage = coverage
        else:
            print("[⚠️] AFL coverage stats not found.")

        time.sleep(1)

    # After loop
    plot_coverage()



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()
    main_loop(iterations=args.iterations, seeds_per_round=args.seeds)