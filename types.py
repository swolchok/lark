import UserString

__all__ = ['String']
# XXX: something more efficient, perhaps?
class String(UserString.MutableString):
  pass
