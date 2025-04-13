#!/bin/bash

# === Configuration ===
SCRIPT="agent/refinement_loop.py"
ENV_FILE=".env"

# === Disable crash pattern warning in containers ===
export AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1

# === Load API key ===
if [ -f "$ENV_FILE" ]; then
  export $(grep GEMINI_API_KEY "$ENV_FILE" | xargs)
else
  echo "[!] .env file not found. Exiting."
  exit 1
fi

# === Handle arguments ===
ITERATIONS=5
SEEDS=5

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --iterations) ITERATIONS="$2"; shift ;;
    --seeds-per-round) SEEDS="$2"; shift ;;
    *) echo "[!] Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# === Run pipeline ===
echo "🚀 Running refinement loop with $ITERATIONS iterations and $SEEDS seeds/round"
PYTHONPATH=. python3 $SCRIPT --iterations $ITERATIONS --seeds $SEEDS
