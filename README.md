Gitless
=======

A version control system built on top of Git.

This is under active development.


About
-----

Gitless is an experimental version control system built on top of Git. Keep in
mind that Gitless might change in non-retrocompatible ways (so don't script
around it just yet) as we seek to answer the fundamental question that drives
this software project: if we were to challenge the very core concepts in
version control systems, what would version control look like?

In its current state, Gitless is a distributed version control system that
supports all of the most commonly used Git features. We are missing some things
like submodules and cherry-picking but these are coming soon (maybe; only if we
don't find a superior, more robust way of achieving the same goal). Either way,
since Gitless is implemented on top of Git (could be considered what Git
pros call a 'porcelain' of Git) you can always fallback to the `git` command to
finish a task.

More info, downloads and documentation @ [Gitless's website](
    http://people.csail.mit.edu/sperezde/gitless "Gitless's website").


Installing
----------

Note that the installation **won't interfere** with your Git installation in any
way, you can keep using Git, and switch between Git and Gitless seamleslly.

You need to have Python and Git installed. If you don't, search for their
official websites, install them and come back.

The easiest way to install Gitless is using the Python Package Manager `pip`. If
you don't have `pip`, just search the web for it, and you'll find installation
instructions on their website. Now, once you have `pip` installed just do:

    $> pip install gitless

You should now be able to start executing the `gl` command.



Contributing
------------

We only have two branches, `master` and `develop`. We code in `develop` and
merge the changes onto `master` when the changes are stable and we're ready to
cut a new release. So you'll find on `develop` the latest changes.

We follow (to some extent) the [Google Python Style Guide](
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
    "Google Python Style Guide").
Before contributing, take a few seconds to look at the style guide and the
Gitless's code so that your edits are consistent with the codebase.

To contribute: fork project, make changes, send pull request.
