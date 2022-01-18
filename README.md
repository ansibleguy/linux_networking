# Ansible Role - Linux Network Configuration

Ansible Role to deploy network configuration/interfaces on linux servers. 


**Tested:**
* Debian 11

## Functionality

* **Network interfaces**
  * bridges
  * bonding
  * vlans


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
  * anti-lockout via network verification script
  * support for:
    * interface bonding
    * interface bridging
    * vlan interfaces
    * traffic forwarding (_router-like_)

## Info

* **Note:** This role does not (_yet_) support IPv6!


* **Note:** Dynamic routing is available using [THIS](https://github.com/ansibleguy/infra_dynamic_routing) role


* **Note:** this role currently only supports debian systems (_ubuntu partly_)


* **Note:** Most of this functionality can be opted in or out using the main defaults file and variables!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


## Requirements

* Python 'netaddr' module on the controller.
* Community and posix collection: ```ansible-galaxy install -r requirements.yml```

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

  verification:
    enable: true
    # tests to run when a network change is done
    #   if the tests fail; the changes of the current session will be restored
    tests:
      ping:
        google_dns: '8.8.8.8'
      netcat:  # will test if the remote port is reachable
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