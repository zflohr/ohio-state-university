#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **args) {
    int arraySize, i, *dynamicArray, *arrayPointer;
    if(argc != 2) {
        printf("This program takes one command line argument.");
        return -1;
    }
    arraySize = strtol(args[1], NULL, 10);
    dynamicArray = (int *) malloc(sizeof(int)*arraySize);
    arrayPointer = dynamicArray;
    for (i = 0; i < arraySize; i++) {
        *arrayPointer++ = i;
        printf("Element: %d Address: %lu Address: %lu\n", dynamicArray[i], &dynamicArray[i], dynamicArray + i);
    }
    free(dynamicArray);
}
