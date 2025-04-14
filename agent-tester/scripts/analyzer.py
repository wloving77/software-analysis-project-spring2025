import os
from pathlib import Path
import subprocess
import re
from klee.ktest import KTest


def extract_all_klee_inputs(root_dir):
    inputs = []
    for subdir in Path(root_dir).resolve().glob("run_*"):
        for ktest in subdir.rglob("*.ktest"):
            print(f"[KLEE] Found KTest file: {ktest}")
            try:
                kt = KTest.fromfile(str(ktest))
                input_objects = {}

                for name, data in kt.objects:
                    match = re.fullmatch(r"input_(\d+)", name)
                    if match:
                        index = int(match.group(1))
                        input_objects[index] = data

                if not input_objects:
                    continue

                input_strs = []
                for index in sorted(input_objects):
                    data = input_objects[index]
                    for i in range(0, len(data), 4):
                        val = int.from_bytes(
                            data[i : i + 4], byteorder="little", signed=True
                        )
                        input_strs.append(str(val))

                inputs.append(" ".join(input_strs))
            except Exception as e:
                print(f"[!] Failed to parse {ktest}: {e}")
    return inputs


def extract_all_afl_inputs(root_dir):
    inputs = []
    for subdir in Path(root_dir).resolve().glob("run_*"):
        queue_dir = subdir / "default/queue"
        if not queue_dir.exists():
            continue
        for testcase in queue_dir.iterdir():
            if testcase.is_file():
                try:
                    inputs.append(testcase.read_text(errors="ignore"))
                except Exception as e:
                    print(f"[!] Could not read {testcase}: {e}")
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
