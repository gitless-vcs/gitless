# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Module for pretty printing Gitless output."""


import sys


# Stdout.

def blank(p=sys.stdout.write):
  return p('#\n')


def msg(text, p=sys.stdout.write):
  return p('# %s\n' % text)


def exp(text, p=sys.stdout.write):
  return p('#   (%s)\n' % text)


def item(i, opt_text='', p=sys.stdout.write):
  return p('#     %s%s\n' % (i, opt_text))


def sep(p=sys.stdout.write):
  return p(
      '########################################################################'
      '########\n')


# Err.

def err(text, p=sys.stderr.write):
  return p('# %s\n' % text)


def err_exp(text, p=sys.stderr.write):
  return p('#   (%s)\n' % text)


def err_blank(p=sys.stderr.write):
  return p('#\n')


def err_item(i, opt_text='', p=sys.stderr.write):
  return p('#     %s%s\n' % (i, opt_text))


# Misc.

def conf_dialog(text):
  """Gets confirmation from the user.

  Prints a confirmation message to stdout with the given text and waits for
  user confirmation.

  Args:
    text: the text to include in the confirmation.

  Returns:
    True if the user confirmed she wanted to continue or False if otherwise.
  """
  sys.stdout.write('# %s. Do you wish to continue? (y/N)' % text)
  # Python 2/3 compatibility.
  try:
    # Disable pylint's redefined-builtin warning and undefined-variable
    # (raw_input is undefined in python 3) error.
    # pylint: disable=W0622
    # pylint: disable=E0602
    input = raw_input
  except NameError:
    pass
  user_input = input(' ')
  return user_input and user_input[0].lower() == 'y'


def dir_err_exp(fp, subcmd):
  """Prints the dir error exp to stderr."""
  err('{0} is a directory. Can\'t {1} a directory'.format(fp, subcmd))
