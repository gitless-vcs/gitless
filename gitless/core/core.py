# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's library."""


import os
import re

import pygit2
from sh import git, ErrorReturnCode

from gitless.gitpylib import stash as git_stash
from gitless.gitpylib import status as git_status


# Errors

class GlError(Exception): pass

class NotInRepoError(GlError): pass

class BranchIsCurrentError(GlError): pass

class MergeInProgressError(GlError): pass

class RebaseInProgressError(GlError): pass


def init_repository(url=None):
  """Creates a new Gitless's repository in the cwd.

  Args:
    url: if given the local repository will be a clone of the remote repository
      given by this url.

  Returns:
    the Gitless's repository created
  """
  cwd = os.getcwd()
  try:
    pygit2.discover_repository(cwd)
    raise GlError('You are already in a Gitless repository')
  except KeyError:
    # Expected
    if not url:
      repo = pygit2.init_repository(cwd)
      # We also create an initial root commit
      git.commit(allow_empty=True, m='Initialize repository')
      return repo

    try:
      git.clone(url, cwd)
    except ErrorReturnCode as e:
      raise GlError(e.stderr)

    repo = pygit2.Repository(cwd)
    # We get all remote branches as well and create local equivalents.
    for rb_name in repo.remotes['origin'].listall_branches():
      if rb_name == 'master':
        continue
      rb = repo.lookup_branch(
          'origin/{0}'.format(rb_name), pygit2.GIT_BRANCH_REMOTE)
      new_b = repo.create_branch(rb_name, rb.peel(pygit2.Commit))
      new_b.upstream = rb
    return repo


class Repository(object):
  """A Gitless's repository.

  Attributes:
    path: absolute path to the Gitless's dir (the .git dir).
    root: absolute path to the root of this repository.
    cwd: the current working directory relative to the root of this
      repository ('' if they are equal).
    current_branch: the current branch (a Branch object).
    remotes: a dictionary remote name -> Remote object.
  """

  def __init__(self):
    """Create a Repository out of the current working repository.

    Raises:
      NotInRepoError: if there's no current working repository.
    """
    try:
      path = pygit2.discover_repository(os.getcwd())
    except KeyError:
      raise NotInRepoError('You are not in a Gitless\'s repository')
    self.git_repo = pygit2.Repository(path)
    self.remotes = RemoteCollection(self.git_repo.remotes, self)


  @property
  def path(self):
    return self.git_repo.path

  @property
  def root(self):
    return self.path[:-6]  # strip trailing /.git/

  @property
  def cwd(self):
    ret = os.path.relpath(os.getcwd(), self.root)
    return '' if ret == '.' else ret

  def revparse_single(self, revision):
    return self.git_repo.revparse_single(revision)


  # Branch related methods


  @property
  def current_branch(self):
    if self.git_repo.head_is_detached:
      # Maybe we are in the middle of a rebase?
      rebase_path = os.path.join(self.git_repo.path, 'rebase-apply')
      if os.path.exists(rebase_path):
        rf = open(os.path.join(rebase_path, 'head-name'), 'r')
        # cut the refs/heads/ part that precedes the branch name
        b_name = rf.readline().strip()[11:]
      else:
        raise Exception('Gl confused')
    else:
      b_name = self.git_repo.head.shorthand
    return self.lookup_branch(b_name)


  def create_branch(self, name, commit):
    """Create a new branch.

    Args:
      name: the name of the new branch.
      commit: the commit that is to become the "head" of the new branch.
    """
    try:
      return Branch(
          self.git_repo.create_branch(name, commit, False),  # force=False
          self)
    except ValueError as e:
      # Edit pygit2's error msg (the message exposes Git details that will
      # confuse the Gitless's user)
      raise ValueError(
          str(e).replace('refs/heads/', '').replace('reference', 'branch'))

  def lookup_branch(self, branch_name):
    """Return the branch object corresponding to the given branch name."""
    git_branch = self.git_repo.lookup_branch(
        branch_name, pygit2.GIT_BRANCH_LOCAL)
    if git_branch:
      return Branch(git_branch, self)

  def listall_branches(self):
    """Return a list with the names of all the branches in this repository.

    Use lookup_branch if you want to get the Branch object corresponding to
    each name.
    """
    return self.git_repo.listall_branches(pygit2.GIT_BRANCH_LOCAL)

  def switch_current_branch(self, b, move_over=False):
    """Switches to the given branch.

    Args:
      b: the destination branch.
      move_over: if True, then uncommited changes made in the current branch are
        moved to the destination branch (defaults to False).
    """
    if b.is_current:
      raise ValueError(
          'You are already on branch {0}. No need to switch.'.format(
            b.branch_name))

    # TODO: let the user switch even if a merge or rebase is in progress
    self.current_branch._check_op_not_in_progress()

    # Helpers functions for switch

    def unmark_au_files():
      """Saves the filepaths marked as assumed unchanged and unmarks them."""
      assumed_unchanged_fps = git_status.au_files()
      if not assumed_unchanged_fps:
        return

      au_fp = os.path.join(
          self.path, 'GL_AU_{0}'.format(self.current_branch.branch_name))
      with open(au_fp, 'w') as f:
        for fp in assumed_unchanged_fps:
          f.write(fp + '\n')
          git('update-index', '--no-assume-unchanged', fp)

    def remark_au_files():
      """Re-marks files as assumed unchanged."""
      au_fp = os.path.join(self.path, 'GL_AU_{0}'.format(b.branch_name))
      if not os.path.exists(au_fp):
        return

      with open(au_fp, 'r') as f:
        for fp in f:
          fp = fp.strip()
          git('update-index', '--assume-unchanged', fp)

      os.remove(au_fp)


    # Stash doesn't save assumed unchanged files, so we save which files are
    # marked as assumed unchanged and unmark them. And when switching back we
    # look at this info and re-mark them.

    unmark_au_files()
    if not move_over:
      git_stash.all(_stash_msg(self.current_branch.branch_name))

    self.git_repo.checkout(b.git_branch)

    git_stash.pop(_stash_msg(b.branch_name))
    remark_au_files()


class RemoteCollection(object):

  def __init__(self, git_remote_collection, gl_repo):
    self.git_remote_collection = git_remote_collection
    self.gl_repo = gl_repo

  def __len__(self):
    return len(self.git_remote_collection)

  def __iter__(self):
    return (Remote(r, self.gl_repo) for r in self.git_remote_collection)

  def __getitem__(self, name):
    return Remote(self.git_remote_collection.__getitem__(name), self.gl_repo)

  def create(self, name, url):
    if '/' in name:
      raise ValueError(
          'Invalid remote name \'{0}\': remotes can\'t have \'/\''.format(name))
    if not url.strip():
      raise ValueError('Invalid url \'{0}\''.format(url))

    # Check that the given url corresponds to a git repo
    try:
      git('ls-remote', '--heads', url)
    except ErrorReturnCode as e:
      raise ValueError(e.stderr)

    self.git_remote_collection.create(name, url)

  def delete(self, name):
    self.git_remote_collection.delete(name)


class Remote(object):

  def __init__(self, git_remote, gl_repo):
    self.git_remote = git_remote
    self.gl_repo = gl_repo

  @property
  def name(self):
    return self.git_remote.name

  @property
  def url(self):
    return self.git_remote.url

  def listall_branches(self):
    """Return a list with the names of all the branches in this repository.

    Use lookup_branch if you want to get the RemoteBranch object corresponding
    to each name.
    """
    regex = re.compile(r'.*\trefs/heads/(.*)')
    for head in git('ls-remote', '--heads', self.name):
      yield regex.match(head).group(1)

  def lookup_branch(self, branch_name):
    """Return the RemoteBranch object corresponding to the given branch name."""
    if not git('ls-remote', '--heads', self.name, branch_name):
      return None
    # The branch exists in the remote
    git.fetch(self.git_remote.name, branch_name)
    git_branch = self.gl_repo.git_repo.lookup_branch(
        self.git_remote.name + '/' + branch_name, pygit2.GIT_BRANCH_REMOTE)
    return RemoteBranch(git_branch, self.gl_repo)


class RemoteBranch(object):
  """A branch that lives on some remote repository.

  Attributes:
    branch_name: the name of this branch.
    remote_name: the name of the remote that represents the remote repository
      where this branch lives.
    head: commit that is the head of this branch.
  """

  def __init__(self, git_branch, gl_repo):
    self.git_branch = git_branch
    self.gl_repo = gl_repo


  @property
  def branch_name(self):
    return self.git_branch.branch_name[len(self.remote_name) + 1:]

  @property
  def remote_name(self):
    return self.git_branch.remote_name

  @property
  def target(self):
    """Object Id of the commit this branch points to."""
    self._update()
    return self.git_branch.target

  @property
  def head(self):
    self._update()
    return self.git_branch.peel()

  def _update(self):
    git.fetch(self.remote_name, self.branch_name)
    self.git_branch = self.gl_repo.git_repo.lookup_branch(
        self.remote_name + '/' + self.branch_name, pygit2.GIT_BRANCH_REMOTE)


class Branch(object):
  """An independent line of development.

  Attributes:
    branch_name: the name of this branch.
    upstream: the upstream of this branch.
    is_current: True if this branch is the current branch in the repository it
      belongs to.
    merge_in_progress: True if a merge op is in progress in this branch.
    rebase_in_progress: True if a rebase op is in progress in this branch.
    head: commit that is the head of this branch.
  """

  def __init__(self, git_branch, gl_repo):
    self.git_branch = git_branch
    self.gl_repo = gl_repo


  def delete(self):
    if self.is_current:
      raise BranchIsCurrentError('Can\'t delete the current branch')

    branch_name = self.branch_name
    self.git_branch.delete()
    # We also cleanup any stash left.
    git_stash.drop(_stash_msg(branch_name))

  @property
  def branch_name(self):
    try:
      return self.git_branch.branch_name
    except AttributeError:
      return 'master'

  @property
  def upstream(self):
    if not self.git_branch.upstream:
      return None

    try:
      self.git_branch.upstream.remote_name
    except ValueError:
      # It is a local branch
      return Branch(self.git_branch.upstream, self.gl_repo)
    return RemoteBranch(self.git_branch.upstream, self.gl_repo)

  @upstream.setter
  def upstream(self, new_upstream):
    self.git_branch.upstream = new_upstream.git_branch if new_upstream else None

  @property
  def upstream_name(self):
    upstream = self.git_branch.upstream
    if upstream:
      return upstream.branch_name
    raise KeyError('Branch has no upstream set')

  @property
  def head(self):
    self._update()
    return self.git_branch.peel()

  @property
  def target(self):
    """Object Id of the commit this branch points to."""
    self._update()
    return self.git_branch.target

  @property
  def is_current(self):
    return self.gl_repo.current_branch.branch_name == self.branch_name

  def _update(self):
    self.git_branch = self.gl_repo.git_repo.lookup_branch(
        self.branch_name, pygit2.GIT_BRANCH_LOCAL)


  # Merge related methods

  def merge(self, src):
    """Merges the divergent changes of the src branch onto this one."""
    self._check_is_current()
    self._check_op_not_in_progress()

    result, unused_ff_conf = self.gl_repo.git_repo.merge_analysis(src.target)
    if result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
      raise GlError('Nothing to merge')
    try:
      git.merge(src.branch_name)
    except ErrorReturnCode as e:
      raise GlError(e.stdout + e.stderr)

  @property
  def merge_in_progress(self):
    try:
      self.gl_repo.git_repo.lookup_reference('MERGE_HEAD')
      return True
    except KeyError:
      return False

  def abort_merge(self):
    if not self.merge_in_progress:
      raise GlError('No merge in progress, nothing to abort')
    git.merge(abort=True)


  # Rebase related methods

  def rebase(self, src):
    self._check_is_current()
    self._check_op_not_in_progress()

    try:
      out = git.rebase(src.target)
      if re.match(r'Current branch [^\s]+ is up to date.\n', out.stdout):
        raise GlError('Nothing to rebase')
    except ErrorReturnCode as e:
      if 'Please commit or stash them' in e.stderr:
        raise GlError('Local changes would be lost')
      elif ('The following untracked working tree files would be overwritten'
          in e.stderr):
        raise GlError('Local changes would be lost')
      raise GlError('There are conflicts you need to resolve')

  @property
  def rebase_in_progress(self):
    return os.path.exists(
        os.path.join(self.gl_repo.git_repo.path, 'rebase-apply'))

  def abort_rebase(self):
    if not self.rebase_in_progress:
      raise GlError('No rebase in progress, nothing to abort')
    git.rebase(abort=True)


  def create_commit(self, files, msg, author=None):
    """Record a new commit in this branch.

    Args:
      files: the (modified) files to commit.
      msg: the commit message.
      author: the author of the commit (defaults to the default author
        according to the repository's configuration).
    """
    if not author:
      author = self.gl_repo.git_repo.default_signature

    # We replicate the behaviour of doing `git commit <file>...`
    # If file f is in the list of files to be committed => commit the working
    # version and clear the staged version.
    # If file f is not in the list of files to be committed => leave its staged
    # version (if any) intact.

    def get_tree_and_update_index():

      def update(index):
        """Add/remove files to the given index."""
        for f in files:
          if not os.path.exists(f):
            index.remove(f)
          else:
            index.add(f)

      # Update index to how it should look like after the commit
      index = self.gl_repo.git_repo.index
      index.read()
      update(index)
      index.write()

      # To create the commit tree with only the changes to the given files we:
      #   (i)   reset the index to HEAD,
      #   (ii)  update it with the changes to commit,
      #   (iii) create a tree out of this modified index, and
      #   (iv)  discard the changes after being done.
      index.read_tree(self.gl_repo.git_repo.head.peel().tree)
      update(index)
      tree_oid = index.write_tree()

      index.read()  #  discard changes

      return tree_oid


    if not (self.merge_in_progress or self.rebase_in_progress):
      self.gl_repo.git_repo.create_commit(
          # the name of the reference to update (it will point to the new
          # commit)
          self.git_branch.name,
          author, author,  # use author for committer field as well
          msg,
          get_tree_and_update_index(),  # the commit tree
          [self.git_branch.target])
      return

    # There's a merge/rebase in progress

    if self.gl_repo.git_repo.index.conflicts:
      raise GlError('Unresolved conflicts')

    # temp hack
    def internal_resolved_cleanup():
      path = self.gl_repo.path
      for f in os.listdir(path):
        if f.startswith('GL_RESOLVED'):
          os.remove(os.path.join(path, f))
          #print 'removed %s' % f

    internal_resolved_cleanup()
    if self.rebase_in_progress:
      try:
        git.rebase('--continue')
      except ErrorReturnCode as e:
        raise GlError(e.stderr)
    else:
      # do the merge commit
      self.gl_repo.git_repo.create_commit(
          self.git_branch.name,  # the reference name
          author, author,  # use author for committer field as well
          msg,
          get_tree_and_update_index(),  # the commit tree
          [self.git_branch.target,
           self.gl_repo.git_repo.lookup_reference('MERGE_HEAD').target])
      self.gl_repo.git_repo.state_cleanup()


  def publish(self, branch):
    self._check_op_not_in_progress()

    # TODO: allow publish to local branch
    try:
      assert self.branch_name.strip()
      assert branch.branch_name in self.gl_repo.remotes[
          branch.remote_name].listall_branches()

      return git.push(
          branch.remote_name,
          '{0}:{1}'.format(self.branch_name, branch.branch_name))
    except ErrorReturnCode as e:
      raise GlError(e.stderr)


  # Some helpers for checking preconditions

  def _check_op_not_in_progress(self):
    if self.merge_in_progress:
      raise MergeInProgressError('Merge in progress')
    if self.rebase_in_progress:
      raise RebaseInProgressError('Rebase in progress')

  def _check_is_current(self):
    if not self.is_current:
      raise BranchIsCurrentError(
        'Branch "{0}" is the current branch'.format(self.branch_name))


def _stash_msg(name):
  """Computes the stash msg to use for stashing changes in branch name."""
  return '---gl-{0}---'.format(name)
