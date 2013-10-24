################ Lispy: Scheme Interpreter in Python

## (c) Peter Norvig, 2010; See http://norvig.com/lispy.html

################ Symbol, Env classes

from __future__ import division

Symbol = str

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms,args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if var in self else self.outer.find(var)

def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    import math, operator as op
    env.update(vars(math)) # sin, sqrt, ...
    env.update(
     {'+':op.add, '-':op.sub, '*':op.mul, '/':op.div, 'not':op.not_,
      '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
      'equal?':op.eq, 'eq?':op.is_, 'length':len, 'cons':lambda x,y:[x]+y,
      'car':lambda x:x[0],'cdr':lambda x:x[1:], 'append':op.add,  
      'list':lambda *x:list(x), 'list?': lambda x:isa(x,list), 
      'null?':lambda x:x==[], 'symbol?':lambda x: isa(x, Symbol)})
    return env

global_env = add_globals(Env())

isa = isinstance

################ eval

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if x.t == "symbol":             # variable reference
        return env.find(x)[x]
    elif not x.t == "list":         # constant literal
        return x.i               
    
    xlist = x.l
    xcar = xlist[0]

    if xcar == 'quote':          # (quote exp)
        (_, exp) = xlist
        return exp
    elif xcar == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = xlist
        return eval((conseq if eval(test, env) else alt), env)
    elif xcar == 'set!':           # (set! var exp)
        (_, var, exp) = xlist
        env.find(var)[var] = eval(exp, env)
    elif xcar == 'define':         # (define var exp)
        (_, var, exp) = xlist
        env[var] = eval(exp, env)
    elif xcar == 'lambda':         # (lambda (var*) exp)
        (_, vars, exp) = xlost
        return lambda *args: eval(exp, Env(vars, args, env))
    elif xcar == 'begin':          # (begin exp*)
        for exp in xlist[1:]:
            val = eval(exp, env)
        return val
    else:                          # (proc exp*)
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)

################ parse, read, and user interaction
class Node(object):
    """docstring fss Node"""
    def __init__(self, t):
        self.t = t

    def to_string(self):
        if self.t=="int": return str(self.i)
        elif self.t=="float": return str(self.f)
        else: return self.s


def read(s):
    "Read a Scheme expression from a string."
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').split()

def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: 
        i = int(token)
        n = Node("int")
        n.i = i
        return n
    except ValueError:
        try:
            f = float(token)
            n = Node("float")
            n.f = f
            return n
        except ValueError:
            s = Symbol(token)
            n = Node("symbol")
            n.s = s
            return n

def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isa(exp, list) else str(exp)

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(raw_input(prompt)))
        if val is not None: print to_string(val)

if __name__ == '__main__':
    while True:
        try: repl()
        except KeyboardInterrupt:
            print "\nbye!\n"
            break
        except Exception as e: print 'Error: %s' % e