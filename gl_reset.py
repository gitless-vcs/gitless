#!/usr/bin/python

"""gl-reset - Reset files to some previous committed version.

Implements the gl-reset command, part of the Gitless suite.
"""

import argparse
import os

import cmd
import lib


def main():
  parser = argparse.ArgumentParser(
      description='Reset files to some previous committed version.')
  parser.add_argument(
      'commit_point', help='a commit point to reset the files to')
  parser.add_argument(
      'files', nargs='+',
      help='a file_pattern representing the file(s) to reset')
  args = parser.parse_args()
  cp = args.commit_point
  for fp in args.files:
    _reset_file(fp, cp)


def _reset_file(fp, cp):
  """Resets file fp to commit point cp.
  
  Will output to screen if some error is encountered.
  """
  ret = lib.reset(fp, cp)
  if ret is lib.FILE_NOT_FOUND:
    print 'Can\'t reset inexistent file %s' % fp
  elif ret is lib.FILE_IS_UNTRACKED:
    print 'Can\'t reset untracked file %s' % fp
  elif ret is lib.SUCCESS:
    print 'File %s reset sucessfully to its state at %s' % (fp, cp)
  else:
    raise Exception('Unrecognized ret code %s' % ret)



if __name__ == '__main__':
  cmd.run(main)
