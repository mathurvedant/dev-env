#! /bin/bash

for field in {5..7}
do
  for i in `virsh list --all | grep "vm" | cut -d" " -f$field | grep -v '^$'`; do virsh destroy $i; virsh start $i;done
done

ovs-appctl vm/port-show | grep IP: -B 7 |grep -v flags | grep -v vrf | grep -v MAC | grep -v mirror | grep -v route_id | grep -v anti-spoof


