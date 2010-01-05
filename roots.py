'''Roots of Lisp primitives in Python.
Let's see how far we can get embedding an Arc-like Lisp in Python.
'''

# We can't use tuples here because we need mutable cons cells.
# Objects are big and slow.
cons = lambda x, y: [x,y]
car = lambda x: x[0]
cdr = lambda x: x[1]

nil = None
# Atom is a problem: we're going to expose Python 2-tuples in our Lisp
# eventually, and those are probably atoms. Let's just get it working
# and then we'll worry about the distinction; the associated car/cdr
# implementations are bad too.
atom = lambda x: not (isinstance(x, tuple) and len(x) == 2)

# Readable types:
# - lists
# - strings
# - numbers as in Python
# - symbols

def _topylist(L):
  acc = []
  while L is not None:
    acc.append(car(L))
    L = cdr(L)
  return acc

def _toarclist(L):
  res = nil
  for x in reversed(L):
    res = cons(x, res)
  return res

def last(x):
  while cdr(x) is not nil:
    x = cdr(x)
  return x

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
  return _toarclist(args)
