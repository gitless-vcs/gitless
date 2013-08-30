Gitless
=======

A version control system built on top of Git.

More info and documentation @ <http://people.csail.mit.edu/sperezde/gitless>.


Installing
----------

### Requirements

* You need to have Python 2.7.0+ installed.
* You need to have a rather recent Git version, 1.7.12+ should be fine.

### Instructions

To build from source do 'make'. This will create a bin folder with compiled
python files as well as a bash wrapper for the 'gl' command. Using this instead
of the .py script directly should be faster. Once you have the bin folder, you
can add this folder to your PATH variable or you can do 'sudo make install' and
this will install Gitless in /usr/local/gitless and create a symlink in
/usr/local/bin (make uninstall undoes this operation, make clean removes the
bin directory).


Coding
------

### Setting up the environment

You can you can do 'make debug-install' to set up the environment for rapidly
trying out your changes. This will create a symlink to the 'gl' python script in
/usr/local/bin. You can then execute the 'gl' command by just typing 'gl' in
your shell. You only need to execute this script once.


### General structure of the code

There are three distinct 'layers'; starting
from the bottom and going up:

* *gitpylib*. This is a Python library for Git. Has methods for the most 
  frequently used Git features and abstracts the user of the library from the
  burden of having to know which is the correct command to perform some Git
  operation. This is an independent project available @
  <http://github.com/spderosso/gitpylib>.
* *Gitless lib modules*. These are the \*lib.py files. They hold all the
  Gitless-related logic.
* *Command line frontend*. These are the gl\* files and are the frontend to
  Gitless.
