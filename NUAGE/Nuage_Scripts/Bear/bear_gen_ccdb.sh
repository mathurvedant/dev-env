#!/bin/bash

# This script generates a compilation database for the VCA GIT Repo using bear.
# The compilation database is generated in a file called "compile_commands.json"
# under the VCA directory.
#
# This script should ALWAYS be run from the VCA directory of a GIT Repo and assumes
# that the GIT Repo has all git submodules inited and updated.
#
# The script executes some git clean up commands so it is recommended to run it with
# the GIT Repo staging area clean. Otherwise changes may be lost in certain cases.

help=$1
if [ "$help" == "--help" ]
then
    printf "\n"
    printf "This is a script to generate a compilation database for VRS.\n"
    printf "This script should ALWAYS be run from the VCA directory of\n"
    printf "a git repo. The script assumes that the git repo has all of\n"
    printf "its submodules inited and updated.\n\n"
    printf "WARNING: The script uses 'git clean' commands underneath hence\n"
    printf "it is recommended to run this on a git repo with a clean staging\n"
    printf "area. Otherwise changes may be lost. Use at your own risk!\n\n"
    printf "Usage: bear_gen_ccdb.sh [--help] [--skip-git-clean]\n\n"
    exit
fi

skip_git_clean=$1
skip_clean=0

printf "BEAR_GEN_CC: Preparing current directory `pwd` for compilation database generation\n"

#No need to edit schema files with ovs25
#sed -i -e 's|"/vswitchd/|"/ovs/vswitchd/|' vrs/build-aux/vrs-ovsschema-merge.py
#sed -i -e 's|"/vrs/|"/ovs/vrs/|' vrs/build-aux/vrs-ovsschema-merge.py
#sed -i -e 's|"/build-aux/|"/ovs/build-aux/|' vrs/build-aux/vrs-ovsschema-merge.py

cd ovs
./boot.sh
./configure --enable-Werror --with-vendor=vrs --prefix=/usr --sysconfdir=/etc --localstatedir=/var  CFLAGS="-g -O0 `xml2-config --cflags`" LIBS="-lrt -lm `xml2-config --libs` -lpthread -lanl"

printf "BEAR_GEN_CC: Generating Bear Compilation Database...\n"
bear make
cd ..
mv ovs/compile_commands.json ./compile_commands.json
git add compile_commands.json

printf "BEAR_GEN_CC: Cleaning up..\n"
if [ "$skip_git_clean" == "--skip-git-clean" ]
then
    printf "\n"
    printf "BEAR_GEN_CC: Cleanup will skip git clean.\n"
    skip_clean=1
fi

if [ $skip_clean -ne 1 ]
then
    cd ovs
    git clean -f
    cd ..
    git clean -f
fi

#git checkout vrs/build-aux/vrs-ovsschema-merge.py
git reset compile_commands.json

printf "BEAR_GEN_CC: Compilation Database Created: `pwd`/compile_commands.json \n"
printf "BEAR_GEN_CC: Done!\n"

