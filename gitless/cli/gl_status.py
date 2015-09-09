# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl status - Show the status of files in the repo."""


from __future__ import unicode_literals

import os

from clint.textui import colored

from gitless import core

from . import helpers, pprint


def parser(subparsers, repo):
  """Adds the status parser to the given subparsers object."""
  desc = 'show status of the repo'
  status_parser = subparsers.add_parser(
      'status', help=desc, description=desc.capitalize())
  status_parser.add_argument(
      'paths', nargs='*', help='the specific path(s) to status',
      action=helpers.PathProcessor, repo=repo)
  status_parser.set_defaults(func=main)


def main(args, repo):
  curr_b = repo.current_branch
  pprint.msg('On branch {0}, repo-directory {1}'.format(
    colored.green(curr_b.branch_name), colored.green('//' + repo.cwd)))

  if curr_b.merge_in_progress:
    pprint.blank()
    _print_conflict_exp('merge')
  elif curr_b.fuse_in_progress:
    pprint.blank()
    _print_conflict_exp('fuse')

  tracked_mod_list = []
  untracked_list = []
  paths = frozenset(args.paths)
  for f in curr_b.status():
    if paths and (f.fp not in paths):
      continue
    if f.type == core.GL_STATUS_TRACKED and f.modified:
      tracked_mod_list.append(f)
    elif f.type == core.GL_STATUS_UNTRACKED:
      untracked_list.append(f)

  relative_paths = True  # git seems to default to true
  try:
    relative_paths = repo.config.get_bool('status.relativePaths')
  except KeyError:
    pass

  pprint.blank()
  tracked_mod_list.sort(key=lambda f: f.fp)
  _print_tracked_mod_files(tracked_mod_list, relative_paths, repo)
  pprint.blank()
  pprint.blank()
  untracked_list.sort(key=lambda f: f.fp)
  _print_untracked_files(untracked_list, relative_paths, repo)
  return True


def _print_tracked_mod_files(tracked_mod_list, relative_paths, repo):
  pprint.msg('Tracked files with modifications:')
  pprint.exp('these will be automatically considered for commit')
  pprint.exp(
      'use gl untrack f if you don\'t want to track changes to file f')
  pprint.exp(
      'if file f was committed before, use gl checkout f to discard '
      'local changes')
  pprint.blank()

  if not tracked_mod_list:
    pprint.item('There are no tracked files with modifications to list')
    return

  root = repo.root
  for f in tracked_mod_list:
    exp = ''
    color = colored.yellow
    if not f.exists_at_head:
      exp = ' (new file)'
      color = colored.green
    elif not f.exists_in_wd:
      exp = ' (deleted)'
      color = colored.red
    elif f.in_conflict:
      exp = ' (with conflicts)'
      color = colored.cyan

    fp = os.path.relpath(os.path.join(root, f.fp)) if relative_paths else f.fp
    if fp == '.':
      continue

    pprint.item(color(fp), opt_text=exp)


def _print_untracked_files(untracked_list, relative_paths, repo):
  pprint.msg('Untracked files:')
  pprint.exp('these won\'t be considered for commit')
  pprint.exp('use gl track f if you want to track changes to file f')
  pprint.blank()

  if not untracked_list:
    pprint.item('There are no untracked files to list')
    return

  root = repo.root
  for f in untracked_list:
    exp = ''
    color = colored.blue
    if f.in_conflict:
      exp = ' (with conflicts)'
      color = colored.cyan
    elif f.exists_at_head:
      color = colored.magenta
      if f.exists_in_wd:
        exp = ' (exists at head)'
      else:
        exp = ' (exists at head but not in working directory)'

    fp = os.path.relpath(os.path.join(root, f.fp)) if relative_paths else f.fp
    if fp == '.':
      continue

    pprint.item(color(fp), opt_text=exp)


def _print_conflict_exp(op):
  pprint.msg(
      'You are in the middle of a {0}; all conflicts must be resolved before '
      'commiting'.format(op))
  pprint.exp(
      'use gl {0} --abort to go back to the state before the {0}'.format(op))
  pprint.exp('use gl resolve f to mark file f as resolved')
  pprint.exp('once you solved all conflicts do gl commit to continue')
  pprint.blank()
