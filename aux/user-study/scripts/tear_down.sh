#!/bin/bash

# Usage: source ./tear_down.sh


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

t "Remove commands"

c rm ~/.ut/ut-run

c rm ~/.ut/ut-pr-kilos-send
c rm ~/.ut/ut-pr-kilos-update

c rm ~/.ut/ut-pr-meters-send
c rm ~/.ut/ut-pr-meters-update

t "Remove fit-cli remote"

c rm -rf ~/.ut/fit-cli

t "Remove ~/.ut"
c rm -rf ~/.ut

t "Unset vars"
c unset FIT_CLI_REMOTE
c unset SNIPPETS

t "Tear down done"
