#include <stdio.h>
#include <stdlib.h>
#include "swap.h"

int swap(int *arg1, int *arg2) {
    int storeArg1Address = *arg1;
    *arg1 = *arg2;
    *arg2 = storeArg1Address;
    printf("%d, %d\n", *arg1, *arg2);
    return;
}
