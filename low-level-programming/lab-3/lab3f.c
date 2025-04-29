#include <stdio.h>
#include <stdlib.h>

int main() {
    int staticArray[10][15], i, j;
    for (i = 0; i < 10; i++) {
        for (j = 0; j < 15; j++) {
            staticArray[i][j] = i * j;
            printf("Element at position [%d][%d]: %d   Address: %lu\n", i, j, staticArray[i][j], &staticArray[i][j]);
        }
    }
    for (i = 0; i < 10; i++) {
        printf("array[%d]: %lu\n", i, staticArray[i]);
    }
}
