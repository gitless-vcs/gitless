# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Helper module for gl_{track, untrack, resolve}."""


from __future__ import unicode_literals

import os

from . import pprint


VOWELS = ('a', 'e', 'i', 'o', 'u')


def parser(help_msg, subcmd):
  def f(subparsers):
    p = subparsers.add_parser(subcmd, help=help_msg)
    p.add_argument(
        'files', nargs='+', help='the file(s) to {0}'.format(subcmd))
    p.set_defaults(func=main(subcmd))
  return f


def main(subcmd):
  def f(args, repo):
    curr_b = repo.current_branch
    success = True

    root = repo.root
    for fp in args.files:
      try:
        getattr(curr_b, subcmd + '_file')(os.path.relpath(fp, root))
        pprint.msg(
            'File {0} is now a{1} {2}{3}d file'.format(
              fp, 'n' if subcmd.startswith(VOWELS) else '', subcmd,
              '' if subcmd.endswith('e') else 'e'))
      except KeyError:
        pprint.err('Can\'t {0} a non-existent file: {1}'.format(subcmd, fp))
        success = False
      except ValueError as e:
        pprint.err(e)
        success = False

    return success
  return f
