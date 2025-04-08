# Compiler and toolchain definitions
CC=clang
AFL_CC=afl-clang-fast
KLEE_CC=clang
CFLAGS=-O0 -g
SRC=src/proof_of_concept.c

# Output directories relative to agent-tester
LLVM_DIR=../artifacts/klee/llvm
REWRITE_DIR=../artifacts/klee/rewrite
AFL_DIR=../artifacts/afl/afl_output
BIN_DIR=../artifacts/binary

# Ensure output dirs exist
$(LLVM_DIR) $(AFL_DIR) $(BIN_DIR):
	mkdir -p $@

# LLVM bitcode output (for original proof.c)
$(LLVM_DIR)/proof.bc: $(SRC) | $(LLVM_DIR)
	$(KLEE_CC) -emit-llvm -c -g $(SRC) -o $@

# AFL binary (instrumented for fuzzing)
$(AFL_DIR)/proof_afl: $(SRC) | $(AFL_DIR)
	$(AFL_CC) $(CFLAGS) $(SRC) -o $@

# Native binary (regular debug build)
$(BIN_DIR)/proof: $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC) -o $@

# === New generic rule: build LLVM .bc from any .c file in REWRITE_DIR ===
# Example: make ../artifacts/klee/llvm/rewrite_test.bc
$(LLVM_DIR)/%.bc: $(REWRITE_DIR)/%.c | $(LLVM_DIR)
	$(KLEE_CC) -emit-llvm -c -g $< -o $@

# === Top-level build targets ===
.PHONY: all proof.bc proof_afl proof
all: proof.bc proof_afl proof

proof.bc: $(LLVM_DIR)/proof.bc
proof_afl: $(AFL_DIR)/proof_afl
proof: $(BIN_DIR)/proof

# === Clean all build artifacts ===
.PHONY: clean
clean:
	rm -f $(LLVM_DIR)/*.bc \
	      $(AFL_DIR)/* \
	      $(BIN_DIR)/* \
		  ${REWRITE_DIR}/*
