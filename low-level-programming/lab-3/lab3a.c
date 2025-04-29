#include <stdio.h>
#include <stdlib.h>
#include "swap.h"

int main(int argc, char **args) {
    int arg1, arg2;
    if(argc != 3) {
        printf("This program takes two command line arguments.");
        return -1;
    }
    arg1 = strtol(args[1], NULL, 10);
    arg2 = strtol(args[2], NULL, 10);
    swap(&arg1, &arg2);
}
