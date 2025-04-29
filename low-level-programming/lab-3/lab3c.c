#include <stdio.h>
#include <stdlib.h>

int main() {
    int staticArray[20], *arrayPointer, i;
    arrayPointer = staticArray;
    for (i = 0; i < 20; i++) {
        *arrayPointer++ = i;
        printf("Element: %d Address: %lu Address: %lu\n", staticArray[i], &staticArray[i], staticArray + i);
    }
}
