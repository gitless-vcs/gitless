#!/usr/bin/env python2.7

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl - Main Gitless's command. Dispatcher to the other cmds."""


import check_pyversion

import argparse
import sys

import cmd
import gl_track
import gl_untrack
import gl_status
import gl_diff
import gl_commit
import gl_branch
import gl_checkout
import gl_merge
import gl_rebase
import gl_remote
import gl_resolve
import gl_push
import gl_init
import gl_history
import pprint


def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()

  sub_cmds = {
      gl_track, gl_untrack, gl_status, gl_diff, gl_commit, gl_branch,
      gl_checkout, gl_merge, gl_resolve, gl_rebase, gl_remote, gl_push,
      gl_init, gl_history}
  for sub_cmd in sub_cmds:
    sub_cmd.parser(subparsers)

  args = parser.parse_args()
  return args.func(args)


if __name__ == '__main__':
  cmd.run(main)
