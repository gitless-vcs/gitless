# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.

"""Module for dealing with Git files."""


import collections
import os.path
import re

import pygit2
from sh import git


# Possible diff output lines.
DIFF_INFO = 4  # line carrying diff info for new hunk.
DIFF_SAME = 5  # line that git diff includes for context.
DIFF_ADDED = 6
DIFF_MINUS = 7


def diff(fp, curr_b):
  """Compute the diff of the given file with its last committed version.

  Args:
    fp: the path of the file to diff (e.g., 'paper.tex').

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
  # if the file is untracked, au or ignored, diff won't output stuff
  _, git_s, is_au = curr_b._status_file(fp)
  if (git_s == pygit2.GIT_STATUS_WT_NEW or
      git_s == pygit2.GIT_STATUS_IGNORED or is_au):
    diff_cmd = git.diff.bake('--', os.devnull)
  else:
    diff_cmd = git.diff.bake('HEAD', '--')

  root = curr_b.gl_repo.root
  out = str(diff_cmd(fp, _cwd=root, _tty_out=False, _ok_code=[1]))
  if not out:
    return [], 0, 0, 0, None
  header, body = _split_diff(out.splitlines())
  return _process_diff_output(body) + (header,)


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

  additions = 0
  removals = 0

  # @@ -(start of old),(length of old) +(start of new),(length of new) @@
  new_hunk_regex = r'^@@ -([0-9]+)[,]?([0-9]*) \+([0-9]+)[,]?([0-9]*) @@'
  get_info_or_zero = lambda g: 0 if g == '' else int(g)
  for line in diff_out:
    new_hunk_info = re.search(new_hunk_regex, line)
    if new_hunk_info:
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
      removals += 1
    elif line.startswith('+'):
      resulting.append(LineData(line, DIFF_ADDED, None, new_line_number))
      new_line_number += 1
      additions += 1

  max_line_digits = len(str(max_line_digits))  # digits = len(string of number).
  max_line_digits = max(MIN_LINE_PADDING, max_line_digits + 1)
  return resulting, max_line_digits, additions, removals
