CC=clang
SRC_DIR=src
INC_DIR=include
BUILD_DIR=build
CFLAGS=-Wall -Wextra -I$(INC_DIR)

SRC=$(wildcard $(SRC_DIR)/*.c)
OBJ=$(SRC:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

TARGET=tcc_test

# ---- Default build ----
all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $^ -o $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# ---- Build with AFL instrumentation ----
afl: export CC=afl-clang-fast
afl: clean all

# ---- Build for KLEE (LLVM bitcode) ----
bc:
	clang -emit-llvm -c -g $(SRC) -I$(INC_DIR) -o $(BUILD_DIR)/main.bc

# ---- Clean ----
clean:
	rm -rf $(BUILD_DIR) $(TARGET)

.PHONY: all afl bc clean
