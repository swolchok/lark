# Write this in pseudo-Lark. We have to take a different strategy from
# Arc because we're not on top of a Lisp or Scheme, so roots comes first instead of in arc.arc.
from roots import *
from sexpr import str2sexpr
from symbol import *
from types import *

xcar = lambda x: car(x) if acons(x) else None

# Let's not let them poke at raw Python variables without explicitly
# them.

arc_globals = {nil: nil, ac_global_name(t): t}

# Evaluate an Arc expression, represented as an s-expression.
# Env is a dictionary of lexically-bound variables (symbol->value).
def ac_eval(s, env):
  if isinstance(s, String):
    return s
  elif literal(s):
    return s
  elif s is nil:
    return s
  elif isSymbol(s):
    return ac_var_ref(s, env)
  elif xcar(s) == Symbol('quote'):
    return cadr(s)
  elif xcar(s) == Symbol('if'):
    return ac_if(cdr(s), env)
#  elif xcar(s) == Symbol('fn'):
#    return ac_fn(cadr(s), cddr(s), env)
#  elif xcar(s) == Symbol('assign'):
#    return ac_set(cdr(s), env)
#  elif acons(s):
#    return ac_call(car(s), cdr(s), env)
  else:
    raise Exception('Bad object in expression %s (type %s)' % (s, type(s)))


def literal(x):
  return isinstance(x, bool) or isinstance(x, int) or isinstance(x, float)


def ac_global_name(s):
  return Symbol('_' + str(s))


def ac_var_ref(s, env):
  if s in env:
    return env[s]
  return arc_globals[ac_global_name(s)]


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

def tle():
  while True:
    print 'Lark> ',
    expr = str2sexpr(raw_input())[0]
    print ac_eval(expr, {})
