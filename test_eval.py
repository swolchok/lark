import unittest

import eval
from larktypes import String
from roots import *
from symbol import *

class TestEval(unittest.TestCase):
  def teststring(self):
    self.assertEqual(eval.ac_eval(String('ab'), {}), String('ab'))

  def testint(self):
    self.assertEqual(eval.ac_eval(1, {}), 1)

  def testfloat(self):
    self.assertEqual(eval.ac_eval(0.5, {}), 0.5)

  def testvarref(self):
    self.assertEqual(eval.ac_eval(Symbol('a'), {Symbol('a'): 42}), 42)

  def testquote(self):
    self.assertEqual(eval.ac_eval([Symbol('quote'), [Symbol('a'), nil]], {}),
                     Symbol('a'))

  def testif(self):
    self.assertEqual(eval.ac_eval([Symbol('if'), nil], {}), nil)
    self.assertEqual(eval.ac_eval(list(Symbol('if'), t, 1, 2), {}), 1)

  def testfncall(self):
    # (fn (a) (if a 1 2))
    fun = list(Symbol('fn'), list(Symbol('a')),
               list(Symbol('if'), Symbol('a'), 1, 2))
    self.assertEqual(eval.ac_eval(list(fun, nil), {}), 2)
    self.assertEqual(eval.ac_eval(list(fun, String('x')), {}), 1)


if __name__ == '__main__':
  unittest.main()
