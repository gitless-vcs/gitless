# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""Helper module for gl_{track, untrack, resolve}."""


import os

import pprint

from gitless.core import file as file_lib


VOWELS = ('a', 'e', 'i', 'o', 'u')


def parser(help_msg, subcmd):
  def f(subparsers):
    p = subparsers.add_parser(
        subcmd, help=help_msg)
    p.add_argument(
        'files', nargs='+', help='the file(s) to {}'.format(subcmd))
    p.set_defaults(func=main(subcmd))
  return f


def main(subcmd):
  def f(args):
    success = True

    for fp in args.files:
      ret = getattr(file_lib, subcmd)(fp)
      if ret == file_lib.FILE_NOT_FOUND:
        pprint.err('Can\'t {} a non-existent file: {}'.format(subcmd, fp))
        success = False
      elif ret == file_lib.FILE_IS_DIR:
        pprint.dir_err_exp(fp, subcmd)
        success = False
      elif ret is file_lib.FILE_ALREADY_UNTRACKED:
        pprint.err('File {} is already untracked'.format(fp))
        success = False
      elif ret is file_lib.FILE_ALREADY_TRACKED:
        pprint.err('File {} is already tracked'.format(fp))
        success = False
      elif ret is file_lib.FILE_IS_IGNORED:
        pprint.err('File {} is ignored. Nothing to {}'.format(fp, subcmd))
        pprint.err_exp(
            'edit the .gitignore file to stop ignoring file {}'.format(fp))
        success = False
      elif ret is file_lib.FILE_IN_CONFLICT:
        pprint.err('Can\'t {} a file in conflict'.format(subcmd))
        success = False
      elif ret is file_lib.FILE_NOT_IN_CONFLICT:
        pprint.err('File {} has no conflicts'.format(fp))
        success = False
      elif ret is file_lib.FILE_ALREADY_RESOLVED:
        pprint.err(
            'Nothing to resolve. File {} was already marked as resolved'.format(
                fp))
        success = False
      elif ret is file_lib.SUCCESS:
        pprint.msg(
            'File {} is now a{} {}{}d file'.format(
                fp, 'n' if subcmd.startswith(VOWELS) else '', subcmd,
                '' if subcmd.endswith('e') else 'e'))
      else:
        raise Exception('Unexpected return code {}'.format(ret))

    return success
  return f
