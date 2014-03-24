# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Module for pretty printing Gitless output."""


from clint.textui import puts

import re
import sys

from gitless.core import file as file_lib


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
  puts(
      '########################################################################'
      '########', stream=p)


# Err.

def err(text):
  msg(text, p=sys.stderr.write)


def err_exp(text):
  exp(text, p=sys.stderr.write)


def err_blank():
  blank(p=sys.stderr.write)


def err_item(i, opt_text='', p=sys.stderr.write):
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


def diff(processed_diff, max_line_digits, p=sys.stdout.write):
  """Uses line-by-line diff information to format lines nicely.

  Args:
    processed_diff: a list of LineData objects.
    max_line_digits: largest number of digits in a line number (for padding).
    p: a writer function (defaults to sys.stdout.write).

  Returns:
    a list of strings making up the formatted diff output.
  """

  def is_unchanged(status):
    """Check if a diff status code does not correspond to + or -.

    Args:
      status: status code of a line.

    Returns:
      True if status is file_lib.DIFF_SAME or file_lib.DIFF_INFO.
    """
    return status == file_lib.DIFF_SAME or status == file_lib.DIFF_INFO

  processed = []
  for index, line_data in enumerate(processed_diff):
    # check if line is a single line diff (do diff within line if so).
    # condition: The current line was ADDED to the file AND
    # the line after is non-existent or unchanged AND
    # the line before was removed from the file AND
    # the line two before is non-existent or unchanged.
    # In other words: bold if only one line was changed in this area.
    if (line_data.status == file_lib.DIFF_ADDED and
       (index == len(processed_diff) - 1 or
           is_unchanged(processed_diff[index + 1].status)) and
       (index - 1 >= 0 and
           processed_diff[index - 1].status == file_lib.DIFF_MINUS) and
       (index - 2 < 0 or is_unchanged(processed_diff[index - 2].status))):
      interest = _highlight(
          processed_diff[index - 1].line[1:], line_data.line[1:])
      if interest:
        # show changed line with bolded diff in both red and green.
        starts, ends = interest
        # first bold negative diff.
        processed[-1] = _format_line(
            processed_diff[index - 1], max_line_digits,
            bold_delim=(starts[0], ends[0]))
        processed += [_format_line(
            line_data, max_line_digits, bold_delim=(starts[1], ends[1]))]
      else:
        processed += [_format_line(line_data, max_line_digits)]
    else:
      processed += [_format_line(line_data, max_line_digits)]
  # TODO: print as we process.
  return p('\n'.join(processed) + '\n')


def _format_line(line_data, max_line_digits, bold_delim=None):
  """Format a standard diff line.

  Args:
    line_data: a namedtuple with the line info to be formatted.
    max_line_digits: maximum number of digits in a line number (for padding).
    bold_delim: optional arg indicate where to start/end bolding.

  Returns:
    a colored version of the diff line using ANSI control characters.
  """
  # Color constants.
  GREEN = '\033[32m'
  GREEN_BOLD = '\033[1;32m'
  RED = '\033[31m'
  RED_BOLD = '\033[1;31m'
  CLEAR = '\033[0m'

  line = line_data.line
  formatted = ''

  if line_data.status == file_lib.DIFF_SAME:
    formatted = (
        str(line_data.old_line_number).ljust(max_line_digits) +
        str(line_data.new_line_number).ljust(max_line_digits) + line)
  elif line_data.status == file_lib.DIFF_ADDED:
    formatted = (
        ' ' * max_line_digits + GREEN +
        str(line_data.new_line_number).ljust(max_line_digits))
    if not bold_delim:
      formatted += line
    else:
      bold_start, bold_end = bold_delim
      formatted += (
          line[:bold_start] + GREEN_BOLD + line[bold_start:bold_end] + CLEAR +
          GREEN + line[bold_end:])
  elif line_data.status == file_lib.DIFF_MINUS:
    formatted = (
        RED + str(line_data.old_line_number).ljust(max_line_digits) +
        ' ' * max_line_digits)
    if not bold_delim:
      formatted += line
    else:
      bold_start, bold_end = bold_delim
      formatted += (
          line[:bold_start] + RED_BOLD + line[bold_start:bold_end] +
          CLEAR + RED + line[bold_end:])
  elif line_data.status == file_lib.DIFF_INFO:
    formatted = CLEAR + '\n' + line

  return formatted + CLEAR


def _highlight(line1, line2):
  """Returns the sections that should be bolded in the given lines.

  Args:
    line1: a line from a diff output without the first status character.
    line2: see line1

  Returns:
    two tuples. The first tuple indicates the starts of where to bold
    and the second tuple indicated the ends.
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
    return (bold_start1 + 1, bold_start2 + 1), (bold_end1 + 2, bold_end2 + 2)
  return None
