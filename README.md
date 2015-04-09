Gitless
=======

[![PyPI version](https://badge.fury.io/py/gitless.png)](
    http://badge.fury.io/py/gitless)
[![Build Status](https://travis-ci.org/sdg-mit/gitless.png?branch=develop)](
    https://travis-ci.org/sdg-mit/gitless)

Gitless is an experimental version control system built on top of Git. Many
people complain that Git is hard to use. We think the problem lies deeper than
the user interface, in the concepts underlying Git. Gitless is an experiment to
see what happens if you put a simple veneer on an app that changes the
underlying concepts. Because Gitless is implemented on top of Git (could be
considered what Git pros call a 'porcelain' of Git), you can always fall
back on Git. And of course your coworkers you share a repo with need never know
that you're not a Git aficionado.

More info, downloads and documentation @ [Gitless's website](
    http://gitless.com "Gitless's website").

Questions or comments about Gitless can be sent to the [
  Gitless users mailing list](
      https://groups.google.com/forum/#!forum/gl-users
      "Gitless users mailing list").


Install
-------

Note that the installation **won't interfere** with your Git installation in any
way, you can keep using Git, and switch between Git and Gitless seamlessly.

We currently require Git (1.7.12+) to be installed (but this requirement is
going to disappear soon once we finish with our migration to pygit2).

Note to Windows users: we currently have no binary release for Windows. If you
are having trouble getting v0.7 to work in Windows (we now depend on pygit2 in
addition to `git`), you can try v0.6.3 instead (which depends only on
`git`) and people have managed to get it working.


### Binary releases

Binary releases for Mac OS and Linux are available @
[Gitless's website](http://gitless.com "Gitless's website"). This is the easiest
way to get Gitless.

If you've downloaded a binary release of Gitless everything is contained in the
gl binary, so to install simply do:

    $ cp path-to-downloaded-gl-binary /usr/local/bin/gl

You can put the binary in other locations as well, just be sure to update your
PATH.

If for some reason this doesn't work (maybe you are running an old version of
your OS?), try one of the other options (installing from source code or via
the Python Package Index).


### Installing from source

To install from source you need to have Python (2.6, 2.7, 3.2+ or pypy)
installed.

Additionaly, you need to [install pygit2](
http://www.pygit2.org/install.html "pygit2 install").

Then, download the source code tarball available @
[Gitless's website](http://gitless.com "Gitless's website") and do:

    $ ./setup.py install


### Installing via the Python Package Index

If you are a Python fan you might find it easier to install
Gitless via the Python Package Index. To do this, you need to have
Python (2.6, 2.7, 3.2+ or pypy) installed.

Additionaly, you need to [install pygit2](
http://www.pygit2.org/install.html "pygit2 install").

Then, just do:

    $ pip install gitless


Contribute
----------

There are several ways you can contribute to the project:

- Design: if you have any feedback about Gitless's design we would love to
hear from you. You can create an issue in the project with your
feedback/questions/suggestions or shoot us an email.
- Reporting bugs: did you find a bug? create an issue for it and we'll fix it
ASAP.
- Code: you can browse through the open issues and see if there's something
there you would like to hack on. Is something missing? feel free to propose it!

After you've contributed you can send us a pull request adding yourself to the
AUTHORS file if you want to.

If you're planning on submitting code here are some useful things to know:

- We only have two branches, `master` and `develop`. We code in `develop` and
merge the changes onto `master` when the changes are stable and we're ready to
cut a new release. So you'll find on `develop` the latest changes.

- We follow (to some extent) the [Google Python Style Guide](
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
    "Google Python Style Guide").
Before submitting code, take a few seconds to look at the style guide and the
Gitless's code so that your edits are consistent with the codebase.

- Finally, if you don't want [Travis](
    https://travis-ci.org/sdg-mit/gitless "Travis") to
be mad at you, check that the tests pass in python 2.6, 2.7, 3.2 and 3.3 and
that you don't have any pylint *errors* (warnings and refactor suggestions are
ok).
