lab2: lab2main.o bit_op.o
	gcc -ansi -pedantic -g -o lab2 lab2main.o bit_op.o

lab2main.o: lab2main.c
	gcc -ansi -pedantic -g -c lab2main.c

bit_op.o: bit_op.c
	gcc -ansi -pedantic -g -c bit_op.c

clean:
	rm *.o *.c *.h Makefile lab2
