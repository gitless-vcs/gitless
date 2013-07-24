#!/usr/bin/env python2.7

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl-log - Show commit history.

Implements the gl-log command, part of the Gitless suite.
"""


import check_pyversion

import argparse

import history_lib

import cmd


def main():
  parser = argparse.ArgumentParser(
      description='Show commit history')
  parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  args = parser.parse_args()

  history_lib.show(verbose=args.verbose)
  return cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
