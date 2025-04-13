#include <stdio.h>
#include <string.h>
#include <stdlib.h>  // for getenv

int main(int argc, char* argv[]) {
    char buf[100] = {0};

    if (argc > 1) {
        FILE *f = fopen(argv[1], "r");
        if (f) {
            fread(buf, 1, sizeof(buf) - 1, f);
            fclose(f);
        }

        // Normalize newline if needed
        buf[strcspn(buf, "\r\n")] = '\0';

        // Multiple clearly separated branches
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

            // ✅ Only crash if the env variable is explicitly set
            if (getenv("AFL_ALLOW_CRASH")) {
                char *x = NULL;
                *x = 42;  // Intentional crash
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
    } else {
        puts("Branch: no input file");
    }

    return 0;
}
