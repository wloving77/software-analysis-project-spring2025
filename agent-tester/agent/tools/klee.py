import subprocess
import sys
from pathlib import Path
from langchain.tools import tool

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


@tool
def run_klee_pipeline(input: str) -> str:
    """Runs the full KLEE symbolic execution pipeline"""
    import shlex

    try:
        flags = shlex.split(input)
        subprocess.run(
            ["python3", f"{REPO_ROOT}/scripts/klee_orchestrator.py", *flags], check=True
        )
        return f"KLEE pipeline completed successfully with flags: {input}"
    except Exception as e:
        return f"KLEE pipeline failed: {str(e)}"
