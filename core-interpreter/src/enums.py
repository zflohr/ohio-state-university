from enum import Enum

class Token(Enum):
    """An enumeration for the tokens of the Core language."""
    PROGRAM = 1
    BEGIN = 2
    END = 3
    INT = 4
    IF = 5
    THEN = 6
    ELSE = 7
    WHILE = 8
    LOOP = 9
    READ = 10
    WRITE = 11
    SEMICOLON = 12
    COMMA = 13
    ASSIGNMENT = 14
    LOGICAL_NOT = 15
    LEFT_BRACKET = 16
    RIGHT_BRACKET = 17
    LOGICAL_AND = 18
    LOGICAL_OR = 19
    LEFT_PARENTHESIS = 20
    RIGHT_PARENTHESIS = 21
    ADDITION = 22
    SUBTRACTION = 23
    MULTIPLICATION = 24
    NOT_EQUAL = 25
    EQUAL = 26
    LESS_THAN = 27
    GREATER_THAN = 28
    LESS_THAN_OR_EQUAL = 29
    GREATER_THAN_OR_EQUAL = 30
    INTEGER = 31
    IDENTIFIER = 32

class StopToken(Enum):
    """An enumeration for events that stop Core tokenization."""
    EOF = 33
    ILLEGAL = 34
