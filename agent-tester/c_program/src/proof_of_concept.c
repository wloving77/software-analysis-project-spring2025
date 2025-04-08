// c_program/src/test_target.c
#include <stdio.h>
#include <string.h>

int main(int argc, char* argv[]) {
    char buf[100];
    if (argc > 1) {
        strncpy(buf, argv[1], 100);
        if (strcmp(buf, "secret") == 0) {
            printf("You found the secret path!\n");
        } else {
            printf("Try again.\n");
        }
    } else {
        printf("No input provided.\n");
    }
    return 0;
}
