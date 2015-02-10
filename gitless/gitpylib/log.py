# gitpylib - a Python library for Git.
# Licensed under GNU GPL v2.


import collections
import re

from . import common
from . import file as git_file


Commit = collections.namedtuple(
  'Commit', ['id', 'author', 'msg', 'diffs'])

CommitAuthor = collections.namedtuple(
  'CommitAuthor', ['name', 'email', 'date', 'date_relative'])

CommitDiff = collections.namedtuple(
  'CommitDiff', ['fp_before', 'fp_after', 'diff'])


def log(include_diffs=False):
  log_fmt = r'[[%H] [%an] [%ae] [%aD] [%ar]]%n%B'
  out, _ = common.safe_git_call(
      'log --format=format:"{0}" {1}'.format(
        log_fmt, '-p' if include_diffs else ''))
  return _parse_log_output(out)


def _parse_log_output(out):
  def _create_ci(m, msg, diffs):
    processed_diffs = []
    for diff in diffs:
      fp_before, fp_after = re.match(
          'diff --git a/(.*) b/(.*)', diff[0]).group(1, 2)
      processed_diffs.append(
          CommitDiff(
            fp_before, fp_after,
            git_file._process_diff_output(git_file._split_diff(diff)[1])))
    return Commit(
        m.group(1), CommitAuthor(*m.group(2, 3, 4, 5)), '\n'.join(msg),
        processed_diffs)

  if not out:
    return []

  pattern = re.compile(r'\[\[(.*)\] \[(.*)\] \[(.*)\] \[(.*)\] \[(.*)\]\]')
  out_it = iter(out.splitlines())
  m = None
  msg = None
  diffs = []
  curr_diff = None
  ret = []
  try:
    line = next(out_it)
    while True:
      m = re.match(pattern, line)
      if not m:
        raise common.UnexpectedOutputError('log', line)
      line = next(out_it)
      msg = []
      while not line.startswith('diff --git') and not line.startswith('[['):
        msg.append(line)
        line = next(out_it)
      diffs = []
      curr_diff = []
      while not line.startswith('[['):
        curr_diff.append(line)
        line = next(out_it)
        while not line.startswith('diff --git') and not line.startswith('[['):
          curr_diff.append(line)
          line = next(out_it)
        diffs.append(curr_diff)
        curr_diff = []

      ret.append(_create_ci(m, msg, diffs))
  except StopIteration:
    if curr_diff:
      diffs.append(curr_diff)
    ret.append(_create_ci(m, msg, diffs))
  return ret
