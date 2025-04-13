import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def log_coverage(iteration: int, coverage: int, csv_path="artifacts/logs/coverage.csv"):
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "a") as f:
        f.write(f"{iteration},{coverage}\n")

def plot_coverage(csv_path="artifacts/logs/coverage.csv", out_path="plots/coverage_plot.png"):
    df = pd.read_csv(csv_path, header=None, names=["iteration", "coverage"])
    plt.figure()
    plt.plot(df["iteration"], df["coverage"], marker='o')
    plt.title("AFL Path Coverage Over Iterations")
    plt.xlabel("Iteration")
    plt.ylabel("Paths Covered")
    plt.grid(True)
    Path(out_path).parent.mkdir(exist_ok=True)
    plt.savefig(out_path)
    print(f"[📈] Coverage plot saved to {out_path}")
