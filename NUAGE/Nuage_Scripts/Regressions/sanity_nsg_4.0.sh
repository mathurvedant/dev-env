#!/bin/bash

help=$1

if [ "$help" == "--help" ]
then
    printf "\nsanity_4.0.sh <tesbed> <pause_msg> <repeat_count>\n"
    exit
fi

printf "\nQueueing sanity run %d times...\n" $3

#Queue 4.0 Sanity for repeat count specified.
for ((i=1;i<=$3;i+=1))
do
regress -testbed $1 -vsdMode standalone -physTopology nsg -platform dctor -priority P1 -runLevel regular -forcePause $2 -vrs 4.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite Sanity -useimages 4.0/latest
done
