# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl rebase - Rebase one branch onto another."""


from . import sync_cmd


parser = sync_cmd.parser('rebase')
