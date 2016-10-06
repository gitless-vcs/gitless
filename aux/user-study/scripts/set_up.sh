#!/bin/bash

# Usage: source ./set_up.sh


LB='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m'

function t {
  printf "\n${LB}$1${NC}\n"
}

function c {
  printf "\n${GREEN}$@${NC}\n"
  "$@"
}


c git --version
c gl --version

t "Create ~/.ut dir"

mkdir ~/.ut

t "Set up commands"

c cp run.sh ~/.ut/ut-run
c cp set_up_remote.sh ~/.ut/ut-remote

c cp pr_kilos_send.sh ~/.ut/ut-pr-kilos-send
c cp pr_kilos_update.sh ~/.ut/ut-pr-kilos-update

c cp pr_meters_send.sh ~/.ut/ut-pr-meters-send
c cp pr_meters_update.sh ~/.ut/ut-pr-meters-update

t "Set up fit-cli remote"
c ./set_up_remote.sh

t "Export FIT_CLI_REMOTE var"
c export FIT_CLI_REMOTE=~/.ut/fit-cli

t "Export SNIPPETS var"
c cp snippets.txt ~/.ut/snippets.txt
c export SNIPPETS=~/.ut/snippets.txt

t "Add .ut to PATH"
c export PATH=~/.ut/:$PATH

t "Set up done"
