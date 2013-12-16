# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Module for pretty printing Gitless output."""


import sys


# Stdout.

def blank(p=sys.stdout.write):
  return p('#\n')


def msg(msg, p=sys.stdout.write):
  return p('# %s\n' % msg)


def exp(msg, p=sys.stdout.write):
  return p('#   (%s)\n' % msg)


def item(i, opt_msg='', p=sys.stdout.write):
  return p('#     %s%s\n' % (i, opt_msg))


def sep(p=sys.stdout.write):
  return p(
      '########################################################################'
      '########\n')


# Err.

def err(msg, p=sys.stderr.write):
  return p('# %s\n' % msg)


def err_exp(msg, p=sys.stderr.write):
  return p('#   (%s)\n' % msg)


def err_blank(p=sys.stderr.write):
  return p('#\n')


def err_item(i, opt_msg='', p=sys.stderr.write):
  return p('#     %s%s\n' % (i, opt_msg))


# Misc.

def conf_dialog(msg):
  """Gets confirmation from the user.

  Prints a confirmation message to stdout with the given msg and waits for
  user confirmation.

  Args:
    msg: the msg to include in the confirmation.

  Returns:
    True if the user confirmed she wanted to continue or False if otherwise.
  """
  sys.stdout.write('# %s. Do you wish to continue? (y/N)' % msg)
  user_input = raw_input(' ')
  return user_input and user_input[0].lower() == 'y'


def dir_err_exp(fp, subcmd):
  """Prints the dir error exp to stderr."""
  err('{} is a directory. Can\'t {} a directory'.format(fp, subcmd))
