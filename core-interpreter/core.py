"""This module provides the tokenizer for the Core interpreter.

Each instance of the Tokenizer class tokenizes a file whose path is 
passed as an argument to the class constructor expression. A new line 
of the file is read in each call to the private instance method 
_tokenize_line(), which stores the line's tokens as integer 
representations in a private instance list that gets emptied at the 
start of the method. The public instance methods of the Tokenizer class 
provide an API for the Core interpreter's parser in the bnf_grammar 
module.

The following are the legal tokens of Core:

    Reserved words:
        program, begin, end, int, if, then, 
        else, while, loop, read, write

    Special symbols:
        ; , = ! [ ] && || ( ) + - * != == < > <= >=

    All unsigned integers

    Identifiers:
        The first character must be a capital letter of the English 
        alphabet. Any number of decimal digits and/or capital letters 
        may follow thereafter in any order.
        A regular expression in PCRE2 syntax: [A-Z]([A-Z] | \d)*

    White space:
        White space is required between any pair of tokens unless one 
        or both of them are special symbols, in which case white space 
        is optional. White space is not a regular token.
"""

import enums

RESERVED = {
    'PROGRAM': 'program', 
    'BEGIN': 'begin', 
    'END': 'end', 
    'INT': 'int',
    'IF': 'if', 
    'THEN': 'then', 
    'ELSE': 'else', 
    'WHILE': 'while', 
    'LOOP': 'loop', 
    'READ': 'read', 
    'WRITE': 'write'
}
SPECIAL = {
    'SEMICOLON': ';', 
    'COMMA': ',', 
    'ASSIGNMENT': '=', 
    'LOGICAL_NOT': '!', 
    'LEFT_BRACKET': '[', 
    'RIGHT_BRACKET': ']', 
    'LOGICAL_AND': '&&', 
    'LOGICAL_OR': '||',
    'LEFT_PARENTHESIS': '(', 
    'RIGHT_PARENTHESIS': ')', 
    'ADDITION': '+', 
    'SUBTRACTION': '-', 
    'MULTIPLICATION': '*', 
    'NOT_EQUAL': '!=', 
    'EQUAL': '==', 
    'LESS_THAN': '<', 
    'GREATER_THAN': '>',
    'LESS_THAN_OR_EQUAL': '<=', 
    'GREATER_THAN_OR_EQUAL': '>='
}
WHITE_SPACE = [' ', '\t', '\r', '\n']
DECIMAL_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
SPECIAL_INTERMEDIATE_STATES = ['&', '|']
SPECIAL_AMBIGUOUS_FINAL_STATES = ['=', '!', '<', '>']
CAPITALS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

class Tokenizer:
    """A tokenizer for the Core programming language.

    Attributes:
        Public instance methods: 
            __init__
            get_token
            skip_token
            int_val
            id_name
            token_type
            get_file_name
            shutdown

        Private instance methods: 
            _illegal_token
            _legal_token
            _token_delimiter
            _end_of_file
            _tokenize_line

        Public instance variables:
            line_number: An integer representing the number of the 
                line of the input file used to create _stream that is 
                currently being tokenized.

        Private instance variables:
            _stream: An instance of io.TextIOWrapper that provides
                high-level access to an io.BufferedIOBase buffered
                binary stream.
            _error_message: a string containing a message to go to
                stderr during exception raising.
            _token: a string of characters defined in _tokenize_line()
                and appended to during line-scanning; the string gets
                emptied when the deterministic finite automaton (DFA)
                returns to a starting state. 
            _tokens: a list of integers in the interval [1,34] that each
                correspond to a Core token identified during
                line-scanning with the exception of 33 and 34, which
                correspond to an illegal token and end-of-file,
                respectively.
            _integers: a dict whose keys are indices of integers in
                _tokens that correspond to Core integer tokens
                identified during line-scanning and whose values are the
                string representations of the Core integer tokens.
            _identifiers: a dict whose keys are indices of integers in
                _tokens that correspond to Core identifier tokens
                identified during line-scanning and whose values are the
                Core identifier tokens.
            _token_index: an integer defined in _tokenize_line() that
                represents the current index of _tokens for retrieving
                and printing values therein. The index is either
                incremented or zeroed after calls to skip_token().
    """

    def __init__(self, filename: str) -> None:
        """Initialize the instance based on a file to be tokenized.

        Create a text stream for reading from filename, initialize
        private instance attributes, and call the private method
        _tokenize_line() to tokenize the first line of filename.

        Args:
            filename: The name of a file for the instance to tokenize.
        """
        self._stream = open(filename, 'r') 
        self.line_number = 0 
        self._error_message = ''
        self._tokens = [] 
        self._integers, self._identifiers = {}, {}
        self._tokenize_line()
    
    def _illegal_token(self) -> None:
        """Execute a routine in response to an illegal Core token.

        Append the enumeration corresponding to the illegal Core token
        stored in self._token to self._tokens, and prepare an error
        message for program termination.
        """
        self._error_message = ("Error! File \"{file_name}\", line "
                               "{line_number}: Illegal token starting with "
                               "\"{illegal_token}\"."
                               .format(file_name = self._stream.name,
                                       line_number = self.line_number, 
                                       illegal_token = self._token))
        self._tokens += [enums.StopToken.ILLEGAL.value]

    def _legal_token(self, token_type: str) -> None:
        """Execute a routine in response to a legal Core token.

        Append the enumeration corresponding to the Core token stored in
        self._token to self._tokens. If self._token is an identifier or
        a string representation of an integer, store it as the value of
        a key that is the index of the integer that just got appended to
        self._tokens in self._identifiers or self._integers,
        respectively. Reset Boolean flags and self._token to bring the
        DFA back to a starting state. 

        Args:
            token_type: The type of token stored in self._token. Allowed
                values are 'reserved', 'special', 'integer', and
                'identifier'.
        """
        self._is_reserved = self._is_special = False
        self._is_integer = self._is_identifier = False
        if token_type == 'reserved': 
            self._tokens += [
                enums.Token[
                    list(RESERVED.keys())[
                        list(RESERVED.values()).index(self._token)]].value]
        if token_type == 'special':
            self._tokens += [
                enums.Token[
                    list(SPECIAL.keys())[
                        list(SPECIAL.values()).index(self._token)]].value]
        if token_type == 'integer':
            self._tokens += [enums.Token.INTEGER.value]
            self._integers[len(self._tokens) - 1] = self._token
        if token_type == 'identifier':
            self._tokens += [enums.Token.IDENTIFIER.value]
            self._identifiers[len(self._tokens) - 1] = self._token
        self._token = '' 

    def _token_delimiter(self, token_type: str) -> None:
        """Determine if the current token is legally delimited.

        If the current token in self._token is delimited by white space
        or a special symbol, or if the end of the file has been reached,
        then call _legal_token().

        Args:
            token_type: The type of token stored in self._token. Allowed
                values are 'reserved', 'special', 'integer', and
                'identifier'.
        """
        if self._end_of_line:
            self._legal_token(token_type)
        else:
            if self._next_char in WHITE_SPACE:
                self._legal_token(token_type)
            if (self._next_char 
                    in set([symbol[0] for symbol in list(SPECIAL.values())])):
                if self._next_char not in SPECIAL_INTERMEDIATE_STATES:
                    self._legal_token(token_type)
                else:
                    if self._char_index + 2 < len(self._line):
                        if self._next_char == self._line[self._char_index + 2]:
                            self._legal_token(token_type)

    def _end_of_file(self) -> None:
        """Execute a routine in response to reaching end of file.

        Append the enumeration corresponding to EOF to self._tokens,
        close the file object, and set a Boolean flag to prevent
        recursion in _tokenize_line().
        """
        self._tokens += [enums.StopToken.EOF.value]
        self._stream.close()
        self._eof = True

    def _tokenize_line(self) -> None:
        """Tokenize a line from the text stream.

        Begin this method by setting Boolean flags and emptying
        self._token to bring the DFA to a starting state. Read a line
        from the text stream, and loop over each character in the line.
        When the DFA is at a starting state, compare the character of
        the current iteration of the for-loop to characters stored in
        global constants to determine the type of token that could start
        with that character; if the character is whitespace, then skip
        to the next iteration. Bring the DFA out of a starting state by
        toggling a Boolean flag, which indicates the token type for
        successive iterations until the DFA is reset to a starting
        state. Concatenate the current character to self._token in each
        iteration of the for-loop unless the DFA is at a starting state
        and the character is whitespace, and perform one-character
        lookaheads if self._token is an identifier, integer, or certain
        special symbol to force greedy tokenization. Call
        _token_delimiter(), _illegal_token(), _legal_token(), and/or
        _end_of_file() based on results of one-character lookaheads
        and/or comparisons to global constants. Return the DFA to a
        starting state after each call to _legal_token(). Recurse if the
        current line of the text stream contains only whitespace
        characters.
        """
        del self._tokens[:]
        self._integers, self._identifiers = {}, {}
        self._token_index = 0
        self._token = ''
        is_line_all_white = special_final_state = True
        self._eof = self._end_of_line = False
        self._is_reserved = self._is_special = False
        self._is_integer = self._is_identifier = False
        self._line = self._stream.readline()
        self.line_number += 1
        if not self._line:
            self._end_of_file()
        for self._char_index, char in enumerate(self._line):
            if self._char_index == len(self._line) - 1:
                self._end_of_line = True
            else:
                self._next_char = self._line[self._char_index + 1]
            if not self._token:
                if char in WHITE_SPACE:
                    continue
                if char in set([word[0] for word in list(RESERVED.values())]):
                    self._is_reserved = True
                if char in set(
                        [symbol[0] for symbol in list(SPECIAL.values())]):
                    self._is_special = True
                if char in DECIMAL_DIGITS:
                    self._is_integer = True
                if char in CAPITALS:
                    self._is_identifier = True
            self._token += char
            is_line_all_white = False
            if self._is_reserved:
                if any(self._token == word[:len(self._token)] 
                           for word in list(RESERVED.values())):
                    if any(self._token == word 
                               for word in list(RESERVED.values())):
                        self._token_delimiter('reserved')
                    if self._end_of_line:
                        self._is_reserved = False
                else:
                    self._is_reserved = False
            if self._is_special:
                if not special_final_state:
                    self._legal_token('special')
                    special_final_state = True
                else:
                    if self._token in SPECIAL_INTERMEDIATE_STATES:
                        if not self._end_of_line:
                            if self._token == self._next_char:
                                special_final_state = False
                            else:
                                self._token += self._next_char
                                self._is_special = False
                                special_final_state = False
                        else:
                            self._is_special = False
                            special_final_state = False
                    if self._token in SPECIAL_AMBIGUOUS_FINAL_STATES:
                        if not self._end_of_line:
                            if self._next_char == '=':
                                special_final_state = False
                    if special_final_state:
                        self._legal_token('special')
            if self._is_integer:
                if not self._end_of_line:
                    if self._next_char in DECIMAL_DIGITS:
                        continue
                self._token_delimiter('integer')
                if self._is_integer:
                    self._token += self._next_char
                    self._is_integer = False
            if self._is_identifier:
                if not self._end_of_line:
                    if self._next_char in DECIMAL_DIGITS + CAPITALS:
                        continue
                self._token_delimiter('identifier')
                if self._is_identifier:
                    self._token += self._next_char
                    self._is_identifier = False
            if (self._token and self._is_reserved is self._is_special 
                    is self._is_integer is self._is_identifier):
                self._illegal_token()
                break
        if not self._eof and is_line_all_white:
            self._tokenize_line()

    def get_token(self) -> int:
        """Return the token at the current token index.

        Returns:
            The integer in self._tokens at self._token_index.

        Raises:
            SystemExit: The current integer in self._tokens corresponds 
                to an illegal token. Print a message to stderr, and 
                exit the Python interpreter.
        """
        token = self._tokens[self._token_index]
        if token == enums.StopToken.ILLEGAL.value:
            self._stream.close()
            raise SystemExit(self._error_message)
        return token

    def skip_token(self) -> None:
        """Increment the token index, or call _tokenize_line()."""
        if self._token_index < len(self._tokens) - 1:
            self._token_index += 1
        else:
            self._tokenize_line()

    def int_val(self) -> int:
        """Return the source integer of the current token index.

        Returns: 
            The integer whose string representation in the text stream
            corresponds to the integer at the current index of
            self._tokens. 

        Raises:
            SystemExit: The integer at the current index of
                self._tokens does not correspond to an integer token.
                Print a message to stderr, and exit the Python
                interpreter.
        """
        try:
            string_int = self._integers[self._token_index]
            return int(string_int)
        except KeyError:
            self._stream.close()
            raise SystemExit('Error! The current token is not an integer!')

    def id_name(self) -> str:
        """Return the source identifier of the current token index.

        Returns:
            The identifier from the text stream that corresponds to the
            integer at the current index of self._tokens.
        
        Raises:
            SystemExit: The integer at the current index of
                self._tokens does not correspond to an identifier token.
                Print a message to stderr, and exit the Python
                interpreter.
        """
        try:
            return self._identifiers[self._token_index]
        except KeyError:
            self._stream.close()
            raise SystemExit('Error! The current token is not an identifier!')

    def token_type(self) -> str:
        """Return the type of token at the current token index.

        Returns:
           The type of Core token represented by the integer in
           self._tokens at self._token_index. 

        """
        if self._tokens[self._token_index] == 31:
            return 'integer'
        if self._tokens[self._token_index] == 32:
            return 'identifier'
        if self._tokens[self._token_index] == 33:
            return 'eof'
        if (enums.Token(self._tokens[self._token_index]).name 
                in list(RESERVED.keys())):
            return 'reserved word'
        if (enums.Token(self._tokens[self._token_index]).name 
                in list(SPECIAL.keys())):
            return 'special symbol'

    def get_file_name(self) -> str:
        """Return the name of the file being tokenized."""
        return self._stream.name
    
    def shutdown(self) -> None:
        """Close the file stream."""
        self._stream.close()
