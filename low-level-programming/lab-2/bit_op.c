#include <stdio.h>
#include <stdlib.h>
#include "bit_op.h"

unsigned long take_bits(unsigned long number, int startIndex, int length){

    int sizeOfUnsignedLong = (sizeof(unsigned long) * 8); /*size of UL in bits*/

    /*Error messages for invalid startIndex and length:*/
    if(startIndex < 0){
        printf("Error: The starting index cannot be less than zero.\n");
        exit(1);
    }
    if(startIndex > (sizeOfUnsignedLong - 1)){
        printf("Error: The starting index cannot be greater than %d.\n", sizeOfUnsignedLong - 1);
        exit(1);
    }
    if(length <= 0){
        printf("Error: The length of the binary fragment cannot be less than, or equal to, zero.\n");
        exit(1);
    }
    if(length > (sizeOfUnsignedLong - startIndex)){
        printf("Error: The length of the binary fragment cannot be greater than %d for a starting index of %d.\n", sizeOfUnsignedLong - startIndex, startIndex);
        exit(1);
    }

    /*Code to execute if no errors occur:*/
    number = number << startIndex >> (sizeOfUnsignedLong - length);
    return number;
}
