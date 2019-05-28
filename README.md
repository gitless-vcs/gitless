Gitless
=======

[![PyPI version](https://img.shields.io/pypi/v/gitless.svg)](https://pypi.org/project/gitless "PyPI version")
[![Homebrew Formula](https://img.shields.io/homebrew/v/gitless.svg)](https://formulae.brew.sh/formula/gitless "Homebrew Formula")

[![Travis Build Status](https://img.shields.io/travis/sdg-mit/gitless/master.svg)](https://travis-ci.org/sdg-mit/gitless "Travis Build Status")
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/sdg-mit/gitless?svg=true)](https://ci.appveyor.com/project/spderosso/gitless "AppVeyor Build Status")

[Gitless](http://gitless.com "Gitless's website") is an experimental version
control system built on top of Git. Many
people complain that Git is hard to use. We think the problem lies deeper than
the user interface, in the concepts underlying Git. Gitless is an experiment to
see what happens if you put a simple veneer on an app that changes the
underlying concepts. Because Gitless is implemented on top of Git (could be
considered what Git pros call a "porcelain" of Git), you can always fall
back on Git. And of course your coworkers you share a repository with need never
know that you're not a Git aficionado.


Install
-------

Note that the installation **won't interfere** with your Git installation in any
way, you can keep using Git, and switch between Git and Gitless seamlessly.

We currently require Git (1.7.12+) to be installed (but this requirement is
going to disappear soon once we finish with our migration to [pygit2](https://github.com/libgit2/pygit2)).


### Installing from source

To install from source you need to have Python (2.7, 3.2+ or PyPy)
installed.

Note to Windows users: Python 3 is not supported yet,
see [#146](https://github.com/sdg-mit/gitless/issues/146) for more info.

Additionally, you need to [install pygit2](
http://www.pygit2.org/install.html "pygit2 install").

Then, [download the source code tarball](http://gitless.com "Gitless's website")
and do:

    $ ./setup.py install


### Installing via the Python Package Index

If you are a Python fan you might find it easier to install
Gitless via the Python Package Index. To do this, you need to have
Python (2.7, 3.2+ or PyPy) installed.

Note to Windows users: Python 3 is not supported yet,
see [#146](https://github.com/sdg-mit/gitless/issues/146) for more info.

Additionally, you need to [install pygit2](
http://www.pygit2.org/install.html "pygit2 install").

Then, just do:

    $ pip install gitless

### Installing via Homebrew (macOS only)

If you are using [Homebrew](http://brew.sh/ "Homebrew homepage"), a package
manager for macOS, you can install Gitless with:

```
brew update
brew install gitless
```

### Binary release (macOS only)

A binary release for macOS is available from the
[Gitless website](http://gitless.com "Gitless's website").

If you've downloaded a binary release of Gitless everything is contained in the
gl binary, so to install simply do:

    $ cp path-to-downloaded-gl-binary /usr/local/bin/gl

You can put the binary in other locations as well, just be sure to update your
`PATH`.

If for some reason this doesn't work (maybe you are running an old version of
your OS?), try one of the other options (installing from source or via
the Python Package Index).

### Installing via Snapcraft (Linux only)

If you are using [Snapcraft](https://snapcraft.io/ "Snapcraft"), a
package manager for Linux, you can install the most recent release
of Gitless with:

```
snap install --channel=beta gitless
```

You can also use the `edge` channel to install the most recent build.

Documentation
-------------

`gl -h`, `gl subcmd -h` or check
[our documentation](http://gitless.com "Gitless's website")


Contribute
----------

If you find a bug, you can help us by submitting an issue to our
GitHub Repository. If you'd like to contribute
code, here are some useful things to know:

- We follow (to some extent) the [Google Python Style Guide](
    https://google.github.io/styleguide/pyguide.html
    "Google Python Style Guide").
Before submitting code, take a few seconds to look at the style guide and the
Gitless's code so that your edits are consistent with the codebase

- Finally, if you don't want [Travis](
    https://travis-ci.org/sdg-mit/gitless "Travis") to
be mad at you, check that tests pass in Python 2.7 and 3.2+. Tests can be run with:
  ```
  pip install nose
  nosetests # run tests other than end-to-end tests
  nosetests ./gitless/tests/test_e2e.py # run end-to-end tests
  ```
