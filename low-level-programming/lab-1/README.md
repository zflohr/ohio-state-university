# Lab 1: Introduction to GCC, GDB, Make, and stdio.h

The purpose of this lab was to become familiar with the GNU project C and C++
compiler (GCC), the GNU debugger (GDB), GNU Make, and makefiles.
[lab1.c](lab1.c), [lab1_func.c](lab1_func.c), and
[local_file.h](local_file.h) were provided by the course instructor. The C
source code was passed as operands to `gcc` to create an executable file with
embedded debugging information, which ran a program that used functions of the
`stdio.h` header file of the C standard library to print a description of the
program to stdout, to read characters from stdin, and to print the characters
on separate lines to stdout. The important functions involved are `printf()`,
`getchar()`, and `putchar()`.

`gdb` was used to set breakpoints at lines containing `getchar()` and to inspect
return values of `getchar()` after executing the lines.
[gdb_screenshot_1.png](gdb_screenshot_1.png),
[gdb_screenshot_2.png](gdb_screenshot_2.png), and
[gdb_screenshot_3.png](gdb_screenshot_3.png) show my use of the GNU debugger.
The [makefile](Makefile) contains rules for recompiling the C source files and
relinking object files to update the executable file when the C source files
change.
