#!/bin/bash

cd ovs

# COMPRESSED SSL
./configure --enable-Werror --with-vendor=vrs --prefix=/usr --sysconfdir=/etc --localstatedir=/var  CPPFLAGS="-DSTATSD_BUFFER_COMPRESS"  CFLAGS="-g -O0 `xml2-config --cflags`" LIBS="-lrt -lm `xml2-config --libs` -lpthread -lanl" && make
cp vrs/sbin/nuage-statsd/nuage-statsd ~/statsd_bins/nuage-statsd-compressed-ssl
cp vrs/sbin/nuage-statsd/mock/statsd-mock-collector ~/statsd_bins/statsd-mock-collector-compressed
cp vrs/sbin/nuage-statsd/mock/statsd-mock-generator ~/statsd_bins/statsd-mock-generator-compressed

cd ..
git clean -f

cd ovs
# UNCOMPRESSED SSL
./configure --enable-Werror --with-vendor=vrs --prefix=/usr --sysconfdir=/etc --localstatedir=/var CFLAGS="-g -O0 `xml2-config --cflags`" LIBS="-lrt -lm `xml2-config --libs` -lpthread -lanl" && make
cp vrs/sbin/nuage-statsd/nuage-statsd ~/statsd_bins/nuage-statsd-uncompressed-ssl
cp vrs/sbin/nuage-statsd/mock/statsd-mock-collector ~/statsd_bins/statsd-mock-collector-uncompressed
cp vrs/sbin/nuage-statsd/mock/statsd-mock-generator ~/statsd_bins/statsd-mock-generator-uncompressed

cd ..
git clean -f
