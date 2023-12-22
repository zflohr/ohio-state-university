"""This module provides the procedures of the Core interpreter.

Each class defined herein encapsulates the production of a nonterminal 
of the Core BNF grammar. The class names are the names of the 
nonterminals. Every class has "parse" and "print" methods. Every class 
except DeclSeq, Decl, Id, Int, and CompOp also has an "execute" or 
"evaluate" method. The combination of these methods enables the three 
distinct stages of the Core interpreter: parsing, printing, and 
execution. During parsing, each "parse" method instantiates classes 
that represent the nonterminals that appear in the production that is 
encapsulated by the class whose "parse" method is being invoked. The 
"parse" method then invokes the "parse" methods of the class instances 
it creates. This approach enables recursive descent parsing of an 
abstract parse tree (APT) that is wholly encapsulated in an instance of 
the Prog class. Consequently, the classes herein are not intended to be 
exported individually. The "print" and "execute/evaluate" methods use 
the parse tree to pretty-print and execute the Core program, 
respectively.
"""

import sys
from typing import NoReturn, TextIO

import __main__

def context_free_error_checker(expected_token_number: int = 0,
                               expected_token_type: str = 'multiple') -> None:
    """Determine if the current token violates the Core BNF grammar.

    Determine if a context-free error exists in the Core program by 
    comparing the current token in the token stream with the expected 
    token as determined by the production of the current nonterminal in 
    the APT. If the current token is the expected token, then increment 
    the index of the token stream. Otherwise, shut down the tokenizer 
    and terminate the Core interpreter.

    Args:
        expected_token_number: The integer representing a Core token 
            whose existence at the current index of the token stream 
            would maintain adherence to the BNF grammar. It is 
            determined by the current nonterminal in the APT.
        expected_token_type: The type of the token corresponding to
            expected_token_number. Allowed values are "reserved word", 
            "special symbol", "integer", "identifier", "multiple", and 
            "eof".

    Raises:
        SystemExit: The current token in the token stream is not the 
            expected token. Print a message to stderr, and exit the 
            Python interpreter.
    """
    token_number = __main__.tokenizer.get_token()
    if token_number != expected_token_number:
        token_type = __main__.tokenizer.token_type()
        line_number = __main__.tokenizer.line_number
        if token_type == 'reserved word':
            token = __main__.core.RESERVED[
                __main__.core.enums.Token(token_number).name]
        if token_type == 'special symbol':
            token = __main__.core.SPECIAL[
                __main__.core.enums.Token(token_number).name]
        if token_type == 'integer':
            token = __main__.tokenizer.int_val()
        if token_type == 'identifier':
            token = __main__.tokenizer.id_name()
        if (expected_token_type 
                in ['reserved word', 'special symbol', 'multiple', 'eof']):
            if token_type == 'eof':
                error_message = ("Error! Unexpected end of file \"{0}\"."
                                 .format(__main__.tokenizer.get_file_name()))
            else:
                error_message = ("Error! File \"{0}\", line {1}: unexpected "
                                 "{2} \"{3}\"."
                                 .format(__main__.tokenizer.get_file_name(),
                                         line_number, token_type, token))
        if expected_token_type == 'identifier':
            if token_type == 'eof':
                error_message = ("Error! Unexpected end of file \"{0}\". "
                                 "Expected an identifier."
                                 .format(__main__.tokenizer.get_file_name()))
            else:
                error_message = ("Error! File \"{0}\", line {1}: unexpected "
                                 "{2} \"{3}\". Expected an identifier."
                                 .format(__main__.tokenizer.get_file_name(),
                                         line_number, token_type, token))
        if expected_token_type == 'integer':
            if token_type == 'eof':
                error_message = ("Error! Unexpected end of file \"{0}\". "
                                 "Expected an integer."
                                 .format(__main__.tokenizer.get_file_name()))
            else:
                error_message = ("Error! File \"{0}\", line {1}: unexpected "
                                 "{2} \"{3}\". Expected an integer."
                                 .format(__main__.tokenizer.get_file_name(),
                                         line_number, token_type, token))
        __main__.tokenizer.shutdown()
        sys.exit(error_message)
    else:
        if (expected_token_type 
                in ['reserved word', 'special symbol', 'integer']):
            __main__.tokenizer.skip_token()

def runtime_error(data: TextIO, error_cause: str, invalid_line: int | str = '',
                  name: str = '') -> NoReturn:
    """Terminate the Core interpreter in response to runtime errors.

    Prepare an error message based on the cause of the runtime error 
    that resulted in a call to this function during execution of the 
    Core program, and terminate the Core interpreter.

    Args:
        data: An instance of io.TextIOWrapper that provides high-level 
            access to the buffered binary stream containing input data 
            for "read" statements in the Core program.
        error_cause: The cause of the runtime error that resulted in a 
            call to this function.
        invalid_line: A line number or contents of a line to reference 
            in a message printed to stderr.
        name: The name of an identifier to reference in a message 
            printed to stderr.

    Raises:
        SystemExit: Print a message to stderr, and exit the Python 
            interpreter.
    """
    data.close()
    if error_cause == 'input eof':
        sys.exit("Runtime error! End of data file \"{0}\" has been "
                              "reached!".format(data.name))
    if error_cause == 'input empty line':
        sys.exit("Runtime error! Data file \"{0}\" cannot contain "
                              "empty lines!".format(data.name))
    if error_cause == 'input invalid line':
        sys.exit("Runtime error! Invalid line in data file \"{0}\":"
                              " \"{1}\"".format(data.name, invalid_line[:-1]))
    if error_cause == 'uninitialized identifier':
        sys.exit("Runtime error! File \"{0}\", line {1}: identifier"
                              " \"{2}\" has not been initialized!"
                              .format(__main__.tokenizer.get_file_name(),
                                      invalid_line, name))

class Prog:
    """Encapsulation of the production for the <prog> nonterminal.

    BNF grammar:
        <prog> ::= program <decl seq> begin <stmt seq> end

    Attributes:
        Public instance methods:
            parse
            print
            execute
    """

    decl_seq_path = True
    pretty_print_indent = ' ' * 2

    def parse(self) -> None:
        """Construct the children of the root of the APT.

        Construct the nodes corresponding to <decl seq> and <stmt seq>
        nonterminals, and initiate construction of the next level of 
        the APT by calling the parse() methods of the class instances 
        representing the nodes at the current level. Call 
        context_free_error_checker() to ensure that the terminals that 
        appear in the production of <prog> exist at the proper 
        locations in the token stream.
        """
        context_free_error_checker(__main__.core.enums.Token['PROGRAM'].value,
                                   'reserved word')
        self._decl_seq = DeclSeq()
        self._decl_seq.parse()
        Prog.decl_seq_path = False 
        context_free_error_checker(__main__.core.enums.Token['BEGIN'].value,
                                   'reserved word')
        self._stmt_seq = StmtSeq(indent_level = 1)
        self._stmt_seq.parse()
        context_free_error_checker(__main__.core.enums.Token['END'].value,
                                   'reserved word')
        context_free_error_checker(__main__.core.enums.StopToken['EOF'].value,
                                   'eof')

    def print(self) -> None:
        """Print the production of the <prog> nonterminal to stdout.

        Print the terminals in the production of <prog>, calling print()
        methods of the class instances representing the nonterminals of 
        the current level that were constructed during parsing to 
        initiate printing at the next level of the APT.
        """
        print('program')
        self._decl_seq.print()
        print('begin')
        self._stmt_seq.print()
        print('end')

    def execute(self, data: TextIO) -> None:
        """Execute the <stmt seq> nonterminal in the <prog> production.

        Call the execute() method of the class instance representing the
        <stmt seq> nonterminal that was constructed during parsing to 
        initiate execution of the Core program at the next level of the 
        <stmt seq> branch of the APT.
        """
        self._stmt_seq.execute(data)

class DeclSeq:
    """Encapsulation of the production for the <decl seq> nonterminal.

    BNF grammar:
        <decl seq> ::= <decl> | <decl> <decl seq>

    Attributes:
        Public instance methods:
            __init__
            parse
            print
    """

    def __init__(self) -> None:
        self._decl_seq = None

    def parse(self) -> None:
        """Construct the children of a <decl seq> node in the APT.

        Unconditionally construct a node corresponding to the <decl> 
        nonterminal, which appears in both alternators in the production
        of <decl seq>. Conditionally construct a node corresponding to 
        the <decl seq> nonterminal, which only appears in one alternator
        in the production of <decl seq>. Call the parse() methods of 
        the class instances representing the nodes to initiate 
        construction of the next level of the APT.
        """
        self._decl = Decl() 
        self._decl.parse()
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['INT'].value:
            self._decl_seq = DeclSeq()
            self._decl_seq.parse()

    def print(self) -> None:
        """Print the parsed alternator of <decl seq> to stdout.

        Call print() methods of the class instances representing the 
        nodes at the current level that were constructed during parsing 
        to initiate printing at the next level of the APT.
        """
        print(Prog.pretty_print_indent, end = '')
        self._decl.print()
        if self._decl_seq:
            self._decl_seq.print()

class Decl:
    """Encapsulation of the production for the <decl> nonterminal.

    BNF grammar:
        <decl> ::= int <id list>;

    Attributes:
        Public instance methods:
            parse
            print
    """

    def parse(self) -> None:
        """Construct the children of a <decl> node in the APT.

        Construct a node corresponding to the <id list> nonterminal, 
        which appears in the only alternator in the production of 
        <decl>. Call the parse() method of the class instance 
        representing the node to initiate construction of the next 
        level of the APT. Call context_free_error_checker() to ensure 
        that the terminals that appear in the production of <decl> 
        exist at the proper locations in the token stream.
        """
        context_free_error_checker(__main__.core.enums.Token['INT'].value,
                                   'reserved word')
        self._id_list = IdList()
        self._id_list.parse()
        context_free_error_checker(
            __main__.core.enums.Token['SEMICOLON'].value, 'special symbol')

    def print(self) -> None:
        """Print the production of the <decl> nonterminal to stdout.

        Print the terminals in the production of <decl>, calling the 
        print() method of the class instance representing the 
        nonterminal at the current level that was constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        print('int ', end = '')
        self._id_list.print()
        print(';')

class IdList:
    """Encapsulation of the production for the <id list> nonterminal.

    BNF grammar:
        <id list> ::= <id> | <id>, <id list>

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            execute
    """

    _is_output = False

    def __init__(self, line_number: int | None  = None) -> None:
        self._id_list = None
        self._line = line_number

    def parse(self) -> None:
        """Construct the children of an <id list> node in the APT.

        Conditionally construct a node corresponding to the <id list> 
        nonterminal, which only appears in one alternator in the 
        production of <id list>. Call the static parse() method of the
        Id class and the parse() method of the class instance 
        representing an <id list> node (if it was created) to initiate 
        construction of the next level of the APT.
        """
        self._id = Id.parse()
        self._id.line[self._line] = __main__.tokenizer.line_number
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['COMMA'].value:
            __main__.tokenizer.skip_token()
            self._id_list = IdList(self._line)
            self._id_list.parse()

    def print(self) -> None:
        """Print the parsed alternator of <id list> to stdout.

        Print the terminals in the parsed alternator of <id list>, 
        calling the print() methods of the class instances representing 
        the nonterminals at the current level that were constructed 
        during parsing to initiate printing at the next level of the 
        APT.
        """
        self._id.print()
        if self._id_list:
            print(', ', end = '')
            self._id_list.print()

    def execute(self, data: TextIO, is_input: bool, line_number: int) -> None:
        """Execute an <id list> nonterminal in a <stmt seq> branch.

        Perform input/output operations based on whether the caller is
        encapsulated in an instance of the In or Out class. If the 
        caller is a member of In, then read a line from the data 
        stream, convert the string representation of the integer in the 
        line to an int object, and pass the int to the set_value() 
        method of the Id object that was returned during parsing of the 
        current node. Call the modular runtime_error() method if the 
        current line in the data stream is the end of the file or empty 
        or it contains string representations of non-integers. If the 
        caller is a member of Out, then print the name and value of the 
        Id object that was returned during parsing to stdout. If a 
        class instance representing the <id list> nonterminal was 
        constructed during parsing, then call its execute() method to 
        initiate execution of the Core program at the next level of the 
        current <stmt seq> branch of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            is_input: A value of True indicates the caller is a member 
                of an In object; False indicates the caller is a member 
                of an Out object.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this IdList instance appears in the 
                Core program.
        """
        if is_input:
            line = data.readline()
            if not line:
                runtime_error(data, 'input eof')
            if line == '\n':
                runtime_error(data, 'input empty line')
            try:
                value = int(line)
            except ValueError:
                runtime_error(data, 'input invalid line', line)
            self._id.set_value(value)
        else:
            if not IdList._is_output:
                IdList._is_output = True
                print('\n----------Program Output----------')
            value = self._id.get_value(data, line_number)
            name = self._id.get_name()
            print(name,'=',value)
        if self._id_list:
            self._id_list.execute(data, is_input, line_number)

class Id:
    """Encapsulation of the production for the <id> nonterminal.

    BNF grammar:
        <id> ::= [A-Z]([A-Z] | \d)* (a regular expression in PCRE2 syntax)

    Attributes:
        Public instance methods:
            __init__
            print
            set_value
            get_value
            get_name

        Public static methods:
            parse

        Private static methods:
            _context_sensitive_error
    """

    _declared_ids = []

    def __init__(self, name: str) -> None:
        self._name = name
        self._initialized = False
        self.line = {}

    @staticmethod
    def parse() -> 'Id':
        """Return an Id object representing an <id> node in the APT.

        Compare the name of the current identifier in the token stream 
        with the value of the _name attribute of the Id instances in 
        Id._declared_ids. If no match is found and this function is 
        called during parsing of a <decl seq> branch, then instantiate 
        the Id class, append the instance with the new name to 
        Id._declared_ids, and return the instance. If a match is found 
        and this function is called during parsing of a <stmt seq> 
        branch, then return the matched Id instance. If a match is 
        found and this function is called during parsing of a 
        <decl seq> branch or no match is found and this function is 
        called during parsing of a <stmt seq> branch, then call the 
        static _context_sensitive_error() method of the Id class to 
        raise an exception.

        Returns:
            A reference to an Id instance stored in a private class 
            attribute of the Id class.
        """
        context_free_error_checker(
            __main__.core.enums.Token['IDENTIFIER'].value, 'identifier')
        id_name = __main__.tokenizer.id_name()
        if Prog.decl_seq_path:
            if (id_name not in 
                    [declared_id._name for declared_id in Id._declared_ids]):
                Id._declared_ids += [Id(id_name)]
                __main__.tokenizer.skip_token()
                return Id._declared_ids[-1]
        else:
            for declared_id in Id._declared_ids:
                if id_name == declared_id._name:
                    __main__.tokenizer.skip_token()
                    return declared_id
        Id._context_sensitive_error(id_name)

    def print(self) -> None:
        """Print the name of this Id instance to stdout."""
        print(self._name, end = '')

    def set_value(self, value: int) -> None:
        """Associate a value with this Id instance.

        Args:
            value: The value to associate with this Id instance.
        """
        if not self._initialized:
            self._initialized = True
        self._value = value

    def get_value(self, data: TextIO, line_number: int) -> int:
        """Return the value of this Id instance.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose execute() method resulted in a 
                call to this method of this Id instance appears in the 
                Core program.

        Returns:
            The value associated with this Id instance.
        """
        if self._initialized:
            return self._value
        else:
            runtime_error(data, 'uninitialized identifier', 
                          self.line[line_number], self._name)

    def get_name(self) -> str:
        """Return the name of this Id instance.

        Returns:
            The name that was given to this Id instance during parsing 
            of a <decl seq> node in the APT.
        """
        return self._name

    @staticmethod 
    def _context_sensitive_error(id_name: str) -> NoReturn:
        """Terminate the program because of context-sensitive errors.

        Prepare an error message based on whether the Core interpreter 
        is currently parsing a <decl seq> or a <stmt seq> branch, and 
        terminate.

        Args:
            id_name: The name of an identifier that has been doubly 
                declared in a <decl seq> branch or an identifier that 
                appears in a <stmt seq> branch but not in any 
                <decl seq> branch.

        Raises:
            SystemExit: Print a message to stderr, and exit the Python 
                interpreter.
        """
        if Prog.decl_seq_path:
            adverb = 'already'
        else:
            adverb = 'not'
        __main__.tokenizer.shutdown()
        sys.exit("Error! File \"{0}\", line {1}: identifier \"{2}\" "
                              "has {3} been declared!"
                              .format(__main__.tokenizer.get_file_name(),
                                      __main__.tokenizer.line_number,
                                      id_name, adverb))

class StmtSeq:
    """Encapsulation of the production for the <stmt seq> nonterminal.

    BNF grammar:
        <stmt seq> ::= <stmt> | <stmt> <stmt seq>

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            execute
    """

    def __init__(self, indent_level: int) -> None:
        self._stmt_seq = None
        self._indent_level = indent_level

    def parse(self) -> None:
        """Construct the children of a <stmt seq> node in the APT.

        Unconditionally construct a node corresponding to the <stmt> 
        nonterminal, which appears in both alternators in the production
        of <stmt seq>. Conditionally construct a node corresponding to 
        the <stmt seq> nonterminal, which only appears in one alternator
        in the production of <stmt seq>. Call the parse() methods of 
        the class instances representing the nodes to initiate 
        construction of the next level of the APT.
        """
        self._stmt = Stmt(self._indent_level)
        self._stmt.parse()
        token_number = __main__.tokenizer.get_token()
        if token_number not in [
                __main__.core.enums.Token['END'].value,
                __main__.core.enums.Token['ELSE'].value]:
            self._stmt_seq = StmtSeq(self._indent_level)
            self._stmt_seq.parse()

    def print(self) -> None:
        """Print a parsed alternator of <stmt seq> to stdout.

        Call print() methods of the class instances representing the 
        nodes at the current level that were constructed during parsing 
        to initiate printing at the next level of the APT.
        """
        print(Prog.pretty_print_indent * self._indent_level, end = '')
        self._stmt.print()
        if self._stmt_seq:
            self._stmt_seq.print()

    def execute(self, data: TextIO) -> None:
        """Execute a parsed alternator of the <stmt seq> production.

        Call the execute() methods of the class instances representing 
        the nonterminals in an alternator of the <stmt seq> production 
        that were constructed during parsing to initiate execution of 
        the Core program at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        self._stmt.execute(data)
        if self._stmt_seq:
            self._stmt_seq.execute(data)
        
class Stmt:
    """Encapsulation of the production for the <stmt> nonterminal.

    BNF grammar:
        <stmt> ::= <assign> | <if> | <loop> | <in> | <out>

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            execute
    """

    def __init__(self, indent_level: int) -> None:
        self._assign = None
        self._if = None
        self._loop = None
        self._input = None
        self._output = None
        self._indent_level = indent_level

    def parse(self) -> None:
        """Construct the children of a <stmt> node in the APT.

        Conditionally construct a node based on the current token in 
        the token stream. The node corresponds to a nonterminal that 
        appears in one of the five alternators of the production for 
        the <stmt> nonterminal. Call the parse() method of the class 
        instance representing the node to initiate construction of the 
        next level of the APT. 
        """
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['IDENTIFIER'].value:
            self._assign = Assign()
            self._assign.parse()
        elif token_number == __main__.core.enums.Token['IF'].value:
            self._if = If(self._indent_level)
            self._if.parse()
        elif token_number == __main__.core.enums.Token['WHILE'].value:
            self._loop = Loop(self._indent_level)
            self._loop.parse()
        elif token_number == __main__.core.enums.Token['READ'].value:
            self._input = In()
            self._input.parse()
        elif token_number == __main__.core.enums.Token['WRITE'].value:
            self._output = Out()
            self._output.parse()
        else:
            context_free_error_checker()

    def print(self) -> None:
        """Print an alternator of the <stmt> nonterminal to stdout.

        Call the print() method of the class instance representing the 
        node at the current level that was constructed during parsing 
        to initiate printing at the next level of the APT.
        """
        if self._assign:
            self._assign.print()
        if self._if:
            self._if.print()
        if self._loop:
            self._loop.print()
        if self._input:
            self._input.print()
        if self._output:
            self._output.print()

    def execute(self, data: TextIO) -> None:
        """Execute a parsed alternator of the <stmt> production.

        Call the execute() method of the class instance representing 
        the nonterminal in an alternator of the <stmt> production 
        that was constructed during parsing to initiate execution of 
        the Core program at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        if self._assign:
            self._assign.execute(data)
        if self._if:
            self._if.execute(data)
        if self._loop:
            self._loop.execute(data)
        if self._input:
            self._input.execute(data)
        if self._output:
            self._output.execute(data)

class In:
    """Encapsulation of the production for the <in> nonterminal.

    BNF grammar:
        <in> ::= read <id list>;

    Attributes:
        Public instance methods:
            parse
            print
            execute
    """

    def parse(self) -> None:

        """Construct the children of an <in> node in the APT.

        Construct a node corresponding to the <id list> nonterminal, 
        which appears in the only alternator in the production of 
        <in>. Call the parse() method of the class instance 
        representing the node to initiate construction of the next 
        level of the APT. Call context_free_error_checker() to ensure 
        that the terminals that appear in the production of <in> exist 
        at the proper locations in the token stream.
        """
        self._line = __main__.tokenizer.line_number
        context_free_error_checker(
            __main__.core.enums.Token['READ'].value, 'reserved word')
        self._id_list = IdList(self._line)
        self._id_list.parse()
        context_free_error_checker(
            __main__.core.enums.Token['SEMICOLON'].value, 'special symbol')

    def print(self) -> None:
        """Print the production of the <in> nonterminal to stdout.

        Print the terminals in the production of <in>, calling the 
        print() method of the class instance representing the 
        nonterminal at the current level that was constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        print('read ', end = '')
        self._id_list.print()
        print(';')
    
    def execute(self, data: TextIO) -> None:
        """Execute the <id list> nonterminal in the <in> production.

        Call the execute() method of the class instance representing 
        the nonterminal in the production of the <in> nonterminal 
        that was constructed during parsing to initiate execution of 
        the Core program at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        self._id_list.execute(data, is_input = True, line_number = self._line)

class Out:
    """Encapsulation of the production for the <out> nonterminal.

    BNF grammar:
        <out> ::= write <id list>;

    Attributes:
        Public instance methods:
            parse
            print
            execute
    """

    def parse(self) -> None:
        """Construct the children of an <out> node in the APT.

        Construct a node corresponding to the <id list> nonterminal, 
        which appears in the only alternator in the production of 
        <out>. Call the parse() method of the class instance 
        representing the node to initiate construction of the next 
        level of the APT. Call context_free_error_checker() to ensure 
        that the terminals that appear in the production of <out> exist 
        at the proper locations in the token stream.
        """
        self._line = __main__.tokenizer.line_number
        context_free_error_checker(
            __main__.core.enums.Token['WRITE'].value, 'reserved word')
        self._id_list = IdList(self._line)
        self._id_list.parse()
        context_free_error_checker(
            __main__.core.enums.Token['SEMICOLON'].value, 'special symbol')

    def print(self) -> None:
        """Print the production of the <out> nonterminal to stdout.

        Print the terminals in the production of <out>, calling the 
        print() method of the class instance representing the 
        nonterminal at the current level that was constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        print('write ', end = '')
        self._id_list.print()
        print(';')

    def execute(self, data: TextIO) -> None:
        """Execute the <id list> nonterminal in the <out> production.

        Call the execute() method of the class instance representing 
        the nonterminal in the production of the <out> nonterminal 
        that was constructed during parsing to initiate execution of 
        the Core program at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        self._id_list.execute(data, is_input = False, line_number = self._line)

class Loop:
    """Encapsulation of the production for the <loop> nonterminal.

    BNF grammar:
        <loop> ::= while <cond> loop <stmt seq> end;

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            execute
    """

    def __init__(self, indent_level: int) -> None:
        self._indent_level = indent_level

    def parse(self) -> None:
        """Construct the children of a <loop> node in the APT.

        Construct nodes corresponding to <cond> and <stmt seq> 
        nonterminals, which appear in the only alternator in the 
        production of <loop>. Call the parse() method of the class 
        instances representing the nodes to initiate construction of 
        the next level of the APT. Call context_free_error_checker() to 
        ensure that the terminals that appear in the production of 
        <loop> exist at the proper locations in the token stream.
        """
        self._line = __main__.tokenizer.line_number
        context_free_error_checker(
            __main__.core.enums.Token['WHILE'].value, 'reserved word')
        self._condition = Cond(self._line)
        self._condition.parse()
        context_free_error_checker(
            __main__.core.enums.Token['LOOP'].value, 'reserved word')
        self._stmt_seq = StmtSeq(self._indent_level + 2)
        self._stmt_seq.parse()
        context_free_error_checker(
            __main__.core.enums.Token['END'].value, 'reserved word')
        context_free_error_checker(
            __main__.core.enums.Token['SEMICOLON'].value, 'special symbol')

    def print(self) -> None:
        """Print the production of the <loop> nonterminal to stdout.

        Print the terminals in the production of <loop>, calling the 
        print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        print('while ', end = '')
        self._condition.print()
        print('')
        print(Prog.pretty_print_indent * (self._indent_level + 1), 
              'loop', sep = '')
        self._stmt_seq.print()
        print(Prog.pretty_print_indent * self._indent_level, 'end;', sep = '')
    
    def execute(self, data: TextIO) -> None:
        """Execute the nonterminals in the <loop> production.

        Evaluate the <cond> node that was constructed during parsing to 
        resolve it to a Boolean, and execute the <stmt seq> node while 
        the <cond> node evaluates to True. Calling the execute() and 
        evaluate() methods of the class instances that represent the 
        <cond> and <stmt seq> nodes initiates execution and evaluation 
        at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        while self._condition.evaluate(data, self._line):
            self._stmt_seq.execute(data)

class If:
    """Encapsulation of the production for the <if> nonterminal.

    BNF grammar:
        <if> ::= if <cond> then <stmt seq> end; 
                 | if <cond> then <stmt seq> else <stmt seq> end;

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            execute
    """

    def __init__(self, indent_level: int) -> None:
        self._indent_level = indent_level
        self._else_stmt_seq = None

    def parse(self) -> None:
        """Construct the children of an <if> node in the APT.

        Construct nodes corresponding to <cond> and <stmt seq> 
        nonterminals, which appear in both alternators in the 
        production of <if>. Conditionally construct another node 
        corresponding to a <stmt seq> nonterminal based on the current 
        token in the token stream after the first <stmt seq> node is 
        fully parsed to terminals in the APT. Call the parse() method 
        of the class instances representing the nodes to initiate 
        construction of the next level of the APT. Call 
        context_free_error_checker() to ensure that the terminals that 
        appear in the production of <if> exist at the proper locations 
        in the token stream.
        """
        self._line = __main__.tokenizer.line_number
        context_free_error_checker(
            __main__.core.enums.Token['IF'].value, 'reserved word')
        self._condition = Cond(self._line)
        self._condition.parse()
        context_free_error_checker(
            __main__.core.enums.Token['THEN'].value, 'reserved word')
        self._then_stmt_seq = StmtSeq(self._indent_level + 1)
        self._then_stmt_seq.parse()
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['ELSE'].value:
            __main__.tokenizer.skip_token()
            self._else_stmt_seq = StmtSeq(self._indent_level + 1)
            self._else_stmt_seq.parse()
        context_free_error_checker(__main__.core.enums.Token['END'].value,
                                   'reserved word')
        context_free_error_checker(
            __main__.core.enums.Token['SEMICOLON'].value, 'special symbol')

    def print(self) -> None:
        """Print an alternator of the <if> production to stdout.

        Print the terminals in the parsed alternator of <if>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        print('if ', end = '')
        self._condition.print()
        print(' then')
        self._then_stmt_seq.print()
        if self._else_stmt_seq:
            print(Prog.pretty_print_indent * self._indent_level, 
                  'else', sep = '')
            self._else_stmt_seq.print()
        print(Prog.pretty_print_indent * self._indent_level, 'end;', sep = '')

    def execute(self, data: TextIO) -> None:
        """Execute the nonterminals in the parsed <if> alternator.

        Evaluate the <cond> node that was constructed during parsing to 
        resolve it to a Boolean, and execute the first <stmt seq> node 
        if the <cond> node evaluates to True. If the <cond> node 
        evaluates to False, then execute the second <stmt seq> node if 
        it exists. Calling the execute() and evaluate() methods of the 
        class instances that represent the <cond> and <stmt seq> nodes 
        initiates execution and evaluation at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        if self._condition.evaluate(data, self._line):
            self._then_stmt_seq.execute(data)
        else:
            if self._else_stmt_seq:
                self._else_stmt_seq.execute(data)

class Cond:
    """Encapsulation of the production for the <cond> nonterminal.

    BNF grammar:
        <cond> ::= <comp> | !<cond> | [<cond> && <cond>] 
                   | [<cond> || <cond>]

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            evaluate
    """

    def __init__(self, line_number: int) -> None:
        self._comparison = None
        self._not_condition = None
        self._left_condition = None
        self._conjunction_right_condition = None
        self._disjunction_right_condition = None
        self._line = line_number

    def parse(self) -> None:
        """Construct the children of a <cond> node in the APT.

        Conditionally construct nodes corresponding to <comp> and 
        <cond> nonterminals based on token checks that occur before and 
        during parsing. Call the parse() method of the class instances 
        representing the nodes to initiate construction of the next 
        level of the APT. Call context_free_error_checker() to ensure 
        that the terminals that appear in the production of <cond> 
        exist at the proper locations in the token stream.
        """
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['LEFT_PARENTHESIS'].value:
            self._comparison = Comp(self._line)
            self._comparison.parse()
        elif token_number == __main__.core.enums.Token['LOGICAL_NOT'].value:
            __main__.tokenizer.skip_token()
            self._not_condition = Cond(self._line)
            self._not_condition.parse()
        elif token_number == __main__.core.enums.Token['LEFT_BRACKET'].value:
            __main__.tokenizer.skip_token()
            self._left_condition = Cond(self._line)
            self._left_condition.parse()
            token_number = __main__.tokenizer.get_token()
            if token_number == __main__.core.enums.Token['LOGICAL_AND'].value:
                __main__.tokenizer.skip_token()
                self._conjunction_right_condition = Cond(self._line)
                self._conjunction_right_condition.parse()
            elif token_number == __main__.core.enums.Token['LOGICAL_OR'].value:
                __main__.tokenizer.skip_token()
                self._disjunction_right_condition = Cond(self._line)
                self._disjunction_right_condition.parse()
            else:
                context_free_error_checker()
            context_free_error_checker(
                __main__.core.enums.Token['RIGHT_BRACKET'].value,
                'special symbol')
        else:
            context_free_error_checker()

    def print(self) -> None:
        """Print an alternator of the <cond> production to stdout.

        Print the terminals in the parsed alternator of <cond>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        if self._comparison:
            self._comparison.print()
        if self._not_condition:
            print('!', end = '')
            self._not_condition.print()
        if self._conjunction_right_condition:
            print('[ ', end = '')
            self._left_condition.print()
            print(' && ', end = '')
            self._conjunction_right_condition.print()
            print(' ]', end = '')
        if self._disjunction_right_condition:
            print('[ ', end = '')
            self._left_condition.print()
            print(' || ', end = '')
            self._disjunction_right_condition.print()
            print(' ]', end = '')

    def evaluate(self, data: TextIO, line_number: int) -> bool:
        """Evaluate the nonterminals in the parsed <cond> alternator.

        Evaluate the <cond> or <comp> nodes that were constructed 
        during parsing to resolve them to Booleans. Perform negation,
        conjunction, or disjunction on the resolved Booleans if the 
        alternator that became encapsulated during parsing was the 
        second, third, or fourth of the production of <cond>, 
        respectively. Calling the evaluate() method of the class 
        instances that represent the nodes initiates evaluation at the 
        next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this Cond instance appears in the 
                Core program.

        Returns:
            The evaluation of the alternator of the production of 
            <cond> that became encapsulated in this Cond instance 
            during parsing.
        """
        if self._comparison:
            return self._comparison.evaluate(data, line_number)
        if self._not_condition:
            return not self._not_condition.evaluate(data, line_number)
        if self._conjunction_right_condition:
            return (self._left_condition.evaluate(data, line_number) 
                    and self._conjunction_right_condition.evaluate(
                        data, line_number))
        if self._disjunction_right_condition:
            return (self._left_condition.evaluate(data, line_number) 
                    or self._disjunction_right_condition.evaluate(
                        data, line_number))

class Comp:
    """Encapsulation of the production for the <comp> nonterminal.

    BNF grammar:
        <comp> ::= (<op> <comp op> <op>)

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            evaluate
    """

    def __init__(self, line_number: int) -> None:
        self._line = line_number

    def parse(self) -> None:
        """Construct the children of a <comp> node in the APT.

        Construct nodes corresponding to <op> and <comp op> 
        nonterminals, which appear in the only alternator in the 
        production of <comp>. Call the parse() method of the class 
        instances representing the nodes to initiate construction of 
        the next level of the APT. Call context_free_error_checker() to 
        ensure that the terminals that appear in the production of 
        <comp> exist at the proper locations in the token stream.
        """
        context_free_error_checker(
            __main__.core.enums.Token['LEFT_PARENTHESIS'].value,
            'special symbol')
        self._left_operand = Op(self._line)
        self._left_operand.parse()
        self._comp_operator = CompOp()
        self._comp_operator.parse()
        self._right_operand = Op(self._line)
        self._right_operand.parse()
        context_free_error_checker(
            __main__.core.enums.Token['RIGHT_PARENTHESIS'].value,
            'special symbol')
    
    def print(self) -> None:
        """Print the production of the <comp> nonterminal to stdout.

        Print the terminals in the production of <comp>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        print('( ', end = '')
        self._left_operand.print()
        self._comp_operator.print()
        self._right_operand.print()
        print(' )', end = '')

    def evaluate(self, data: TextIO, line_number: int) -> bool:
        """Evaluate the nonterminals in the production of <comp>.

        Evaluate the <op> and <comp op> nodes that were constructed 
        during parsing to resolve them to integers and a comparison 
        operator, respectively. Perform the comparison operation that 
        corresponds to the operator that the <comp op> node resolves 
        to, and return the Boolean result of that operation. Calling 
        the evaluate() method of the class instances that represent the 
        nodes initiates evaluation at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this Comp instance appears in the 
                Core program.

        Returns:
            The evaluation of the production of <comp> that became 
            encapsulated in this Comp instance during parsing.
        """
        operator = self._comp_operator.get_op_name()
        if operator == 'NOT_EQUAL':
            return (self._left_operand.evaluate(data, line_number) 
                    != self._right_operand.evaluate(data, line_number))
        if operator == 'EQUAL':
            return (self._left_operand.evaluate(data, line_number) 
                    == self._right_operand.evaluate(data, line_number))
        if operator == 'LESS_THAN':
            return (self._left_operand.evaluate(data, line_number) 
                    < self._right_operand.evaluate(data, line_number))
        if operator == 'GREATER_THAN':
            return (self._left_operand.evaluate(data, line_number) 
                    > self._right_operand.evaluate(data, line_number))
        if operator == 'LESS_THAN_OR_EQUAL':
            return (self._left_operand.evaluate(data, line_number) 
                    <= self._right_operand.evaluate(data, line_number))
        if operator == 'GREATER_THAN_OR_EQUAL':
            return (self._left_operand.evaluate(data, line_number) 
                    >= self._right_operand.evaluate(data, line_number))

class CompOp:
    """Encapsulation of the production for the <comp op> nonterminal.

    BNF grammar:
        <comp op> ::= != | == | < | > | <= | >=

    Attributes:
        Public instance methods:
            parse
            print
            get_op_name
    """

    def parse(self) -> None:
        """Construct the child of a <comp op> node in the APT.

        Construct a leaf node corresponding to a token that is one of 
        the six comparison operators of Core. Call 
        context_free_error_checker() to ensure that the current token 
        in the token stream is a terminal in the production of 
        <comp op>.
        """
        token_number = __main__.tokenizer.get_token()
        if token_number not in [
                __main__.core.enums.Token['NOT_EQUAL'].value, 
                __main__.core.enums.Token['EQUAL'].value, 
                __main__.core.enums.Token['LESS_THAN'].value,
                __main__.core.enums.Token['GREATER_THAN'].value,
                __main__.core.enums.Token['LESS_THAN_OR_EQUAL'].value,
                __main__.core.enums.Token['GREATER_THAN_OR_EQUAL'].value]:
            context_free_error_checker()
        self._operator = __main__.core.enums.Token(token_number).name
        __main__.tokenizer.skip_token()

    def print(self) -> None:
        """Print an alternator of the <comp op> production to stdout."""
        print('', __main__.core.SPECIAL[self._operator], '', end = '')

    def get_op_name(self) -> str:
        """Return the terminal child of the <comp op> node."""
        return self._operator

class Assign:
    """Encapsulation of the production for the <assign> nonterminal.

    BNF grammar:
        <assign> ::= <id> = <exp>;
    
    Attributes:
        Public instance methods:
            parse
            print
            execute
    """

    def parse(self) -> None:
        """Construct the children of an <assign> node in the APT.

        Construct nodes corresponding to <id> and <exp> nonterminals, 
        which appear in the only alternator in the production of 
        <assign>. Call the parse() method of the classes or class 
        instances representing the nodes to initiate construction of 
        the next level of the APT. Call context_free_error_checker() to 
        ensure that the terminals that appear in the production of 
        <assign> exist at the proper locations in the token stream.
        """
        self._line = __main__.tokenizer.line_number
        self._id = Id.parse()
        context_free_error_checker(
            __main__.core.enums.Token['ASSIGNMENT'].value, 'special symbol')
        self._expression = Exp(self._line)
        self._expression.parse()
        context_free_error_checker(
            __main__.core.enums.Token['SEMICOLON'].value, 'special symbol')

    def print(self) -> None:
        """Print the production of the <assign> nonterminal to stdout.

        Print the terminals in the production of <assign>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        self._id.print()
        print(' = ', end = '')
        self._expression.print()
        print(';')

    def execute(self, data: TextIO) -> None:
        """Execute the parsed children of the <assign> node.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
        """
        value = self._expression.evaluate(data, self._line)
        self._id.set_value(value)

class Exp:
    """Encapsulation of the production for the <exp> nonterminal.

    BNF grammar:
        <exp> ::= <fac> | <fac> + <exp> | <fac> - <exp>

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            evaluate
    """

    def __init__(self, line_number: int) -> None:
        self._add_expression = None
        self._subtract_expression = None
        self._line = line_number

    def parse(self) -> None:
        """Construct the children of an <exp> node in the APT.

        Construct a node corresponding to the <fac> nonterminal, which 
        appears in all alternators in the production of <exp>. 
        Conditionally construct another node corresponding to an <exp> 
        nonterminal based on the current token in the token stream 
        after the <fac> node is fully parsed to terminals in the APT. 
        Call the parse() method of the class instances representing the 
        nodes to initiate construction of the next level of the APT.
        """
        self._factor = Fac(self._line)
        self._factor.parse()
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['ADDITION'].value:
            __main__.tokenizer.skip_token()
            self._add_expression = Exp(self._line)
            self._add_expression.parse()
        if token_number == __main__.core.enums.Token['SUBTRACTION'].value:
            __main__.tokenizer.skip_token()
            self._subtract_expression = Exp(self._line)
            self._subtract_expression.parse()

    def print(self) -> None:
        """Print an alternator of the <exp> production to stdout.

        Print the terminals in the parsed alternator of <exp>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        self._factor.print()
        if self._add_expression:
            print(' + ', end = '')
            self._add_expression.print()
        if self._subtract_expression:
            print(' - ', end = '')
            self._subtract_expression.print()

    def evaluate(self, data: TextIO, line_number: int) -> int:
        """Evaluate the nonterminals in the parsed <exp> alternator.

        Evaluate the <fac> and <exp> nodes that were constructed 
        during parsing to resolve them to integers or identifiers. 
        Perform addition or subtraction on the resolved nodes if the 
        alternator that became encapsulated during parsing was the 
        second or third of the production of <exp>, respectively. 
        Calling the evaluate() method of the class instances that 
        represent the nodes initiates evaluation at the next level of 
        the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this Exp instance appears in the 
                Core program.

        Returns:
            The evaluation of the alternator of the production of <exp> 
            that became encapsulated in this Exp instance during 
            parsing.
        """
        if self._add_expression:
            return (self._factor.evaluate(data, line_number) 
                    + self._add_expression.evaluate(data, line_number))
        elif self._subtract_expression:
            return (self._factor.evaluate(data, line_number) 
                    - self._subtract_expression.evaluate(data, line_number))
        else:
            return self._factor.evaluate(data, line_number)

class Fac:
    """Encapsulation of the production for the <fac> nonterminal.

    BNF grammar:
        <fac> ::= <op> | <op> * <fac>

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            evaluate
    """

    def __init__(self, line_number: int) -> None:
        self._factor = None
        self._line = line_number

    def parse(self) -> None:
        """Construct the children of a <fac> node in the APT.

        Construct a node corresponding to the <op> nonterminal, which 
        appears in both alternators in the production of <fac>. 
        Conditionally construct another node corresponding to a <fac> 
        nonterminal based on the current token in the token stream 
        after the <op> node is fully parsed to terminals in the APT. 
        Call the parse() method of the class instances representing the 
        nodes to initiate construction of the next level of the APT.
        """
        self._operand = Op(self._line)
        self._operand.parse()
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['MULTIPLICATION'].value:
            __main__.tokenizer.skip_token()
            self._factor = Fac(self._line)
            self._factor.parse()

    def print(self) -> None:
        """Print an alternator of the <fac> production to stdout.

        Print the terminals in the parsed alternator of <fac>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        self._operand.print()
        if self._factor:
            print(' * ', end = '')
            self._factor.print()

    def evaluate(self, data: TextIO, line_number: int) -> int:
        """Evaluate the nonterminals in the parsed <fac> alternator.

        Evaluate the <op> and <fac> nodes that were constructed during 
        parsing to resolve them to integers or identifiers. Perform 
        multiplication on the resolved nodes if the alternator that 
        became encapsulated during parsing was the second of the 
        production of <fac>. Calling the evaluate() method of the class 
        instances that represent the nodes initiates evaluation at the 
        next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this Fac instance appears in the 
                Core program.

        Returns:
            The evaluation of the alternator of the production of <fac> 
            that became encapsulated in this Fac instance during 
            parsing.
        """
        if self._factor:
            return (self._operand.evaluate(data, line_number) 
                    * self._factor.evaluate(data, line_number))
        else:
            return self._operand.evaluate(data, line_number)

class Op:
    """Encapsulation of the production for the <op> nonterminal.

    BNF grammar:
        <op> ::= <int> | <id> | (<exp>) 

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            evaluate
    """

    def __init__(self, line_number: int) -> None:
        self._int = None
        self._id = None
        self._parenth_exp = None
        self._line = line_number

    def parse(self) -> None:
        """Construct the children of an <op> node in the APT.

        Conditionally construct a leaf node corresponding to an integer 
        or an identifier token or construct a node corresponding to a
        parenthetical <exp> nonterminal based on the current token in 
        the token stream. Call the parse() method of the class instance 
        representing the node to initiate construction of the next 
        level of the APT. Call context_free_error_checker() to ensure 
        that the terminals that appear in the parsed alternator of the 
        production of <op> exist at the proper locations in the token 
        stream.
        """
        token_number = __main__.tokenizer.get_token()
        if token_number == __main__.core.enums.Token['INTEGER'].value:
            self._int = Int(__main__.tokenizer.int_val())
            self._int.parse()
        elif token_number == __main__.core.enums.Token['IDENTIFIER'].value:
            self._id = Id.parse()
            self._id.line[self._line] = __main__.tokenizer.line_number
        elif (token_number 
                == __main__.core.enums.Token['LEFT_PARENTHESIS'].value):
            self._parenth_exp = ParenthExp(self._line)
            self._parenth_exp.parse()
            context_free_error_checker(
                __main__.core.enums.Token['RIGHT_PARENTHESIS'].value, 
                'special symbol')
        else:
            context_free_error_checker()

    def print(self) -> None:
        """Print an alternator of the <op> production to stdout.

        Print the terminals in the parsed alternator of <op>, calling 
        the print() method of the class instances representing the 
        nonterminals at the current level that were constructed during 
        parsing to initiate printing at the next level of the APT.
        """
        if self._int:
            self._int.print()
        if self._id:
            self._id.print()
        if self._parenth_exp:
            print('( ', end = '')
            self._parenth_exp.print()
            print(' )', end = '')

    def evaluate(self, data: TextIO, line_number: int) -> int:
        """Evaluate the child of the parsed <op> alternator.

        Get the value of the leaf node or, if a (<exp>) node was 
        constructed during parsing, evaluate it to resolve it to an 
        integer or an identifier. Calling the evaluate() method of the 
        class instance that represents the (<exp>) node initiates 
        evaluation at the next level of the APT.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this Op instance appears in the 
                Core program.

        Returns:
            The value of the leaf node or the evaluation of the third
            alternator of the production of <op> that became 
            encapsulated in this Op instance during parsing.
        """
        if self._int:
            return self._int.get_value() 
        if self._id:
            return self._id.get_value(data, line_number)
        if self._parenth_exp:
            return self._parenth_exp.evaluate(data, line_number)

class ParenthExp:
    """Encapsulation of the third alternator of the production of <op>.

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            evaluate
    """

    def __init__(self, line_number: int) -> None:
        self._line = line_number

    def parse(self) -> None:
        """Construct the child of a (<exp>) node in the APT.

        Construct a node corresponding to the <exp> nonterminal. Call 
        the parse() method of the class instance representing the node 
        to initiate construction of the next level of the APT. Call 
        context_free_error_checker() to ensure that parentheses exist 
        at the proper locations in the token stream.
        """
        context_free_error_checker(
            __main__.core.enums.Token['LEFT_PARENTHESIS'].value, 
            'special symbol')
        self._expression = Exp(self._line)
        self._expression.parse()

    def print(self) -> None:
        """Initiate printing at the next level of the APT."""
        self._expression.print()

    def evaluate(self, data: TextIO, line_number: int) -> int:
        """Evaluate the child of the parsed (<exp>) node.

        Args:
            data: An instance of io.TextIOWrapper that provides 
                high-level access to the buffered binary stream 
                containing input data for "read" statements in the Core 
                program.
            line_number: The line whereat the alternator of the 
                production of <stmt> that is encapsulated in the 
                Statement instance whose parse() method resulted in the 
                construction of this ParenthExp instance appears in the 
                Core program.

        Returns:
            The evaluation of the <exp> node that became encapsulated 
            in this ParenthExp instance during parsing.
        """
        return self._expression.evaluate(data, line_number)

class Int:
    """Encapsulation of the production for the <int> nonterminal.

    BNF grammar:
        <int> ::= \d+ (a regular expression in PCRE2 syntax)

    Attributes:
        Public instance methods:
            __init__
            parse
            print
            get_value
    """

    def __init__(self, value: int) -> None:
        self._value = value

    def parse(self) -> None:
        """Ensure that the current token is an integer."""
        context_free_error_checker(
            __main__.core.enums.Token['INTEGER'].value, 'integer')

    def print(self) -> None:
        """Print the value of this Int instance."""
        print(self._value, end = '')

    def get_value(self) -> int:
        """Get the value of this Int instance.

        Returns:
            The value associated with this Int instance.
        """
        return self._value

