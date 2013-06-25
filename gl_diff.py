#!/usr/bin/python

"""gl-diff - Show changes in files.

Implements the gl-diff command, part of the Gitless suite. The gl-diff command
allows the user to show the difference between the current version of a file and
its version in the repo.
"""

import argparse

import cmd
import lib
import pprint


def main():
  parser = argparse.ArgumentParser(
      description="Show changes in files.")
  parser.add_argument(
      "file", help="the file to diff")
  args = parser.parse_args()
  fp = args.file
  ret, out = lib.diff(fp)
  errors_found = False

  if ret is lib.FILE_NOT_FOUND:
    pprint.err('Can\'t diff an inexistent file: %s' % fp)
    errors_found = True
  elif ret is lib.FILE_IS_UNTRACKED:
    ppring.err(
        'You tried to diff untracked file %s. It\'s probably a mistake. If you '
        'really care about changes in this file you should start tracking '
        'changes to it with gl track %s' % (fp, fp))
    errors_found = True
  elif ret is lib.SUCCESS:
    pprint.msg('Diff of file %s with its last committed version' % fp)
    pprint.exp(
        'lines starting with \'-\' are lines that are not in the current '
        'version but that are present in the last committed version of the '
        'file')
    pprint.exp (
        'lines starting with \'+\' are lines that are in the current version '
        'but not in the last committed version of the file')
    pprint.msg("\n".join(out.splitlines()[4:]))
  else:
    raise Exception('Unrecognized ret code %s' % ret)

  return cmd.ERRORS_FOUND if errors_found else cmd.SUCCESS


if __name__ == '__main__':
  cmd.run(main)
