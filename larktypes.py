class String(bytearray):
  def __init__(self, s):
    if isinstance(s, str):
      bytearray.__init__(self, s, 'utf-8')
    else:
      bytearray.__init__(self, s)
