#!/bin/bash

./boot.sh
./configure --enable-Werror --with-vendor=vrs --prefix=/usr --sysconfdir=/etc --localstatedir=/var  CFLAGS="-g -O0 `xml2-config --cflags`" LIBS="-lrt -lm `xml2-config --libs` -lpthread -lanl" && make
