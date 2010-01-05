import unittest

from roots import list
import sexpr

def interned(L):
  return [intern(x) for x in L]

class TestSexpr(unittest.TestCase):
  def testsymbol(self):
    self.assert_(sexpr.str2sexpr('a')[0] is intern('a'))

  def teststring(self):
    self.assertEqual(sexpr.str2sexpr('"1"')[0], '1')

  def testnum(self):
    self.assertEqual(sexpr.str2sexpr('1')[0], 1)

  def testfloat(self):
    self.assertEqual(sexpr.str2sexpr('0.5')[0], 0.5)

  def testescape(self):
    self.assertEqual(sexpr.str2sexpr('\\"string\\"')[0], '"string"')

  def testemptylist(self):
    self.assertEqual(sexpr.str2sexpr('()')[0], list())

  def testshortlist(self):
    self.assertEqual(sexpr.str2sexpr('(1)')[0], list(1))

  def testlist(self):
    self.assertEqual(sexpr.str2sexpr('(a b c)')[0], list('a', 'b', 'c'))

if __name__ == '__main__':
  unittest.main()
