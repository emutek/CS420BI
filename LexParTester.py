from LexicalStep import Lex, print_lex_to_console
from ParsingStep import Par
import sys

def main():
    if len(sys.argv) < 3:
        print("too few arguments, exiting")
        return
    file_name = sys.argv[2]
    with open(file_name) as file_input:
        if sys.argv[1] == 'lex':
            lex = Lex(file_input, True)
            print_lex_to_console(lex)
            return
        elif sys.argv[1] == 'par':
            lex = Lex(file_input, True)
            par = Par(lex, True)
            goal = par.jobsworth()
            if len(sys.argv) < 4:
                return
            file_output = open(sys.argv[3], 'w')
            file_output.write(str(goal))
        else:
            print("i'm not a software developer you know")
            return

if __name__ == "__main__":
    main()