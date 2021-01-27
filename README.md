Gitless
=======

[![PyPI version](https://img.shields.io/pypi/v/gitless.svg)](https://pypi.org/project/gitless "PyPI version")
[![Homebrew Formula](https://img.shields.io/homebrew/v/gitless.svg)](https://formulae.brew.sh/formula/gitless "Homebrew Formula")

[![Travis Build Status](https://img.shields.io/travis/gitless-vcs/gitless/master.svg)](https://travis-ci.org/gitless-vcs/gitless "Travis Build Status")
[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/gitless-vcs/gitless?svg=true)](https://ci.appveyor.com/project/spderosso/gitless-11bfm "AppVeyor Build Status")

[Gitless](http://gitless.com "Gitless's website") is a version control system built on top of Git, that is easy to learn and use:

- **Simple commit workflow**

    Track or untrack files to control what changes to commit. Changes to tracked files are committed by default, but you can easily customize the set of files to commit using flags
- **Independent branches**

    Branches in Gitless include your working changes, so you can switch between branches without having to worry about conflicting uncommitted changes
- **Friendly command-line interface**

    Gitless commands will give you good feedback and help you figure out what to do next
- **Compatible with Git**

    Because Gitless is implemented on top of Git, you can always fall back on Git. And your coworkers you share a repo with need never know that you're not a Git aficionado. Moreover, you can use Gitless with GitHub or with any Git hosting service


Install
-------

Installing Gitless won't interfere with your Git installation in any
way. You can keep using Git and switch between Git and Gitless seamlessly.

We currently require Git (1.7.12+) to be installed, but this requirement is
going to disappear soon once we finish with our migration to [pygit2](https://github.com/libgit2/pygit2).


### Binary release (macOS and Linux only)

Binary releases for macOS and Linux are available from the
[Gitless website](http://gitless.com "Gitless's website").

If you've downloaded a binary release of Gitless everything is contained in the
gl binary, so to install simply do:

    $ cp path-to-downloaded-gl-binary /usr/local/bin/gl

You can put the binary in other locations as well, just be sure to update your
`PATH`.

If for some reason this doesn't work (maybe you are running an old version of
your OS?), try one of the other options (installing from source or via
the Python Package Index).

### Installing from source

To install from source you need to have Python 3.7+ installed.

Additionally, you need to [install pygit2](
http://www.pygit2.org/install.html "pygit2 install").

Then, [download the source code tarball](http://gitless.com "Gitless's website")
and do:

    $ ./setup.py install


### Installing via the Python Package Index

If you are a Python fan you might find it easier to install
Gitless via the Python Package Index. To do this, you need to have
Python 3.7+ installed.

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

### Installing via Snapcraft (Linux only)

If you are using [Snapcraft](https://snapcraft.io/ "Snapcraft"), a
package manager for Linux, you can install the most recent release
of Gitless with:

```
snap install --channel=beta gitless
```

You can also use the `edge` channel to install the most recent build.

### Installing via the Arch User Repository (Arch Linux only)

If you are using [Arch Linux](https://www.archlinux.org/) or any of
its derivatives, you can use your favorite
[AUR Helper](https://wiki.archlinux.org/index.php/AUR_helpers) and install:
- [gitless](https://aur.archlinux.org/packages/gitless/) for the latest
  released version
- [gitless-git](https://aur.archlinux.org/packages/gitless-git/) to 
  build the latest version straight from this repo

Documentation
-------------

`gl -h`, `gl subcmd -h` or check
[our documentation](http://gitless.com "Gitless's website")


Contribute
----------

If you find a bug, create an issue in our
GitHub repository. If you'd like to contribute
code, here are some useful things to know:

- To install gitless for development, [install pygit2](
  http://www.pygit2.org/install.html "pygit2 install"), clone the repo,
  `cd` to the repo root and do `./setup.py develop`. This will install
  the `gl` command with a symlink to your source files. You can make
  changes to your code and run `gl` to test them.
- We follow, to some extent, the [Google Python Style Guide](
    https://google.github.io/styleguide/pyguide.html
    "Google Python Style Guide").
Before submitting code, take a few seconds to look at the style guide and the
Gitless code so that your edits are consistent with the codebase.

- Finally, if you don't want [Travis](
    https://travis-ci.org/gitless-vcs/gitless "Travis") to
be mad at you, check that tests pass in Python 3.7+. Tests can be run with:
  ```
  python -m unittest discover gitless/tests
  ```
