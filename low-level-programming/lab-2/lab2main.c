#include <stdio.h>
#include <stdlib.h>
#include "bit_op.h"

int main(void){
    unsigned long number, ret;
    int startIndex, length;
    unsigned int numberOfComputations, iteration;

    printf("How many numbers do you need to compute? ");
    scanf("%u", &numberOfComputations);

    for (iteration = 0; iteration < numberOfComputations; ++iteration){
        printf("Please enter number, startIndex, and length in that order,\n");
        printf("with each integer separated by a comma and a space: \n");
        scanf("%lu, %d, %d", &number, &startIndex, &length);
        ret = take_bits(number, startIndex, length);
        printf("%lu, %d, %d = %lu\n", number, startIndex, length, ret);
    }
}
