Gitless's Release Notes
=======================

- kendall.0.1
-------------

* Before defaulting to using vim we now check to see if the user specified a
  value for Git's 'core.editor' config option or if the $EDITOR env variable is
  set.
* Added a 'Requirements' section to the installation instructions.
* Changed shebang lines to /usr/bin/env python instead of harcoding the Python
  binary at /usr/bin/python.


3rd July 2013 - kendall.0.0
---------------------------

First Gitless release.
