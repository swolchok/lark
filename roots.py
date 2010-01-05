'''Roots of Lisp primitives in Python.
Let's see how far we can get embedding an Arc-like Lisp in Python.
'''
from symbol import *

# Functions we'll expose eventually need to be defined with def or they
# won't have names.

# We can't use tuples here because we need mutable cons cells.
# Objects are big and slow.
def cons(x,y):
  return [x, y]
def car(x):
  return x[0]
def cdr(x):
  return x[1]

def caar(x):
  return x[0][0]
def cadr(x):
  return x[1][0]
def cdar(x):
  return x[0][1]
def cddr(x):
  return x[1][1]

pylist = list

# Atom is a problem: we're going to expose Python 2-tuples in our Lisp
# eventually, and those are probably atoms. Let's just get it working
# and then we'll worry about the distinction; the associated car/cdr
# implementations are bad too.
def acons(x): 
  return isinstance(x, pylist) and len(x) == 2

def atom(x):
  return not acons(x)

# Readable types:
# - lists
# - strings
# - numbers as in Python
# - symbols

def topylist(L):
  acc = []
  while L is not nil:
    acc.append(car(L))
    L = cdr(L)
  return acc

def toarclist(L):
  res = nil
  for x in reversed(L):
    res = cons(x, res)
  return res

def last(x):
  while cdr(x) is not nil:
    x = cdr(x)
  return x


def revappend(x, y):
#   if x is nil:
#     return y
#   return revappend(cdr(x), cons(car(x), y))
  while x is not nil:
    y = cons(car(x), y)
    x = cdr(x)
  return y

def reverse(x):
  return revappend(x, nil)

def append(x, y):
  return revappend(reverse(x), y)

def nconc(x, y):
  if x is nil:
    return y
  else:
    # XXX: representation dependent.
    last(x)[1] = y
    return x

def nconc1(x, y):
  return nconc(x, list(y))

def list(*args):
  return toarclist(args)

def revmap(func, L):
#   def rec(func, L, acc):
#     if L is nil:
#       return acc
#     return rec(func, cdr(L), cons(func(car(L)), acc))
#   return rec(func, L, nil)
  acc = nil
  while L is not nil:
    acc = cons(func(car(L)), acc)
    L = cdr(L)
  return acc

def map(func, L):
  # TODO: nreverse.
  return reverse(revmap(func, L))
