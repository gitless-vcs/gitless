#!/bin/bash

# Gitless - a version control system built on top of Git.
# Copyright (c) 2013  Santiago Perez De Rosso.
# Licensed under GNU GPL, version 2.

# Creates symlinks to the python files in /usr/bin. After running the install
# script you can execute the commands by just typing "gl-track", "gl-untrack"
# and so on in your shell. You only need to execute this script once.

# You'll need to edit this array if you add/remove commands.
cmds=(
    "track" "untrack" "status" "diff" "commit" "branch" "checkout" "rm" "merge"
    "resolve" "rebase" "remote" "push" "init" "history")

dir=$(pwd)

for cmd in ${cmds[@]}; do
  sudo rm "/usr/bin/gl-${cmd}"
  sudo ln -s "${dir}/gl_${cmd}.py" "/usr/bin/gl-${cmd}"
done

# The gl command.
sudo rm "/usr/bin/gl"
sudo ln -s "${dir}/gl.py" "/usr/bin/gl"
