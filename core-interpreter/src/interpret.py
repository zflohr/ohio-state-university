"""This script provides the entry point to the Core interpreter.

usage: interpret.py [-h] program data

positional arguments:
    program     the path of the file containing the Core program to be
                interpreted

    data        the path of the file containing data for "read" 
                instructions in the Core program

options:
    -h, --help  show this help message, and exit
"""

import argparse

import bnf_grammar
import core

def main():
    """Interpret a Core program.

    Retrieve the paths of a Core file and data file from command line 
    arguments passed to this script; instantiate the Tokenizer class of 
    the core module; and tokenize, parse, print, and execute the Core 
    program.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('program', 
                        help = 'the path of the file containing the Core '
                               'program to be interpreted')
    parser.add_argument('data', 
                        help = 'the path of the file containing data for '
                               '"read" instructions in the Core program')
    args = parser.parse_args()
    global tokenizer 
    tokenizer = core.Tokenizer(args.program)
    program = bnf_grammar.Prog()
    program.parse()
    program.print()
    data = open(args.data, 'r')
    program.execute(data)
    data.close()

if __name__ == '__main__':
    main()
