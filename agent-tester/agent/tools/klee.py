import subprocess
from langchain.tools import tool

@tool
def run_klee_pipeline() -> str:
    """Runs the full KLEE symbolic execution pipeline."""
    try:
        subprocess.run(["python3", "scripts/klee_orchestrator.py"], check=True)
        return "KLEE pipeline completed successfully."
    except Exception as e:
        return f"KLEE pipeline failed: {str(e)}"
