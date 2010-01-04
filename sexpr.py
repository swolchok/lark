#!/usr/bin/env python
##
##  sexpr.py - by Yusuke Shinyama
##
##  * public domain *
##
##  Stripped down for Lark by Scott Wolchok.


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

  def __init__(self, next_filter,
               comment_begin=COMMENT_BEGIN,
               comment_end=COMMENT_END,
               separator=SEPARATOR,
               paren_begin=PAREN_BEGIN,
               paren_end=PAREN_END,
               quote=QUOTE,
               escape=ESCAPE):
    self.next_filter = next_filter
    self.comment_begin = comment_begin
    self.comment_end = comment_end
    self.separator = separator
    self.paren_begin = paren_begin
    self.paren_end = paren_end
    self.quote = quote
    self.escape = escape
    self.special = comment_begin + separator + paren_begin + paren_end + quote + escape
    self.reset()
    self.symbols = set()

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
    # NOTICE: None != nil (an empty list)
    self.build = None                   # partially constructed list.
    self.build_stack = []     # to store a chain of partial lists.
    return self


  def close_str(self):
    # XXX: need mutable strings.
    sym = ''.join(self.sym)
    self.sym = []
    return sym

  def close_symbol(self):
    sym = intern(self.close_str())
    self.symbols.add(sym)
    return sym

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
          if self.build is None:
            self.feed_next(sym)
          else:
            self.build.append(sym)
        if c in self.comment_begin:
          # comment
          self.incomment = True
        elif c in self.quote:
          # quote symbol.
          self.inquote = not self.inquote
        elif c in self.paren_begin:
          # beginning a new list.
          self.build_stack.append(self.build)
          empty = []
          if self.build == None:
            # begin from a scratch.
            self.build = empty
          else:
            # begin from the end of the current list.
            self.build.append(empty)
            self.build = empty
        elif c in self.paren_end:
          # terminating the current list
          if self.build == None:
            # there must be a working list.
            self.illegal_close_paren(i)
          else:
            if len(self.build_stack) == 1:
              # current working list is the last one in the stack.
              self.feed_next(self.build)
            self.build = self.build_stack.pop()
    return self

  # terminate
  def terminate(self):
    # a working list should not exist.
    if self.build != None:
      # error - still try to construct a partial structure.
      if self.sym:
        self.build.append(self.close_symbol())
      if len(self.build_stack) == 1:
        x = self.build
      else:
        x = self.build_stack[1]
      self.build = None
      self.build_stack = []
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


# test stuff
def test():
  assert str2sexpr('"string"') == ['string']
  assert str2sexpr('\\"string\\"') == ['"string"']
  assert str2sexpr('(this ;comment\n is (a test (sentences) (des()) (yo)))') == \
         [['this', 'is', ['a', 'test', ['sentences'], ['des', []], ['yo']]]]
  assert str2sexpr('''(paren\\(\\)theses_in\\#symbol "space in \nsymbol"
                   this\\ way\\ also. "escape is \\"better than\\" quote")''') == \
         [['paren()theses_in#symbol', 'space in \nsymbol', 'this way also.', 'escape is "better than" quote']]
  assert str2sexpr('()') == [[]]
#  str2sexpr('(this (is (a (parial (sentence')
  return  


# main
if __name__ == '__main__':
  test()
