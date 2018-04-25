#!/bin/bash

help=$1

if [ "$help" == "--help" ]
then
    printf "\ncode_coverage_aar_regressions <tesbed> <PR number> <custom_gash_repo_branch>\n"
    exit
fi

#NSG Express
echo "Queueing NSG Express"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel express -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -useimages dctor/0.0/latest

#NSG DPI
echo "Queueing NSG DPI"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel regular -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_dpi -useimages dctor/0.0/latest

#NPM FUNCTIONAL
echo "Queuing NPM FUNCTIONAL"
regress -testbed $1 -coverage true -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel regular -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite npm_functional -useimages dctor/0.0/latest

#NPM EVENTS
echo "Queueing NPM EVENTS"
regress -testbed $1 -coverage true -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel regular -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite npm_events -useimages dctor/0.0/latest

#NSG APM
echo "Queueing NSG APM"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -priority P0 -runLevel regular -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_apm -useimages dctor/0.0/latest

#NSG APM PC
echo "Queueing NSG APM PC"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -priority P0 -runLevel regular -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_apm_pc -useimages dctor/0.0/latest

#NSG DUC PPS
echo "Queueing DUC PPS"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -eunLevel regular -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite nsg_duc_pps -useimages dctor/0.0/latest

#NSG NATT
echo "Queueing NSG NATT"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel extreme -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite "NsgNattEnhancements" -useimages dctor/0.0/latest

#NSG DUC NATT
echo "Queueing NSG DUC NATT"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel extreme -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite "NsgDucNattEnhancements" -useimages dctor/0.0/latest

#NSG REMOTE UPLINK PREFERENCE
echo "Queueing NSG REMOTE UPLINK PREFERENCE"
regress -testbed $1 -coverage true -vsdMode standalone -customRepo vmathur/gash:$3 -physTopology nsg -platform dctor -subTopology default -priority P0 -runLevel regular -vsd 0.0/latest -vrs 0.0/PR$2 -vsd 0.0/latest -altimages 7750/0.0/latest 7750/0.0/latest -runSuite "NsgUbrRemoteUplinkPreference" -useimages dctor/0.0/latest -forcePause "CODE_COVERAGE_REGRESSIONS"

