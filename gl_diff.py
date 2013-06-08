#!/usr/bin/python

"""gl-diff - Show changes in files.

Implements the gl-diff command, part of the Gitless suite. The gl-diff command
allows the user to show the difference between the current version of a file and
its version in the repo.
"""

import argparse

import lib


def main():
  parser = argparse.ArgumentParser(
      description="Show changes in files.")
  parser.add_argument(
      "file_pattern", help="a file_pattern representing the file(s) to diff")
  args = parser.parse_args()
  fp = args.file_pattern
  res, out = lib.diff(fp)

  if res is lib.FILE_NOT_FOUND:
    print 'Can\'t diff an inexistent file: %s' % fp
  elif res is lib.FILE_IS_UNTRACKED:
    print ('You tried to diff untracked file %s. It\'s probably a mistake. '
           'If you really care about changes in this file you should start '
           'tracking changes to it with gl track %s' % (fp, fp))
  else:
    print 'Diff of file %s with its last committed version' % fp
    print ('  (lines starting with \'-\' are lines that are not in the current '
           'version but that are present in the last committed version of the '
           'file)')
    print ('  (lines starting with \'+\' are lines that are in the current '
           'version but not in the last committed version of the file)')
    print "\n".join(out.splitlines()[4:])


if __name__ == '__main__':
  main()
