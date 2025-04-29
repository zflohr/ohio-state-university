lab1: lab1.o lab1_func.o
	gcc -ansi -pedantic -g -o lab1 lab1.o lab1_func.o

lab1.o: lab1.c
	gcc -ansi -pedantic -g -c lab1.c

lab1_func.o: lab1_func.c
	gcc -ansi -pedantic -g -c lab1_func.c

clean:
	rm *.o lab1
