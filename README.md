Gitless
=======

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
    http://people.csail.mit.edu/sperezde/gitless "Gitless's website").


Install
-------

Note that the installation **won't interfere** with your Git installation in any
way, you can keep using Git, and switch between Git and Gitless seamleslly.

You need to have Python and Git installed. If you don't, search for their
official websites, install them and come back.

The easiest way to install Gitless is using the Python Package Manager `pip`. If
you don't have `pip`, just search the web for it, and you'll find installation
instructions on their website. Now, once you have `pip` installed just do:

    $> pip install gitless

You should now be able to start executing the `gl` command.



Contribute
----------

There are several ways you can contribute to the project:

- design: if you have any feedback about Gitless's design we would love to
hear from you. Feel free to create an issue in the project with your
feedback/questions/suggestions or shoot us an email.
- reporting bugs: did you find a bug? create an issue for it and we'll fix it
ASAP.
- code: you can browse through the open issues and see if there's something
there you would like to hack on. Is something missing? feel free to propose it!

If you're planning on submitting code: fork project, make changes, send pull
request.

We only have two branches, `master` and `develop`. We code in `develop` and
merge the changes onto `master` when the changes are stable and we're ready to
cut a new release. So you'll find on `develop` the latest changes.

We follow (to some extent) the [Google Python Style Guide](
    http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
    "Google Python Style Guide").
Before submitting code, take a few seconds to look at the style guide and the
Gitless's code so that your edits are consistent with the codebase.

Alo, if you don't want @ [Travis](
    https://travis-ci.org/sdg-mit/gitless "Travis") to
be mad at you check that the tests pass in python 2.6, 2.7, 3.2 and 3.3 and that
you don't have any pylint errors.
