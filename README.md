Gitless
=======

A version control system built on top of Git.

More info and documentation @ <http://people.csail.mit.edu/sperezde/gitless>.


Installing
----------

### Requirements

* You need to have Python 2.7.0+ installed, and use this instead of any Python
  3x binaries you might have installed. In other words, if you do 'python
  --version' in your shell it must output something of the kind 'Python 2.7.x'.
* You need to have a rather recent Git version, 1.7.12+ should be fine.

### Instructions

To build from source do 'make'. This will create a bin folder with compiled
python files as well as bash wrappers for the commands. Using these instead of
the .py scripts directly should be faster. Once you have the bin folder, you
can add this folder to your PATH variable or you can do 'sudo make install' and
this will install Gitless in /usr/local/gitless and create symlinks in
/usr/local/bin (make uninstall undoes this operation, make clean removes the
bin directory).


Coding
------

If you wish to modify Gitless to suit your needs or build something else out of
it this is the section for you. In this section we explain the general structure
of the code, plus some other useful tips.


### Setting up the environment

You can you can use debug-install.sh to set up the environment for rapidly
trying out your changes. This will create symlinks to the python scripts in
/usr/bin. After running this install script you can execute the gl commands by
just typing 'gl', 'gl-track', 'gl-untrack' and so. You only need to execute this
script once (unless you add some new command).


### General structure of the code

Code is architectured as follows: there are three distinct 'layers'. Starting
from the button and going up:

* *gitpylib*. This is a Python library for Git. Has methods for the most 
  frequently used Git features and abstracts the user of the library from the
  burden of having to know which is the correct command to perform some Git
  operation. This is an independent project available @
  <http://github.com/spderosso/gitpylib>.
* *Gitless lib modules*. These are the \*lib.py files. This hold all the
  Gitless-related logic.
* *Command line frontend*. These are the gl\* files and are the frontend to
  Gitless.
