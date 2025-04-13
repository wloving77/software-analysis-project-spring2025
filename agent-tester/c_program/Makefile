# === Compiler and toolchain definitions ===
CC=clang
AFL_CC=afl-clang-fast
KLEE_CC=clang
CFLAGS=-O0 -g
SRC=src/proof_of_concept.c

# === Output directories ===
LLVM_DIR=../artifacts/klee/llvm
REWRITE_DIR=../artifacts/klee/rewrite
AFL_DIR=../artifacts/afl/compiled_afl
BIN_DIR=../artifacts/standard_binary

# === Ensure output dirs exist ===
$(LLVM_DIR) $(AFL_DIR) $(BIN_DIR):
	mkdir -p $@

# === LLVM bitcode output for KLEE from rewritten code ===
# Usage: make ../artifacts/klee/llvm/proof_of_concept_klee.bc
$(LLVM_DIR)/%.bc: $(REWRITE_DIR)/%.c | $(LLVM_DIR)
	$(KLEE_CC) -emit-llvm -c -g $< -o $@

# === Build LLVM bitcode from original proof_of_concept ===
$(LLVM_DIR)/proof.bc: $(SRC) | $(LLVM_DIR)
	$(KLEE_CC) -emit-llvm -c -g $(SRC) -o $@

# === AFL-instrumented binary ===
$(AFL_DIR)/proof_of_concept: $(SRC) | $(AFL_DIR)
	$(AFL_CC) $(CFLAGS) $(SRC) -o $@

# === Native binary (non-instrumented debug build) ===
$(BIN_DIR)/proof: $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC) -o $@

# === Top-level build targets ===
.PHONY: all proof.bc proof_afl proof

all: proof.bc proof_afl proof

proof.bc: $(LLVM_DIR)/proof_of_concept_klee.bc
proof_afl: $(AFL_DIR)/proof_of_concept
proof: $(BIN_DIR)/proof

# === Run the binary with a test file ===
.PHONY: test
test: $(AFL_DIR)/proof_of_concept
	@echo "secret" > test_input.txt
	-$(AFL_DIR)/proof_of_concept test_input.txt

# === Clean all build artifacts ===
.PHONY: clean
clean:
	rm -f $(LLVM_DIR)/*.bc \
	      $(AFL_DIR)/* \
	      $(BIN_DIR)/* \
	      $(REWRITE_DIR)/* \
	      test_input.txt
