from TokenEnum import *

class Token:
    def __init__(self, toktype, string=None, string2=None):
        self.type = toktype
        self.data = string
        self.data2 = string2

def sub_isal(ch):
    return ch.isalpha() or ch.isdecimal() or ch == '_'

def sub_isdec(ch):
    return ch.isdecimal()

def sub_isn_spch(ch):
    return ch != '%' and ch != '\\'

def sub_count(top, do_i_cont, l, start=1):
    i = start
    while i < l:
        ch = top[i]
        if do_i_cont(ch):
            i = i + 1
            continue
        break

    return i

class Lex:
    def __init__(self, file, simple=True):
        self.file = file
        self.buffer = []
        self.simple = simple
        # self.lookahead = []
        
    def __iter__(self):
        return self
    
    def __next__(self):
        return self.sub_next()

    def look_ahead(self):
        pass

    def top(self):
        # if len(self.lookahead) > 0:
        #     token = self.lookahead[0]
        # else:
        #     token = self.sub_next()
        #     self.lookahead.append(token)
        # return token
        pass
    
    def next(self):
        # if len(self.lookahead) > 0:
        #     token = self.lookahead[0]
        #     self.lookahead = self.lookahead[1:]
        # else:
        #     token = self.sub_next()
        # return token
        return self.sub_next()

    def sub_next(self):
        if len(self.buffer) == 0:
            self.preproc_line()

        top = self.buffer.pop()
        #if top[0] != '\n': print(top, end=' ')
        #else: print('')

        if top[0].isalpha() or top[0] == '_': return self.deal_alpha(top)
        elif top[0].isdecimal(): return self.deal_decimal(top)
        elif top[0] == '.': return self.deal_period(top)
        elif top[0] == '\n': return Token(TokNewline)
        elif top[0] == '"': return self.deal_dquotes(top)
        elif top[0] == '+': return self.deal_plus(top)
        else: return self.deal_single(top)

    def preproc_line(self):
        line = self.file.readline()
        if len(line) == 0:
            raise StopIteration

        buffer_buffer = line.split('"')
        buffer_buffer[0] = buffer_buffer[0].split()
        for i in range(1, len(buffer_buffer)):
            if i%2 == 0:
                buffer_buffer[i-1][0] = buffer_buffer[i-1][0] + '"'
                buffer_buffer[i] = buffer_buffer[i].split()
            else:
                buffer_buffer[i] = ['"' + buffer_buffer[i]]

        for fluff in buffer_buffer:
            for nugget in fluff:
                self.buffer.append(nugget)

        if line[-1] == '\n':
            self.buffer.append('\n')

        if len(self.buffer) == 0:
            raise StopIteration

        self.buffer.reverse()
        return

    def trim(self, top, i, l):
        if i != l:
            self.buffer.append(top[i:])
            top = top[:i]
        return top

    def deal_plus(self, top):
        l = len(top)
        if l == 1 or top[1] != '+':
            self.trim(top, 1, l)
            return Token(TokPlus)
        
        self.trim(top, 2, l)
        return Token(TokPPlus)
        
    def deal_dquotes(self, top):
        l = len(top)
        if l == 1 or top[-1] != '"': return Token(TokError, "expected closing dquotes")
        top = top[1:-1]
        if self.simple: return Token(TokString, top)

        i = 0
        l = l - 2
        flag_met_per = False
        tnum = TokString
        while True:
            i = sub_count(top, sub_isn_spch, l, i)
            if i == l: break
            if top[i] == '\\':
                if top[i+1] == 'n': top = top[:i] + '\n' + top[i+2:]
                elif top[i+1] == '\\': top = top[:i] + '\\' + top[i+2:]
                else: return Token(TokError, "undefined use of \\")
                i = i + 1
                l = l - 1
            elif top[i] == '%':
                if top[i+1] == '%':
                    top = top[:i] + '%' + top[i+2:]
                    i = i + 1
                    l = l - 1
                    continue
                if flag_met_per == True:
                    return Token(TokError, "more than one special %")
                flag_met_per = True
                if top[i+1] == 'd':
                    tnum = TokString2
                    top_left = top[:i]
                    top = top[i+2:]
                    i = 0
                    l = l - i - 2
                elif top[i+1] == 'f':
                    tnum = TokString3
                    top_left = top[:i]
                    top = top[i+2:]
                    i = 0
                    l = l - i - 2
                else: return Token(TokError, "undefined use of %")
        
        if flag_met_per:
            return Token(tnum, top_left, top)
        return Token(tnum, top)

                


    def deal_single(self, top):
        tnum = TokError
        t = top[0]
        if t == '(': tnum = TokLparen
        elif t == ')': tnum = TokRparen
        elif t == '{': tnum = TokLcurly
        elif t == '}': tnum = TokRcurly
        elif t == '[': tnum = TokLbrack
        elif t == ']': tnum = TokRbrack
        elif t == ',': tnum = TokComma
        elif t == '-': tnum = TokMinus
        elif t == '/': tnum = TokSlash
        elif t == '*': tnum = TokAsterisk
        elif t == '>': tnum = TokGreater
        elif t == '<': tnum = TokLess
        elif t == ';': tnum = TokSemicol
        elif t == '=': tnum = TokEqual

        if tnum == TokError: return Token(TokError, "symbol not in alphabet")
        top = self.trim(top, 1, len(top))

        return Token(tnum)

    def deal_decimal(self, top):
        l = len(top)
        i = sub_count(top, sub_isdec, l)

        tnum = TokNum
        if i < l and top[i] == '.':
            i = sub_count(top, sub_isdec, l, i+1)
            tnum = TokNum2

        top = self.trim(top, i, l)

        return Token(tnum, top)

    def deal_period(self, top):
        l = len(top)
        i = sub_count(top, sub_isdec, l)
        if i < 2:
            return Token(TokError, "expected decimals after period")
        
        top = self.trim(top, i, l)
        
        return Token(TokNum2, top)

    def deal_alpha(self, top):
        l = len(top)
        i = sub_count(top, sub_isal, l)

        top = self.trim(top, i, l)
        
        if top == 'int': return Token(TokInt)
        elif top == 'float': return Token(TokFloat)
        elif top == 'void': return Token(TokVoid)
        elif top == 'for': return Token(TokFor)
        elif top == 'if': return Token(TokIf)
        elif top == 'return': return Token(TokReturn)
        elif top == 'printf' and not self.simple: return Token(TokPrintf)
        return Token(TokId, top)

def print_lex_to_console(lex):
    ln = 1
    print(ln, '. ', sep='', end='')
    for token in lex:
        if isinstance(token, Token):
            if not token.data == None:
                print(token.type, "'", token.data, "'", sep='', end=' ')
            elif token.type == TokNewline:
                print('')
                ln = ln + 1
                print(ln, '. ', sep='', end='')
            elif token.type == TokError:
                print("\nLexError:", token.data, "at", ln, "\n")
                raise Exception
            else:
                print(token.type, end=' ')
        else: raise Exception

def main():
    input_file = open("testfiles/faillex1.txt")
    lex = Lex(input_file)

    print_lex_to_console(lex)
    

if __name__ == "__main__":
    main()