# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Some helpers for commands."""


from __future__ import unicode_literals

import argparse
import os
import subprocess
import sys
import shlex
import shutil

from gitless import core

from . import pprint


def get_branch(branch_name, repo):
  return _get_ref("branch", branch_name, repo)


def get_tag(tag_name, repo):
  return _get_ref("tag", tag_name, repo)


def _get_ref(ref_type, ref_name, repo):
  ref_type_cap = ref_type.capitalize()
  r = getattr(repo, "lookup_" + ref_type)(ref_name)
  if not r:
    if '/' not in ref_name:
      raise ValueError(
          '{0} "{1}" doesn\'t exist'.format(ref_type_cap, ref_name))

    # It might be a remote ref
    remote, remote_ref = ref_name.split('/', 1)
    try:
      remote_repo = repo.remotes[remote]
    except KeyError:
      raise ValueError(
          'Remote "{0}" doesn\'t exist, and there is no local '
          '{1} "{2}"'.format(remote, ref_type_cap, ref_name))

    r = getattr(remote_repo, "lookup_" + ref_type)(remote_ref)
    if not r:
      raise ValueError('{0} "{1}" doesn\'t exist in remote "{2}"'.format(
          ref_type_cap, remote_ref, remote))
  return r


def get_branch_or_use_upstream(branch_name, arg, repo):
  if not branch_name: # use upstream branch
    current_b = repo.current_branch
    upstream_b = current_b.upstream
    if not upstream_b:
      raise ValueError(
          'No {0} branch specified and the current branch has no upstream '
          'branch set'.format(arg))

    ret = current_b.upstream
    pprint.warn(
        'No {0} branch specified, using upstream branch {1}'.format(arg, ret))
  else:
    ret = get_branch(branch_name, repo)
  return ret


def page(fp, repo):
  if not sys.stdout.isatty():  # we are being piped or redirected
    if sys.platform != 'win32':
      # Prevent Python from throwing exceptions on SIGPIPE
      from signal import signal, SIGPIPE, SIG_DFL
      signal(SIGPIPE, SIG_DFL)
    # memory-friendly way to output contents of file to stdout
    with open(fp, 'r') as f:
      shutil.copyfileobj(f, sys.stdout)
    return

  # On Windows, we need to call 'more' through cmd.exe (with 'cmd'). The /C is
  # so that the command window gets closed after 'more' finishes
  default_pager = 'less' if sys.platform != 'win32' else 'cmd /C more'
  try:
    pager = repo.config['core.pager']
  except KeyError:
    pager = '' # empty string will evaluate to False below
  pager = pager or os.environ.get('PAGER', None) or default_pager
  cmd = shlex.split(pager) # split into constituents
  if os.path.basename(cmd[0]) == 'less':
    cmd.extend(['-r', '-f']) # append arguments

  cmd.append(fp) # add file name to page command
  try:
    ret = subprocess.call(cmd, stdin=sys.stdin, stdout=sys.stdout)
    if ret != 0:
      pprint.err('Call to pager {0} failed'.format(pager))
  except OSError:
    pprint.err('Couldn\'t launch pager {0}'.format(pager))
    pprint.err_exp('change the value of git\'s core.pager setting')


class PathProcessor(argparse.Action):

  def __init__(
      self, option_strings, dest, repo=None, skip_dir_test=None,
      skip_dir_cb=None, **kwargs):
    self.repo = repo
    self.skip_dir_test = skip_dir_test
    self.skip_dir_cb = skip_dir_cb
    super(PathProcessor, self).__init__(option_strings, dest, **kwargs)

  def __call__(self, parser, namespace, paths, option_string=None):
    root = self.repo.root if self.repo else ''
    repo_dir = self.repo.path[:-1] if self.repo else ''  # strip trailing /
    def process_paths():
      for path in paths:
        path = os.path.abspath(path)
        if os.path.isdir(path):
          for curr_dir, dirs, fps in os.walk(path, topdown=True):
            if curr_dir.startswith(repo_dir):
              dirs[:] = []
              continue
            curr_dir_rel = os.path.relpath(curr_dir, root)
            if (curr_dir_rel != "." and self.skip_dir_test and
                self.skip_dir_test(curr_dir_rel)):
              if self.skip_dir_cb:
                self.skip_dir_cb(curr_dir_rel)
              dirs[:] = []
              continue
            for fp in fps:
              yield os.path.join(curr_dir_rel, fp)
        else:
          if not path.startswith(repo_dir):
            yield os.path.relpath(path, root)

    setattr(namespace, self.dest, process_paths())


class CommitIdProcessor(argparse.Action):

  def __init__(self, option_strings, dest, repo=None, **kwargs):
    self.repo = repo
    super(CommitIdProcessor, self).__init__(option_strings, dest, **kwargs)

  def __call__(self, parser, namespace, revs, option_string=None):
    cids = (self.repo.revparse_single(rev).id for rev in revs)
    setattr(namespace, self.dest, cids)


def oei_flags(subparsers, repo):
  subparsers.add_argument(
      '-o', '--only', nargs='+',
      help='use only files given (files must be tracked modified or untracked)',
      action=PathProcessor, repo=repo, metavar='file')
  subparsers.add_argument(
      '-e', '--exclude', nargs='+',
      help='exclude files given (files must be tracked modified)',
      action=PathProcessor, repo=repo, metavar='file')
  subparsers.add_argument(
      '-i', '--include', nargs='+',
      help='include files given (files must be untracked)',
      action=PathProcessor, repo=repo, metavar='file')


def oei_fs(args, repo):
  """Compute the final fileset per oei flags."""
  only = frozenset(args.only if args.only else [])
  exclude = frozenset(args.exclude if args.exclude else [])
  include = frozenset(args.include if args.include else [])

  curr_b = repo.current_branch
  if not _oei_validate(only, exclude, include, curr_b):
    raise ValueError('Invalid input')

  if only:
    ret = only
  else:
    # Tracked modified files
    ret = frozenset(
        f.fp for f in curr_b.status()
        if f.type == core.GL_STATUS_TRACKED and f.modified) # using generator expression
    # We get the files from status with forward slashes. On Windows, these
    # won't match the paths provided by the user, which are normalized by
    # PathProcessor
    if sys.platform == 'win32':
      ret = frozenset(p.replace('/', '\\') for p in ret)
    ret -= exclude
    ret |= include

  ret = sorted(list(ret))
  return ret


def _oei_validate(only, exclude, include, curr_b):
  """Validates user input per oei flags.

  This function will print to stderr in case user-provided values are invalid
  (and return False).

  Returns:
    True if the input is valid, False if otherwise.
  """
  if only and (exclude or include):
    pprint.err(
        'You provided a list of filenames to be committed only (-o) but also '
        'provided a list of files to be excluded (-e) or included (-i)')
    return False

  err = []

  def validate(fps, check_fn, msg):
    ''' fps: files
        check_fn: lambda(file) -> boolean
        msg: string-format of pre-defined constant string.
    '''
    ret = True
    if not fps:
      return ret
    for fp in fps:
      try:
        f = curr_b.status_file(fp)
      except KeyError:
        err.append('File {0} doesn\'t exist'.format(fp))
        ret = False # set error flag, but keep assessing other files
      else: # executed after "try", exception will be ignored here
        if not check_fn(f):
          err.append(msg(fp)) # dynamic string formatting
          ret = False
    return ret

  only_valid = validate(
      only, lambda f: f.type == core.GL_STATUS_UNTRACKED or (
          f.type == core.GL_STATUS_TRACKED and f.modified),
      'File {0} is not a tracked modified or untracked file'.format)
  exclude_valid = validate(
      exclude, lambda f: f.type == core.GL_STATUS_TRACKED and f.modified,
      'File {0} is not a tracked modified file'.format)
  include_valid = validate(
      include, lambda f: f.type == core.GL_STATUS_UNTRACKED,
      'File {0} is not an untracked file'.format)

  if only_valid and exclude_valid and include_valid:
    return True

  for e in err:
    pprint.err(e)
  return False
