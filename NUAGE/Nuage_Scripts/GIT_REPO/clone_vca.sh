#!/bin/bash

# This script creates a new directory with the specified name and performs
# a git clone of a user specific VCA repo and sets up official VCA repo as a
# remote repoi inside the new directory. In addition it sets up cscope and
# compile_commands.json file needed for YCM auto-complete and on-the-fly
# compilation.

HELP=$1
if [ "$HELP" == "--help" ]
then
    printf "\n"
    printf "Usage: clone_vca.sh <dir-name> <csl> [--help]\n\n"
    exit
fi

DIRNAME=$1
if [ -z "$DIRNAME" ]
then
    printf "CLONE_VCA: Directory name  not provided. Please provide a directory name\n"
    exit
fi


CSL=$2
if [ -z "$CSL" ]
then
    CSL=vmathur
    printf "CLONE_VCA: CSL not provided. Defaulting to vmathur\n"
fi

GIT_CLONE_URL=git@github.mv.usa.alcatel.com:$CSL/VCA.git
GIT_OFFICIAL_VCA_URL=git@github.mv.usa.alcatel.com:VCA/VCA.git

printf "CLONE_VCA: Git clone user url: %s\n" $GIT_CLONE_URL
printf "CLONE_VCA: Git clone official url: %s\n" $GIT_OFFICIAL_VCA_URL

mkdir $DIRNAME

cd $DIRNAME

git clone $GIT_CLONE_URL

cd VCA

git remote add official $GIT_OFFICIAL_VCA_URL
git fetch official

git submodule init
git submodule sync
git submodule update

git pull official vca-master

cscope -bkqvR

bear_gen_ccdb.sh

printf "CLONE_VCA: Done!\n"

