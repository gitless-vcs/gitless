# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Module for dealing with Git files."""


import collections
import os.path
import re

from . import common


SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_NOT_FOUND_AT_CP = 3

# Possible diff output lines.
DIFF_INFO = 4  # line carrying diff info for new hunk.
DIFF_SAME = 5  # line that git diff includes for context.
DIFF_ADDED = 6
DIFF_MINUS = 7


def stage(fp):
  """Stages the given file.

  Args:
    fp: the path of the file to stage (e.g., 'paper.tex').

  Returns:
    - SUCCESS: the operation completed successfully.
    - FILE_NOT_FOUND: the given file doesn't exist.
  """
  if not os.path.exists(fp):
    return FILE_NOT_FOUND

  fp = common.real_case(fp)

  common.safe_git_call('add "{0}"'.format(fp))
  return SUCCESS


def unstage(fp):
  """Unstages the given file.

  Args:
    fp: the path of the file to unstage (e.g., 'paper.tex').

  Returns:
    - SUCCESS: the operation completed successfully.
  """
  fp = common.real_case(fp)

  # "git reset" currently returns 0 (if successful) while "git reset
  # $pathspec" returns 0 iff the index matches HEAD after resetting (on all
  # paths, not just those matching $pathspec). See
  # http://comments.gmane.org/gmane.comp.version-control.git/211242.
  # So, we need to ignore the return code (unfortunately) and hope that it
  # works.
  common.git_call('reset HEAD "{0}"'.format(fp))
  return SUCCESS


def show(fp, cp):
  """Gets the contents of file fp at commit cp.

  Args:
    fp: the file path to get contents from.
    cp: the commit point.

  Returns:
    a pair (status, out) where status is one of FILE_NOT_FOUND_AT_CP or SUCCESS
    and out is the content of fp at cp.
  """
  fp = common.real_case(fp)

  ok, out, _ = common.git_call('show {0}:"{1}"'.format(cp, fp))

  if not ok:
    return FILE_NOT_FOUND_AT_CP, None

  return SUCCESS, out


def assume_unchanged(fp):
  """Marks the given file as assumed unchanged.

  Args:
    fp: the path of the file to mark as assumed unchanged.

  Returns:
    - SUCCESS: the operation completed successfully.
  """
  fp = common.real_case(fp)

  common.safe_git_call('update-index --assume-unchanged "{0}"'.format(fp))
  return SUCCESS


def not_assume_unchanged(fp):
  """Unmarks the given assumed unchanged file.

  Args:
    fp: the path of the file to unmark as assumed unchanged.

  Returns:
    - SUCCESS: the operation completed successfully.
  """
  fp = common.real_case(fp)

  common.safe_git_call('update-index --no-assume-unchanged "{0}"'.format(fp))
  return SUCCESS


def diff(fp, staged=False):
  """Compute the diff of the given file with its last committed version.

  Args:
    fp: the path of the file to diff (e.g., 'paper.tex').
    staged: True if a staged diff should be done.

  Returns:
    a 4-tuple of:
      - a list of namedtuples with fields 'line', 'status', 'old_line_number'
      and 'new_line_number' where 'status' is one of DIFF_INFO, DIFF_SAME,
      DIFF_ADDED or DIFF_MINUS and 'old_line_number', 'new_line_number'
      correspond to the line's old line number and new line number respectively.
      (Note that, for example, if the line is DIFF_ADDED, then 'old_line_number'
      is None since that line is not present in the old file).
      - max_line_digits: the maximum amount of line digits found while parsing
      the git diff output, this is useful for padding.
      - number of lines added.
      - number of lines removed.
      - header (the diff header as a list of lines).
  """
  fp = common.real_case(fp)

  st = '--cached' if staged else ''
  out, _ = common.safe_git_call('diff {0} -- "{1}"'.format(st, fp))
  if not out:
    return [], 0, 0, 0, None
  stats_out, _ = common.safe_git_call(
      'diff {0} --numstat -- "{1}"'.format(st, fp))
  header, body = _split_diff(out.splitlines())
  line, padding = _process_diff_output(body)
  additions, removals = _process_diff_stats_output(stats_out)
  return line, padding, additions, removals, header


# Private functions.


def _split_diff(diff_out):
  """Splits the diff output into the diff header and body."""
  first_non_header_line = 0
  for line in diff_out:
    if line.startswith('@@'):
      break
    first_non_header_line += 1
  return diff_out[:first_non_header_line], diff_out[first_non_header_line:]


def _process_diff_output(diff_out):
  MIN_LINE_PADDING = 8
  LineData = collections.namedtuple(
      'LineData',
      ['line', 'status', 'old_line_number', 'new_line_number'])

  resulting = []  # accumulates line information for formatting.
  max_line_digits = 0
  old_line_number = 1
  new_line_number = 1

  # @@ -(start of old),(length of old) +(start of new),(length of new) @@
  new_hunk_regex = r'^@@ -([0-9]+)[,]?([0-9]*) \+([0-9]+)[,]?([0-9]*) @@'
  for line in diff_out:
    new_hunk_info = re.search(new_hunk_regex, line)
    if new_hunk_info:
      get_info_or_zero = lambda g: 0 if g == '' else int(g)
      old_line_number = get_info_or_zero(new_hunk_info.group(1))
      old_diff_length = get_info_or_zero(new_hunk_info.group(2))
      new_line_number = get_info_or_zero(new_hunk_info.group(3))
      new_diff_length = get_info_or_zero(new_hunk_info.group(4))
      resulting.append(
          LineData(line, DIFF_INFO, old_line_number, new_line_number))
      max_line_digits = max([old_line_number + old_diff_length,
                             new_line_number + new_diff_length,
                             max_line_digits])  # start + length of each diff.
    elif line.startswith(' '):
      resulting.append(
          LineData(line, DIFF_SAME, old_line_number, new_line_number))
      old_line_number += 1
      new_line_number += 1
    elif line.startswith('-'):
      resulting.append(LineData(line, DIFF_MINUS, old_line_number, None))
      old_line_number += 1
    elif line.startswith('+'):
      resulting.append(LineData(line, DIFF_ADDED, None, new_line_number))
      new_line_number += 1

  max_line_digits = len(str(max_line_digits))  # digits = len(string of number).
  max_line_digits = max(MIN_LINE_PADDING, max_line_digits + 1)
  return resulting, max_line_digits


def _process_diff_stats_output(diff_stats_out):
  # format is additions tab removals.
  m = re.match(r'([0-9]+)\t([0-9]+)', diff_stats_out)
  return int(m.group(1)), int(m.group(2))
