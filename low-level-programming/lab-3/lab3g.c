#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **args) {
    int rows, columns, i, j, **dynamicArray;
    if(argc != 3) {
        printf("This program takes two command line arguments.");
        return -1;
    }
    rows = strtol(args[1], NULL, 10);
    columns = strtol(args[2], NULL, 10);
    dynamicArray = (int**)malloc(sizeof(int*) * rows);
    for (i = 0; i < rows; i++) {
        dynamicArray[i] = (int*)malloc(sizeof(int) * columns);
    }
    for (i = 0; i < rows; i++) {
        for (j = 0; j < columns; j++) {
            dynamicArray[i][j] = i * j;
            printf("Element at position [%d][%d]: %d   Address: %lu\n", i, j, dynamicArray[i][j], &dynamicArray[i][j]);
        }
    }
    for (i = 0; i < rows; i++) {
        printf("array[%d]: %lu\n", i, dynamicArray[i]);
    }
    for (i = 0; i < rows; i++) {
        free(dynamicArray[i]);
    }
    free(dynamicArray);
}
