# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Helper module for gl_{track, untrack, resolve}."""


from __future__ import unicode_literals

from gitless import core

from . import helpers, pprint


VOWELS = ('a', 'e', 'i', 'o', 'u')


def parser(help_msg, subcmd):
  def f(subparsers, repo):
    p = subparsers.add_parser(
        subcmd, help=help_msg, description=help_msg.capitalize())
    p.add_argument(
        'files', nargs='+', help='the file(s) to {0}'.format(subcmd),
        action=helpers.PathProcessor, repo=repo,
        skip_dir_test=repo and repo.current_branch.path_is_ignored,
        skip_dir_cb=lambda path: pprint.warn(
          'Skipped files under directory {0} since they are all '
          'ignored'.format(path)))
    p.set_defaults(func=main(subcmd))
  return f


def main(subcmd):
  def f(args, repo):
    curr_b = repo.current_branch
    success = True

    for fp in args.files:
      try:
        empty_dir = fp.endswith(core.GL_KEEP_FILENAME)
        getattr(curr_b, subcmd + '_file')(fp)
        if empty_dir:
          fp = fp.replace(core.GL_KEEP_FILENAME, '')
        pprint.ok(
            '{0} {1} is now a{2} {3}{4}d {5}'.format(
              'Empty directory' if empty_dir else 'File',
              fp, 'n' if subcmd.startswith(VOWELS) else '', subcmd,
              '' if subcmd.endswith('e') else 'e',
              'directory' if empty_dir else 'file'))
      except KeyError:
        pprint.err('Can\'t {0} non-existent file {1}'.format(subcmd, fp))
        success = False
      except ValueError as e:
        pprint.err(e)
        success = False

    return success
  return f
