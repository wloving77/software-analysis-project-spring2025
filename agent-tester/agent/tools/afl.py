import subprocess
from langchain.tools import tool

@tool
def run_afl_pipeline() -> str:
    """Runs the full AFL++ pipeline."""
    try:
        subprocess.run(["python3", "scripts/afl_orchestrator.py"], check=True)
        return "AFL pipeline completed successfully."
    except Exception as e:
        return f"AFL pipeline failed: {str(e)}"
