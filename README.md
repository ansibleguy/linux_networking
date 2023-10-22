# Ansible Role - Linux Network Configuration

Ansible Role to deploy network configuration/interfaces on linux servers. 

[![Molecule Test Status](https://badges.ansibleguy.net/linux_networking.molecule.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/molecule.sh.j2)
[![YamlLint Test Status](https://badges.ansibleguy.net/linux_networking.yamllint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/yamllint.sh.j2)
[![PyLint Test Status](https://badges.ansibleguy.net/linux_networking.pylint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/pylint.sh.j2)
[![Ansible-Lint Test Status](https://badges.ansibleguy.net/linux_networking.ansiblelint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/ansiblelint.sh.j2)
[![Ansible Galaxy](https://badges.ansibleguy.net/galaxy.badge.svg)](https://galaxy.ansible.com/ui/standalone/roles/ansibleguy/linux_networking)

**Tested:**
* Debian 11

## Install

```bash
ansible-galaxy install ansibleguy.linux_networking

# or to custom role-path
ansible-galaxy install ansibleguy.linux_networking --roles-path ./roles

# install dependencies
ansible-galaxy install -r requirements.yml
python3 -m pip install -r requirements.txt
```

## Functionality

* **Network interfaces**
  * bridges
  * bonding
  * vlans
  * ipv4 & ipv6


* **Static routing**
  * via interface up-/down-scripts
  * via startup service


* **Default opt-in**:
  * installing basic network-diagnostic tools
  * purging of orphaned interfaces
  * support for:
    * ipv6


* **Default opt-out**:
  * network startup-service to allow specific configurations
  * anti-lockout via network-validation script
  * support for:
    * interface bonding
    * interface bridging
    * vlan interfaces
    * traffic forwarding (_router-like_)

## Info


* **Note:** this role currently only supports debian systems (_ubuntu partly_)


* **Note:** Most of the role's functionality can be opted in or out.

  For all available options - see the default-config located in the main defaults-file!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Note:** The network-validation port-check only supports TCP target-ports as UDP-connectivity cannot be verified that easily.

## Usage

### Config

Define the network config as needed:
```yaml
network:
  support:
    vlan: true
    bridge: true
    bonding: true
    traffic_forwarding: true
    ipv6: true

  purge_orphaned_interfaces: true
    
  interfaces:  # for more config-details see: https://wiki.debian.org/NetworkConfiguration
    ens192:
      address: '192.168.142.90/24'
      gateway: '192.168.142.1'
      script_post-up: ['ip route add 172.16.100.0/24 dev ens192 src 192.168.142.90 via 192.168.142.10']
      aliases:
        - address: '2a09:cd41:f:42ee::1'
          gateway: '2a09:cd41:f:42ee::f'
        - '2a09:cd41:f:42ee::1'
    bridge01:
      bridge_ports: ['ens193', 'ens194']
      script_down: ['/usr/local/sbin/random_script.sh']
    ens195:  # initialize parent interface
    ens195.85:
      vlan: true
      hotplug: false
      address: '10.0.85.90/24'
      gateway: '10.0.85.1'
      nameservers: ['10.0.85.1']
    # nic bonding
    #   supported modes: 'balance-rr', 'active-backup', 'balance-xor', 'broadcast', '802.3ad', 'balance-tlb', 'balance-alb', 'lacp' (lacp => alias for 802.3ad)
    #   lacp bonding => lacp needs the switch-ports to be configured as well
    bond01:
      bond-mode: '802.3ad'
      bond-lacp-rate: 1
      bond-miimon: 100
      address: '192.168.200.10/26'
      bond-slaves: ['ens196', 'ens197']  # don't define slave interfaces on their own
    #   active-passive bonding
    bond02:
      bond-mode: 'active-passive'
      address: '192.168.210.10/26'
      bond-slaves: ['ens198', 'ens199']
      # bond-primary: 'ens198'  # if no primary is defined, it will be chosen automatically

  validation:
    enable: true
    # tests to run when a network change is done
    #   if the tests fail; the changes of the current session will be restored
    tests:
      ping:
        google_dns: '8.8.8.8'
      port:  # will test if the remote port is reachable (only TCP)
        internal_web:
          host: 'someSite.internal'
          port: 443

  startup_service:
    enable: true
    interfaces:
      tunnel01:
        type: 'vti'
        args:
          key: 32
          local: '192.168.133.1'
          remote: '192.168.133.2'
    
    routes:
      '192.168.142.1':
        - net: '10.10.40.0/22'
          metric: 50
      tunnel01:
        - net: '10.10.52.0/24'
    
    routes_cmd:
      - 'ip route add 0.0.0.0/0 via 192.168.142.254 metric 200'
```

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml
```

There are also some useful **tags** available:
* base
* interfaces
* routing

### Example

#### Basic, Bond, Vlan

**Config**
```yaml
network:
  support:
    vlan: true
    bridge: true
    bonding: true
    ipv6: false

  interfaces:
    ens192:
      address: '10.48.2.90/24'
      gateway: '10.48.2.254'
    bond01:
      bond-mode: 'balance-tlb'
      address: '10.48.2.92/24'
      bond-slaves: ['ens224', 'ens256']
    ens161:
    ens161.5:
      vlan: true
      hotplug: false
      address: '10.10.55.10/24'
      nameservers: ['10.0.55.1']
      script_post-up: ['ip route add 192.168.4.0/22 via 10.10.55.1 metric 50']
```

**Result:**
(_prettified_)
```bash
guy@ansible:~# ip a
> 2: ens192:
>     altname enp11s0
>     inet 10.48.2.90/24 brd 10.48.2.255 scope global ens192
> 3: bond01 <MASTER,UP>
>     inet 10.48.2.92/24 brd 10.48.2.255 scope global bond01
> 4: ens256: <SLAVE,UP>
>     altname enp27s0
> 5: ens224: <SLAVE,UP>
>     altname enp19s0
> 6: ens161:
>     altname enp4s0
> 7: ens161.5@ens161:
>     inet 10.10.55.10/24 brd 10.10.55.255 scope global ens161.5

guy@ansible:~# ip route show
> default via 10.48.2.254 dev ens192 onlink 
> 10.10.55.0/24 dev ens161.5 proto kernel scope link src 10.10.55.10 
> 10.48.2.0/24 dev bond01 proto kernel scope link src 10.48.2.92 linkdown 
> 10.48.2.0/24 dev ens192 proto kernel scope link src 10.48.2.90
> 192.168.4.0/22 via 10.10.55.1 dev ens161.5 metric 50

guy@ansible:~# cat /proc/net/bonding/bond01
> Ethernet Channel Bonding Driver: v5.10.0-8-amd64
> 
> Bonding Mode: transmit load balancing
> Primary Slave: None
> Currently Active Slave: ens224
> MII Status: up
> MII Polling Interval (ms): 100
> Up Delay (ms): 200
> Down Delay (ms): 200
> Peer Notification Delay (ms): 0
> 
> Slave Interface: ens224
> MII Status: up
> Speed: 10000 Mbps
> Duplex: full
> Link Failure Count: 0
> Permanent HW addr: xx:xx:xx:xx:xx:xx
> Slave queue ID: 0
> 
> Slave Interface: ens256
> MII Status: up
> Speed: 10000 Mbps
> Duplex: full
> Link Failure Count: 0
> Permanent HW addr: xx:xx:xx:xx:xx:xx
> Slave queue ID: 0
```

#### IPv6 & Aliases

**Config**
```yaml
network:
  validation:
    enable: true
  interfaces:
    eth0:
      address: '10.0.85.90/24'
      gateway: '10.0.85.1'
      aliases:
        - address: '2a09:cd41:f:42ee::1/124'
          gateway: '2a09:cd41:f:42ee::f'
        - '2a09:cd41:f:42ee::2'
```

**Result:**
(_prettified_)
```bash
guy@ansible:~# ping -6 one.one.one.one -I 2a09:cd41:f:42ee::2
> PING one.one.one.one(one.one.one.one (2606:4700:4700::1111)) from 2a09:cd41:f:42ee::2 : 56 data bytes
> 64 bytes from one.one.one.one (2606:4700:4700::1111): icmp_seq=1 ttl=58 time=14.7 ms

guy@ansible:~# ip a
> 1: lo: <LOOPBACK,UP,LOWER_UP>
> 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
>     inet 10.0.85.90/24 brd 10.0.85.255 scope global eth0
>     inet6 2a09:cd41:f:42ee::2/128 scope global deprecated 
>     inet6 2a09:cd41:f:42ee::1/124 scope global deprecated 

guy@ansible:~# cat /etc/network/interfaces.d/eth0
> # Ansible managed
> # ansibleguy.linux_networking
> 
> # for more config-details see: https://wiki.debian.org/NetworkConfiguration
> 
> auto eth0
> allow-hotplug eth0
> 
> iface eth0 inet static
>     address 194.32.76.202/24
>     gateway 194.32.76.1
>     dns-nameservers 8.8.8.8 1.1.1.1
> 
> # Interface aliases (additional ips)
> auto eth0:1
> allow-hotplug eth0:1
> iface eth0:1 inet6 static
>     address 2a09:cd41:f:42ee::1/124
>     gateway 2a09:cd41:f:42ee::f
> 
> auto eth0:2
> allow-hotplug eth0:2
> iface eth0:2 inet6 static
>     address 2a09:cd41:f:42ee::2

```