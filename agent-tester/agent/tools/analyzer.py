import os
from pathlib import Path
import subprocess
from scripts.klee.ktest import KTest

def extract_interesting_afl_inputs(output_dir: str, limit=5):
    crash_dir = Path(output_dir) / "default" / "crashes"
    queue_dir = Path(output_dir) / "default" / "queue"

    seeds = []

    if crash_dir.exists():
        for f in sorted(crash_dir.glob("id:*"))[:limit]:
            with open(f, "r", errors="ignore") as fin:
                seeds.append(fin.read().strip())

    if not seeds and queue_dir.exists():
        for f in sorted(queue_dir.glob("id:*"))[:limit]:
            with open(f, "r", errors="ignore") as fin:
                seeds.append(fin.read().strip())

    return seeds


def extract_klee_inputs(klee_output_dir):
    inputs = []
    for ktest_file in Path(klee_output_dir).glob("*.ktest"):
        try:
            test = KTest.fromfile(str(ktest_file))
            for obj in test.objects:
                if obj.name in [b"input", b"buf"] or obj.name.startswith(b"arg") or obj.name.startswith(b"stdin"):
                    # Decode to ASCII-friendly string if possible
                    decoded = obj.bytes.decode(errors="ignore").strip()
                    if decoded:
                        inputs.append(decoded)
        except Exception as e:
            print(f"[!] Failed to parse {ktest_file}: {e}")
    return inputs



def get_afl_coverage(output_dir):
    """
    Parse AFL's fuzzer_stats to extract meaningful coverage metric.
    Uses 'edges_found' or 'corpus_count' if available.
    """
    stats_path = Path(output_dir) / "fuzzer_stats"
    if not stats_path.exists():
        print(f"[⚠️] fuzzer_stats not found at {stats_path}")
        return -1

    with open(stats_path) as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("edges_found"):
            return int(line.strip().split(":")[1].strip())
        elif line.startswith("corpus_count"):  # fallback
            return int(line.strip().split(":")[1].strip())

    print("[⚠️] No coverage metric found in fuzzer_stats.")
    return -1

