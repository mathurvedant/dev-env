#!/bin/bash

DeleteEntries()
{
    echo "Cleaning up table " $1
    ovsdb-client dump Open_vSwitch $1 | awk {'if(NR>3)print $1'} | while read -r line; do
        echo $line
        `ovsdb-client transact '["Open_vSwitch",{"op":"delete","table":"'$1'","where":[["_uuid","==",["uuid","'$line'"]]]}]'` 2> /dev/null
    done

    ovsdb-client dump | grep -A 3 $1 | awk '{if (NR==4) {print $1}}' | while read -r line; do
        `ovsdb-client transact '["Open_vSwitch",{"op":"delete","table":"'$1'","where":[["_uuid","==",["uuid","'$line'"]]]}]'` 2> /dev/null
    done
}

#Delete tables in a specific order
DeleteEntries Nuage_Alarms
DeleteEntries Nuage_IKE_Monitor_Config
