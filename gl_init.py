#!/usr/bin/env python2.7

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl-init - Create an empty repo or create one from an existing.

Implements the gl-init command, part of the Gitless suite.
"""


import check_pyversion

import argparse

import cmd
import lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description=(
          'Create an empty Gitless\'s repository or create one from an '
          'existing remote repository.'))
  parser.add_argument(
      'repo', nargs='?', help='an optional repo path to create the repo from')
  args = parser.parse_args()
  errors_found = False

  if args.repo:
    ret = lib.init_from_repo(args.repo)
  else:
    ret = lib.init_dir()

  if ret is lib.REPO_UNREACHABLE:
    pprint.err('Couldn\'t reach repository %s' % args.repo)
    pprint.err_exp('make sure you are connected to the internet')
    pprint.err_exp('make sure you have the necessary permissions')
    return cmd.ERRORS_FOUND
  elif ret is lib.NOTHING_TO_INIT:
    pprint.err('Nothing to init, this directory is already a Gitless\'s repo')
    return cmd.ERRORS_FOUND
  elif ret is lib.SUCCESS:
    pprint.msg('Gitless\'s local repository created successfully')
    return cmd.SUCCESS
  else:
    raise Exception('Unexpected return code %s' % ret)


if __name__ == '__main__':
  cmd.run(main, is_init=True)
