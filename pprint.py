"""Module for pretty printing Gitless output."""


def msg(msg, p):
  return p('# %s\n' % msg)

def exp(msg, p):
  return p('#   (%s)\n' % msg)

def file(fp, msg, p):
  return p('#     %s%s\n' % (fp, msg))

def sep(p):
  return p('############################################################\n')
