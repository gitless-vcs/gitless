#!/usr/bin/python

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl-log - Show commit history.

Implements the gl-log command, part of the Gitless suite.
"""

import argparse

import cmd
import lib


def main():
  parser = argparse.ArgumentParser(
      description='Show commit history')
  parser.add_argument(
      '-v', '--verbose', help='be verbose, will output the diffs of the commit',
      action='store_true')
  args = parser.parse_args()

  if args.verbose:
    lib.show_history_verbose()
  else:
    lib.show_history()
  return cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
