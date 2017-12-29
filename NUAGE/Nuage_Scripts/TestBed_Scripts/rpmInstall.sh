#RPM re-install script:
#set -x

if [ "$#" -ne 1 ]; then
    echo "Num of args expected = 1, the commit hash"
    exit 1
fi

mkdir -p installers
pushd installers
rm -f *

#copy files from /usr/global
cp /usr/global/images/vrs/0.0/$1/el7/* .

yum remove nuage-openvswitch -y
rpm -qa | grep nuage-openvswitch-debuginfo | xargs rpm -e

rpm -ivh nuage-openvswitch-0.0*
rpm -ivh nuage-openvswitch-debuginfo*

# Restart openvswitch.
sh /usr/share/openvswitch/scripts/openvswitch.init restart

popd

# Stop and start the attached VMs so that their IPs are resolved again.
for field in {5..7}
do
  for i in `virsh list --all | grep "vm" | cut -d" " -f$field | grep -v '^$'`; do virsh destroy $i; virsh start $i;done
done

ovs-appctl vm/port-show | grep IP: -B 7 |grep -v flags | grep -v vrf | grep -v MAC | grep -v mirror | grep -v route_id | grep -v anti-spoof

