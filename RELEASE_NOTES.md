Gitless's Release Notes
=======================


25th Mar 2014 - kendall.0.6.2
-----------------------------

* Bug fix.


25th Mar 2014 - kendall.0.6.1
-----------------------------

* Bug fix in installation.


25th Mar 2014 - kendall.0.6
---------------------------

* Added stats to `gl diff` (# of additions and deletions).
* Unset upstream support (`gl branch -uu`).
* Better `gl history`.
* Colored output.
* Bug fixes.


3rd Feb 2014 - kendall.0.5
--------------------------

* Now Gitless works with python 2.6, 3.2 and 3.3 (in addition to 2.7).
* A new (simpler, more consistent) `gl remote`
* Show error if user tries to `gl init` from an unreachable remote.
* When initing from a remote create a local equivalent for each remote branch.
* Bug fixes + tests + performance improvements.


16th Jan 2014 - kendall.0.4.4
-----------------------------

* More performance improvements to status.
* Bug fixes in `gl resolve`.


15th Jan 2014 - kendall.0.4.3
-----------------------------

* Fixed bug that occurred when trying to commit after a conflicted rebase/merge.
* Fixed bug that caused error msgs when a commit fails to be incorrect.


15th Jan 2014 - kendall.0.4.2
-----------------------------

* Performance improvements to `gl status` (updated to using gitpylib 0.4.2).
* `gl history` is piped to less (updated to using gitpylib 0.4.2).
* Output an error msg if the user provides a directory to file related ops.
* Sort the files outputted by `gl status` so that it looks nicer.
* Bug fixes.


6th Dec 2013 - kendall.0.4.1
----------------------------

* Bug fixes (in diff and PyPI setup).


23rd Nov 2013 - kendall.0.4
---------------------------

* Revamped `gl diff`.


28th Oct 2013 - kendall.0.3
---------------------------

* General bug fixes.
* UI improvements (made some messages more clear, consistent).
* Allow the user to branch out from certain commit point.
* Improvements to `gl diff`: now it outputs a message if the file is ignored or
  if there are no diffs to show.
* pre-commit hooks now work fine.


4th Sept 2013 - kendall.0.2.1
-----------------------------

* Bug fixes.


4th Sept 2013 - kendall.0.2
---------------------------

* Support for files with spaces.
* General improvements to the `gl checkout` command:
    * Now the commit point is passed with the `-cp` flag (defaults to `HEAD`).
    * Fixed bug that made it impossible to checkout a file without specifying
      its full repo path.
    * Ask for confirmation by the user if there are uncommitted changes that
      could be overwritten by checkout.
* General improvements to the `gl diff` command:
    * Fixed bug that made it impossible to diff a deleted file.
    * Now if no arguments are given all tracked files with modifications are
      diffed.
* Removed the `gl rm` command.
* Now `gl` is the only command (in retrospect, having a "suite of commands" was
  over-engineering, code is much simpler now).
* Massive re-org of project.


16th July 2013 - kendall.0.1
----------------------------

* Minor improvements to output of commands.
* Improvements in Makefile and added Python version checks.
* Made case-sensitiveness consistent with FS.
* Fixed bug that made it impossible to `gl-track` files under directories
  without cd'ing first to that dir.
* Better support for evil branch names.
* Before defaulting to using vim we now check to see if the user specified a
  value for Git's 'core.editor' config option or if the EDITOR env variable is
  set.
* Added a 'Requirements' section to the installation instructions.
* Changed shebang lines to /usr/bin/env python2.7 instead of harcoding the
  Python binary at /usr/bin/python.


3rd July 2013 - kendall.0.0
---------------------------

First Gitless's release.
