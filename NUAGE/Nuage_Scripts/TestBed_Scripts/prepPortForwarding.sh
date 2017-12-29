#!/bin/bash
if [ $# -eq 1 ] ; then
    ip=$1
    itf='eth0'
elif [ $# -gt 1 ] ; then
    ip=$1
    itf=$2
else
    ipList=$(cat /home/$(hostname)/images/esrcalls.tcl | grep vsd)
    echo $ipList
    itf='eth0'
    ip=$(echo $ipList | awk 'match($0,/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/) {print substr($0,RSTART,RLENGTH)}')
fi
echo "following is picked $ip $itf"
echo "the proxy ip is:"
echo $(ip addr show $itf)
iptables -F
iptables -t nat -F
iptables -A FORWARD -i $itf -j ACCEPT
for port in 8443 39090
do
    iptables -t nat -A PREROUTING -i $itf -p tcp -m tcp --dport $port -j DNAT --to-destination $ip
done
sysctl net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
