#!/bin/bash

# Usage: ut-run [git | gl] [task-number]


LB='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m'


function t {
  printf "\n${LB}$1 $2${NC}\n"
}

function c {
  printf "\n${GREEN}$@${NC}\n"
  "$@"
  printf "\n"
}

function maybe_exit {
  if [ "$1" == "$2" ]
  then
    c git config --global core.pager ""
    t "######################################################################"
    t "######################################################################"
    t "######################################################################"
    t "Ready for task $2"
    t "If you ran ut-run from within fit-cli do cd . to refresh the directory"
    c exit 0
  fi
}


c git config --global core.pager cat

t "Reseting remote repo"

c rm -rf ~/.ut/fit-cli
c ut-remote


t "Reseting local repo"
c cd ~/Documents
c rm -rf fit-cli


#### TASK 0 ####
t "#### TASK 0 ####"

maybe_exit $2 "0"

# 0.1
t "0.1" "Open the terminal and clone the fit-cli repo at path-to-repo/fit-cli"
if [ $1 == "git" ]
then
  c git clone $FIT_CLI_REMOTE
  c cd fit-cli
  c git branch
  c git log --oneline
else
  c mkdir fit-cli
  c cd fit-cli
  c gl init $FIT_CLI_REMOTE
  c gl branch
  c gl history -c
fi

c pwd
c ls


#### TASK 1 ####
t "#### TASK 1 ####"

maybe_exit $2 "1"

# 1.1
t "1.1" "Create README.md with these contents"

printf "fit-cli\n=======\nThe ultimate fitness app. Give your gender, age, weight and height to fit-cli and get an estimate of the number of calories you burn per day just for being alive; all of this without leaving the command line!\n" >> README.md
c ls

# 1.2
t "1.2" "Track README.md"
if [ $1 == "git" ]
then
  c git add README.md
  c git status
else
  c gl track README.md
  c gl status
fi

# 1.3
t "1.3" "Let's add usage instructions to the readme. Open README.md and make this change"

printf "\nTo run fit-cli execute the fit.py script which accepts the following optional flags:-g/--gender, -a/--age, -w/--weight, -h/--height.\n" >> README.md
if [ $1 == "git" ]
then
  c git status
else
  c gl status
fi

# 1.4
t "1.4" "Create a commit with all changes to README.md and message added readme"

if [ $1 == "git" ]
then
  c git commit -m "added readme" README.md
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "added readme"
  c gl history -c -v -l 1
  c gl history -c
fi


#### TASK 2 ####
t "#### TASK 2 ####"

maybe_exit $2 "2"

# 2.1
t "2.1" "We are going to be diligent and work in a separate branch. Create a new branch feat/kilos and switch to it"

if [ $1 == "git" ]
then
  c git branch feat/kilos
  c git branch
  c git checkout feat/kilos
  c git branch
else
  c gl branch -c feat/kilos
  c gl branch
  c gl switch feat/kilos
  c gl branch
fi


# 2.2
t "2.2" "Open file fit.py and make this change"

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
  parser.add_argument('-k', '--kilos', action='store_true')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height, use_kg=args.kilos)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False):
  w_const_female = 9.56 if use_kg else 4.35
  w_const_male = 13.75 if use_kg else 6.25
  if gender == 'female':
    return (655 + w_const_female * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + w_const_male * weight + 12.7 * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi

# 2.3
t "2.3" "Create a commit with the changes to fit.py and message kilos feature"

if [ $1 == "git" ]
then
  c git commit -m "kilos feature" fit.py
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "kilos feature"
  c gl history -c -v -l 1
  c gl history -c
fi


# 2.4

t "2.4" "Bob (the CTO) will review our changes. Run the ut-pr-kilos-send command to send a pull request."
ut-pr-kilos-send


# 2.5
t "2.5" "Bob suggested we add a help message to the kilos flag, that's an easy fix. Open fit.py and make this change"
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
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height, use_kg=args.kilos)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False):
  w_const_female = 9.56 if use_kg else 4.35
  w_const_male = 13.75 if use_kg else 6.25
  if gender == 'female':
    return (655 + w_const_female * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + w_const_male * weight + 12.7 * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi


#### TASK 3 ####
t "#### TASK 3 ####"

maybe_exit $2 "3"


# 3.1.1
t "3.1.1" "Create a new branch feat/meters that diverges from master and switch to it"


if [ $1 == "git" ]
then
  c git branch feat/meters master
  c git branch -v
  
  c git checkout feat/meters
  c git stash
  c git checkout feat/meters
  c git branch -v
else
  c gl branch -c feat/meters -dp=master
  c gl switch feat/meters
  c gl branch -v
fi


# 3.1.2
t "3.1.2" "Open file fit.py and make this change"

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
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_m=False):
  h_const= {
      'female': 1.8 if use_m else 4.7,
      'male': 5 if use_m else 12.7
      }
  if gender == 'female':
    return (655 + 4.35 * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + 6.25 * weight + 12.7 * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72


if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi


# 3.2.1
t "3.2.1" "Switch back to master"

if [ $1 == "git" ]
then
  c git stash
  c git checkout master
  c git branch
  c git status
else
  c gl switch master
  c gl branch
  c gl status
fi


# 3.2.2
t "3.2.2" "Open file fit.py and make this change"
printf "#!/usr/bin/python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
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

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi


# 3.2.3
t "3.2.3" "Create a commit with these changes to fit.py with message fix error checking bug"

if [ $1 == "git" ]
then
  c git commit -m "fix error checking bug" fit.py
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "fix error checking bug"
  c gl history -c -v -l 1
  c gl history -c
fi

# 3.2.4
t "3.2.4" "Push the changes"

if [ $1 == "git" ]
then
  c git push
else
  c gl publish
fi


#### TASK 4 ####
t "#### TASK 4 ####"

maybe_exit $2 "4"


# 4.1.1
t "4.1.1" "Switch back to feat/kilos and go back to what we were doing before"

if [ $1 == "git" ]
then
  c git checkout feat/kilos
  c git status
  c git stash list
  c git stash pop stash@{1}
  c git status
  c git diff
else
  c gl switch feat/kilos
  c gl status
  c gl diff
fi

# 4.1.2
t "4.1.2" "Let's change to using a dictionary like Bob wanted. Open fit.py and make this change"
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
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height, use_kg=args.kilos)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False):
  w_const = {
      'female': 9.56 if use_kg else 4.35,
      'male': 13.75 if use_kg else 6.25
      }
  if gender == 'female':
    return (655 + w_const[gender] * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + w_const[gender] * weight + 12.7 * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi


# 4.1.3
t "4.1.3" "Create a commit with these changes to fit.py with message kilos improvements"

if [ $1 == "git" ]
then
  c git commit -m "kilos improvements" fit.py
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "kilos improvements"
  c gl history -c -v -l 1
  c gl history -c
fi

# 4.1.4
t "4.1.4" "Update kilos pr"
c ut-pr-kilos-update

t "Simulating that Bob accepted the PR"
c git checkout -b tmp origin/master
c git merge --no-edit feat/kilos
c git push origin HEAD:master
c git checkout feat/kilos
c git branch -d tmp

if [ $1 == "git" ]
then
  c git status
else
  c gl status
fi


# 4.2.1
t "4.2.1" "Switch to feat/meters and bring back changes"

if [ $1 == "git" ]
then
  c git checkout feat/meters
  c git stash list
  c git stash pop
  c git branch
  c git status
  c git diff
else
  c gl switch feat/meters
  c gl branch
  c gl status
  c gl diff
fi

# 4.2.2
t "4.2.2" "Now let's modify the computation of the rmb to use meters if the user specified so. Open fit.py and make this change"
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
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_m=False):
  h_const= {
      'female': 1.8 if use_m else 4.7,
      'male': 5 if use_m else 12.7
      }
  if gender == 'female':
    return (655 + 4.35 * weight + h_const[gender] * height - 4.7 * age) *  1.1
  else:
    return (66 + 6.25 * weight + h_const[gender] * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi

# 4.2.3
t "4.2.3" "Create a commit with these changes to fit.py with message meters feature"

if [ $1 == "git" ]
then
  c git commit -m "meters feature" fit.py
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "meters feature"
  c gl history -c -v -l 1
  c gl history -c
fi

# 4.2.4
t "4.2.4" "Bob (the CTO) will review our changes. Run the ut-pr-meters-send command to send a pull request."
c ut-pr-meters-send



#### TASK 5 ####
t "#### TASK 5 ####"

maybe_exit $2 "5"


# 5.1.1
t "5.1.1" "Update our local master branch with the new changes in the remote master"

if [ $1 == "git" ]
then
  c git checkout master
  c git pull --rebase
  c git log --oneline master
else
  c gl switch master
  c gl fuse
  c gl history -c
fi

# 5.1.2
t "5.1.2" "Switch back to feat/meters and rebase the changes from master"

if [ $1 == "git" ]
then
  c git checkout feat/meters
  c git rebase master
  c git status
  c git diff
else
  c gl switch feat/meters
  c gl fuse master
  c gl status
  c gl diff
fi

# 5.1.3
t "5.1.3" "Open fit.py and make this change"
printf "#!/usr/bin/python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height,
      use_kg=args.kilos, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


<<<<<<< HEAD
def rmb(gender, age, weight, height, use_kg=False):
  w_const = {
      'female': 9.56 if use_kg else 4.35,
      'male': 13.75 if use_kg else 6.25
      }
  if gender == 'female':
    return (655 + w_const[gender] * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + w_const[gender] * weight + 12.7 * height - 6.76 * age) * 1.1
=======
def rmb(gender, age, weight, height, use_m=False):
  h_const= {
      'female': 1.8 if use_m else 4.7,
      'male': 5 if use_m else 12.7
      }
  if gender == 'female':
    return (655 + 4.35 * weight + h_const[gender] * height - 4.7 * age) *  1.1
  else:
    return (66 + 6.25 * weight + h_const[gender] * height - 6.76 * age) * 1.1
>>>>>>> meters feature


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
  c git status
else
  c gl diff
  c gl status
fi

# 5.2.1
t "5.2.1" "Switch to master"

if [ $1 == "git" ]
then
  c git stash
  c git rebase --abort
  c git checkout master
  c git branch
  c git status
else
  c gl switch master
  c gl branch
  c gl status
fi

# 5.2.2
t "5.2.2" "Open fit.py and make this change"
printf "#!/usr/bin/env python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height, use_kg=args.kilos)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False):
  w_const = {
      'female': 9.56 if use_kg else 4.35,
      'male': 13.75 if use_kg else 6.25
      }
  if gender == 'female':
    return (655 + w_const[gender] * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + w_const[gender] * weight + 12.7 * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py


c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi

# 5.2.3
t "5.2.3" "Create a commit with the changes to fit.py and message fix shebang"

if [ $1 == "git" ]
then
  c git commit -m "fix shebang" fit.py
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "fix shebang"
  c gl history -c -v -l 1
  c gl history -c
fi

# 5.2.4
t "5.2.4" "Push changes"

if [ $1 == "git" ]
then
  c git push
else
  c gl publish
fi


# 5.3.1
t "5.3.1" "Switch back to feat/meters and go back to the state where we where before fixing the bug"

if [ $1 == "git" ]
then
  c git checkout feat/meters
  c git log --oneline
  c git log --oneline master
  c git rebase master

  printf "#!/usr/bin/env python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height,
      use_kg=args.kilos, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


<<<<<<< HEAD
def rmb(gender, age, weight, height, use_kg=False):
  w_const = {
      'female': 9.56 if use_kg else 4.35,
      'male': 13.75 if use_kg else 6.25
      }
  if gender == 'female':
    return (655 + w_const[gender] * weight + 4.7 * height - 4.7 * age) *  1.1
  else:
    return (66 + w_const[gender] * weight + 12.7 * height - 6.76 * age) * 1.1
=======
def rmb(gender, age, weight, height, use_m=False):
  h_const= {
      'female': 1.8 if use_m else 4.7,
      'male': 5 if use_m else 12.7
      }
  if gender == 'female':
    return (655 + 4.35 * weight + h_const[gender] * height - 4.7 * age) *  1.1
  else:
    return (66 + 6.25 * weight + h_const[gender] * height - 6.76 * age) * 1.1
>>>>>>> meters feature


if __name__ == '__main__':
  main()
" > fit.py
  c git status
  c git diff
else
  c gl switch feat/meters
  c gl status
  c gl diff
  c gl history -c
fi



# 5.3.2
t "5.3.2" "Open fit.py and make this change"
printf "#!/usr/bin/env python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height,
      use_kg=args.kilos, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False, use_m=False):
  w_const = {
      'female': 9.56 if use_kg else 4.35,
      'male': 13.75 if use_kg else 6.25
      }
  h_const= {
      'female': 1.8 if use_m else 4.7,
      'male': 5 if use_m else 12.7
      }
  if gender == 'female':
    return (
        655 + w_const[gender] * weight + h_const[gender] * height -
        4.7 * age) *  1.1
  else:
    return (
        66 + w_const[gender] * weight + h_const[gender] * height -
        6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git status
  c git diff
else
  c gl status
  c gl diff
fi


# 5.3.3
t "5.3.3" "Finish with the rebase operation"

if [ $1 == "git" ]
then
  c git add fit.py
  c git rebase --continue
  c git log --oneline -p -1
  c git log --oneline
  c git status
else
  c gl resolve fit.py
  c gl commit -m"meters feature"
  c gl history -c -v -l 1
  c gl history -c
  c gl status
fi


# 5.3.4
t "5.3.4" "Update meters pr"
c ut-pr-meters-update

t "Simulating that Bob accepted the PR"
c git checkout -b tmp origin/master
c git merge --no-edit feat/meters
c git push origin HEAD:master
c git checkout feat/meters
c git branch -d tmp

if [ $1 == "git" ]
then
  c git status
else
  c gl status
fi


#### TASK 6 ####
t "#### TASK 6 ####"

maybe_exit $2 "6"


# 6.1.1
t "6.1.1" "Switch to master and pull changes"


if [ $1 == "git" ]
then
  c git checkout master
  c git branch
  c git pull
  c git log --oneline
else
  c gl switch master
  c gl branch
  c gl fuse
  c gl history -c
fi

# 6.1.2
t "6.1.2" "Open fit.py and make this change"
printf "#!/usr/bin/env python

import argparse


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height,
      use_kg=args.kilos, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False, use_m=False):
  const = {
      'weight': {
          'female': 9.56 if use_kg else 4.35,
          'male': 13.75 if use_kg else 6.25
          },
      'height': {
          'female': 1.8 if use_m else 4.7,
          'male': 5 if use_m else 12.7
          }
      }
  if gender == 'female':
    return (
        655 + const['weight'][gender] * weight +
        const['height'][gender] * height - 4.7 * age) *  1.1
  else:
    return (
        66 + const['weight'][gender] * weight +
        const['height'][gender] * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi

# 6.1.3
t "6.1.3" "Create a commit with the changes to fit.py and message join const dicts"

if [ $1 == "git" ]
then
  c git commit -m "join const dicts" fit.py
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "join const dicts"
  c gl history -c -v -l 1
  c gl history -c
fi

# 6.2.1
t "6.2.1" "Go back to the same state as before the commit"

if [ $1 == "git" ]
then
  c git status
  c git reset --hard HEAD~1
  c git status
else
  c gl status
  c gl branch -c tmp
  c gl branch -sh=HEAD~1
  c gl status
fi

# 6.2.2
t "6.2.2" "Open fit.py and make this change"
printf "#!/usr/bin/env python

import argparse
import collections


def main():
  parser = argparse.ArgumentParser(
      description=(
        'fit-cli: compute your resting metabolic rate from the command line'))
  parser.add_argument('gender', choices=['female', 'male'])
  parser.add_argument('age', type=int)
  parser.add_argument('weight', type=int, help='in pounds')
  parser.add_argument('height', type=int, help='in inches')
  parser.add_argument(
      '-k', '--kilos', action='store_true',
      help='if true, then the weight given as input is interpreted as kg')
  parser.add_argument(
      '-m', '--meters', action='store_true',
      help='if true, the height input will be interpreted in meters')
  args = parser.parse_args()

  result = rmb(
      args.gender, args.age, args.weight, args.height,
      use_kg=args.kilos, use_m=args.meters)

  print('Your resting metabolic rate is {0}'.format(result))


def rmb(gender, age, weight, height, use_kg=False, use_m=False):
  Const = collections.namedtuple('Const', ['weight', 'height'])
  const = Const(
      {'female': 9.56 if use_kg else 4.35,
       'male': 13.75 if use_kg else 6.25},
      {'female': 1.8 if use_m else 4.7,
       'male': 5 if use_m else 12.7})
  if gender == 'female':
    return (
        655 + const.weight[gender] * weight +
        const.height[gender] * height - 4.7 * age) *  1.1
  else:
    return (
        66 + const.weight[gender] * weight +
        const.height[gender] * height - 6.76 * age) * 1.1


if __name__ == '__main__':
  main()
" > fit.py

c ./fit.py male 25 180 72

if [ $1 == "git" ]
then
  c git diff
else
  c gl diff
fi

# 6.2.3
t "6.2.3" "Create a new commit with message switch to using nt for consts"

if [ $1 == "git" ]
then
  c git commit -m "switch to using nt for consts" fit.py
  c git status
  c git log --oneline -p -1
  c git log --oneline
else
  c gl commit -m "switch to using nt for consts"
  c gl status
  c gl history -c -v -l 1
  c gl history -c
fi

# 6.2.4
t "6.2.4" "Using namedtuples looks better than merging the dictionaries, so let's go ahead and push these changes"

if [ $1 == "git" ]
then
  c git push
else
  c gl publish
fi

# Cleanup
git config --global core.pager ""
