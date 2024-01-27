# Develop a HackAssembler program that translates Hack assembly programs into executable Hack binary code
# The source program is supplied in a text file named xxx.asm
# The generated code is written into a text file named xxx.hack
# Assumptions: xxx.asm is error free

# Usage: java HackAssembler xxx.asm
# This command should create (or override) an xxx.hack file that can be executed as-is on the Hack computer

# Staged development
# Develop a basic assembler that translates assembly programs without symbols
# Develop an ability to handle symbols
# Morph the basic assembler into an assembler that can translate any assembly program

import sys
debug = False


class Parser:
    def __init__(self, infile):
        # Constructor for a Parser object that accepts a string specifying a file name
        # Need to know how to read text files
        # start reading a file with a given name
        self.file = infile
        self.commandType = None
        self.symbol = None
        self.jump = None
        self.dest = None
        self.comp = None

    def has_more_commands(self):
        cur_pos = self.file.tell()
        has_line = bool(self.file.readline())
        self.file.seek(cur_pos)
        return has_line

    def advance(self):
        line = self.file.readline().rstrip()
        self.commandType = None
        self.symbol = None
        self.jump = None
        self.dest = None
        self.comp = None
        if debug:
            print('line before: ', line)
        # comments > text beginning with two slashes (//) and ending at the end of the line is considered a comment and is ignored
        line = line.split('//')[0]
        # white space > space characters are ignored. empty lines are ignored.
        line = "".join(line.split())
        # move to the next command in file
        if debug:
            print('line after: ', line)
        if not line:
            print('line empty')
        elif line[0] == '@':
            # print('A instruction')
            self.commandType = 'A_COMMAND'
            # self.symbol = int(line[1:])
            self.symbol = line[1:]
            '''
            try:
                self.symbol = int(self.symbol)
            except Exception as e:
                print(e)
            '''
            # print('value: ', self.symbol)
        elif line[0] == '(':
            self.commandType = 'L_COMMAND'
            # self.symbol = int(line[1:line.find(')')])
            self.symbol = line[1:line.find(')')]
            '''
            try:
                self.symbol = int(self.symbol)
            except Exception as e:
                print(e)
            '''
            # print('symbol: ', self.symbol)
        else:
            self.commandType = 'C_COMMAND'
            l_split = line.split(';')
            if len(l_split) == 2:
                self.jump = l_split[1]
            l_split = l_split[0]
            l_split = l_split.split('=')
            if len(l_split) == 2:
                self.dest = l_split[0]
                self.comp = l_split[1]
            else:
                self.comp = l_split[0]
        print(self.__dict__)


class Code:
    d_dest = {
        None:   '000',
        'M':    '001',
        'D':    '010',
        'MD':   '011',
        'A':    '100',
        'AM':   '101',
        'AD':   '110',
        'AMD':  '111'
    }
    d_jump = {
        None:   '000',
        'JGT':  '001',
        'JEQ':  '010',
        'JGE':  '011',
        'JLT':  '100',
        'JNE':  '101',
        'JLE':  '110',
        'JMP':  '111'
    }
    d_comp = {
        '0':    '0101010',
        '1':    '0111111',
        '-1':   '0111010',
        'D':    '0001100',
        'A':    '0110000',
        '!D':   '0001101',
        '!A':   '0110001',
        '-D':   '0001101',
        '-A':   '0110011',
        'D+1':  '0011111',
        'A+1':  '0110111',
        'D-1':  '0001110',
        'A-1':  '0110010',
        'D+A':  '0000010',
        'D-A':  '0010011',
        'A-D':  '0000111',
        'D&A':  '0000000',
        'D|A':  '0010101',
        'M':    '1110000',
        '!M':   '1110001',
        '-M':   '1110011',
        'M+1':  '1110111',
        'M-1':  '1110010',
        'D+M':  '1000010',
        'D-M':  '1010011',
        'M-D':  '1000111',
        'D&M':  '1000000',
        'D|M':  '1010101'
    }

    @classmethod
    def dest(cls, d):
        return cls.d_dest[d]

    @classmethod
    def comp(cls, c):
        return cls.d_comp[c]

    @classmethod
    def jump(cls, j):
        return cls.d_jump[j]


class SymbolTable:
    # three types of symbols in the Hack language: predefined
    # symbols, labels, and variables.
    def __init__(self):
        # Initialize the symbol table with all the predefined symbols and their
        # pre-allocated RAM addresses
        self.d_symbol = {
            'SP':   0,
            'LCL':  1,
            'ARG':  2,
            'THIS': 3,
            'THAT': 4,
            'R0':   0,
            'R1':   1,
            'R2':   2,
            'R3':   3,
            'R4':   4,
            'R5':   5,
            'R6':   6,
            'R7':   7,
            'R8':   8,
            'R9':   9,
            'R10':  10,
            'R11':  11,
            'R12':  12,
            'R13':  13,
            'R14':  14,
            'R15':  15,
            'SCREEN':   16384,
            'KBD':      24576
        }

    def add_entry(self, sym, addr):
        self.d_symbol[sym] = addr

    def contains(self, sym):
        return sym in self.d_symbol

    def get_address(self, sym):
        return self.d_symbol[sym]


class HackAssembler:
    def __init__(self, f_name):
        # initializes the I/O files and drives the process
        l_split = f_name.split('.')
        self.prog_name = l_split[0]
        self.addr_rom = 0
        self.addr_ram = 16
        infile = open(f_name, 'r')
        parser = Parser(infile)
        symbol_table = SymbolTable()
        # first pass
        while parser.has_more_commands():
            parser.advance()
            print('addr_rom: ', self.addr_rom)
            if parser.commandType == 'C_COMMAND':
                self.addr_rom += 1
            elif parser.commandType == 'A_COMMAND':
                self.addr_rom += 1
            elif parser.commandType == 'L_COMMAND':
                symbol_table.add_entry(parser.symbol, self.addr_rom)
        print(symbol_table.d_symbol)

        # second pass
        infile = open(f_name, 'r')
        parser = Parser(infile)
        outfile = open(self.prog_name + '.hack', 'w')
        while parser.has_more_commands():
            parser.advance()
            code = None
            if parser.commandType == 'C_COMMAND':
                # For each C-instruction, the program concatenates the translated binary codes of the
                # instruction fields into a single 16-bit word.
                code = '111' + Code.comp(parser.comp) + Code.dest(parser.dest) + Code.jump(parser.jump)
                print('C Code: ', code)
            elif parser.commandType == 'A_COMMAND':
                # For each A-instruction of type @Xxx, the program translates the
                # decimal constant returned by the parser into its binary representation
                try:
                    parser.symbol = int(parser.symbol)
                except Exception as e:
                    if symbol_table.contains(parser.symbol):
                        parser.symbol = symbol_table.get_address(parser.symbol)
                    else:
                        symbol_table.add_entry(parser.symbol, self.addr_ram)
                        self.addr_ram += 1
                        parser.symbol = symbol_table.get_address(parser.symbol)
                    print(e)
                code = '0' + format(parser.symbol, '015b')
                # parser.symbol needs to be integer format
                print('A Code: ', code)
            elif parser.commandType == 'L_COMMAND':
                print('L Code: ')
            if code:
                outfile.write(code + '\n')
        infile.close()
        outfile.close()


if __name__ == '__main__':
    if debug:
        print("argv[0]: ", sys.argv[0])
        print("argv[1]: ", sys.argv[1])
    assembler = HackAssembler(sys.argv[1])
    if debug:
        print("program name", assembler.prog_name)
