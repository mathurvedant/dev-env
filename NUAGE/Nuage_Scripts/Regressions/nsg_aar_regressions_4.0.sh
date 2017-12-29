#!/bin/bash

help=$1

if [ "$help" == "--help" ]
then
    printf "\nnsg_aar_regressions_4.0.sh <tesbed> <pause_msg> <PR number>\n"
    exit
fi

#NSG Express
echo "Queueing NSG Express"
regress -testbed $1 -forcePause $2 -vsdMode standalone -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel express -vrs 4.0/PR$3 -vsd 4.0/current -altimages 7750/0.0/latest 7750/0.0/latest -useimages dctor/4.0/latest

#NSG DPI
echo "Queueing NSG DPI"
regress -testbed $1 -forcePause $2 -vsdMode standalone -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 4.0/PR$3 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_dpi -useimages dctor/4.0/latest

#NPM FUNCTIONAL
echo "Queuing NPM FUNCTIONAL"
regress -testbed $1 -forcePause $2 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 4.0/PR$3 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite npm_functional -useimages dctor/4.0/latest

#NPM EVENTS
echo "Queueing NPM EVENTS"
regress -testbed $1 -forcePause $2 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 4.0/PR$3 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite npm_events -useimages dctor/4.0/latest

#NSG APM
echo "Queueing NSG APM"
regress -testbed $1 -forcePause $2 -vsdMode standalone -physTopology nsg -platform dctor -priority P0 -runLevel quick -vsd 4.0/R10 -vrs 4.0/PR$3 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_apm -useimages 4.0/R10

#NSG DUC PPS
echo "Queueing DUC PPS"
regress -testbed $1 -forcePause $2 -vsdMode standalone -customRepo atmahesh/gash:atul_40 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 4.0/PR$3 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_duc_pps -useimages dctor/4.0/latest
