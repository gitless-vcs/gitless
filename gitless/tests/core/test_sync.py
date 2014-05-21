# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Unit tests for sync module."""


import itertools

import gitless.core.file as file_lib
import gitless.core.repo as repo_lib
import gitless.core.sync as sync_lib
import gitless.tests.utils as utils_lib

from . import common


TRACKED_FP = 't_fp'
UNTRACKED_FP = 'u_fp'


class TestPartialCommit(common.TestCore):

  def setUp(self):
    super(TestPartialCommit, self).setUp()
    _setup_fp(TRACKED_FP)
    utils_lib.write_file(UNTRACKED_FP)

  def test_chunking(self):
    chunked_fp_count = 0
    chunk_count = 0
    pc = sync_lib.partial_commit([TRACKED_FP])
    all_chunks = ['chunk1', 'chunk2']
    for chunked_file in pc:
      chunked_fp_count += 1
      for chunk in chunked_file:
        chunk_count += 1
        curr_chunk = 'chunk' + str(chunk_count)
        self.__assert_expected_chunk(
            curr_chunk,
            [c for c in all_chunks if c != curr_chunk],
            _textify_diff(chunk.diff[0]))
    self.assertEqual(1, chunked_fp_count)
    self.assertEqual(2, chunk_count)

  def test_one_chunk_commit(self):
    pc = sync_lib.partial_commit([TRACKED_FP])
    for chunked_file in pc:
      for chunk in chunked_file:
        chunk.include()
        break
    pc.commit('msg')
    ci = repo_lib.history(include_diffs=True)[0]
    self.assertEqual(1, len(ci.diffs))
    self.assertEqual(TRACKED_FP, ci.diffs[0].fp_before)
    self.assertTrue('chunk1' in _textify_diff(ci.diffs[0].diff[0]))
    self.assertFalse('chunk2' in _textify_diff(ci.diffs[0].diff[0]))

  def test_all_chunks_commit(self):
    pc = sync_lib.partial_commit([TRACKED_FP])
    for chunked_file in pc:
      for chunk in chunked_file:
        chunk.include()
    pc.commit('msg')
    ci = repo_lib.history(include_diffs=True)[0]
    self.assertEqual(1, len(ci.diffs))
    self.assertEqual(TRACKED_FP, ci.diffs[0].fp_before)
    self.assertTrue('chunk1' in _textify_diff(ci.diffs[0].diff[0]))
    self.assertTrue('chunk2' in _textify_diff(ci.diffs[0].diff[0]))

  def test_basic_multiple_files(self):
    TRACKED_FP_2 = 't_fp2'
    _setup_fp(TRACKED_FP_2)
    pc = sync_lib.partial_commit([TRACKED_FP, TRACKED_FP_2])
    # Just the first chunk of each file.
    for chunked_file in pc:
      for chunk in chunked_file:
        chunk.include()
        break
    pc.commit('msg')
    ci = repo_lib.history(include_diffs=True)[0]
    self.assertEqual(2, len(ci.diffs))
    self.assertEqual(TRACKED_FP, ci.diffs[0].fp_before)
    self.assertEqual(TRACKED_FP_2, ci.diffs[1].fp_before)
    t_fp_diff = _textify_diff(ci.diffs[0].diff[0])
    t_fp_2_diff = _textify_diff(ci.diffs[1].diff[0])
    self.assertTrue(_chunk_i(TRACKED_FP, 1) in t_fp_diff)
    self.assertFalse(_chunk_i(TRACKED_FP, 2) in t_fp_diff)
    self.assertTrue(_chunk_i(TRACKED_FP_2, 1) in t_fp_2_diff)
    self.assertFalse(_chunk_i(TRACKED_FP_2, 2) in t_fp_2_diff)

  def __assert_expected_chunk(self, expected_chunk, other_chunks, out):
    self.assertTrue(
        expected_chunk in out,
        msg='{0} not found in output'.format(expected_chunk))
    for other_chunk in other_chunks:
      self.assertFalse(
          other_chunk in out, msg='{0} found in output'.format(other_chunk))


def _textify_diff(diff):
  return '\n'.join([ld.line for ld in diff])


def _chunk_i(fp, i):
  return '{0}-chunk{1}'.format(fp, i)


def _setup_fp(fp):
  utils_lib.write_file(fp, contents=_chunk('contents'))
  file_lib.track(fp)
  sync_lib.commit([fp], 'msg')
  new_contents = (
      _chunk(_chunk_i(fp, 1)) + utils_lib.read_file(fp) +
      _chunk(_chunk_i(fp, 2)))
  utils_lib.write_file(fp, contents=new_contents)


def _chunk(content_id):
  CHUNK_SIZE = 10
  contents = ''
  for _ in itertools.repeat(None, CHUNK_SIZE):
    contents += '{0}\n'.format(content_id)
  return contents
