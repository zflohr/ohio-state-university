#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **args) {
    int arraySize, i, *dynamicArray;
    if(argc != 2) {
        printf("This program takes one command line argument.");
        return -1;
    }
    arraySize = strtol(args[1], NULL, 10);
    dynamicArray = (int *) malloc(sizeof(int)*arraySize);
    for (i = 0; i < arraySize; i++) {
        dynamicArray[i] = i;
        printf("%d\n", dynamicArray[i]);
    }
    free(dynamicArray);
}
