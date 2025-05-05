# === Compiler Configuration ===
CC       = gcc
AFL_CC   = afl-clang-fast
KLEE_CC  = clang

CFLAGS   = -O0 -g -I ./include -fprofile-arcs -ftest-coverage
CFLAGS  += -DTCC_TARGET_X86_64
CFLAGS  += -DTCC_VERSION="\"0.9.27\""

LDFLAGS  = -fprofile-arcs -ftest-coverage

# === Source and Build Configuration ===
SRC_DIR      = src
SRC          = $(SRC_DIR)/tcc.c
SRC_NAME     = $(basename $(notdir $(SRC)))

# SOURCES      = $(SRC_DIR)/libtcc.c $(SRC_DIR)/tccpp.c \
#                $(SRC_DIR)/tccgen.c $(SRC_DIR)/tccelf.c \
#                $(SRC_DIR)/x86_64-gen.c $(SRC_DIR)/x86_64-link.c

SRC_NAMES    = $(notdir $(SOURCES))
OBJ_NAMES    = $(SRC_NAMES:.c=.o)
BC_NAMES     = $(SRC_NAMES:.c=.bc)

REWRITE_DIR  = ../artifacts/klee/rewrite

# === Output Directories ===
LLVM_DIR     = ../artifacts/klee/llvm
AFL_DIR      = ../artifacts/afl/compiled_afl
BIN_DIR      = ../artifacts/standard_binary

# === Output Files ===
LLVM_OUT     = $(LLVM_DIR)/tcc.bc
AFL_OUT      = $(AFL_DIR)/tcc
BIN_OUT      = $(BIN_DIR)/tcc

# === Ensure Output Dirs Exist ===
$(LLVM_DIR) $(AFL_DIR) $(BIN_DIR):
	mkdir -p $@

# === Build Targets ===
.PHONY: all klee_bitcode afl_bin native_bin test gcov_bin clean

all: klee_bitcode afl_bin native_bin

klee_bitcode: $(LLVM_DIR)/$(SRC_NAME).bc

$(LLVM_DIR)/%.bc: $(REWRITE_DIR)/%.c | $(LLVM_DIR)
	$(KLEE_CC) $(CFLAGS) -emit-llvm -c -g $< -o $@

$(LLVM_DIR)/$(SRC_NAME).bc: $(SRC) | $(LLVM_DIR)
	$(KLEE_CC) $(CFLAGS) -emit-llvm -c -g $< -o $@

afl_bin: $(AFL_DIR)/$(SRC_NAME)

$(AFL_DIR)/$(SRC_NAME): $(SRC) | $(AFL_DIR)
	$(AFL_CC) $(CFLAGS) $< -o $@

native_bin: $(BIN_DIR)/$(SRC_NAME)

$(BIN_DIR)/$(SRC_NAME): $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

gcov_bin: $(BIN_DIR)/$(SRC_NAME)

clean:
	rm -f $(SRC_DIR)/*.o $(SRC_DIR)/*.bc $(SRC_DIR)/*.gcno
	rm -f $(LLVM_DIR)/*.bc \
	      $(AFL_DIR)/* \
	      $(BIN_DIR)/* \
	      $(REWRITE_DIR)/* \
	      test_input.txt