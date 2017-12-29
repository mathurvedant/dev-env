#!/bin/bash

help=$1
GOOD=$1

printf "\nStarting git bisect from `pwd`\n"

if [ "$help" == "--help" ]
then
    printf "\nvca_git_bisect <last known good revision>\n"
    exit
fi

if [ -z "$GOOD" ]
then
    printf "\nPlease provide a last known good revision\n"
    exit
fi

printf "\nRunning git_bisect...\n"

git bisect start HEAD $GOOD
git bisect run /root/Nuage_Scripts/GIT_BISECT/vca_build.sh
git bisect reset
