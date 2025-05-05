#ifndef CONFIG_H
#define CONFIG_H

/* === Target platform === */
#define TCC_TARGET_X86_64 1  // or define TCC_TARGET_X86_64 depending on your build

/* === General features === */
#define CONFIG_TCC_STATIC 1
#define CONFIG_TCCDIR "./"  // avoid hardcoded /usr/local
#define CONFIG_SYSROOT "./"
#define CONFIG_TCC_ELF 1

/* === Compiler support === */
#define CONFIG_TCC_ASM 1
#define CONFIG_TCC_BCHECK 1
#define CONFIG_USE_LIBGCC 0
#define CONFIG_TCC_BACKTRACE 0
#define CONFIG_TCC_SEMLOCK 0

/* === Limits === */
#define CONFIG_TCC_MAX_PATH 1024

#endif /* CONFIG_H */