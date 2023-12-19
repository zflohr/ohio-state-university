# Core Interpreter

## Description

This is a top-level directory containing an interpreter for the Core 
programming language - a simple, imperative, dynamically typed language 
created for the course CSE 5341 "Principles of Programming Languages." The 
Core interpreter is written in Python, and it therefore runs on the Python 
interpreter. The Core interpreter involves four stages: tokenization, parsing, 
pretty-printing, and execution. During parsing, an abstract parse tree is
created by a recursive descent process and is encapsulated in an instance of 
the Prog class of the [bnf_grammar](src/bnf_grammar.py) module.

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

## Deterministic Finite Automaton (DFA)

![DFA key page 1](docs/diagrams/dfa_page_1.png)
![DFA key page 2](docs/diagrams/dfa_page_2.png)
![DFA diagram](docs/diagrams/dfa_page_3.png)
