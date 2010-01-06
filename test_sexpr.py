import unittest

from roots import list
from symbol import *

import sexpr
import sys

def interned(L):
  return [sys.intern(x) for x in L]

class TestSexpr(unittest.TestCase):
  def testsymbol(self):
    self.assertEqual(sexpr.str2sexpr('a')[0], Symbol('a'))

  def teststring(self):
    self.assertEqual(sexpr.str2sexpr('"1"')[0], b'1')

  def testnum(self):
    self.assertEqual(sexpr.str2sexpr('1')[0], 1)

  def testfloat(self):
    self.assertEqual(sexpr.str2sexpr('0.5')[0], 0.5)

  def testescape(self):
    self.assertEqual(sexpr.str2sexpr('\\"string\\"')[0], Symbol('"string"'))

  def testemptylist(self):
    self.assertEqual(sexpr.str2sexpr('()')[0], list())

  def testshortlist(self):
    self.assertEqual(sexpr.str2sexpr('(1)')[0], list(1))

  def testlist(self):
    self.assertEqual(sexpr.str2sexpr('(a b c)')[0],
                     list(Symbol('a'), Symbol('b'), Symbol('c')))

  def testfncall(self):
    self.assertEqual(sexpr.str2sexpr('((fn (a) a) 1)')[0],
                     list(list(Symbol('fn'), list(Symbol('a')), Symbol('a')), 1))

if __name__ == '__main__':
  unittest.main()
