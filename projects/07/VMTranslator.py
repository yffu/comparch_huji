import sys
debug = True


class Parser:
    def __init__(self, infile):
        self.file = infile
        self.commandType = None
        self.location = None

    def has_more_commands(self):
        cur_pos = self.file.tell()
        has_line = bool(self.file.readline())
        self.file.seek(cur_pos)
        return has_line

    def advance(self):
        self.commandType = None
        self.location = None
        line = self.file.readline().rstrip()
        if debug:
            print('line before: ', line)
        # comments > text beginning with two slashes (//) and ending at the end of the line is considered a comment and is ignored
        line = line.split('//')[0]
        # move to the next command in file
        if debug:
            print('line after: ', line)
        if not line:
            print('line empty')
            return
        line = line.split()
        if line[0] == "push":
            self.commandType = line[0]
            self.location = line[2]


class Code:
    d_symbol = {
        "push": "@{0}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    }

    @classmethod
    def symbol(cls, s):
        return cls.d_symbol[s]


class VMTranslator:
    def __init__(self, f_name):
        l_split = f_name.split('.')
        self.prog_name = l_split[0]
        infile = open(f_name, 'r')
        parser = Parser(infile)
        outfile = open(self.prog_name + '.asm', 'w')
        while parser.has_more_commands():
            parser.advance()
            code = None
            if parser.commandType == "push":
                code = Code.symbol(parser.commandType).format(parser.location)
            if code:
                outfile.write(code + '\n')

        infile.close()
        outfile.close()


if __name__ == '__main__':
    if debug:
        print("argv[0]: ", sys.argv[0])
        print("argv[1]: ", sys.argv[1])
    translator = VMTranslator(sys.argv[1])
