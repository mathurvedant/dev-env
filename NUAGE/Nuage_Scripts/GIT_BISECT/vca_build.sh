#!/bin/bash

RETVAL=0

printf "\nSwitching to ovs directory..."
cd ovs
printf "\nRunning boot.sh..."
./boot.sh > /dev/null
printf "\nRunning configure..."
./configure --enable-Werror --with-vendor=vrs > /dev/null
printf "\nRunning make..."
make > /dev/null

if [ $? -eq 0 ]
then
    RETVAL=0
else
    RETVAL=$?
fi
printf "\nRunning make distclean..."
make distclean > /dev/null
printf "\nSwitching to VCA directory..."
cd ..
exit $RETVAL
