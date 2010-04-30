#! /usr/bin/env python

from string import *
import sys, codecs, getopt
from ast import *
from tokens import *
from parser import *
from grfstrings import *
from generic import ScriptError
from actions.sprite_count import SpriteCountAction
from actions.real_sprite import RealSpriteAction
from actions.action8 import Action8

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

def p_error(p):
    if p == None: print "Unexpected EOF"
    else:
        print p
        print "Syntax error at '%s', line %d" % (p.value, p.lineno)
    sys.exit(2)

import ply.yacc as yacc
parser = yacc.yacc(debug=True)

def usage():
    print "Usage: "+sys.argv[0]+" [<options>] <filenames>"
    print """
    where <filenames> are one or more nml files to parse and available options are
    -h, --help: show this help text
    Mind that you must not swap options and arguments. Options MUST go first.
    """

_debug = 0

def main(argv):
    global _debug
    _debug = 0
    retval = 0
    
    try:                  
        opts, args = getopt.getopt(argv, "hd", ["help","debug"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            _debug = 1
     
    if not args: 
        print "No input files given. Terminating."
        usage()
        sys.exit(2)
    for arg in args:
        tmp = nml(arg)
        retval = retval | tmp
    sys.exit(retval)
    
def filename_output_from_input(name):
    out_name = os.path.splitext(name)[0] + ".nfo"
    return out_name
    
def nml(inputfile):
    if not os.access(inputfile,os.R_OK):
        print "Failed to open "+inputfile
        return 2
    script = open(inputfile, 'r').read().strip()
    if script == "": print "Empty input file: "+inputfile
    result = parser.parse(script)
    
    if _debug > 0:
        print_script(result, 0)
    
    outputfile = filename_output_from_input(inputfile)
    print outputfile+": parsing "+inputfile
    
    read_extra_commands()
    read_lang_files()
    
    outf = codecs.open(outputfile, 'w', 'utf-8')
    
    actions = []
    for block in result:
        actions.extend(block.get_action_list())
    
    outf.write(
'''// Automatically generated by GRFCODEC. Do not modify!
// (Info version 7)
// Escapes: 2+ = 71 = D= = DR 2- = 70 = D+ = DF 2< = 7= = D- = DC 2> = 7! = Du* = DM 2u< = 7< = D* = DnF 2u> = 7> = Du<< = DnC 2/ = 7G = D<< = DO 2% = 7g = D& 2u/ = 7gG = D| 2u% = 7GG = Du/ 2* = 7gg = D/ 2& = 7c = Du% 2| = 7C = D% 2^ 2sto = 2s 2rst = 2r 2+ 2ror = 2rot
// Format: spritenum pcxfile xpos ypos compression ysize xsize xrel yrel

''')
    has_action8 = False
    for i in range(len(actions) - 1, -1, -1):
        if isinstance(actions[i], Action2Var):
            actions[i].resolve_tmp_storage()
        elif isinstance(actions[i], Action8):
            has_action8 = True
    
    if has_action8:
        actions = [SpriteCountAction(len(actions) - 1)] + actions
    
    sprite_num = 0
    for action in actions:
        outf.write(str(sprite_num) + " ")
        if not isinstance(action, RealSpriteAction): outf.write("* ")
        action.write(outf)
        sprite_num += 1
    
    outf.close()
    
    return 0
    
if __name__ == "__main__":
    main(sys.argv[1:])
