# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Module for pretty printing Gitless output."""


from collections import namedtuple
import re
import sys

from clint.textui import colored, puts


SEP = (
    '##########################################################################'
    '######')

# Stdout.

def blank(p=sys.stdout.write):
  puts('#', stream=p)


def msg(text, p=sys.stdout.write):
  puts('# {0}'.format(text), stream=p)


def exp(text, p=sys.stdout.write):
  puts('#   ({0})'.format(text), stream=p)


def item(i, opt_text='', p=sys.stdout.write):
  puts('#     {0}{1}'.format(i, opt_text), stream=p)


def sep(p=sys.stdout.write):
  puts(SEP, stream=p)


# Err.

def err(text):
  msg(text, p=sys.stderr.write)


def err_exp(text):
  exp(text, p=sys.stderr.write)


def err_blank():
  blank(p=sys.stderr.write)


def err_item(i, opt_text=''):
  item(i, opt_text, p=sys.stderr.write)


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
  msg('{0}. Do you wish to continue? (y/N)'.format(text))
  user_input = get_user_input()
  return user_input and user_input[0].lower() == 'y'


def get_user_input(text='> '):
  """Python 2/3 compatible way of getting user input."""
  global input
  try:
    # Disable pylint's redefined-builtin warning and undefined-variable
    # (raw_input is undefined in python 3) error.
    # pylint: disable=W0622
    # pylint: disable=E0602
    input = raw_input
  except NameError:
    pass
  return input(text)


def dir_err_exp(fp, subcmd):
  """Prints the dir error exp to stderr."""
  err('{0} is a directory. Can\'t {1} a directory'.format(fp, subcmd))


def diff(patch, stream=sys.stdout.write):
  # Diff header

  puts('Diff of file "{0}"'.format(patch.old_file_path), stream=stream)
  if patch.old_file_path != patch.new_file_path:
    puts(colored.cyan(
        ' (renamed to {0})'.format(patch.new_file_path)), stream=stream)
    puts(stream=stream)

  if patch.is_binary:
    puts('Not showing diffs for binary file', stream=stream)
    return

  additions = patch.additions
  deletions = patch.deletions
  put_s = lambda num: '' if num == 1 else 's'
  puts('{0} line{1} added'.format(additions, put_s(additions)), stream=stream)
  puts('{0} line{1} removed'.format(deletions, put_s(deletions)), stream=stream)
  puts(stream=stream)

  # Diff body

  for hunk in patch.hunks:
    puts(stream=stream)
    _hunk(hunk, stream=stream)


LineData = namedtuple(
  'LineData', ['st', 'line', 'old_line_number', 'new_line_number'])


def _hunk(hunk, stream=sys.stdout.write):
  puts(colored.cyan('@@ -{0},{1} +{2},{3} @@'.format(
      hunk.old_start, hunk.old_lines, hunk.new_start, hunk.new_lines)),
      stream=stream)
  padding = _padding(hunk)

  del_line, add_line, maybe_bold, saw_add = None, None, False, False
  old_line_number, new_line_number = hunk.old_start, hunk.new_start

  ld = lambda st, line: LineData(st, line, old_line_number, new_line_number)

  for st, line in hunk.lines:
    line = line.rstrip('\n')

    if st == '-' and not maybe_bold:
      maybe_bold = True
      del_line = ld(st, line)
      old_line_number += 1
    elif st == '+' and maybe_bold and not saw_add:
      saw_add = True
      add_line = ld(st, line)
      new_line_number += 1
    elif st == ' ' and maybe_bold and saw_add:
      bold1, bold2 = _highlight(del_line.line, add_line.line)

      puts(_format_line(del_line, padding, bold_delim=bold1), stream=stream)
      puts(_format_line(add_line, padding, bold_delim=bold2), stream=stream)

      del_line, add_line, maybe_bold, saw_add = None, None, False, False

      puts(_format_line(ld(st, line), padding), stream=stream)
      old_line_number += 1
      new_line_number += 1
    else:
      if del_line:
        puts(_format_line(del_line, padding), stream=stream)
      if add_line:
        puts(_format_line(add_line, padding), stream=stream)

      del_line, add_line, maybe_bold, saw_add = None, None, False, False

      puts(_format_line(ld(st, line), padding), stream=stream)

      if st == '-':
        old_line_number += 1
      elif st == '+':
        new_line_number += 1
      else:
        old_line_number += 1
        new_line_number += 1


  if maybe_bold and saw_add:
    bold1, bold2 = _highlight(del_line.line, add_line.line)

    puts(_format_line(del_line, padding, bold_delim=bold1), stream=stream)
    puts(_format_line(add_line, padding, bold_delim=bold2), stream=stream)
  else:
    if del_line:
      puts(_format_line(del_line, padding), stream=stream)
    if add_line:
      puts(_format_line(add_line, padding), stream=stream)


def _padding(hunk):
  MIN_LINE_PADDING = 8

  max_line_number = max([
    hunk.old_start + hunk.old_lines, hunk.new_start + hunk.new_lines])
  max_line_digits = len(str(max_line_number))
  return max(MIN_LINE_PADDING, max_line_digits + 1)


def _format_line(line_data, padding, bold_delim=None):
  """Format a standard diff line.

  Returns:
    a colored version of the diff line using ANSI control characters.
  """
  # Color constants.
  GREEN = '\033[32m'
  GREEN_BOLD = '\033[1;32m'
  RED = '\033[31m'
  RED_BOLD = '\033[1;31m'
  CLEAR = '\033[0m'

  formatted = ''
  line = line_data.st + line_data.line

  if line_data.st == ' ':
    formatted = (
        str(line_data.old_line_number).ljust(padding) +
        str(line_data.new_line_number).ljust(padding) + line)
  elif line_data.st == '+':
    formatted = (
        ' ' * padding + GREEN +
        str(line_data.new_line_number).ljust(padding))
    if not bold_delim:
      formatted += line
    else:
      bold_start, bold_end = bold_delim
      formatted += (
          line[:bold_start] + GREEN_BOLD + line[bold_start:bold_end] + CLEAR +
          GREEN + line[bold_end:])
  elif line_data.st == '-':
    formatted = (
        RED + str(line_data.old_line_number).ljust(padding) +
        ' ' * padding)
    if not bold_delim:
      formatted += line
    else:
      bold_start, bold_end = bold_delim
      formatted += (
          line[:bold_start] + RED_BOLD + line[bold_start:bold_end] +
          CLEAR + RED + line[bold_end:])

  return formatted + CLEAR


def _highlight(line1, line2):
  """Returns the sections that should be bolded in the given lines.

  Returns:
    two tuples. Each tuple indicates the start and end of the section
    of the line that should be bolded for line1 and line2 respectively.
   """
  start1 = start2 = 0
  match = re.search(r'\S', line1)  # ignore leading whitespace.
  if match:
    start1 = match.start()
  match = re.search(r'\S', line2)
  if match:
    start2 = match.start()
  length = min(len(line1), len(line2)) - 1
  bold_start1 = start1
  bold_start2 = start2
  while (bold_start1 <= length and bold_start2 <= length and
         line1[bold_start1] == line2[bold_start2]):
    bold_start1 += 1
    bold_start2 += 1
  match = re.search(r'\s*$', line1)  # ignore trailing whitespace.
  bold_end1 = match.start() - 1
  match = re.search(r'\s*$', line2)
  bold_end2 = match.start() - 1
  while (bold_end1 >= bold_start1 and bold_end2 >= bold_start2 and
         line1[bold_end1] == line2[bold_end2]):
    bold_end1 -= 1
    bold_end2 -= 1
  if bold_start1 - start1 > 0 or len(line1) - 1 - bold_end1 > 0:
    return (bold_start1 + 1, bold_end1 + 2), (bold_start2 + 1, bold_end2 + 2)
  return None, None
