# === Compiler and toolchain definitions ===
CC=gcc
AFL_CC=afl-clang-fast
KLEE_CC=clang
CFLAGS=-O0 -g
SRC=src/mini_qsort.c
SRC_NAME=$(basename $(notdir $(SRC)))

# === Output directories ===
LLVM_DIR=../artifacts/klee/llvm
REWRITE_DIR=../artifacts/klee/rewrite
AFL_DIR=../artifacts/afl/compiled_afl
BIN_DIR=../artifacts/standard_binary

# === Ensure output dirs exist ===
$(LLVM_DIR) $(AFL_DIR) $(BIN_DIR):
	mkdir -p $@

# === LLVM bitcode output for KLEE from rewritten code ===
$(LLVM_DIR)/%.bc: $(REWRITE_DIR)/%.c | $(LLVM_DIR)
	$(KLEE_CC) -emit-llvm -c -g $< -o $@

# === Build LLVM bitcode from original source ===
$(LLVM_DIR)/$(SRC_NAME).bc: $(SRC) | $(LLVM_DIR)
	$(KLEE_CC) -emit-llvm -c -g $(SRC) -o $@

# === AFL-instrumented binary ===
$(AFL_DIR)/$(SRC_NAME): $(SRC) | $(AFL_DIR)
	$(AFL_CC) $(CFLAGS) $(SRC) -o $@

# === Native binary (non-instrumented debug build) ===
$(BIN_DIR)/$(SRC_NAME): $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS) -fprofile-arcs -ftest-coverage $(SRC) -o $@

# === Top-level build targets ===
.PHONY: all klee_bitcode afl_bin native_bin

all: klee_bitcode afl_bin native_bin

klee_bitcode: $(LLVM_DIR)/$(SRC_NAME).bc
afl_bin: $(AFL_DIR)/$(SRC_NAME)
native_bin: $(BIN_DIR)/$(SRC_NAME)

# === Run the binary with a test file ===
.PHONY: test
test: $(AFL_DIR)/$(SRC_NAME)
	@echo "secret" > test_input.txt
	-$(AFL_DIR)/$(SRC_NAME) test_input.txt

# === Clean all build artifacts ===
.PHONY: clean
clean:
	rm -f $(LLVM_DIR)/*.bc \
	      $(AFL_DIR)/* \
	      $(BIN_DIR)/* \
	      $(REWRITE_DIR)/* \
	      test_input.txt
