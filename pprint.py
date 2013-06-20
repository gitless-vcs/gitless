"""Module for pretty printing Gitless output."""


import sys


def blank(p=sys.stdout.write):
  return p('#\n')

def msg(msg, p=sys.stdout.write):
  return p('# %s\n' % msg)

def exp(msg, p=sys.stdout.write):
  return p('#   (%s)\n' % msg)

def item(i, p=sys.stdout.write):
  return file(i, '', p)

def file(fp, msg, p=sys.stdout.write):
  return p('#     %s%s\n' % (fp, msg))

def sep(p=sys.stdout.write):
  return p('############################################################\n')
