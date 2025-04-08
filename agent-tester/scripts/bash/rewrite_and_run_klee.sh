#!/bin/bash
set -e

echo "[1] Rewriting for KLEE with Gemini..."
python3 ../python/klee/generate_klee_rewrite.py ../../c_program/src/proof_of_concept.c 

echo "[2] Compiling LLVM bitcode from rewrite..."
make -C ../../c_program ../artifacts/klee/llvm/proof_of_concept_klee.bc

echo "[3] Running KLEE..."
python3 ../python/klee/run_klee_only.py ../../artifacts/klee/llvm/proof_of_concept_klee.bc

echo "[✓] Done."