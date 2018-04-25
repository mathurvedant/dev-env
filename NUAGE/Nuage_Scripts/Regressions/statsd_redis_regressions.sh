#!/bin/bash

help=$1

if [ "$help" == "--help" ]
then
    printf "\nstatsd_redis_regressions.sh <tesbed> <PR number>\n"
    exit
fi

#NSG Express
echo "Queueing NSG Express"
regress -testbed $1 -vsdMode standalone -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel express -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -useimages dctor/0.0/latest

#NSG DPI
echo "Queueing NSG DPI"
regress -testbed $1 -vsdMode standalone -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_dpi -useimages dctor/0.0/latest

#NPM FUNCTIONAL
echo "Queuing NPM FUNCTIONAL"
regress -testbed $1 -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite npm_functional -useimages dctor/0.0/latest

#NPM EVENTS
echo "Queueing NPM EVENTS"
regress -testbed $1 -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite npm_events -useimages dctor/0.0/latest

#NSG NPM
echo "Queueing NSG NPM"
regress -testbed $1 -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel regular -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_npm -useimages dctor/0.0/latest

#NSG APM
echo "Queueing NSG APM"
regress -testbed $1 -vsdMode standalone -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -priority P0 -runLevel quick -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_apm -useimages dctor/0.0/latest

#NSG APM PC
echo "Queueing NSG APM PC"
regress -testbed $1 -vsdMode standalone -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -priority P0 -runLevel quick -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_apm_pc -useimages dctor/0.0/latest

#NSG NATT
echo "Queueing NSG NATT"
regress -testbed $1 -vsdMode standalone -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel regular -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runTest "nsgNattNpmProvisioningTest" -useimages dctor/0.0/latest

#NSG DUC PPS
echo "Queueing DUC PPS"
regress -testbed $1 -vsdMode standalone -customRepo vmathur/gash:statsd_gash -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel quick -vrs 0.0/PR$2 -vsd 0.0/StatsPR273 -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_duc_pps -useimages dctor/0.0/latest -forcePause "StatsD_Regressions"
