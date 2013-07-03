Gitless
=======

A version control system built on top of Git.

To build from source do 'make'. This will create a bin folder with compiled
python files as well as bash wrappers for the commands. Using these instead of
the .py scripts directly should be faster. Once you have the bin folder, you
can add this folder to your PATH variable or you can do sudo make install and
this will install Gitless in /usr/local/gitless and create symlinks in
/usr/local/bin (make uninstall undoes this operation, make clean removes the
bin directory).
