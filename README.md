Gitless
=======

A version control system built on top of Git.


Installing
----------

To build from source do 'make'. This will create a bin folder with compiled
python files as well as bash wrappers for the commands. Using these instead of
the .py scripts directly should be faster. Once you have the bin folder, you
can add this folder to your PATH variable or you can do 'sudo make install' and
this will install Gitless in /usr/local/gitless and create symlinks in
/usr/local/bin (make uninstall undoes this operation, make clean removes the
bin directory).


Developing
----------

For rapidily trying out your changes you can use debug-install.sh. This will
create symlinks to the python scripts in /usr/bin. After running this install
script you can execute the commands by just typing 'gl', 'gl-track',
'gl-untrack' and so. You only need to execute this script once (unless you add
some new command).
