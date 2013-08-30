Gitless's Release Notes
=======================

 - kendall.0.2
---------------

* New interface for checkout (now the commit point is passed with the -cp flag;
  defaults to HEAD).
* General improvements in the gl diff command:
    * Fixed bug that made it impossible to diff a deleted file.
    * Now if no arguments are given all tracked files with modifications are
      diffed.
* Removed the gl rm command.
* Now gl is the only command (in retrospect, having a "suite of commands" was
  over-engineering, code is much simpler now).


16th July 2013 - kendall.0.1
----------------------------

* Minor improvements in output of commands.
* Improvements in Makefile and added Python version checks.
* Made case-sensitiveness consistent with FS.
* Fixed bug that made it impossible to gl-track files under directories without
  cd'ing first to that dir.
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
