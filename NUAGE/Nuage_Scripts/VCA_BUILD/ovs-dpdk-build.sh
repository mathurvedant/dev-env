#!/bin/bash

./boot.sh
./configure --enable-Werror --with-vendor=vrs --enable-nsgvrs --enable-vrsdpdk --prefix=/usr --sysconfdir=/etc --localstatedir=/var  --enable-ssl CFLAGS="-g -O0" && make
