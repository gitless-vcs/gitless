# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

"""gl resolve - Mark a file with conflicts as resolved."""


import file_cmd


parser = file_cmd.parser('mark files with conflicts as resolved', 'resolve')
