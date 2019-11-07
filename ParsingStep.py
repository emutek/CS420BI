from LexicalStep import Lex, Token
from TokenEnum import *
from ParseEnum import *
from ParsedItems import *

class ParsingException(Exception):
    pass

class ParsingDone(Exception):
    pass

class Par:
    def __init__(self, lex, loud=False):
        self.buffer = []
        self.lex = lex
        self.line_num = 1
        self.lookahead = None
        self.loud = loud

    def sub_next_token(self):
        try:
            token = next(self.lex)
        except StopIteration:
            return Token(TokEOF)
        if token.type == TokError:
            print("Lex error:", token.data)
            raise ParsingException()
        #print (token.type,'', end='')
        if token.type == TokNewline:
            self.line_num += 1
            if self.loud: print('')
            return self.sub_next_token()
        if self.loud: print (token.type,'', end='')
        return token

    def top_token(self):
        if self.lookahead == None:
            self.lookahead = self.sub_next_token()
        return self.lookahead

    def next_token(self):
        if self.lookahead != None:
            token, self.lookahead = self.lookahead, None
        else:
            token = self.sub_next_token()
        return token

    def jobsworth(self):
        goal = ParsedGoal(self.line_num)
        goal.funcs = []
        while self.top_token().type != TokEOF:
            try:
                goal.funcs.append(self.match_func())
            except ParsingException:
                print("Abandoning parsing\n")
                return False
            except ParsingDone: break

        return goal

    def report_parsing_exception(self, string):
        print("At line ", self.line_num, ", ", string, ", SmileyFace", sep='')
        raise ParsingException()

    def match_func(self):
        func = ParsedFunc(self.line_num)
        token = self.next_token()
        if token.type == TokInt: func.returns_int = True
        elif token.type == TokFloat: func.returns_int = False
        else: self.report_parsing_exception("Invalid function declaration")
        
        token = self.next_token()
        if token.type == TokId: func.name = token.data
        else: self.report_parsing_exception("Expected function name")

        token = self.next_token()
        if token.type != TokLparen: self.report_parsing_exception("Expected opening parantheses")

        func.arguments = self.match_args()
        #print(func.arguments, end='')

        token = self.top_token()
        if token.type != TokLcurly: self.report_parsing_exception("Expected opening braces for function definition")

        stmts = self.match_stmts()
        func.stmts = stmts.stmts
        return func

    def match_stmts(self):
        self.next_token()
        stmts = ParsedStmt4(self.line_num)
        while self.top_token().type != TokRcurly:
            stmt = self.match_stmt()
            stmts.stmts.append(stmt)
        
        self.next_token()
        return stmts
    
    def match_stmt(self):
        tt = self.top_token().type
        if tt == TokFor: return self.match_forst()
        elif tt == TokIf: return self.match_ifst()
        elif tt == TokLcurly: return self.match_stmts()
        elif tt == TokReturn: return self.match_retst()
        else:
            instr = self.match_instr()
            if self.next_token().type != TokSemicol:
                self.report_parsing_exception("Expected semicolon after instruction")
            return instr
    
    def match_forst(self):
        forst = ParsedStmt2(self.line_num)
        self.next_token()
        if self.next_token().type != TokLparen:
            self.report_parsing_exception("for statement without opening parentheses")
        forst.initialize = self.match_instr()
        if self.next_token().type != TokSemicol:
            self.report_parsing_exception("No semicolon after init")
        forst.condition = self.match_expr()
        if self.next_token().type != TokSemicol:
            self.report_parsing_exception("No semicolon after cond")
        forst.update = self.match_expr()
        if self.next_token().type != TokRparen:
            self.report_parsing_exception("What were you born in a barn or something?")
        forst.stmt = self.match_stmt()
        return forst

    def match_ifst(self):
        ifst = ParsedStmt3(self.line_num)
        self.next_token()
        if self.next_token().type != TokLparen:
            self.report_parsing_exception("Actually yes you do need to open for ifs as well")
        ifst.condition = self.match_expr()
        if self.next_token().type != TokRparen:
            self.report_parsing_exception("What were you born in a cave?")
        ifst.stmt = self.match_stmt()
        return ifst

    def match_retst(self):
        retst = ParsedStmt5(self.line_num)
        self.next_token()
        retst.expr = self.match_expr()
        if self.next_token().type != TokSemicol:
            self.report_parsing_exception("So what we don't need semicolons anymore?")
        return retst

    def match_instr(self):
        tt = self.top_token().type
        if tt == TokSemicol: return ParsedInst4(self.line_num)
        elif tt == TokInt or tt == TokFloat: return self.match_decl_1107()
        else: return self.match_expr()

    def match_expr(self):
        term = self.match_term()
        has_one_factor = len(term.factors_and_ops) == 1
        also_of_type_1 = has_one_factor and term.factors_and_ops[0].type == PitFactor1
        also_is_lhs = also_of_type_1 and term.factors_and_ops[0].op == 0
        also_equal_pending = also_is_lhs and self.top_token().type == TokEqual
        if also_equal_pending:
            self.next_token()
            expr2 = ParsedExpr2(self.line_num)
            expr2.lhs = term.factors_and_ops[0].lhs
            expr2.expr = self.match_expr()
            return expr2
        expr1 = ParsedExpr1(self.line_num)
        expr1.terms_and_ops.append(term)
        while True:
            if self.top_token().type == TokPlus:
                expr1.terms_and_ops.append(0)
            elif self.top_token().type == TokMinus:
                expr1.terms_and_ops.append(1)
            elif self.top_token().type == TokGreater:
                expr1.terms_and_ops.append(2)
            elif self.top_token().type == TokLess:
                expr1.terms_and_ops.append(3)
            else:
                break
            self.next_token()
            expr1.terms_and_ops.append(self.match_term())
        return expr1



    def match_term(self):
        term = ParsedTerm(self.line_num)
        term.factors_and_ops.append(self.match_factor())
        while True:
            if self.top_token().type == TokAsterisk:
                term.factors_and_ops.append(0)
            elif self.top_token().type == TokSlash:
                term.factors_and_ops.append(1)
            else:
                break
            self.next_token()
            term.factors_and_ops.append(self.match_factor())
        return term

    def match_factor(self):
        tt = self.top_token().type
        if tt == TokId or tt == TokPPlus:
            return self.match_factor12()
        elif tt == TokNum: return ParsedFactor3(self.line_num, int(self.next_token().data))
        elif tt == TokNum2: return ParsedFactor4(self.line_num, float(self.next_token().data))
        elif tt == TokLparen:
            self.next_token()
            factor5 = ParsedFactor5(self.line_num)
            factor5.expr = self.match_expr()
            if self.next_token().type != TokRparen:
                self.report_parsing_exception("Expected closing parentheses")
            return factor5

        self.next_token()
        if tt == TokPlus: op = 0
        elif tt == TokMinus: op = 1
        else: self.report_parsing_exception("Cannot resolve <factor>")
        factor6 = ParsedFactor6(self.line_num)
        factor6.op = op
        factor6.factor = self.match_factor()
        return factor6

    def match_factor12(self):
        token = self.next_token()
        if token.type == TokPPlus:
            op = 1
            token = self.next_token()
            if token.type != TokId:
                self.report_parsing_exception("Increment requires lhv")
            name = token.data
            expr = None
            if self.top_token().type == TokLbrack:
                self.next_token()
                expr = self.match_expr()
                if self.next_token().type != TokRbrack:
                    self.report_parsing_exception("Expected closing brackets")
        elif self.top_token().type != TokLparen:
            name = token.data
            expr = None
            if self.top_token().type == TokLbrack:
                self.next_token()
                expr = self.match_expr()
                if self.next_token().type != TokRbrack:
                    self.report_parsing_exception("Expected closing brackets")
            op = 0
            if self.top_token().type == TokPPlus:
                self.next_token()
                op = 2
        else: return self.match_factor2(token.data)
        factor1 = ParsedFactor1(self.line_num)
        factor1.lhs = (name, expr)
        factor1.op = op
        return factor1

    def match_factor2(self, name):
        factor2 = ParsedFactor2(self.line_num)
        factor2.func_name = name
        self.next_token()
        if self.top_token().type == TokRparen:
            return factor2

        if self.top_token().type == TokString: factor2.call.append(self.next_token().data)
        else: factor2.call.append(self.match_expr())
        while self.top_token().type != TokRparen:
            if self.next_token().type != TokComma:
                self.report_parsing_exception("Expected a comma or closing parentheses")
            if self.top_token().type == TokString: factor2.call.append(self.next_token().data)
            else: factor2.call.append(self.match_expr())
        self.next_token()
        return factor2

    def sub_match_decl(self):
        token = self.next_token()
        if token.type != TokId: self.report_parsing_exception("Expected variable name")
        name = token.data
        size = None
        if self.top_token().type == TokLbrack:
            self.next_token()
            if self.top_token().type != TokNum: self.report_parsing_exception("Size of array must be integer type")
            size = str(self.next_token().data)
            if self.next_token().type != TokRbrack: self.report_parsing_exception("Expected closing brackets")
        return self.top_token().type == TokComma, name, size

    def match_decl_1107(self):
        decl2 = ParsedInst2(self.line_num)
        decl2.declares_int = self.next_token().type == TokInt

        has_more = True
        while has_more:
            has_more, name, size = self.sub_match_decl()
            decl2.declarations.append((name, size))
            if has_more: self.next_token()
        
        return decl2


    def match_decl(self):
        declares_int = self.top_token().type == TokInt
        self.next_token()
        token = self.next_token()
        if token.type != TokId:
            self.report_parsing_exception("Expected variable name")
        name = token.data
        if self.top_token().type == TokLbrack:
            self.next_token()
            token = self.next_token()
            if token.type != TokNum:
                self.report_parsing_exception("Size of array must be integer type")
            size = int(token.data)
            if self.next_token().type != TokRbrack:
                self.report_parsing_exception("Expected closing brackets")
            return self.match_decl2(declares_int, name, size)
            
        else: return self.match_decl1(declares_int, name)

    def match_decl2(self, declares_int, first_name, first_size):
        inst2 = ParsedInst2(self.line_num)
        inst2.declares_int = declares_int
        inst2.declarations.append((first_name, first_size))
        while self.top_token().type == TokComma:
            self.next_token()
            token = self.next_token()
            if token.type != TokId:
                self.report_parsing_exception("Expected variable name")
            name = token.data
            if self.next_token().type != TokLbrack:
                self.report_parsing_exception("Expected opening brackets")
            token = self.next_token()
            if token.type != TokNum:
                self.report_parsing_exception("Size of array must be integer type")
            size = int(token.data)
            if self.next_token().type != TokRbrack:
                self.report_parsing_exception("Expected closing brackets")
            inst2.declarations.append((name, size))
        return inst2

    def match_decl1(self, declares_int, first_name):
        inst1 = ParsedInst1(self.line_num)
        inst1.declares_int = declares_int
        inst1.declarations.append(first_name)
        while self.top_token().type == TokComma:
            self.next_token()
            token = self.next_token()
            if token.type != TokId:
                self.report_parsing_exception("Expected variable name")
            inst1.declarations.append(token.data)
        return inst1

    def match_args(self):
        token = self.top_token()
        if token.type == TokRparen: 
            self.next_token()
            return []

        if token.type == TokVoid:
            self.next_token()
            if self.next_token().type != TokRparen:
                self.report_parsing_exception("Usually a parentheses follows void you animal")
            return [] 

        args = []
        keep_matching_args = True
        while keep_matching_args:
            keep_matching_args, arg = self.match_arg()
            args.append(arg)

        return args
    
    def match_arg(self):      
        token = self.next_token()
        is_int = True
        is_pointer = False
        if token.type == TokInt: pass
        elif token.type == TokFloat: is_int = False
        else: self.report_parsing_exception("Expected argument type")

        token = self.next_token()
        if token.type == TokAsterisk:
            is_pointer = True
            token = self.next_token()

        if token.type == TokId:
            arg = [is_int, is_pointer, token.data]
            token = self.next_token()
            if token.type == TokComma: keep_matching_args = True
            elif token.type == TokRparen: keep_matching_args = False
            else: self.report_parsing_exception("Expected closing parentheses")
            return keep_matching_args, arg
        self.report_parsing_exception("Expected argument name")


def main():
    input_file = open("testfiles/passtest94.txt")
    lex = Lex(input_file, True)
    par = Par(lex, True)
    goal = par.jobsworth()
    input_file.close()
    output_file = open("testing_par.txt", "w")
    output_file.write(str(goal))
    output_file.close()

if __name__ == "__main__":
    main()