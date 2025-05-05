import subprocess
import sys
from pathlib import Path
from langchain.tools import tool


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


@tool
def generate_coverage_report(input: str) -> str:
    """Runs the Coverage Generating script. Pass flags as a single string."""
    import shlex

    try:
        flags = shlex.split(input)
        result = subprocess.run(
            ["python3", f"{REPO_ROOT}/scripts/coverage_orchestrator.py", *flags],
            check=True,
            capture_output=True,
        )
        return f"Coverage Report Generated Successfully with flags: {input} \n Output: {result.stdout}"
    except Exception as e:
        return f"Coverage Generation Failed: {str(e)}"
