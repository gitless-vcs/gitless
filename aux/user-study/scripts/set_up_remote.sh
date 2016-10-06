#!/bin/bash


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


c mkdir ~/.ut/tmp
c cd ~/.ut/tmp
c git config --global user.name ut
c git config --global user.email ut@ut.example.com

c gl init
printf "#!/usr/bin/python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender')
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  args = parser.parse_args()

  result = rmb(args.gender, args.age, args.weight, args.height)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height):
  if gender == 'female':
    return (655 + 4.35 * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + 6.25 * weight + 12.7 * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py
c chmod +x fit.py
c gl commit -m "first cut at fit-cli app" -i fit.py

c cp -r .git ~/.ut/fit-cli.git
c rm -rf ~/.ut/tmp
c cd -

(cd ~/.ut/fit-cli.git; git config --bool core.bare true)
