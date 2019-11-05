from ParseEnum import *

class ParsedItem:
    def __init__(self, itemtype, line_num):
        self.type = itemtype
        self.line_num = line_num
    def stupid_string(self):
        return str(self.type) + ' '+str(self.line_num)+' '

class ParsedGoal(ParsedItem):
    def __init__(self, line_num):
        self.type = PitProgram
        self.line_num = line_num
        self.funcs = []
    def __str__(self):
        strings = ["Program: "]
        for func in self.funcs: strings.append(str(func) + '\n')
        return ''.join(strings)

class ParsedFunc(ParsedItem):
    def __init__(self, line_num):
        self.type = PitFunc
        self.line_num = line_num
        self.returns_int = False
        self.name = ''
        self.arguments = []
        self.stmts = []
    def __str__(self):
        strings = []
        for arg in self.arguments:
            typestr = 'int ' if arg[0] else 'float '
            pointstr = '*' if arg[1] else ''
            strings.append(typestr + pointstr + arg[2])
        ststrings = []
        for stmt in self.stmts:
            ststrings.append(str(stmt) + '\n')
        return self.name + " as " + str(int(self.returns_int)) +" Func("+', '.join(strings)+')\n'+''.join(ststrings)

class ParsedStmt2(ParsedItem):
    def __init__(self, line_num):
        self.type = PitStmt2
        self.line_num = line_num
        self.initialize = None
        self.condition = None
        self.update = None
        self.stmt = None
    def __str__(self):
        strings = ['For(', str(self.initialize), '; ',str(self.condition), '; ',str(self.update), ')\n']
        return ''.join(strings) + str(self.stmt)

class ParsedStmt3(ParsedItem):
    def __init__(self, line_num):
        self.type = PitStmt3
        self.line_num = line_num
        self.condition = None
        self.stmt = None
    def __str__(self):
        strings = ['If(', str(self.condition),')\n',str(self.stmt)]
        return ''.join(strings)

class ParsedStmt4(ParsedItem):
    def __init__(self, line_num):
        self.type = PitStmt4
        self.line_num = line_num
        self.stmts = []
    def __str__(self):
        strings = ['{\n']
        for stmt in self.stmts:
            strings.append(str(stmt)+'\n')
        return ''.join(strings) + '}'

class ParsedStmt5(ParsedItem):
    def __init__(self, line_num):
        self.type = PitStmt5
        self.line_num = line_num
        self.expr = None
    def __str__(self):
        return 'Return('+str(self.expr)+')'
    

class ParsedInst1(ParsedItem):
    def __init__(self, line_num):
        self.type = PitInst1
        self.line_num = line_num
        self.declares_int = False
        self.declarations = []
    def __str__(self):
        typestr = 'int' if self.declares_int else 'float'
        strings = ["Declaration: ", typestr, ' ']
        return ''.join(strings) + ', '.join(self.declarations)

class ParsedInst2(ParsedItem):
    def __init__(self, line_num):
        self.type = PitInst2
        self.line_num = line_num
        self.declares_int = False
        self.declarations = []
    def __str__(self):
        typestr = 'int' if self.declares_int else 'float'
        strings = ["Declaration: ", typestr, ' ']
        decstrings = [str(i) for i in self.declarations]
        return ''.join(strings) + ', '.join(decstrings)

class ParsedInst4(ParsedItem):
    def __init__(self, line_num):
        self.type = PitInst4
        self.line_num = line_num
    def __str__(self):
        return 'Noop'

class ParsedExpr1(ParsedItem):
    def __init__(self, line_num):
        self.type = PitExpr1
        self.line_num = line_num
        self.terms_and_ops = []
    def __str__(self):
        strings = [str(i) for i in self.terms_and_ops]
        return "Arithmetic: " + ' '.join(strings)

class ParsedExpr2(ParsedItem):
    def __init__(self, line_num):
        self.type = PitExpr2
        self.lhs = ('', None)
        self.expr = None
    def __str__(self):
        return "Assignment: ("+str(self.lhs[0])+', '+str(self.lhs[1])+') to '+str(self.expr)

class ParsedTerm(ParsedItem):
    def __init__(self, line_num):
        self.type = PitTerm
        self.line_num = line_num
        self.factors_and_ops = []
    def __str__(self):
        strings = [str(i) for i in self.factors_and_ops]
        return "Term: "+ ' '.join(strings)

class ParsedFactor1(ParsedItem):
    def __init__(self, line_num):
        self.type = PitFactor1
        self.line_num = line_num
        self.lhs = ('', None)
        self.op = 0
    def __str__(self):
        return "Increment: (" + str(self.lhs[0])+', '+str(self.lhs[1]) +') with '+str(self.op)

class ParsedFactor2(ParsedItem):
    def __init__(self, line_num):
        self.type = PitFactor2
        self.line_num = line_num
        self.func_name = ''
        self.call = []
    def __str__(self):
        return "Call: " +self.func_name+' with '+' '.join([str(i) for i in self.call])

class ParsedFactor3(ParsedItem):
    def __init__(self, line_num, integer):
        self.type = PitFactor3
        self.line_num = line_num
        self.num = integer
    def __str__(self):
        return str(self.num)

class ParsedFactor4(ParsedItem):
    def __init__(self, line_num, floater):
        self.type = PitFactor4
        self.line_num = line_num
        self.num = floater
    def __str__(self):
        return str(self.num)

class ParsedFactor5(ParsedItem):
    def __init__(self, line_num):
        self.type = PitFactor5
        self.line_num = line_num
        self.expr = None
    def __str__(self):
        return "("+str(self.expr)+')'

class ParsedFactor6(ParsedItem):
    def __init__(self, line_num):
        self.type = PitFactor6
        self.line_num = line_num
        self.op = 0
        self.factor = None
    def __str__(self):
        optype = '+' if 0 else '-'
        return optype + str(self.factor)