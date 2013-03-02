#!/usr/bin/env python
##
##  sexpr.py - by Yusuke Shinyama
##
##  * public domain *
##
##  Stripped down for Lark by Scott Wolchok.

from roots import cons, list, nconc1
from larktypes import String
from symbol import *

class SExprIllegalClosingParenError(ValueError):
  pass
class SExprIllegalClosingQuoteError(ValueError):
  pass
class SExprPrematureEOFError(ValueError):
  pass

class SExprReader(object):
  '''Usage:
  
  reader = SExprReader(consumer)
  reader.feed('(this is (sexpr))')
  reader.close()
  '''
  
  COMMENT_BEGIN = ';'
  COMMENT_END = '\n'
  SEPARATOR = ' \t\n'
  PAREN_BEGIN = '('
  PAREN_END = ')'
  QUOTE = '"'
  ESCAPE = '\\'
  LISP_QUOTE = '\''

  def __init__(self, next_filter,
               comment_begin=COMMENT_BEGIN,
               comment_end=COMMENT_END,
               separator=SEPARATOR,
               paren_begin=PAREN_BEGIN,
               paren_end=PAREN_END,
               quote=QUOTE,
               lisp_quote = LISP_QUOTE,
               escape=ESCAPE):
    self.next_filter = next_filter
    self.comment_begin = comment_begin
    self.comment_end = comment_end
    self.separator = separator
    self.paren_begin = paren_begin
    self.paren_end = paren_end
    self.quote = quote
    self.lisp_quote = lisp_quote
    self.escape = escape
    self.special = comment_begin + separator + paren_begin + paren_end + quote + escape # + lisp_quote
    self.reset()

  # called if redundant parantheses are found.
  def illegal_close_quote(self, i):
    raise SExprIllegalClosingQuoteError(i)
  def illegal_close_paren(self, i):
    raise SExprIllegalClosingParenError(i)
  def premature_eof(self, i, x):
    raise SExprPrematureEOFError(i, x)

  # reset the internal states.
  def reset(self):
    self.incomment = False              # if within a comment.
    self.inquote = False                # if within a quote
    self.inescape = False               # if within a escape.
    self.sym = []                       # partially constructed symbol.
    self.build_stack = []     # to store a chain of partial lists.
    return self


  def _close_helper(self):
    sym = ''.join(self.sym)
    self.sym = []
    return sym

  def close_str(self):
    return String(self._close_helper())

  def close_symbol(self):
    s = self._close_helper()

    if s == '#t':
      return True
    elif s == '#f':
      return False
    elif s.startswith('#\\'):
      rest = s[2:]
      if rest == 'newline':
        return '\n'
      elif rest == 'space':
        return ' '
      elif rest == 'return':
        return '\r'
      elif rest == 'tab':
        return '\t'
      elif len(rest) == 1:
        return rest
      else:
        raise Exception('Illegal character literal %d!' % s)
    try:
      return int(s)
    except ValueError:
      pass

    try:
      return float(s)
    except ValueError:
      pass

    return Symbol(s)

  def feed_next(self, s):
    self.next_filter.feed(s)

  # analyze strings
  def feed(self, tokens):
    for (i,c) in enumerate(tokens):
      if self.incomment:
        # within a comment - skip
        self.incomment = (c not in self.comment_end)
      elif self.inescape or (c not in self.special):
        # add to the current working symbol
        self.sym.append(c)
        self.inescape = False
      elif c in self.escape:
        # escape
        self.inescape = True
      elif self.inquote and (c not in self.quote):
        self.sym.append(c)
      else:
        # special character (blanks, parentheses, or comment)
        if self.sym:
          # close the current symbol
          if self.inquote:
            if c not in self.quote:
              self.illegal_close_quote(i)
            sym = self.close_str()
          else:
            sym = self.close_symbol()
          if not self.build_stack:
            self.feed_next(sym)
          else:
            self.build_stack[-1] = nconc1(self.build_stack[-1], sym)
        if c in self.comment_begin:
          # comment
          self.incomment = True
        elif c in self.quote:
          # quote symbol.
          self.inquote = not self.inquote
        elif c in self.paren_begin:
          # beginning a new list.
          self.build_stack.append(nil)
        elif c in self.paren_end:
          if not self.build_stack:
            # there must be a working list.
            self.illegal_close_paren(i)
          else:
            build = self.build_stack.pop()
            if self.build_stack:
              self.build_stack[-1] = nconc1(self.build_stack[-1], build)
            else:
              self.feed_next(build)
    return self

  # terminate
  def terminate(self):
    # a working list should not exist.
    if self.build_stack:
      # error - still try to construct a partial structure.
      if self.sym:
        self.build_stack[-1].append(self.close_symbol())
      x = self.build_stack[-1]
      self.premature_eof(len(self.build_stack), x)
    elif self.sym:
      # flush the current working symbol.
      self.feed_next(self.close_symbol())
    return self

  # closing.
  def close(self):
    self.terminate()


##  str2sexpr
##
class _SExprStrConverter(object):
  results = []
  def feed(self, s):
    _SExprStrConverter.results.append(s)
    return
_str_converter = SExprReader(_SExprStrConverter())
# _str_converter_strict = StrictSExprReader(_SExprStrConverter())

def str2sexpr(s):
  '''parse a string as a sexpr.'''
  _SExprStrConverter.results = []
  _str_converter.reset().feed(s).terminate()
  return _SExprStrConverter.results
# def str2sexpr_strict(s):
#   '''parse a string as a sexpr.'''
#   _SExprStrConverter.results = []
#   _str_converter_strict.reset().feed(s).terminate()
#   return _SExprStrConverter.results


##  sexpr2str
##
def sexpr2str(e):
  '''convert a sexpr into Lisp-like representation.'''
  if not isinstance(e, list):
    return e
  return '('+' '.join(map(sexpr2str, e))+')'
