#!/bin/bash

./boot.sh
./configure --enable-Werror --with-vendor=vrs --enable-nsgvrs --prefix=/usr --sysconfdir=/etc --localstatedir=/var  CFLAGS="-g -O0 `xml2-config --cflags`" LIBS="-lrt -lm `xml2-config --libs` -lssl -lcrypto -lgcov -lpthread -lanl -ljemalloc" && make
