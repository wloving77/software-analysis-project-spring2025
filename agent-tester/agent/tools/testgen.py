import subprocess
import sys
from pathlib import Path
from langchain.tools import tool

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


@tool
def generate_test_cases(input: str) -> str:
    """Runs the LLM Test Case Generation Tool."""
    import subprocess
    import shlex

    try:
        flags = shlex.split(input)
        subprocess.run(
            ["python3", f"{REPO_ROOT}/scripts/testgen_orchestrator.py", *flags],
            check=True,
        )
        return f"LLM Testgen run with flags: {input}"
    except Exception as e:
        return f"LLM Testgen run failed: {str(e)}"
