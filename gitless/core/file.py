# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Gitless's file lib."""


import collections
import os
import re

from gitpylib import file as git_file
from gitpylib import status as git_status

import repo as repo_lib
import branch as branch_lib


# Ret codes of methods.
SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4
FILE_IS_UNTRACKED = 5
FILE_NOT_FOUND_AT_CP = 6
FILE_IN_CONFLICT = 7
FILE_IS_IGNORED = 8
FILE_NOT_IN_CONFLICT = 9
FILE_ALREADY_RESOLVED = 10

# Possible Gitless's file types.
TRACKED = 11
UNTRACKED = 12
IGNORED = 13

# Possible diff output lines
DIFF_INFO = 14  # line carrying diff info for new hunk
SAME = 15 # line that git diff includes for context
ADDED = 16
MINUS = 17

# diff formatting variables
MIN_LINE_PADDING = 8

# number is dictionary of {'old' and/or 'new' : integer}
LineData = collections.namedtuple('LineData', 
                           ['line', 'status', 'number'])

def track(fp):
  """Start tracking changes to fp.

  Args:
    fp: the file path of the file to track.

  Returns:
    FILE_NOT_FOUND, FILE_ALREADY_TRACKED, FILE_IN_CONFLICT, FILE_IS_IGNORED or
    SUCCESS.
  """
  f_st, s = _status(fp)
  if f_st == FILE_NOT_FOUND:
    return FILE_NOT_FOUND
  elif f_st.type == TRACKED:
    return FILE_ALREADY_TRACKED
  elif f_st.type == IGNORED:
    return FILE_IS_IGNORED

  # If we reached this point we know that the file to track is a untracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git => add the file.
  #   (ii) an assumed unchanged file => unmark it.
  if s == git_status.UNTRACKED:
    # Case (i).
    git_file.stage(fp)
  elif (s == git_status.ASSUME_UNCHANGED or
        s == git_status.DELETED_ASSUME_UNCHANGED):
    # Case (ii).
    git_file.not_assume_unchanged(fp)
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def untrack(fp):
  """Stop tracking changes to fp.

  Args:
    fp: the file path of the file to untrack.

  Returns:
    FILE_NOT_FOUND, FILE_ALREADY_UNTRACKED, FILE_IN_CONFLICT, FILE_IS_IGNORED or
    SUCCESS.
  """
  f_st, s = _status(fp)
  if f_st == FILE_NOT_FOUND:
    return FILE_NOT_FOUND
  elif f_st.type == IGNORED:
    return FILE_IS_IGNORED
  elif f_st.type == UNTRACKED:
    return FILE_ALREADY_UNTRACKED

  # If we reached this point we know that the file to untrack is a tracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git that is staged (the user executed gl track on a
  #        uncomitted file) => reset changes;
  #   (ii) the file is a previously committed file => mark it as assumed
  #        unchanged.
  if s == git_status.STAGED:
    # Case (i).
    git_file.unstage(fp)
  elif (s == git_status.TRACKED_UNMODIFIED or
        s == git_status.TRACKED_MODIFIED or
        s == git_status.DELETED):
    # Case (ii).
    git_file.assume_unchanged(fp)
  elif s == git_status.IN_CONFLICT:
    return FILE_IN_CONFLICT
  else:
    raise Exception("File %s in unkown status %s" % (fp, s))

  return SUCCESS


def diff(fp):
  """Compute the diff of the given file with its last committed version.

  Args:
    fp: the file path of the file to diff.

  Returns:
    a pair (result, out) where result is one of FILE_NOT_FOUND,
    FILE_IS_UNTRACKED or SUCCESS and out is the output of the diff command.
  """

  f_st, s = _status(fp)
  if f_st == git_status.FILE_NOT_FOUND:
    return (FILE_NOT_FOUND, '')
  elif f_st.type == UNTRACKED:
    return (FILE_IS_UNTRACKED, '')
  elif f_st.type == IGNORED:
    return (FILE_IS_IGNORED, '')

  out = ''
  if s == git_status.STAGED:
    diff_out = git_file.staged_diff(fp)
    out = diff_out.splitlines()[5:]
  elif s == git_status.ADDED_MODIFIED or s == git_status.MODIFIED_MODIFIED:
    git_file.stage(fp)
    diff_out = git_file.staged_diff(fp)
    out = diff_out.splitlines()[5:]
  elif s == git_status.DELETED:
    diff_out = git_file.diff(fp)
    out = diff_out.splitlines()[5:]
  else:
    diff_out = git_file.diff(fp)
    out = diff_out.splitlines()[4:]
  processed, max_line_digits = process_diff_output(out) 
  formatted = format_diff_output(processed, max_line_digits)
  formatted = '\n'.join(formatted)
  return (SUCCESS, formatted)

def process_diff_output(diff_out):
  """Process the git diff output

  Args:
    diff_out: A list of lines output by the git diff command

  Returns:
    A 2-tuple of a list of DiffInfo objects corresponding to each line and
    the largest number of digits in a line number
  """

  resulting = [] # accumulates line information for formatting
  max_line_digits = 0
  old_line_number = 1
  new_line_number = 1
  for line in diff_out:
    # @@ -(start of old),(length of old) +(start of new),(length of new) @@
    new_hunk_regex = "^@@ -([0-9]+),([0-9]+) \+([0-9]+),([0-9]+) @@"
    new_hunk_info = re.search(new_hunk_regex, line)
    if new_hunk_info:
      old_line_number = int(new_hunk_info.group(1))
      old_diff_length = int(new_hunk_info.group(2))
      new_line_number = int(new_hunk_info.group(3))
      new_diff_length = int(new_hunk_info.group(4))
      resulting += [LineData(
          line, DIFF_INFO, {'old' : old_line_number, 'new' : new_line_number})]
      max_line_digits = max([old_line_number + old_diff_length, 
                             new_line_number + new_diff_length,
                             max_line_digits]) # start + length of each diff
    elif line.startswith(' '):
      resulting += [LineData(
          line, SAME, {'old' : old_line_number, 'new' : new_line_number})]
      old_line_number += 1
      new_line_number += 1
    elif line.startswith('-'):
      resulting += [LineData(line, MINUS, {'old' : old_line_number})]
      old_line_number += 1
    elif line.startswith('+'):
      resulting += [LineData(line, ADDED, {'new' : new_line_number})]
      new_line_number += 1

  max_line_digits = len(str(max_line_digits)) # digits = len(string of number)
  max_line_digits = max(MIN_LINE_PADDING, max_line_digits + 1)
  return resulting, max_line_digits

def format_diff_output(processed_diff, max_line_digits):
  """Uses line-by-line diff information to format lines nicely
  
  Args:
    processed_diff: A list of LineData objects
    max_line_digits: Largest number of digits in a line number (for padding)

  Returns:
    A list of strings making up the formatted diff output
  """

  def is_unchanged(status):
    """Check if a diff status code does not correspond to + or -
  
    Args:
      status: Status code of a line
    
    Returns:
      true if status is SAME or DIFF_INFO
    """
    return status == SAME or status == DIFF_INFO

  processed = []
  for index, line_data in enumerate(processed_diff):
    # check if line is a single line diff (do diff within line if so)
    # condition: The current line was ADDED to the file AND
    # the line after is non-existent or unchanged AND
    # the line before was removed from the file AND
    # the line two before is non-existent or unchanged.
    # In other words: bold if only one line was changed in this area
    if (line_data.status == ADDED and
       (index == len(processed_diff) - 1 or 
           is_unchanged(processed_diff[index + 1].status)) and
       (index - 1 >= 0 and processed_diff[index - 1].status == MINUS) and
       (index - 2 < 0 or is_unchanged(processed_diff[index - 2].status))):
      interest = highlight(processed_diff[index-1].line[1:], line_data.line[1:])
      if interest:
        # show changed line with bolded diff in both red and green
        starts, ends = interest
        # first bold negative diff
        processed[-1] = format_line(
            processed_diff[index - 1], max_line_digits, starts[0], ends[0])
        processed += [format_line(
            line_data, max_line_digits, starts[1], ends[1])]
      else:
        processed += [format_line(line_data, max_line_digits)]
    else: 
      processed += [format_line(line_data, max_line_digits)]
  return processed

def highlight(line1, line2):
  """Given two lines, returns the sections that should be bolded if
     the twolines have a common prefix or suffix

  Args:
    line1: A line from a diff output without the first status character
    line2: See line1

  Returns:
    Two tuples.  The first tuple indicates the starts of where to bold
    and the second tuple indicated the ends.
   """
  start1 = start2 = 0
  match = re.search('\S', line1) # ignore leading whitespace
  if match:
    start1 = match.start()
  match = re.search('\S', line2)
  if match:
    start2 = match.start()
  length = min(len(line1), len(line2)) - 1
  bold_start1 = start1
  bold_start2 = start2
  while (bold_start1 <= length and bold_start2 <= length and
         line1[bold_start1] == line2[bold_start2]):
    bold_start1 += 1
    bold_start2 += 1 
  match = re.search('\s*$', line1) # ignore trailing whitespace
  bold_end1 = match.start() - 1
  match = re.search('\s*$', line2)
  bold_end2 = match.start() - 1
  while (bold_end1 >= bold_start1 and bold_end2 >= bold_start2 and
         line1[bold_end1] == line2[bold_end2]):
    bold_end1 -= 1
    bold_end2 -= 1
  if bold_start1 - start1 > 0 or len(line1) - 1 - bold_end1 > 0:
    return (bold_start1 + 1, bold_start2 + 1), (bold_end1 + 2, bold_end2 + 2)
  return None

def format_line(line_data, max_line_digits, bold_start = -1, bold_end = -1):
  """Format a standard diff line

  Args:
    line_data: A LineData tuple to be formatted
    max_line_digits: Maximum number of digits in a line number (for padding)
    bold_start: For single-line modifications, indicated where to start bolding
    bold_end: For single-line modifications, indicates where to end bolding

  Returns:
    A colored version of the diff line using ANSI control characters
  """

  # Color constants
  GREEN = '\033[32m'
  GREEN_BOLD = '\033[1;32m'
  RED = '\033[31m'
  RED_BOLD = '\033[1;31m'
  CLEAR = '\033[0m'
  line = line_data.line
  formatted = ""
  if line_data.status == SAME:
    formatted =  (str(line_data.number['old']).ljust(max_line_digits) + 
        str(line_data.number['new']).ljust(max_line_digits) + line)

  elif line_data.status == ADDED:
    formatted = (' ' * max_line_digits + GREEN + 
        str(line_data.number['new']).ljust(max_line_digits))
    if bold_start == -1:
      formatted += line
    else:
      formatted += (line[:bold_start] + GREEN_BOLD + 
          line[bold_start:bold_end] + CLEAR + GREEN + line[bold_end:])
  elif line_data.status == MINUS:
    formatted = (RED + str(line_data.number['old']).ljust(max_line_digits) + 
                 ' ' * max_line_digits)
    if bold_start == -1:
      formatted += line
    else:
      formatted += (line[:bold_start] + RED_BOLD + line[bold_start:bold_end] + 
          CLEAR + RED + line[bold_end:])
  elif line_data.status == DIFF_INFO:
    formatted = CLEAR + '\n' + line 
  return formatted + CLEAR

def checkout(fp, cp='HEAD'):
  """Checkouts file fp at cp.

  Args:
    fp: the filepath to checkout.
    cp: the commit point at which to checkout the file (defaults to HEAD).

  Returns:
    a pair (status, out) where status is one of FILE_NOT_FOUND_AT_CP or SUCCESS
    and out is the content of fp at cp.
  """
  # "show" expects the full path with respect to the repo root.
  rel_fp = os.path.join(repo_lib.cwd(), fp)[1:]
  ret, out = git_file.show(rel_fp, cp)

  if ret == git_file.FILE_NOT_FOUND_AT_CP:
    return (FILE_NOT_FOUND_AT_CP, None)

  s = git_status.of_file(fp)
  unstaged = False
  if s == git_status.STAGED:
    git_file.unstage(fp)
    unstaged = True

  dst = open(fp, 'w')
  dst.write(out)
  dst.close()

  if unstaged:
    git_file.stage(fp)

  return (SUCCESS, out)


def status(fp):
  """Gets the status of fp.

  Args:
    fp: the file to status.

  Returns:
    FILE_NOT_FOUND or a named tuple (fp, type, exists_in_lr, exists_in_wd,
    modified, in_conflict, resolved) where fp is a file path, type is one of
    TRACKED, UNTRACKED or IGNORED and all the remaining fields are booleans. The
    modified field is True if the working version of the file differs from its
    committed version (If there's no committed version, modified is set to
    True.)
  """
  return _status(fp)[0]


def status_all():
  """Gets the status of all files relative to the cwd.

  Returns:
    a list of named tuples (fp, type, exists_in_lr, exists_in_wd, modified,
    in_conflict, resolved) where fp is a file path, type is one of TRACKED,
    UNTRACKED or IGNORED and all the remaining fields are booleans. The
    modified field is True if the working version of the file differs from its
    committed version. (If there's no committed version, modified is set to
    True.)
  """
  ret = []
  for (s, fp) in git_status.of_repo():
    f_st = _build_f_st(s, fp)
    if f_st:
      ret.append(f_st)
  return ret


def resolve(fp):
  """Marks the given file in conflict as resolved.

  Args:
    fp: the file to mark as resolved.

  Returns:
    FILE_NOT_FOUND, FILE_NOT_IN_CONFLICT, FILE_ALREADY_RESOLVED or SUCCESS.
  """
  f_st = status(fp)
  if f_st == FILE_NOT_FOUND:
    return FILE_NOT_FOUND
  if not f_st.in_conflict:
    return FILE_NOT_IN_CONFLICT
  if f_st.resolved:
    return FILE_ALREADY_RESOLVED

  # In Git, to mark a file as resolved we have to add it.
  git_file.stage(fp)
  # We add a file in the Gitless directory to be able to tell when a file has
  # been marked as resolved.
  # TODO(sperezde): might be easier to just find a way to tell if the file is
  # in the index.
  open(_resolved_file(fp), 'w').close()
  return SUCCESS


def internal_resolved_cleanup():
  for f in os.listdir(repo_lib.gl_dir()):
    if f.startswith('GL_RESOLVED'):
      os.remove(os.path.join(repo_lib.gl_dir(), f))
      #print 'removed %s' % f


# Private methods.


def _status(fp):
  s = git_status.of_file(fp)
  if s == git_status.FILE_NOT_FOUND:
    return (FILE_NOT_FOUND, s)
  gls = _build_f_st(s, fp)
  if not gls:
    return (FILE_NOT_FOUND, s)
  return (gls, s)


def _build_f_st(s, fp):
  FileStatus = collections.namedtuple(
      'FileStatus', [
          'fp', 'type', 'exists_in_lr', 'exists_in_wd', 'modified',
          'in_conflict', 'resolved'])
  # TODO(sperezde): refactor this.
  ret = FileStatus(fp, UNTRACKED, False, True, True, False, False)
  if s == git_status.TRACKED_UNMODIFIED:
    ret = FileStatus(fp, TRACKED, True, True, False, False, False)
  elif s == git_status.TRACKED_MODIFIED:
    ret = FileStatus(fp, TRACKED, True, True, True, False, False)
  elif s == git_status.STAGED:
    # Staged file don't exist in the lr for Gitless.
    ret = FileStatus(fp, TRACKED, False, True, True, False, False)
  elif s == git_status.ASSUME_UNCHANGED:
    # TODO(sperezde): detect whether it is modified or not?
    ret = FileStatus(fp, UNTRACKED, True, True, True, False, False)
  elif s == git_status.DELETED:
    ret = FileStatus(fp, TRACKED, True, False, True, False, False)
  elif s == git_status.DELETED_STAGED:
    # This can only happen if the user did a rm of a new file. The file doesn't
    # exist anymore for Gitless.
    git_file.unstage(fp)
    ret = None
  elif s == git_status.DELETED_ASSUME_UNCHANGED:
    ret = None
  elif s == git_status.IN_CONFLICT:
    wr = _was_resolved(fp)
    ret = FileStatus(fp, TRACKED, True, True, True, not wr, wr)
  elif s == git_status.IGNORED or s == git_status.IGNORED_STAGED:
    ret = FileStatus(fp, IGNORED, False, True, True, True, False)
  elif s == git_status.MODIFIED_MODIFIED:
    # The file was marked as resolved and then modified. To Gitless, this is
    # just a regular tracked file.
    ret = FileStatus(fp, TRACKED, True, True, True, False, True)
  elif s == git_status.ADDED_MODIFIED:
    # The file is a new file that was added and then modified. This can only
    # happen if the user gl tracks a file and then modifies it.
    ret = FileStatus(fp, TRACKED, False, True, True, False, False)
  return ret


def _was_resolved(fp):
  """Returns True if the given file had conflicts and was marked as resolved."""
  return os.path.exists(_resolved_file(fp))


def _resolved_file(fp):
  return os.path.join(
      repo_lib.gl_dir(), 'GL_RESOLVED_%s_%s' % (branch_lib.current(), fp))
