# Core Interpreter

## Description

This is a top-level directory containing an interpreter for the Core 
programming language - a simple, imperative, dynamically typed language 
created for the course CSE 5341 "Principles of Programming Languages." The 
Core interpreter is written in Python, and it therefore runs on the Python 
interpreter. The Core interpreter involves four stages: tokenization, parsing, 
printing, and execution. During parsing, an abstract parse tree is
created by a recursive descent process and is encapsulated in an instance of 
the Prog class of the [bnf_grammar](src/bnf_grammar.py) module. During printing,
the parsed Core program is pretty-printed to standard output.

## Instructions

Requires Python 3.10 or higher.  

Keep all [source files](src) in the same directory.

The [script](src/interpret.py) must be executed from the command line. It
requires the following positional arguments:
  1. *program* - The path of the file containing the Core program to be
                 interpreted.
  2. *data* - The path of the file containing input data for `read` statements 
              in the Core program. This file must contain only integers, and 
              each integer must be on a separate line. This file must not
              contain empty lines. If the Core interpreter executes a `read` 
              statement, it will consume as many integers from the data file as
              there are identifiers in the `read` statement.  

Example programs and data can be found [here](example-input). To run the first
example program with example data as input, run the following command from
the src/ directory:  

          python3 interpret.py ../example-input/program_1.core ../example-input/data.txt

## BNF Grammar for Core

\<prog> ::= program \<decl seq> begin \<stmt seq> end  
\<decl seq> ::= \<decl> | \<decl> \<decl seq>  
\<stmt seq> ::= \<stmt> | \<stmt> \<stmt seq>  
\<decl> ::= int \<id list>;  
\<id list> ::= \<id> | \<id>, \<id list>  
\<stmt> ::= \<assign> | \<if> | \<loop> | \<in> | \<out>  
\<assign> ::= \<id> = \<exp>;  
\<if> ::= if \<cond> then \<stmt seq> end; | if \<cond> then \<stmt seq> else 
\<stmt seq> end;  
\<loop> ::= while \<cond> loop \<stmt seq> end;  
\<in> ::= read \<id list>;  
\<out> ::= write \<id list>;  
\<cond> ::= \<comp> | !\<cond> | [\<cond> && \<cond>] | [\<cond> || \<cond>]  
\<comp> ::= (\<op> \<comp op> \<op>)  
\<exp> ::= \<fac> | \<fac> + \<exp> | \<fac> - \<exp>  
\<fac> ::= \<op> | \<op> * \<fac>  
\<op> ::= \<int> | \<id> | (\<exp>)  
\<comp op> ::= != | == | < | > | <= | >=  
\<id> ::= \[A-Z]([A-Z] | \d)\* (a regular expression in PCRE2 syntax)  
\<int> ::= \d+ (a regular expression in PCRE2 syntax)  

## Tokens of Core

### Reserved words:  
`program, begin, end, int, if, then, else, while, loop, read, write`

### Special Symbols:
`; , = ! [ ] && || ( ) + - * != == < > <= >=`

### Integers:
All unsigned integers are legal.  

A regular expression in PCRE2 syntax for a Core integer: `\d+`

### Identifiers:
The first character must be a capital letter of the English alphabet. Any 
number of decimal digits and/or capital letters may follow thereafter in any 
order.  

A regular expression in PCRE2 syntax for a Core identifier: `[A-Z]([A-Z] | \d)*`

### White Space:
White space is required between any pair of tokens unless one or both of them 
are special symbols, in which case white space is optional. White space is not 
a regular token.

## Deterministic Finite Automaton (DFA)

![DFA key page 1](docs/diagrams/dfa_page_1.png)
![DFA key page 2](docs/diagrams/dfa_page_2.png)
![DFA diagram](docs/diagrams/dfa_page_3.png)
