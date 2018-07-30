#!/bin/bash

help=$1

if [ "$help" == "--help" ]
then
    printf "\ncode_coverage_express <tesbed> <forcepause>\n"
    exit
fi

#NSG Express
echo "Queueing NSG Express for Coverage"
regress -testbed $1 -coverage true -vsdMode standalone -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel express -vrs 0.0/latest-coverage -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -useimages dctor/0.0/latest

#DC Express
echo "Queueing DC Express for Coverage"
regress -testbed $1 -coverage true -physTopology dctorOvs -priority P0 -runLevel express -vrs 0.0/latest-coverage -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -useimages dctor/0.0/latest -forcePause $2


