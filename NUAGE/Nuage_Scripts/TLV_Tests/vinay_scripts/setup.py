#!/usr/bin/python

import sys
import os
import time
import json
import subprocess
import re
import uuid
import ipaddr
import random
import argparse
from pprint import pprint
import logging

logfile = '/var/tmp/setup.log'
CRED = '\033[91m'
CEND = '\033[0m'

def exe(cmd):
    logging.debug("%s" % cmd)
    if os.system(cmd + ' >/dev/null 2>&1'):
       logging.debug(CRED+"\tFailed cmd: %s %s" % (cmd, CEND))

class NS_setup(object):
    xml_format = "<domain type='kvm'>\
      <name>%s</name>\
      <uuid>%s</uuid>\
      <description>%s</description>\
     <memory>131072</memory>\
     <os>\
       <type arch='x86_64' machine='rhel6.2.0'>hvm</type>\
     </os>\
     <on_poweroff>destroy</on_poweroff>\
     <on_reboot>restart</on_reboot>\
     <on_crash>restart</on_crash>\
     <devices>\
       <emulator>/usr/libexec/qemu-kvm</emulator>\
       <interface type='bridge'>\
         <mac address='%s'/>\
         <source bridge='alubr0'/>\
         <virtualport type='openvswitch'/>\
         <target dev='%s'/>\
         <model type='rtl8139'/>\
       </interface>\
       </devices>\
    </domain>"

    def __init__(self, n_vms, n_brs):
        self.n_vms = n_vms
        self.n_brs = n_brs
        self.ports = []
        if n_vms:
           for i in range(1, n_vms+1):
               self.ports.append("vm"+str(i))
        if n_brs:
           for i in range(1, n_brs+1):
               self.ports.append("br"+str(i))
        #print "ns_setup: "+str(self.ports)
    def create_xml(self, vm_name = "vm1", dev_name = "vm1-veth1"):
        cmd = 'ip netns exec '+vm_name+' ip a'
        output = subprocess.check_output(cmd, shell=True)
        logging.debug("%s" % output)
        uuid_str = str(uuid.uuid1())
        pattern = 'link/ether ([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
        match = re.search(pattern, output)
        m = match.group(0).split()
        mac = m[1]
        f = open('/var/tmp/'+dev_name+'.xml', 'w')
        logging.debug(self.xml_format % (dev_name, uuid_str, uuid_str, mac, dev_name))
        f.write(self.xml_format % (dev_name, uuid_str, uuid_str, mac, dev_name))

    def setup(self):
        for p in self.ports:
            exe("ip netns del "+p)
            exe("ip netns add "+p)
            exe("ip link add "+p+"-veth0 type veth peer name "+p+"-veth1")
            exe("ip link set "+p+"-veth0 netns "+p)
            exe("ip netns exec "+p+" ip link set "+p+"-veth0 up")
            exe("ip netns exec "+p+" ip link set lo up")
            exe("ip link set "+p+"-veth1  up")
            exe("ip netns exec "+p+" sysctl net.ipv4.ip_forward=1")
            self.create_xml(p, p+'-veth1')

    def destroy(self):
        for p in self.ports:
            exe("virsh undefine "+p+"-veth1")
            exe("ip link delete "+p+"-veth1")
            exe("ip netns del "+p)
            exe("rm -f /var/tmp/"+p+"-veth1.xml")
    def get_uuids(self):
        from lxml import etree
        uuids = {}
        for p in self.ports:
            try :
                doc = etree.parse('/var/tmp/'+p+'-veth1.xml')
            except IOError:
                return uuids
            uuidElem = doc.find('uuid')
            uuids[p+'-veth1'] = uuidElem.text
        """
        for u in uuids:
            print ('uuid[%s] => %s' % (u, uuids[u]))
        """
        return uuids
    def get_macs(self):
        macs = {}
        for p in self.ports:
            cmd = 'ip netns exec '+p+' ip a'
            try :
                output = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError:
                return macs
            #print output
            pattern = 'link/ether ([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            match = re.search(pattern, output)
            if match != None:
               m = match.group(0).split()
               #print m[1]
               macs[p+'-veth1'] = m[1]
        """
        for m in macs:
            print ('macs[%s] => %s' % (m, macs[m]))
        """
        return macs

    def reinit(self):
        self.destroy()
        self.setup()

class ovs_class(object):
    add_flow = "ovs-ofctl add-flow alubr0 "
    del_flow = "ovs-ofctl del-flows alubr0 "

    @staticmethod
    def ovs_bump_gen_id():
        logging.info("ovs gen_id bumped ...")
        exe("ovs-ofctl add-flow alubr0 \"flow_type=ofctl-events,flags=bump_gen_id\"")
    @staticmethod
    def ovs_cleanup():
        exe("ovs-ofctl add-flow alubr0 \"flow_type=ofctl-events,flags=cleanup\"")
        logging.info("ovs cleanup done ...")
    @staticmethod
    def ovs_check_internal_ports():
        for port in ['svc-rl-tap1', 'svc-rl-tap2', 'svc-pat-tap', 'svc-spat-tap']:
            p = subprocess.Popen(["ovs-appctl", "dpif/show"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1 = subprocess.Popen(('grep', port), stdin=p.stdout,
                              stdout=subprocess.PIPE)
            result = p1.communicate()[0]
            if not len(result):
               logging.critical("%s does not exists" % port)
               logging.critical("result-> %d %s" % (len(result), result))
               return False
            else:
               logging.critical("%s exists" % port)
        return True

    @staticmethod
    def ovs_hit_rules():
        p = subprocess.Popen(["ovs-appctl", "bridge/dump-flows", "alubr0"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p1 = subprocess.Popen(('grep', '-v', 'es=0'), stdin=p.stdout,
                          stdout=subprocess.PIPE)
        result = p1.communicate()[0]
        return result

    @staticmethod
    def expect_rule(pattern, expect, desc=''):
        rule = ovs_class.ovs_find_rule(pattern)
        if expect and not rule:
           assert 0, ('Expected %s rule: %s not found'\
                  % (desc, pattern))
        elif not expect and rule:
           assert 0, ('UnExpected %s rule %s found, rule: %s'\
                  % (desc, pattern, rule))
        logging.info("%s rule: %s" %
                (("Found" if expect else "Not found"),\
                (rule if expect else pattern)))
        return rule

    @staticmethod
    def ovs_flows():
        op = subprocess.check_output(['ovs-appctl',\
                'bridge/dump-flows', 'alubr0'])
        op = re.sub(r'duration.*n_bytes=\d+,', '', op)
        flows = set(op.strip().split('\n'))
        return flows
    @staticmethod
    def ovs_find_rule(pattern):
        op = subprocess.check_output(['ovs-appctl',\
                'bridge/dump-flows', 'alubr0'])
        match = re.search('.*'+pattern+'.*',  op)
        if match:
           #logging.info("found rule : %s" % match.group())
           return match.group()
        return None

    def create_port_cfg(self):
        json_str = ""
        json_str = "{ \n \"hosts\" : \n\t["
        for v in self.vms:
            vm = self.vms[v]
            json_str += "\n\t\t{"
            json_str += ("\n\t\t\t\"%s\" : \"%s\" ," % ('type', 'vm'))
            for i in ['interface', 'mac',  'name', 'uuid']:
                json_str += ("\n\t\t\t\"%s\" : \"%s\" ," % (i, vm[i]))
            json_str += ("\n\t\t\t\"%s\" : %d \n\t\t}," % ('vlan', 0))
            #self.vm_start(vm);
        #time.sleep(1)
        json_str = json_str[:-1]
        json_str += "\n\t]\n}"
        logging.debug("==> %s" % json_str)
        json_dict = eval(json_str)
        with open('/var/tmp/port-cfg', 'w') as f:
                  json.dump(json_dict, f, separators=(', ',':'),
                            sort_keys=True,
                            indent = 4, ensure_ascii=False)
        logging.info("port-cfg Generated ...")

    def vm_restart(self):
        cmd = '/usr/bin/nuage-port-config.pl --secret --add --bridge alubr0 '\
              '--config /var/tmp/port-cfg'
        exe(cmd)

    def auto_gen_vm(self):
        logging.info("Auto-generating VM config ...")
        vm_per_evpn = self.n_vms/len(self.evpns)
        p = self.ports
        i = 0
        self.vms = {}
        #print p
        for pi in p:
            self.vms[pi] = {}
            self.vms[pi]['interface'] = pi
        if not vm_per_evpn:
           vm_per_evpn = 1
        #print vm_per_evpn
        for e in self.evpns:
            evpn = self.evpns[e]
            evpn['vms'] = []
            for j in range(vm_per_evpn):
                if (i+j) < len(p):
                   evpn['vms'].append(p[i+j])
                   self.vms[p[i+j]]['evpn'] = evpn['properties']['evpn_id']
                   i = ((i+vm_per_evpn) if len(evpn['vms']) == vm_per_evpn else i)
        for e in self.evpns:
            evpn = self.evpns[e]
            #print ('%s/%s' %(ovs.evpns[e]['properties']['subnet'],\
            #       ovs.evpns[e]['properties']['mask']))
            nw = self.evpns[e]['properties']['subnet'] +'/'+\
                 self.evpns[e]['properties']['mask']
            network = ipaddr.IPv4Network(nw)
            for vm in evpn['vms']:
                random_ip = ipaddr.IPv4Address(random.randrange(int(network.network) + 1,\
                                    int(network.broadcast) - 1))
                self.vms[vm]['ip'] = str(random_ip)
                #print vms[vm]['ip']
            #print str(evpn['properties']['evpn_id'])+" => "+str(evpn['vms'])
        """
        for vm in self.vms:
            print vm+' => '+ str(self.vms[vm])
        """

    def readconfig(self):
        with open(self.cfg_file) as data_file:
            data = json.load(data_file)
        vrfs1 = data['vrfs']
        evpns1 = data['evpns']
        vms1 = data['vms']
        brs1 = data['bridge_ports']
        self.tests = data['tests']

        vport_macs = self.nss.get_macs()
        uuids = self.nss.get_uuids()
        for v in vrfs1:
            self.vrfs[v['id']] = v
            v['tnl_id'] = v['id']*10
            v['vms'] = []
            v['evpns'] = []
        for e in evpns1:
            self.evpns[e['properties']['evpn_id']] = e
            e['vms'] = []
            self.vrfs[e['vrf']]['evpns'].append(e['properties']['evpn_id'])
        #self.template_vm = vms1.get('template')
        #del vms1['template']
        if self.auto_generate:
           for vm in vms1:
               if vm['interface'] == 'template':
                  self.template_vm = vm
           self.auto_gen_vm()
           self.auto_gen_pending = False
        else:
           for vm in vms1:
               self.vms[vm['interface']] = vm
               if vm['interface'] == 'template':
                  continue
           self.template_vm = self.vms['template']
           del self.vms['template']
        """
        print "==========="
        for e in self.evpns:
            print self.evpns[e]
        print "==========="
        #print "\n\n\n"
        #print self.vms
        """
        for i in self.vms:
            vm = self.vms[i]
            vm['mac'] = vport_macs.get(vm['interface'])
            vm['uuid'] = uuids.get(vm['interface'])
            vm['gw_ip'] = self.evpns[vm['evpn']]['properties']['gw_ip']
            vm['gw_ipv6'] = self.evpns[vm['evpn']]['properties'].get('gw_ipv6')
            for p in self.template_vm:
                if vm.get(p) == None:
                   vm[p] = self.template_vm[p]
                   #print("%s: %s" % (vm, self.vms[vm][p]))
            vm['vrf'] = self.evpns[vm['evpn']]['vrf']
            if not self.auto_generate:
               self.evpns[vm['evpn']]['vms'].append(vm['interface'])
            self.vrfs[vm['vrf']]['vms'].append(vm['interface'])
        for bp in brs1:
            bp['mac'] = vport_macs.get(bp['interface'])
            bp['uuid'] = uuids.get(bp['interface'])
            for p in self.template_vm:
                if bp.get(p) == None:
                   bp[p] = self.template_vm[p]
                   #print("%s: %s" % (vm, self.vms[vm][p]))
            bp['vrf'] = self.evpns[bp['evpn']]['vrf']
            self.brs[bp['interface']] = bp

    def __init__(self, cfg_file, n_vms, n_brs = 2, auto_generate = False):
        self.cfg_file = cfg_file
        self.vrfs = {}
        self.evpns = {}
        self.vms = {}
        self.brs = {}
        self.n_brs = n_brs
        self.n_vms = n_vms
        self.auto_generate = auto_generate
        self.ports = []
        self.nss = NS_setup(n_vms, n_brs)
        self.auto_gen_pending =  True if auto_generate else False
        if n_vms:
           for i in range(1, n_vms+1):
               self.ports.append("vm"+str(i)+'-veth1')
        if n_brs:
           for i in range(1, n_brs+1):
               self.ports.append("br"+str(i)+'-veth1')
        if not self.auto_generate:
           #self.ns_reinit()
           self.readconfig()
           exe("rm -f /var/tmp/port-cfg")
           self.create_port_cfg()
        #print "ovs_setup: "+str(self.ports)
    def cleanup(self):
        print("Cleaning up ovs configs ...")
        self.nss.destroy()
    def ovs_stop(self):
        os.system("echo "" > /var/log/openvswitch/ovs-vswitchd.log")
        #os.system("/usr/share/openvswitch/scripts/openvswitch.init restart")
        exe("/usr/share/openvswitch/scripts/openvswitch.init stop")
    def ovs_start(self):
        os.system("echo "" > /var/log/openvswitch/ovs-vswitchd.log")
        #os.system("/usr/share/openvswitch/scripts/openvswitch.init restart")
        exe("/usr/share/openvswitch/scripts/openvswitch.init start")

    def ovs_restart(self):
        os.system("echo "" > /var/log/openvswitch/ovs-vswitchd.log")
        #os.system("/usr/share/openvswitch/scripts/openvswitch.init restart")
        exe("/usr/share/openvswitch/scripts/openvswitch.init restart")
        #os.system("service openvswitch restart")
        exe("ovs-appctl vlog/disable-rate-limit")
        exe("ovs-appctl vlog/set any:file:info")
        exe("ovs-appctl vlog/set vrs_ofproto:file:dbg")
        exe("ovs-appctl vlog/set vrs_ofproto_vrf:file:dbg")
        exe("ovs-appctl vlog/set vrs_ofproto_evpn:file:dbg")
        exe("ovs-appctl vlog/set vrs_ofproto_dpif:file:dbg")
        exe("ovs-appctl vlog/set vrs_iptables:file:dbg")

        cmd = '/usr/bin/ovsdb-client transact \'["Open_vSwitch", {"op" :'\
              ' "delete", "table" : "Nuage_Evpn_Dhcp_Pool_Table", '\
              '"where" : [ ] } ]\''
        exe(cmd)
        cmd = '/usr/bin/ovsdb-client transact \'["Open_vSwitch", {"op" :'\
              ' "delete", "table" : "Nuage_Evpn_Dhcp_Pool_Dhcp_Entry_Table",'\
              ' "where" : [ ] } ]\''
        exe(cmd)
        #print "----------------------------"
        logging.info("ovs restart done.")
        #print "----------------------------"

    def vm_add_port(self, vm):
        exe("ovs-vsctl add-port alubr0 "+vm['interface'])
    def ns_reinit(self):
        self.nss.destroy()
        self.nss.setup()
        self.readconfig()
        exe("rm -f /var/tmp/port-cfg")
        self.create_port_cfg()
    def ns_vm_dhcp(self):
        for v in self.vms:
            vm = self.vms[v]
            if vm.get('isfake') == "False":
              continue
            token = vm["interface"].split("-")
            peer = token[0] +"-veth0"
            logging.debug("Peer Interface of %s => %s" % (vm["interface"], peer))
            exe("ip netns exec "+token[0]+" dhclient -v -r "+peer)
            exe("ip netns exec "+token[0]+" dhclient -v "+peer)
            if self.evpn_ip6_enabled(vm['evpn']) and vm.get('ipv6'):
               logging.debug("ipv6 address config: %s = > %s " %(peer, vm['ipv6']))
               exe('ip netns exec '+token[0]+' ip -6 addr del '+vm['ipv6']+\
                   '/64 dev '+peer)
               exe('ip netns exec '+token[0]+' ip -6 route del '+vm['ipv6']+\
                   ' dev '+peer)
               exe('ip netns exec '+token[0]+' ip -6 route del default via '+\
                   vm['gw_ipv6'])
               exe('ip netns exec '+token[0]+' ip -6 addr add '+vm['ipv6']+\
                   '/64 dev '+peer)
               exe('ip netns exec '+token[0]+' ip -6 route add '+vm['ipv6']+\
                   ' dev '+peer)
               exe('ip netns exec '+token[0]+' ip -6 route add default via '+\
                   vm['gw_ipv6'])
        logging.info("All VMs Dhcp Done.")

    def vm_start(self, vm):
        if vm.get('isfake') == "False":
           exe("virsh destroy "+vm['interface'])
        exe("virsh undefine "+vm['interface'])
        exe("virsh define  /var/tmp/"+vm['interface']+".xml")
        if vm.get('isfake') == "False":
           exe("virsh start "+vm['interface']);
        #print "----------------------------"
        logging.debug("VM % started .." % vm['interface'])
        #print "----------------------------"

    def add_vrf(self, vrf, tnl_id):
        exe("ovs-ofctl add-vrf alubr0 "+str(vrf)+" "+str(tnl_id))
        #print "----------------------------"
        logging.debug("vrf %s Created .." % str(vrf))
        #print "----------------------------"

    def add_evpn(self, evpn, vrf, flags, tnl_id, subnet, mask, gw_ip, gw_mac,\
                 v6_subnet, v6_mask, v6_gw, dhcp_pool_range):
        flags_str = ""
        for f in flags.split(','):
            flags_str = flags_str + "flags="+f+","
        exe("ovs-ofctl add-evpn alubr0 "+str(vrf)+" evpn_id="+str(evpn)+\
            ",vni_id="+str(tnl_id)+","+flags_str+"subnet="+subnet+",mask="+\
            mask+",gw_ip="+gw_ip+",gw_mac="+gw_mac+",subnetv6="+v6_subnet+\
            ",gw_ipv6="+v6_gw+",maskv6="+v6_mask+",dhcp_pool_range="+\
            dhcp_pool_range)
        #print "----------------------------"
        print evpn
        logging.debug("evpn %s Created .." % str(evpn))
        #print "----------------------------"

    def vm_evpn_membership(self, interface, evpn, vm_uuid, port_type = "vm"):
        exe(self.add_flow + "flow_type=route,type="+port_type+\
            ",ip,flags=membership,evpn_id="+str(evpn)+\
            ",interface="+str(interface)+",vm_uuid="+vm_uuid)
        #print "----------------------------"
        logging.debug("Associated %s with evpn %s" % (interface, str(evpn)))
        #print "----------------------------"

    def vm_acl(self, interface, evpn, vm_uuid, port_type = "vm"):
        acls = ["pre", "post", "redirect" ]
        for acl in acls:
            exe(self.add_flow + "flow_type=acl,type="+port_type+\
                ",priority=0,flags="+acl+",interface="+interface+",vm_uuid="+\
                vm_uuid+",action=allow")
            #print "----------------------------"
            logging.debug("Configured %s ACL %s" % (acl, interface))
            #print "----------------------------"

    def vm_dhcp_info(self, interface, evpn, vm_uuid, proto, vm_ip):
        exe(self.add_flow + "flow_type=dhcp,interface="+interface+",vm_uuid="+\
            vm_uuid+","+proto+"="+vm_ip)
        #print "----------------------------"
        logging.debug("Associated %s with dhcp entry %s" % (interface, vm_ip))
        #print "----------------------------"

    def vm_fips(self, interface, uuid, vm_ip, vrf, fip, pub_vrf,\
                port_type = "vm", op = 'add'):
        exe((self.add_flow if op == 'add' else self.del_flow)+\
            "flow_type=route,type="+port_type+\
            ",ip,flags=nat,vrf_id="+str(vrf)+",interface="+interface+\
            ",vm_uuid="+uuid+",nw_dst="+vm_ip+",public_ip="+fip+",pub_vrfid="+\
            str(pub_vrf))
        #print "----------------------------"
        logging.debug("%sAssociated %s  with fip %s" % (('Dis-' if op == "delete" else ""),\
              interface, fip))
        #print "----------------------------"

    def vm_enable_mac_learning(self, vm, port_type = "vm"):
        exe(self.add_flow + "flow_type=route,type="+port_type+\
            ",flags=enable-learning,interface="+vm['interface']+",vm_uuid="+\
            vm['uuid'])

    def vm_routes(self, vm, proto, vrf, evpn, interface, vm_uuid, vm_ip,\
                  vm_mac, port_type = "vm"):
        dst = ('nw_dst' if proto == 'ip' else 'ipv6_dst')
        exe(self.add_flow + "flow_type=route,type="+port_type+\
            ",flags=evpn,vrf_id="+str(vrf)+",evpn_id="+str(evpn)+",interface="+\
            str(interface)+",vm_uuid="+vm_uuid+",dl_dst="+vm_mac)
        exe(self.add_flow + "flow_type=route,type="+port_type+","+proto+\
            ",flags=evpn-redirect,vrf_id="+str(vrf)+",evpn_id="+str(evpn)+","+\
            dst+"="+ (vm_ip if (port_type == "vm") \
                      else self.evpns[evpn]['properties']['subnet']+'/8'))
        exe(self.add_flow+ "flow_type=qos,interface="+str(interface)+",type="+\
            port_type+",""vm_uuid="+vm_uuid+","\
            "ingress_rate="+str(vm['ingress_rate'])+",ingress_peak_rate="+\
            str(vm['ingress_peak_rate'])+",ingress_burst="+\
            str(vm['ingress_burst'])+","\
            "ingress_bum_rate="+str(vm['ingress_bum_rate'])+\
            ",ingress_bum_peak_rate="+str(vm['ingress_bum_peak_rate'])+\
            ",ingress_bum_burst="+str(vm['ingress_bum_burst'])+","\
            "ingress_fip_rate="+str(vm['ingress_fip_rate'])+\
            ",ingress_fip_peak_rate="+str(vm['ingress_fip_peak_rate'])+\
            ",ingress_fip_burst="+str(vm['ingress_fip_burst'])+","\
            "egress_fip_rate="+str(vm['egress_fip_rate'])+\
            ",egress_fip_peak_rate="+str(vm['egress_fip_peak_rate'])+\
            ",egress_fip_burst="+str(vm['egress_fip_burst'])+","\
            "egress_class="+str(vm['egress_class']))
        exe(self.add_flow + "flow_type=route,type="+port_type+\
            ",flags=arp-route,"+proto+",vrf_id="+str(vrf)+\
            ",evpn_id="+str(evpn)+","+dst+"="+vm_ip+",dl_dst="+vm_mac)
        exe(self.add_flow + "flow_type=route,type="+port_type+\
            ",flags=evpn,vrf_id="+str(vrf)+",evpn_id="+str(evpn)+",interface="+\
            str(interface)+",vm_uuid="+vm_uuid+",dl_dst="+vm_mac)
        #print "----------------------------"
        logging.debug("vm routes added for %s ip: %s" % (interface, vm_ip))
        #print "----------------------------"

    def ofctlby_property(self, base, values):
        for i in values:
            v = values[i]
            v_exclude = []
            if v.get('exclude', "None")!= "None":
               v_exclude = v['exclude']
            cmd = ""
            for p in v['properties']:
                #print p +" -> "+str(v['properties'][p])
                if p in v_exclude:
                   logging.debug("skiping .. %s" % p)
                   continue
                if str(v['properties'][p]).find(',') != -1:
                   attr_str = ""
                   for f in str(v['properties'][p]).split(','):
                       attr_str = attr_str + p +"="+f+","
                   cmd = cmd +attr_str+","
                else:
                   cmd = cmd +p+"="+str(v['properties'][p])+","
            if v.get('vrf', 'none') != 'none':
                cmd = str(v['vrf'])+" "+cmd
            exe(base +" "+ cmd)

    def bridge_port_setup(self):
        for i in self.vrfs:
            vrf = self.vrfs[i]
            self.add_vrf(vrf['id'], vrf['tnl_id'])
        self.ofctlby_property('ovs-ofctl add-evpn alubr0', self.evpns)
        for i in self.brs:
            p = self.brs[i]
            exe("nuage-sw-gwcli.pl --add --name "+p['interface']\
                +" --type bridge  --vlan 0 --interface "+p['interface']\
                +" --uuid "+p['uuid'])
            self.vm_evpn_membership(p['interface'], p['evpn'], p['uuid'],\
                                    "bridge")
            self.vm_acl(p['interface'], p['evpn'], p['uuid'], "bridge")
            self.vm_routes(p, 'ip', p['vrf'], p['evpn'], p['interface'],\
                           p['uuid'], p['ip'], p['mac'], "bridge")
            self.vm_enable_mac_learning(p, "bridge")

    def evpn_ip6_enabled(self, evpn_id):
        #print evpns[evpn_id]['properties'].get('subnetv6')
        return (self.evpns[evpn_id].get('exclude') == None or \
                'subnetv6' not in self.evpns[evpn_id]['exclude']) and \
               self.evpns[evpn_id]['properties'].get('subnetv6') != None
    def vm_ipv6_enabled(self, vm):
        return self.vms[vm].get('ipv6') \
               and self.evpn_ip6_enabled(self.vms[vm]['evpn'])

    def vm_port_setup(self):
        self.vm_restart()
        for i in self.vrfs:
            vrf = self.vrfs[i]
            self.add_vrf(vrf['id'], vrf['tnl_id'])
        self.ofctlby_property('ovs-ofctl add-evpn alubr0', self.evpns)
        for v in self.vms:
            vm = self.vms[v]
            self.vm_add_port(vm)
            self.vm_evpn_membership(vm['interface'], vm['evpn'], vm['uuid'])
            self.vm_acl(vm['interface'], vm['evpn'], vm['uuid'])
            self.vm_routes(vm, 'ip', vm['vrf'], vm['evpn'], vm['interface'],\
                      vm['uuid'], vm['ip'], vm['mac'])
            self.vm_dhcp_info(vm['interface'], vm['evpn'], vm['uuid'], 'ip',\
                              vm['ip'])
            if self.evpn_ip6_enabled(vm['evpn']):
               logging.debug("evpn %d ipv6 enabled" % vm['evpn'])
               self.vm_dhcp_info(vm['interface'], vm['evpn'], vm['uuid'],\
                                 'ipv6', vm['ipv6'])
               self.vm_routes(vm, 'ipv6', vm['vrf'], vm['evpn'], vm['interface'],\
                              vm['uuid'],vm['ipv6'], vm['mac'])
            else:
               logging.debug("evpn %d ipv6 disabled" % vm['evpn'])
            logging.debug("-----------------")
            #vm_enable_mac_learning(vm)
        logging.info("Done vm_port_setup ...")

    def fip_config(self, op = "add"):
        for v in self.vms:
            vm = self.vms[v]
            if not vm.get('fip'):
               continue
            self.vm_fips(vm['interface'], vm['uuid'], vm['ip'], vm['vrf'],\
                         vm['fip'], vm['pub_vrf'], "vm", op)
    def fip_ecmp_route_delete(self):
        for v in self.vms:
            vm = self.vms[v]
            if not vm.get('fip'):
               continue
            exe(self.del_flow + "flow_type=route,ip,flags=ecmp,vrf_id="+\
                str(vm['pub_vrf'])+",nw_dst="\
                +vm['fip']+",n_hop=0\|1,nhop_flag=remote");
            logging.info("Deleted ecmp route for fip %s, vrf 0x%x"\
                         % (vm['fip'], vm['pub_vrf']))

    def static_routes(self):
        for i in self.vrfs:
            vrf = self.vrfs[i]
            for rt in vrf['static_routes']:
                exe(self.add_flow + "flow_type=route,ip,flags=ecmp,vrf_id="+\
                    str(vrf['id'])+",nw_dst="\
                    +rt['ip']+",n_hop=0\|1,nhop_flag=remote,mvpn_id="\
                    +str(vrf['id']*11)+",tep_addr="+rt['tep_addr'])
                #print "----------------------------"
                logging.debug("static ecmp remote route added for %s in vrf %s"\
                      % (rt['ip'], str(vrf['id'])))
                #print "----------------------------"

    def print_qos_cfg(self):
        clis = ["qdisc", "class", "filter" ]
        logging.info("\n********* Ingress fip qos  *********")
        for c in clis:
            os.system("tc -p -s -d "+c+" show dev svc-rl-tap1")

        for v in self.vms:
            vm = self.vms[v]
            logging.info("\n********* Egress fip qos for "+vm['interface']+ " *********")
            for c in clis:
                os.system("tc -p -s -d "+c+" show dev "+vm['interface'])
    def print_topology(self):
        for v in self.vrfs:
            vrf = self.vrfs[v]
            print('\tvrf_id: %d(0x%x)' % (v, v))
            for e in vrf['evpns']:
                evpn = self.evpns[e]
                print('\t    evpn_id: %d(0x%x)' % (e, e))
                for vm in evpn['vms']:
                    ip = self.vms[vm]['ip']
                    ipv6 = self.vms[vm].get('ipv6')
                    logging.info('\t\t\t[ %s ]\t %-16s %-128s' % (vm, ip, (ipv6 if ipv6 else "")))

    def port_show(self, port_type = "vm"):
        os.system("ovs-appctl "+port_type+"/port-show");

    def vm_port_show(self):
        self.port_show()

    def bridge_port_show(self):
        self.port_show("bridge")

    def vrf_show(self):
        os.system("ovs-appctl vrf/show alubr0");
    def evpn_show(self):
        os.system("ovs-appctl evpn/show alubr0");
    def print_setup_log(self):
        os.system("cat /var/tmp/setup.log");

class Menu :
    def __init__(self, menu, verbose = False):
        self.menu = menu
        self.verbose = verbose
    def run (self):
        while True:
            #print("Config-File : %s"% (ovs.cfg_file))
            if os.path.exists(logfile) and os.path.getsize(logfile) >= 2000:
               os.system("echo ""  > "+logfile)
            for m in self.menu:
                print("\t%-3s  %-32s %s " % (str(m)+\
                      '.', self.menu[m][0],\
                      ("" if len(self.menu[m]) <  3 or not self.verbose   else   '[ '+\
                       self.menu[m][2]+' ]')))
            ch = raw_input("Choose ? ")
            print ""
            if not ch.isdigit():
               continue;
            if (len(self.menu) -1) >= int(ch):
                self.menu[int(ch)][1]()

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg-file", default='config.json', help="JSON config-file")
    parser.add_argument("--vms",  default=8, help="Number of vm-vports", type=int)
    parser.add_argument("--generate", "--generate",action="store_true",\
                        help="Generate vms, ips dynamically")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Increase output verbosity")
    args = parser.parse_args()

    print args
    if args.verbose:
       logging.basicConfig(format='', level=logging.DEBUG)
       #logging.basicConfig(format='%(levelname)s:%(message)s ', level=logging.DEBUG)
    else:
       #logging.basicConfig(format='%(levelname)s:%(message)s ', level=logging.INFO)
       logging.basicConfig(format='', level=logging.INFO)
    cfg_file = args.cfg_file
    ovs = ovs_class(cfg_file, args.vms, 2, args.generate)
    menu = {
             0: [ 'ovs-restart', ovs.ovs_restart, "Restart the OVS" ],
             1: [ 'vm-port-setup', ovs.vm_port_setup,\
                                   "setup routes for vm resolution" ],
             2: [ 'bridge-port-setup', ovs.bridge_port_setup,\
                                   "setup routes for bridge port resolution" ],
             3: [ 'remote static routes', ovs.static_routes,\
                                   "configure static routes" ],
             4: [ 'fip config', ovs.fip_config,\
                                   "configure fip routes" ],
             5: [ 'vrf/show', ovs.vrf_show ],
             6: [ 'evpn/show', ovs.evpn_show ],
             7: [ 'vm/port-show', ovs.vm_port_show ],
             8: [ 'bridge/port-show', ovs.bridge_port_show ],
             9: [ 'Egress fip qos config show', ovs.print_qos_cfg ],
             10: [ 'Topology', ovs.print_topology,\
                      "current topoloy, may need to re-init in  case of auto-generate"],
             11: [ 'namespace vm dhcp', ovs.ns_vm_dhcp,\
                      "dhclient for vports, assign ipv6 if configured"],
             12: [ 're intialize', ovs.ns_reinit,\
                      "destroy and recreate namespaces, xmls, veth pairs"],
             13: [ 'Cleanup', ovs.cleanup,\
                      "destroy namespaces, xmls, veth pairs"],
        }
    menu_object = Menu(menu, args.verbose)
    menu_object.run()

if __name__ == "__main__":
   main(sys.argv[1:])
