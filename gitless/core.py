# -*- coding: utf-8 -*-
# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's library."""


from __future__ import unicode_literals

import collections
import io
from locale import getpreferredencoding
import os
import re
import sys

import pygit2
from sh import git, ErrorReturnCode


IS_PY2 = sys.version_info[0] == 2
ENCODING = getpreferredencoding() or 'utf-8'


# Errors

class GlError(Exception): pass

class NotInRepoError(GlError): pass

class BranchIsCurrentError(GlError): pass

class MergeInProgressError(GlError): pass

class RebaseInProgressError(GlError): pass


# File status

GL_STATUS_UNTRACKED = 1
GL_STATUS_TRACKED = 2
GL_STATUS_IGNORED = 3


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
  except KeyError:  # Expected
    if not url:
      repo = pygit2.init_repository(cwd)
      # We also create an initial root commit
      git.commit(allow_empty=True, m='Initialize repository')
      return repo

    try:
      git.clone(url, cwd)
    except ErrorReturnCode as e:
      raise GlError(stderr(e))

    # We get all remote branches as well and create local equivalents.
    repo = Repository()
    remote = repo.remotes['origin']
    for rb in (remote.lookup_branch(bn) for bn in remote.listall_branches()):
      if rb.branch_name == 'master':
        continue
      new_b = repo.create_branch(rb.branch_name, rb.head)
      new_b.upstream = rb
    return repo


class Repository(object):
  """A Gitless's repository.

  Attributes:
    path: absolute path to the Gitless's dir (the .git dir).
    root: absolute path to the root of this repository.
    cwd: the current working directory relative to the root of this
      repository ('' if they are equal).
    config: the repository's configuration.
    current_branch: the current branch (a Branch object).
    remotes: the configured remotes (see RemoteCollection).
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
    self.path = self.git_repo.path
    self.root = self.path[:-6]  # strip trailing /.git/
    self.config = self.git_repo.config

  @property
  def cwd(self):
    ret = os.path.relpath(os.getcwd(), self.root)
    return '' if ret == '.' else ret

  def revparse_single(self, revision):
    if '/' in revision:
      # Might be a remote branch
      remote, remote_branch = revision.split('/', 1)
      try:
        return self.remotes[remote].lookup_branch(remote_branch).head
      except KeyError:
        pass

    return self.git_repo.revparse_single(revision)


  # Branch related methods


  @property
  def current_branch(self):
    if self.git_repo.head_is_detached:
      # Maybe we are in the middle of a rebase?
      rebase_path = os.path.join(self.path, 'rebase-apply')
      if os.path.exists(rebase_path):
        rf = io.open(
            os.path.join(rebase_path, 'head-name'), mode='r', encoding=ENCODING)
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

    curr_b = self.current_branch

    # TODO: let the user switch even if a merge or rebase is in progress
    curr_b._check_op_not_in_progress()

    # Helper functions for switch

    def au_fp(branch):
      return os.path.join(
          self.path, 'GL_AU_{0}'.format(branch.branch_name.replace('/', '_')))

    def unmark_au_files():
      """Saves the filepaths marked as assumed unchanged and unmarks them."""
      assumed_unchanged_fps = curr_b._au_files()
      if not assumed_unchanged_fps:
        return

      with io.open(au_fp(curr_b), mode='w', encoding=ENCODING) as f:
        for fp in assumed_unchanged_fps:
          f.write(fp + '\n')
          git('update-index', '--no-assume-unchanged', fp,
              _cwd=self.root)

    def remark_au_files():
      """Re-marks files as assumed unchanged."""
      au = au_fp(b)
      if not os.path.exists(au):
        return

      with io.open(au, mode='r', encoding=ENCODING) as f:
        for fp in f:
          git('update-index', '--assume-unchanged', fp.strip(),
              _cwd=self.root)

      os.remove(au)


    # Stash doesn't save assumed unchanged files, so we save which files are
    # marked as assumed unchanged and unmark them. And when switching back we
    # look at this info and re-mark them.

    unmark_au_files()
    if not move_over:
      git.stash.save('--all', '--', _stash_msg(curr_b.branch_name))

    self.git_repo.checkout(b.git_branch)

    s_id = _stash_id(_stash_msg(b.branch_name))
    if s_id:
      git.stash.pop(s_id)

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
      raise ValueError(stderr(e))

    self.git_remote_collection.create(name, url)

  def delete(self, name):
    self.git_remote_collection.delete(name)


class Remote(object):
  """Tracked remote repository.

  Attributes:
    name: the name of this remote.
    url: the url of this remote.
  """

  def __init__(self, git_remote, gl_repo):
    self.git_remote = git_remote
    self.gl_repo = gl_repo
    self.name = self.git_remote.name
    self.url = self.git_remote.url


  def listall_branches(self):
    """Return a list with the names of all the branches in this repository.

    Use lookup_branch if you want to get the RemoteBranch object corresponding
    to each name.
    """
    regex = re.compile(r'.*\trefs/heads/(.*)')
    for head in stdout(git('ls-remote', '--heads', self.name)).splitlines():
      yield regex.match(head).group(1)

  def lookup_branch(self, branch_name):
    """Return the RemoteBranch object corresponding to the given branch name."""
    if not stdout(git('ls-remote', '--heads', self.name, branch_name)):
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
    self.remote_name = self.git_branch.remote_name
    self.branch_name = self.git_branch.branch_name[len(self.remote_name) + 1:]

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
    self.branch_name = self.git_branch.branch_name


  def delete(self):
    if self.is_current:
      raise BranchIsCurrentError('Can\'t delete the current branch')

    branch_name = self.branch_name
    self.git_branch.delete()

    # We also cleanup any stash left
    s_id = _stash_id(_stash_msg(branch_name))
    if s_id:
      git.stash.drop(s_id)

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

  def history(self):
    return self.gl_repo.git_repo.walk(
        self.target, pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_TIME)

  def diff_commits(self, c1, c2):
    return c1.tree.diff_to_tree(c2.tree)

  @property
  def _index(self):
    """Convenience wrapper of Git's index."""
    class Index(object):

      def __init__(self, git_index):
        self._git_index = git_index
        self._git_index.read()

      def __enter__(self):
        return self

      def __exit__(self, type, value, traceback):
        if not value:  # no exception
          self._git_index.write()
          return True

      def __getattr__(self, name):
        return getattr(self._git_index, name)

    return Index(self.gl_repo.git_repo.index)

  _st_map = {
    # git status: gl status, exists_at_head, exists_in_wd, modified

    pygit2.GIT_STATUS_CURRENT: (GL_STATUS_TRACKED, True, True, False),
    pygit2.GIT_STATUS_IGNORED: (GL_STATUS_IGNORED, False, True, True),

    ### WT_* ###
    pygit2.GIT_STATUS_WT_NEW: (GL_STATUS_UNTRACKED, False, True, True),
    pygit2.GIT_STATUS_WT_MODIFIED: (GL_STATUS_TRACKED, True, True, True),
    pygit2.GIT_STATUS_WT_DELETED: (GL_STATUS_TRACKED, True, False, True),

    ### INDEX_* ###
    pygit2.GIT_STATUS_INDEX_NEW: (GL_STATUS_TRACKED, False, True, True),
    pygit2.GIT_STATUS_INDEX_MODIFIED: (GL_STATUS_TRACKED, True, True, True),
    pygit2.GIT_STATUS_INDEX_DELETED: (GL_STATUS_TRACKED, True, False, True),

    ### WT_NEW | INDEX_* ###
    # WT_NEW | INDEX_NEW -> can't happen
    # WT_NEW | INDEX_MODIFIED -> can't happen
    # WT_NEW | INDEX_DELETED -> could happen if user broke gl layer (e.g., did
    # `git rm` and then created file with same name). Also, for some reason,
    # files with conflicts have this status code
    pygit2.GIT_STATUS_WT_NEW | pygit2.GIT_STATUS_INDEX_DELETED: (
      GL_STATUS_TRACKED, True, True, True),

    ### WT_MODIFIED | INDEX_* ###
    pygit2.GIT_STATUS_WT_MODIFIED | pygit2.GIT_STATUS_INDEX_NEW: (
      GL_STATUS_TRACKED, False, True, True),
    pygit2.GIT_STATUS_WT_MODIFIED | pygit2.GIT_STATUS_INDEX_MODIFIED: (
      GL_STATUS_TRACKED, True, True, True),
    # WT_MODIFIED | INDEX_DELETED -> can't happen

    ### WT_DELETED | INDEX_* ### -> can't happen
    }

  FileStatus = collections.namedtuple(
    'FileStatus', [
        'fp', 'type', 'exists_at_head', 'exists_in_wd', 'modified',
        'in_conflict'])

  def _au_files(self):
    for f_out in stdout(git('ls-files', '-v', _cwd=self.gl_repo.root)).splitlines():
      if f_out[0] == 'h':
        yield f_out[2:].strip()

  def status(self):
    """Return a generator of file statuses (see FileStatus).

    Ignored and tracked unmodified files are not reported.
    File paths are always relative to the repo root.
    """
    index = self._index

    for fp, git_s in self.gl_repo.git_repo.status().items():
      in_conflict = False
      if index.conflicts:
        try:  # `fp in index.conflicts` doesn't work
          index.conflicts[fp]
          in_conflict = True
        except KeyError:
          pass
      yield self.FileStatus(fp, *(self._st_map[git_s] + (in_conflict,)))

    # status doesn't report au files
    au_files = self._au_files()
    if au_files:
      for fp in au_files:
        exists_in_wd = os.path.exists(os.path.join(self.gl_repo.root, fp))
        yield self.FileStatus(
            fp, GL_STATUS_UNTRACKED, True, exists_in_wd, True, False)

  def status_file(self, path):
    """Return the status (see FileStatus) of the given path."""
    return self._status_file(path)[0]

  def _status_file(self, path):
    assert not os.path.isabs(path)

    git_s = self.gl_repo.git_repo.status_file(path)

    cmd_out = stdout(git(
      'ls-files', '-v', '--full-name', path, _cwd=self.gl_repo.root))
    if cmd_out and cmd_out[0] == 'h':
      exists_in_wd = os.path.exists(os.path.join(self.gl_repo.root, path))
      return (
          self.FileStatus(
            path, GL_STATUS_UNTRACKED, True, exists_in_wd, True, False),
          git_s, True)

    index = self._index
    in_conflict = False
    if index.conflicts:
      try:  # `fp in index.conflicts` doesn't work
        index.conflicts[path]
        in_conflict = True
      except KeyError:
        pass
    f_st = self.FileStatus(path, *(self._st_map[git_s] + (in_conflict,)))
    return f_st, git_s, False


  # File related methods

  def track_file(self, path):
    """Start tracking changes to path."""
    assert not os.path.isabs(path)

    gl_st, git_st, is_au = self._status_file(path)

    if gl_st.type == GL_STATUS_TRACKED:
      raise ValueError('File {0} is already tracked'.format(path))
    elif gl_st.type == GL_STATUS_IGNORED:
      raise ValueError(
          'File {0} is ignored. Edit the .gitignore file to stop ignoring '
          'file {0}'.format(path))

    # If we reached this point we know that the file to track is a untracked
    # file. This means that in the Git world, the file could be either:
    #   (i)  a new file for Git => add the file;
    #   (ii) an assumed unchanged file => unmark it.
    if git_st == pygit2.GIT_STATUS_WT_NEW:  # Case (i)
      with self._index as index:
        index.add(path)
    elif is_au:  # Case (ii)
      git('update-index', '--no-assume-unchanged', path,
          _cwd=self.gl_repo.root)
    else:
      raise GlError('File {0} in unkown status {1}'.format(path, git_st))

  def untrack_file(self, path):
    """Stop tracking changes to the given path."""
    assert not os.path.isabs(path)

    gl_st, git_st, is_au = self._status_file(path)

    if gl_st.type == GL_STATUS_UNTRACKED:
      raise ValueError('File {0} is already untracked'.format(path))
    elif gl_st.type == GL_STATUS_IGNORED:
      raise ValueError(
          'File {0} is ignored. Edit the .gitignore file to stop ignoring '
          'file {0}'.format(path))
    elif gl_st.in_conflict:
      raise ValueError('File {0} has conflicts'.format(path))

    # If we reached this point we know that the file to untrack is a tracked
    # file. This means that in the Git world, the file could be either:
    #   (i)  a new file for Git that is staged (the user executed `gl track` on
    #        an uncomitted file) => reset changes;
    #   (ii) the file is a previously committed file => mark it as assumed
    #        unchanged.
    if git_st == pygit2.GIT_STATUS_INDEX_NEW:  # Case (i)
      with self._index as index:
        index.remove(path)
    elif not is_au:  # Case (ii)
      git('update-index', '--assume-unchanged', path,
          _cwd=self.gl_repo.root)
    else:
      raise GlError('File {0} in unkown status {1}'.format(path, git_st))

  def resolve_file(self, path):
    """Mark the given path as resolved."""
    assert not os.path.isabs(path)

    gl_st, _, _ = self._status_file(path)
    if not gl_st.in_conflict:
      raise ValueError('File {0} has no conflicts'.format(path))

    with self._index as index:
      index.add(path)

  def checkout_file(self, path, commit):
    """Checkouts the given path at the given commit."""
    assert not os.path.isabs(path)

    data = self.gl_repo.git_repo[commit.tree[path].id].data
    with io.open(os.path.join(self.gl_repo.root, path), mode='wb') as dst:
      dst.write(data)

    # So as to not get confused with the status of the file we also add it
    with self._index as index:
      index.add(path)

  def diff_file(self, path):
    """Diff the working version of the given path with its committed version."""
    assert not os.path.isabs(path)

    git_repo = self.gl_repo.git_repo
    try:
      blob_at_head = git_repo[git_repo.head.peel().tree[path].id]
    except KeyError:  # no blob at head
      wt_blob = git_repo[git_repo.create_blob_fromworkdir(path)]
      nil_blob = git_repo[git_repo.create_blob('')]
      return nil_blob.diff(wt_blob, 0, path, path)

    try:
      wt_blob = git_repo[git_repo.create_blob_fromworkdir(path)]
    except KeyError:  # no blob at wd (the file was deleted)
      nil_blob = git_repo[git_repo.create_blob('')]
      return blob_at_head.diff(nil_blob, 0, path, path)

    return blob_at_head.diff(wt_blob, 0, path, path)


  # Merge related methods

  def merge(self, src):
    """Merges the divergent changes of the src branch onto this one."""
    self._check_is_current()
    self._check_op_not_in_progress()

    result, unused_ff_conf = self.gl_repo.git_repo.merge_analysis(src.target)
    if result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
      raise GlError('Nothing to merge')
    try:
      git.merge(src.branch_name, '--no-ff')
    except ErrorReturnCode as e:
      raise GlError(stdout(e) + stderr(e))

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
      out = stdout(git.rebase(src.target))
      if re.match(r'Current branch [^\s]+ is up to date.\n', out):
        raise GlError('Nothing to rebase')
    except ErrorReturnCode as e:
      err_msg = stderr(e)
      if 'Please commit or stash them' in err_msg:
        raise GlError('Local changes would be lost')
      elif ('The following untracked working tree files would be overwritten'
          in err_msg):
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
      index = self._index
      with index:
        update(index)

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
    index = self._index
    if index.conflicts:
      raise GlError('Unresolved conflicts')

    if self.rebase_in_progress:
      try:
        git.rebase('--continue')
      except ErrorReturnCode as e:
        raise GlError(stderr(e))
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

    if not isinstance(branch, RemoteBranch):  # TODO: allow this
      raise GlError(
          'Can\'t publish to a local branch (yet---this will be implemented in '
          'the future)')

    try:
      assert self.branch_name.strip()
      assert branch.branch_name in self.gl_repo.remotes[
          branch.remote_name].listall_branches()

      cmd = git.push(
          branch.remote_name,
          '{0}:{1}'.format(self.branch_name, branch.branch_name))
      if 'Everything up-to-date' in stderr(cmd):
        raise GlError('No commits to publish')
    except ErrorReturnCode as e:
      err_msg = stderr(e)
      if 'Updates were rejected' in err_msg:
        raise GlError('There are changes you need to rebase/merge')
      raise GlError(err_msg)


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


# Some helpers for stashing

def _stash_id(msg):
  """Gets the stash id of the stash with the given msg.

  Args:
    msg: the message of the stash to retrieve.

  Returns:
    the stash id of the stash with the given msg or None if no matching stash is
    found.
  """
  out = stdout(git.stash.list(grep=': {0}'.format(msg), _tty_out=False))

  if not out:
    return None

  result = re.match(r'(stash@\{.+\}): ', out)
  if not result:
    raise GlError('Unexpected output of git stash: {0}'.format(out))

  return result.group(1)


def _stash_msg(name):
  """Computes the stash msg to use for stashing changes in branch name."""
  return '---gl-{0}---'.format(name)


# Misc

def stdout(p):
  return p.stdout.decode(ENCODING)


def stderr(p):
  return p.stderr.decode(ENCODING)
