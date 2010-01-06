# Write this in pseudo-Lark. We have to take a different strategy from
# Arc because we're not on top of a Lisp or Scheme, so roots comes first
# instead of in arc.arc.

# XXX: ac-dbname and ac-nameit have been elided for now because I'm not sure
# how to translate them.

from roots import *
from sexpr import str2sexpr
from symbol import *
from larktypes import *

xcar = lambda x: car(x) if acons(x) else None

# Let's not let them poke at raw Python variables without explicitly
# exposing them.

def ac_global_name(s):
  return Symbol('_' + str(s))

EXPOSED_FUNCTIONS = (car, cdr, caar, cadr, cdar, cddr, cons,
                     list, last, append, reverse, nconc, nconc1,
                     map)

arc_globals = dict((ac_global_name(Symbol(f.func_name)), f) for f in EXPOSED_FUNCTIONS)
arc_globals[ac_global_name(t)] = t
arc_globals[ac_global_name(Symbol('+'))] = lambda *args: sum(args) 
                   

class InterpretedFunction(object):
  # Hacky, non-performant function class for interpreter.
  # When we have a bytecode compiler, life will be better.
  def __init__(self, TK):
      pass

# Evaluate an Arc expression, represented as an s-expression.
# Env is a dictionary of lexically-bound variables (symbol->value).
# Arc just has a list because Scheme actually keeps track of the variables and
# values, but in Lark we keep track of them ourselves.
def ac_eval(s, env):
  print 'DEBUG: eval %s in %s' % (s, env)
  if isinstance(s, String):
    return s
  elif literal(s):
    return s
  elif s is nil:
    return s
  elif isSymbol(s):
    print 'DEBUG: var ref'
    return ac_var_ref(s, env)
  elif xcar(s) == Symbol('quote'):
    return cadr(s)
  elif xcar(s) == Symbol('if'):
    return ac_if(cdr(s), env)
  elif xcar(s) == Symbol('fn'):
   return ac_fn(cadr(s), cddr(s), env)
  elif xcar(s) == Symbol('assign'):
    return ac_set(cdr(s), env)
  elif acons(s):
    print 'DEBUG: funcall'
    return ac_call(car(s), cdr(s), env)
  else:
    raise Exception('Bad object in expression %s (type %s)' % (s, type(s)))


def literal(x):
  return isinstance(x, bool) or isinstance(x, int) or isinstance(x, float)


def ac_var_ref(s, env):
  assert isSymbol(s)
  print 'DEBUG: Referencing %s (type %s) in env with keys' % (s, type(s)),
  for key in env:
    print key, type(key)
  if s in env:
    return env[s]
  glo = arc_globals[ac_global_name(s)]
  print 'DEBUG: returning global %s' % glo
  return glo


# Should False Python objects be false eventually?
# We're not even close to exposing Python right now, I think.
def ar_false(x):
  return x is nil or x == False

def ac_if(s, env):
  while s is not nil:
    if cdr(s) is nil:
      return ac_eval(car(s), env)
    elif not ar_false(ac_eval(car(s), env)):
      return ac_eval(cadr(s), env)
    s = cddr(s)

  return nil

def ac_fn(args, body, env):
  if ac_complex_args(args):
    raise NotImplementedError()
  elif body is nil:  # My extension to deal with empty body. No ac-body*.
    return lambda *args: nil
  else:
    env = env.copy() # Not sure if this is necessary. Being paranoid.
    print 'DEBUG: define function with argslist %s' % args
    assert isSymbol(xcar(args))
    def temp(*fargs):
      env.update(zip(args, fargs))
      return ac_body(body, env)
    return temp


def ac_body(body, env):
  if body is nil:
    return nil
  return car(revmap(lambda x: ac_eval(x, env), body))


# Elided ac_setn; it's ac_set.
def ac_set(x, env):
  if x is nil:
    return nil
  return cons(ac_set1(ac_macex(car(x)), cadr(x), env),
              ac_set(cddr(x), env))


def ac_set1(a, b1, env):
  # Omitting dbname because it's done in ac_fn too.
  if isSymbol(a):
    b = ac_eval(b1, env)
    if a is nil:
      raise Exception('Can\'t rebind nil')
    elif a is t:
      raise Exception('Can\'t rebind t')
    elif a in env:
      env[a] = b
    else:
      arc_globals[ac_global_name(a)] = b
  else:
    raise Exception('First arg to set must be a symbol! (Given %s)' % a)


def ac_macex(x):
  # STUB. TODO.
  if isSymbol(x):
    return x
  else:
    raise NotImplementedError()


def ac_complex_args(args):
  '''Does a fn arg list use optional params or destructuring?'''
  if args is nil or isSymbol(args):
    return False
  elif acons(args) and isSymbol(car(args)):
    return ac_complex_args(cdr(args))
  else:
    return True


def ac_call(fn, args, env):
  return ac_eval(fn, env)(*topylist(map(lambda x: ac_eval(x, env), args)))


def tle():
  while True:
    print 'Lark> ',
    expr = str2sexpr(raw_input())[0]
    print ac_eval(expr, {})


if __name__ == '__main__':
  tle()
