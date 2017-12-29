#!/bin/bash

help=$1

if [ "$help" == "--help" ]
then
    printf "\nsanity_0.0.sh <tesbed> <pause_msg> <repeat_count>\n"
    exit
fi

printf "\nQueueing sanity run %d times...\n" $3

#Queue 0.0 Sanity for repeat count specified.
for ((i=1;i<=$3;i+=1))
do
regress -testbed $1 -runLevel express -physTopology dctorOvs -useimages 0.0/latest -priority P1 -forcePause $2 -vrs 0.0/latest -exitAfterSetup true
done
