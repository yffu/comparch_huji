import sys
debug = True


class Parser:
    # parses each VM command into its lexical elements
    def __init__(self, f_name):
        self.file = open(f_name, 'r')
        self.commandType = None
        self.arg1 = None
        self.arg2 = None
        self.comment = None
        self.d_class = {
            "push": "C_PUSH",
            "pop": "C_POP",
            "add": "C_ARITHMETIC",
            "sub": "C_ARITHMETIC",
            "neg": "C_ARITHMETIC",
            "eq": "C_ARITHMETIC",
            "gt": "C_ARITHMETIC",
            "lt": "C_ARITHMETIC",
            "and": "C_ARITHMETIC",
            "or": "C_ARITHMETIC",
            "not": "C_ARITHMETIC"
        }

    def has_more_commands(self):
        cur_pos = self.file.tell()
        has_line = bool(self.file.readline())
        self.file.seek(cur_pos)
        return has_line

    def advance(self):
        self.commandType = None
        self.arg1 = None
        self.arg2 = None
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
        self.comment = "// " + line + "\n"
        line = line.split()
        if line[0] in self.d_class:
            self.commandType = self.d_class[line[0]]
        if self.commandType == "C_PUSH":
            self.arg1 = line[1]
            self.arg2 = line[2]
        elif self.commandType == "C_POP":
            self.arg1 = line[1]
            self.arg2 = line[2]
        elif self.commandType == "C_ARITHMETIC":
            self.arg1 = line[0]

    def close(self):
        self.file.close()


class CodeWriter:
    # writes the assembly code that implements the parsed command
    def __init__(self, prog_name):
        self.cnt = 0
        self.prog_name = prog_name
        self.file = outfile = open(prog_name + '.asm', 'w')
        self._d_symbol = {
            # addr = segmentPointer + i, *SP = *addr, SP++
            "C_PUSH":
                ("{0}\n"
                 "D=A\n"
                 "@SP\n"
                 "A=M\n"
                 "M=D\n"
                 "@SP\n"
                 "M=M+1\n"),
            # addr = segmentPointer + i, *SP--, *addr = *SP
            "C_POP":
                ("@SP\n"
                 "M=M-1\n"
                 "@SP\n"
                 "A=M\n"
                 "D=M\n"
                 "{0}\n"
                 "M=D\n"),
            "C_PUSH_pointer":
                ("@{0}\n"
                 "D=A\n"
                 "@SP\n"
                 "A=M\n"
                 "M=D\n"
                 "@SP\n"
                 "M=M+1\n"),
            "add": ("@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "M=D+M\n"
                    "@SP\n"
                    "M=M+1\n"),
            "sub": ("@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "M=M-D\n"
                    "@SP\n"
                    "M=M+1\n"),
            "neg": ("@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "M=-M\n"
                    "@SP\n"
                    "M=M+1\n"),
            "and": ("@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "M=D&M\n"
                    "@SP\n"
                    "M=M+1\n"),
            "or": ("@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "D=M\n"
                    "@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "M=D|M\n"
                    "@SP\n"
                    "M=M+1\n"),
            "not": ("@SP\n"
                    "M=M-1\n"
                    "A=M\n"
                    "M=!M\n"
                    "@SP\n"
                    "M=M+1\n"),
            "eq": ("@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M\n"
                   "@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M-D\n"
                   "@IS_EQ_{0}\n"
                   "D;JEQ\n"
                   "(NOT_EQ_{0})\n"
                   "D=0\n"
                   "@SET_RESULT_{0}\n"
                   "0;JMP\n"
                   "(IS_EQ_{0})\n"
                   "D=-1\n"
                   "(SET_RESULT_{0})\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n"),
            "lt": ("@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M\n"
                   "@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M-D\n"
                   "@IS_LT_{0}\n"
                   "D;JLT\n"
                   "(NOT_LT_{0})\n"
                   "D=0\n"
                   "@SET_RESULT_{0}\n"
                   "0;JMP\n"
                   "(IS_LT_{0})\n"
                   "D=-1\n"
                   "(SET_RESULT_{0})\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n"),
            "gt": ("@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M\n"
                   "@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M-D\n"
                   "@IS_GT_{0}\n"
                   "D;JGT\n"
                   "(NOT_GT_{0})\n"
                   "D=0\n"
                   "@SET_RESULT_{0}\n"
                   "0;JMP\n"
                   "(IS_GT_{0})\n"
                   "D=-1\n"
                   "(SET_RESULT_{0})\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n"),
            "C_END": "(END)\n@END\n0;JMP\n"
        }
        self._d_segment = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
            "constant": "",
            "static": "",
            "pointer": "",
            "temp": ""
        }

    def symbol(self, s):
        if s in self._d_symbol:
            return self._d_symbol[s]
        else:
            return ""

    def seg_var(self, s):
        if s in self._d_segment:
            return self._d_segment[s]
        else:
            return ""

    def write_comment(self, comment):
        self.file.write(comment)

    def write_arithmetic(self, command):
        self.file.write(self.symbol(command).format(self.cnt))
        if command in ("eq", "lt", "gt"):
            self.cnt += 1

    def write_push_pop(self, command, segment, index):
        if segment == "constant":
            self.file.write(self.symbol(command).format("@"+index))
        elif segment == "static":
            self.file.write("@SP\nM=M-1\n@SP\nA=M\nD=M\n")
            self.file.write("@{0}.{1}\nM=D\n".format(self.prog_name, index))
        elif segment == "temp":
            # push:     addr = 5 + i, *SP = *addr, SP++
            if command == "C_PUSH":
                code = ("{0}\n"
                 "D=M\n"
                 "@SP\n"
                 "A=M\n"
                 "M=D\n"
                 "@SP\n"
                 "M=M+1\n")
                self.file.write(code.format(f"@{int(index)+5}"))
            # pop:     addr = 5 + i, *SP --, *addr = *SP
            elif command == "C_POP":
                self.file.write(self.symbol(command).format(f"@{int(index)+5}"))
        elif segment == "pointer":
            if index == "0":
                segment = self.symbol("this")
            elif index == "1":
                segment = self.symbol("that")
            if command == "C_PUSH":
                # push:     *SP = THIS, SP++
                # pop:      SP--, THIS = *SP
                self.file.write("@{0}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n".format(segment))
            elif command == "C_POP":
                # push:     *SP = THAT, SP++
                # pop:      SP--, THAT = *SP
                self.file.write("@{0}\nD=A\n@SP\nM=M-1\n@SP\nA=M\nM=D\n".format(segment))
        else:
            if command == "C_PUSH":
                code = (
                 "@{0}\n"
                 "D=M\n"
                 "@{1}\n"
                 "A=D+A\n"
                 "D=M\n"
                 "@SP\n"
                 "A=M\n"
                 "M=D\n"
                 "@SP\n"
                 "M=M+1\n")
                self.file.write(code.format(self.seg_var(segment), index))
            elif command == "C_POP":
                code = (
                 "@{0}\n"
                 "D=M\n"
                 "@{1}\n"
                 "D=D+A\n"
                 "@SP\n"
                 "M=M-1\n"
                 "A=M+1\n"
                 "M=D\n"
                 "A=A-1\n"
                 "D=M\n"
                 "A=A+1\n"
                 "A=M\n"
                 "M=D\n")
                self.file.write(code.format(self.seg_var(segment), index))

    def close(self):
        self.write_comment("//end\n")
        self.file.write(self.symbol("C_END"))
        self.file.close()


class VMTranslator:
    # drives the process
    def __init__(self, f_name):
        l_split = f_name.split('.')
        # Parser handles the input file
        parser = Parser(f_name)
        code_writer = CodeWriter(l_split[0])
        while parser.has_more_commands():
            parser.advance()
            command = None
            # CodeWriter to handle the input file - uses class methods and is not instantiated
            if parser.commandType == "C_PUSH":
                code_writer.write_comment(parser.comment)
                code_writer.write_push_pop(parser.commandType, parser.arg1, parser.arg2)
            elif parser.commandType == "C_POP":
                code_writer.write_comment(parser.comment)
                code_writer.write_push_pop(parser.commandType, parser.arg1, parser.arg2)
            elif parser.commandType == "C_ARITHMETIC":
                code_writer.write_comment(parser.comment)
                code_writer.write_arithmetic(parser.arg1)

        parser.close()
        code_writer.close()


if __name__ == '__main__':
    # StackArithmetic\SimpleAdd\SimpleAdd.vm
    # StackArithmetic\StackTest\StackTest.vm
    # MemoryAccess\BasicTest\BasicTest.vm
    if debug:
        print("argv[0]: ", sys.argv[0])
        print("argv[1]: ", sys.argv[1])
    translator = VMTranslator(sys.argv[1])
