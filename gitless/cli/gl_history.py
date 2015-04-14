# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl history - Show commit history."""


from __future__ import unicode_literals

from datetime import datetime, tzinfo, timedelta
import os
import subprocess
import tempfile

from clint.textui import colored, indent

from . import pprint


def parser(subparsers):
  """Adds the history parser to the given subparsers object."""
  history_parser = subparsers.add_parser(
      'history', help='show commit history')
  history_parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  history_parser.set_defaults(func=main)


def main(args, repo):
  curr_b = repo.current_branch
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
    for ci in curr_b.history():
      merge_commit = len(ci.parent_ids) > 1
      color = colored.magenta if merge_commit else colored.yellow
      if merge_commit:
        pprint.puts(color('Merge commit'), stream=tf.write)
        merges_str = ' '.join(str(oid)[:7] for oid in ci.parent_ids)
        pprint.puts(color('Merges:    {0}'.format(merges_str)), stream=tf.write)
      pprint.puts(color('Commit Id: {0}'.format(ci.id)), stream=tf.write)
      pprint.puts(
          color('Author:    {0} <{1}>'.format(ci.author.name, ci.author.email)),
          stream=tf.write)
      ci_author_dt = datetime.fromtimestamp(
          ci.author.time, FixedOffset(ci.author.offset))
      pprint.puts(
          color('Date:      {0:%c %z}'.format(ci_author_dt)), stream=tf.write)

      pprint.puts(stream=tf.write)
      with indent(4):
        pprint.puts(ci.message, stream=tf.write)
      pprint.puts(stream=tf.write)
      pprint.puts(stream=tf.write)
      if args.verbose and len(ci.parents) == 1:  # TODO: merge commits diffs
        for patch in curr_b.diff_commits(ci.parents[0], ci):
          pprint.diff(patch, stream=tf.write)
          pprint.puts(stream=tf.write)
  subprocess.call('less -r -f {0}'.format(tf.name), shell=True)
  os.remove(tf.name)
  return True


class FixedOffset(tzinfo):

  def __init__(self, offset):
    self.__offset = timedelta(minutes=offset)

  def utcoffset(self, _):
    return self.__offset

  def dst(self, _):
    return timedelta(0)
