Gitless
=======

A version control system built on top of Git.

This is under active development.

More info, downloads and documentation @
<http://people.csail.mit.edu/sperezde/gitless>.


About
-----

Gitless is an experimental version control system built on top of Git. We are
exploring what conceptual integrity means with the goal of building a rigorous
foundation for concept design. We encourage you to try out the current version
of Gitless and send feedback. Keep in mind that Gitless might change in
non-retrocompatible ways (so don't script around it just yet) as we seek to
answer the fundamental question that drives this software project: if we were
to challenge the very core concepts in version control systems, what would
version control look like?

In its current state, Gitless is a distributed version control system that
supports all of the most commonly used Git features. We are missing some things
like submodules and cherry-picking but these are coming soon (maybe; only if we
don't find a superior, more robust way of achieving the same goal). Either way,
since Gitless is implemented on top of Git (could be considered what Git
pros call a 'porcelain' of Git) you can always fallback to the 'git' command to
finish a task.

Check out the documentation section to get started. If you are a novice user
that never used any version control system the documentation should be enough to
get you started. If you are a Git pro looking to see what's different from your
beloved Git you'll be able to spot the differences by glancing through the
documentation (section on Gitless vs. {Git, Mercurial} coming soon).


Documentation
-------------

TODO


Contributing
------------

We only have two branches, `master` and `develop`. We code in `develop` and
merge the changes onto `master` when the changes are stable and we're ready to
cut a new release. So you'll find on the `develop` branch the latest changes.

The following steps should get you ready to contribute:

  $> git clone https://github.com/spderosso/gitpylib.git
  $> cd gitpylib
  $> git checkout develop
  $> sudo ./setup.py develop
  $> cd ..
  $> git clone https://github.com/spderosso/gitless.git
  $> cd gitless
  $> git checkout develop
  $> sudo ./setup.py develop
