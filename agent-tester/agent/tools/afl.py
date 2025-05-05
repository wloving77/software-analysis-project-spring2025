import subprocess
import sys
from pathlib import Path
from langchain.tools import tool

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


@tool
def run_afl_pipeline(input: str) -> str:
    """Runs AFL++ with specified CLI flags. Example: '--num-seeds 10 --afl-runtime 30'"""
    import shlex

    input = input.strip()
    # if not input:
    #     return "No flags provided. Example: '--num-seeds 10 --afl-runtime 30'"

    try:
        flags = shlex.split(input)
        subprocess.run(
            ["python3", f"{REPO_ROOT}/scripts/afl_orchestrator.py", *flags], check=True
        )
        return f"AFL pipeline completed with flags: {input}"
    except subprocess.CalledProcessError as e:
        return f"AFL pipeline failed: {e}"
