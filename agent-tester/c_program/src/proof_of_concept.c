#include <stdio.h>
#include <string.h>
#include <stdlib.h>  // for getenv

#ifdef KLEE
#include <klee/klee.h>
#endif

int main(int argc, char* argv[]) {
    char buf[100] = {0};

#ifdef KLEE
    klee_make_symbolic(buf, sizeof(buf), "input");
#else
    if (argc > 1) {
        FILE *f = fopen(argv[1], "r");
        if (f) {
            fread(buf, 1, sizeof(buf) - 1, f);
            fclose(f);
        }
    }
#endif

    printf("[INPUT] %s\n", buf);
    buf[strcspn(buf, "\r\n")] = '\0';

    if (strcmp(buf, "secret") == 0) {
        puts("Branch: secret");
        return 1;
    }

    if (strcmp(buf, "admin") == 0) {
        puts("Branch: admin");
        return 2;
    }

    if (strcmp(buf, "debug") == 0) {
        puts("Branch: debug");
        return 3;
    }

    if (strcmp(buf, "crash") == 0) {
        puts("Branch: crashing");

        const char *flag = getenv("AFL_ALLOW_CRASH");
        if (flag && strcmp(flag, "1") == 0) {
            volatile char *x = NULL;
            *x = 42;
        }

        return 4;
    }

    if (strncmp(buf, "key=", 4) == 0) {
        puts("Branch: config key provided");
        if (strchr(buf, '!')) {
            puts("Bonus config feature!");
        }
        return 5;
    }

    puts("Branch: fallback/default");
    return 0;
}
