#include <stdio.h>
#include <stdlib.h>

int main() {
    int staticArray[20], i;
    for (i = 0; i < 20; i++) {
        staticArray[i] = i;
        printf("%d\n", staticArray[i]);
    }
}
